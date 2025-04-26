"""
Wind Plots Module for the Precision Rifle Load Development App
Provides visualization of wind drift based on MOA values at different distances.
Supports multiple profiles for different calibers and bullet configurations.
"""

import os
import sys
import yaml
import numpy as np
import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg which works with both PyQt5 and PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QFormLayout, QLineEdit, QGroupBox, QScrollArea,
    QMessageBox, QDoubleSpinBox, QSizePolicy, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QDialogButtonBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal

from utils.settings_manager import SettingsManager


# Default profiles to use if no saved profiles exist
DEFAULT_PROFILES = [
    {
        "name": ".223 Rem 75gr @ 2700fps",
        "description": "Wind drift profile for .223 Remington with 75gr bullets at 2700fps",
        "distances": [
            {"distance": 300, "moa_at_7ms": 3.7},
            {"distance": 500, "moa_at_7ms": 7.8},
            {"distance": 700, "moa_at_7ms": 12.4},
            {"distance": 1000, "moa_at_7ms": 20.0}
        ]
    },
    {
        "name": "6.5 Creedmoor 140gr @ 2800fps",
        "description": "Wind drift profile for 6.5 Creedmoor with 140gr bullets at 2800fps",
        "distances": [
            {"distance": 300, "moa_at_7ms": 2.8},
            {"distance": 500, "moa_at_7ms": 5.9},
            {"distance": 700, "moa_at_7ms": 9.2},
            {"distance": 1000, "moa_at_7ms": 15.3}
        ]
    }
]


class ProfileDialog(QDialog):
    """Dialog for creating or editing a wind plot profile"""
    
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        
        self.setWindowTitle("Wind Plot Profile")
        self.setMinimumWidth(400)
        
        # Initialize with existing profile data if provided
        self.profile = profile or {"name": "", "description": "", "distances": []}
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Profile name
        name_layout = QFormLayout()
        self.name_edit = QLineEdit(self.profile["name"])
        name_layout.addRow("Profile Name:", self.name_edit)
        layout.addLayout(name_layout)
        
        # Profile description
        desc_layout = QFormLayout()
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(self.profile["description"])
        self.desc_edit.setMaximumHeight(80)
        desc_layout.addRow("Description:", self.desc_edit)
        layout.addLayout(desc_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_profile_data(self):
        """Get the profile data from the dialog"""
        self.profile["name"] = self.name_edit.text()
        self.profile["description"] = self.desc_edit.toPlainText()
        return self.profile


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding plots in PyQt"""
    
    def __init__(self, parent=None, width=10, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Make the canvas expandable
        FigureCanvas.setSizePolicy(
            self,
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        FigureCanvas.updateGeometry(self)


class WindPlotWidget(QWidget):
    """Widget for creating and displaying wind drift plots"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get settings manager
        self.settings_manager = SettingsManager.get_instance()
        
        # Initialize data structures
        self.profiles = []  # List of profiles
        self.current_profile_index = 0  # Index of the currently selected profile
        
        # Load profiles from file
        self.load_profiles()
        
        # Set up the UI
        self.setup_ui()
        
        # Populate the profile dropdown
        self.populate_profile_dropdown()
        
        # Load the current profile data
        self.load_current_profile()
    
    def get_profiles_file_path(self):
        """Get the path to the profiles file"""
        # Platform-specific config directory
        if sys.platform == 'win32':
            config_dir = os.path.join(os.environ['APPDATA'], 'PrecisionRifleLoadDevelopment')
        elif sys.platform == 'darwin':
            config_dir = os.path.expanduser('~/Library/Application Support/PrecisionRifleLoadDevelopment')
        else:
            config_dir = os.path.expanduser('~/.config/precision-rifle-load-development')
        
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Return the path to the profiles file
        return os.path.join(config_dir, "wind_plot_profiles.yaml")
    
    def load_profiles(self):
        """Load profiles from the YAML file"""
        profiles_file = self.get_profiles_file_path()
        
        try:
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and "profiles" in data and isinstance(data["profiles"], list):
                        self.profiles = data["profiles"]
                    else:
                        # If the file exists but doesn't contain valid data, use default profiles
                        self.profiles = DEFAULT_PROFILES
                        self.save_profiles()  # Save the default profiles to the file
            else:
                # If the file doesn't exist, use default profiles
                self.profiles = DEFAULT_PROFILES
                self.save_profiles()  # Save the default profiles to the file
        except Exception as e:
            print(f"Error loading profiles: {e}")
            # If there's an error, use default profiles
            self.profiles = DEFAULT_PROFILES
            self.save_profiles()  # Try to save the default profiles to the file
    
    def save_profiles(self):
        """Save profiles to the YAML file"""
        profiles_file = self.get_profiles_file_path()
        
        try:
            with open(profiles_file, 'w') as f:
                yaml.dump({"profiles": self.profiles}, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving profiles: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save profiles: {e}")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create a scroll area for the entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Create a widget to hold all content
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        
        # Add header
        header_label = QLabel("Wind Drift Plot Generator")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        content_layout.addWidget(header_label)
        
        # Add description
        description_text = (
            "This tool creates precision wind drift reference charts for long-range shooting. "
            "Create profiles for different calibers and bullet configurations, and generate "
            "plots showing wind drift based on wind speed and direction."
        )
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        content_layout.addWidget(description_label)
        
        # Profile selection section
        profile_section = QGroupBox("Profile Management")
        profile_layout = QVBoxLayout(profile_section)
        
        # Profile selection dropdown and buttons
        profile_header_layout = QHBoxLayout()
        
        # Profile dropdown
        profile_label = QLabel("Select Profile:")
        profile_header_layout.addWidget(profile_label)
        
        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.on_profile_selected)
        profile_header_layout.addWidget(self.profile_combo, 1)
        
        # Profile management buttons
        new_profile_button = QPushButton("New")
        new_profile_button.clicked.connect(self.create_new_profile)
        profile_header_layout.addWidget(new_profile_button)
        
        edit_profile_button = QPushButton("Edit")
        edit_profile_button.clicked.connect(self.edit_current_profile)
        profile_header_layout.addWidget(edit_profile_button)
        
        delete_profile_button = QPushButton("Delete")
        delete_profile_button.clicked.connect(self.delete_current_profile)
        profile_header_layout.addWidget(delete_profile_button)
        
        profile_layout.addLayout(profile_header_layout)
        
        # Profile description
        self.profile_description = QLabel()
        self.profile_description.setWordWrap(True)
        self.profile_description.setStyleSheet("font-style: italic;")
        profile_layout.addWidget(self.profile_description)
        
        content_layout.addWidget(profile_section)
        
        # Create input section
        input_section = QGroupBox("Distance Parameters")
        input_layout = QVBoxLayout(input_section)
        
        # Create table for distance and MOA inputs
        self.input_table = QTableWidget(0, 2)
        self.input_table.setHorizontalHeaderLabels(["Distance (m)", "MOA at 7 m/s, 90°"])
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        input_layout.addWidget(self.input_table)
        
        # Add/Remove row buttons
        buttons_layout = QHBoxLayout()
        
        add_row_button = QPushButton("Add Distance")
        add_row_button.clicked.connect(self.add_input_row)
        buttons_layout.addWidget(add_row_button)
        
        remove_row_button = QPushButton("Remove Selected")
        remove_row_button.clicked.connect(self.remove_input_row)
        buttons_layout.addWidget(remove_row_button)
        
        input_layout.addLayout(buttons_layout)
        
        # Generate plot button
        generate_button = QPushButton("Generate Wind Plots")
        generate_button.clicked.connect(self.generate_plots)
        generate_button.setStyleSheet("font-weight: bold; padding: 8px;")
        input_layout.addWidget(generate_button)
        
        content_layout.addWidget(input_section)
        
        # Create tabs for plots
        self.plot_tabs = QTabWidget()
        content_layout.addWidget(self.plot_tabs)
    
    def populate_profile_dropdown(self):
        """Populate the profile dropdown with available profiles"""
        self.profile_combo.clear()
        
        for profile in self.profiles:
            self.profile_combo.addItem(profile["name"])
        
        # Set the current index to the previously selected profile
        if self.profiles and 0 <= self.current_profile_index < len(self.profiles):
            self.profile_combo.setCurrentIndex(self.current_profile_index)
    
    def on_profile_selected(self, index):
        """Handle profile selection change"""
        if 0 <= index < len(self.profiles):
            self.current_profile_index = index
            self.load_current_profile()
    
    def load_current_profile(self):
        """Load the currently selected profile data"""
        if not self.profiles:
            return
        
        profile = self.profiles[self.current_profile_index]
        
        # Update profile description
        self.profile_description.setText(profile["description"])
        
        # Clear existing rows
        while self.input_table.rowCount() > 0:
            self.input_table.removeRow(0)
        
        # Add rows for each distance in the profile
        for distance_data in profile["distances"]:
            row = self.input_table.rowCount()
            self.input_table.insertRow(row)
            
            # Distance input
            distance_spin = QDoubleSpinBox()
            distance_spin.setRange(100, 2000)
            distance_spin.setValue(distance_data["distance"])
            distance_spin.setSuffix(" m")
            distance_spin.setDecimals(0)
            distance_spin.setSingleStep(100)
            self.input_table.setCellWidget(row, 0, distance_spin)
            
            # MOA input
            moa_spin = QDoubleSpinBox()
            moa_spin.setRange(0.1, 100)
            moa_spin.setValue(distance_data["moa_at_7ms"])
            moa_spin.setSuffix(" MOA")
            moa_spin.setDecimals(1)
            moa_spin.setSingleStep(0.1)
            self.input_table.setCellWidget(row, 1, moa_spin)
    
    def create_new_profile(self):
        """Create a new profile"""
        dialog = ProfileDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the profile data from the dialog
            new_profile = dialog.get_profile_data()
            
            # Add empty distances list
            new_profile["distances"] = []
            
            # Add the profile to the list
            self.profiles.append(new_profile)
            
            # Save the profiles
            self.save_profiles()
            
            # Update the dropdown
            self.populate_profile_dropdown()
            
            # Select the new profile
            self.profile_combo.setCurrentIndex(len(self.profiles) - 1)
    
    def edit_current_profile(self):
        """Edit the current profile"""
        if not self.profiles:
            return
        
        # Get the current profile
        profile = self.profiles[self.current_profile_index]
        
        # Create a dialog with the current profile data
        dialog = ProfileDialog(self, profile)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the updated profile data from the dialog
            updated_profile = dialog.get_profile_data()
            
            # Update the profile in the list
            self.profiles[self.current_profile_index] = updated_profile
            
            # Save the profiles
            self.save_profiles()
            
            # Update the dropdown
            self.populate_profile_dropdown()
            
            # Update the profile description
            self.profile_description.setText(updated_profile["description"])
    
    def delete_current_profile(self):
        """Delete the current profile"""
        if not self.profiles:
            return
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the profile '{self.profiles[self.current_profile_index]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Remove the profile from the list
            del self.profiles[self.current_profile_index]
            
            # Save the profiles
            self.save_profiles()
            
            # Update the dropdown
            self.populate_profile_dropdown()
            
            # Select the first profile if available
            if self.profiles:
                self.current_profile_index = 0
                self.profile_combo.setCurrentIndex(0)
                self.load_current_profile()
            else:
                # If no profiles remain, create a default one
                self.profiles = DEFAULT_PROFILES[:1]  # Just use the first default profile
                self.save_profiles()
                self.populate_profile_dropdown()
                self.load_current_profile()
    
    def add_input_row(self):
        """Add a new row to the input table"""
        row = self.input_table.rowCount()
        self.input_table.insertRow(row)
        
        # Distance input (double spin box)
        distance_spin = QDoubleSpinBox()
        distance_spin.setRange(100, 2000)
        distance_spin.setValue(300 if row == 0 else 700 if row == 1 else 1000)
        distance_spin.setSuffix(" m")
        distance_spin.setDecimals(0)
        distance_spin.setSingleStep(100)
        self.input_table.setCellWidget(row, 0, distance_spin)
        
        # MOA input (double spin box)
        moa_spin = QDoubleSpinBox()
        moa_spin.setRange(0.1, 100)
        moa_spin.setValue(3.7 if row == 0 else 12.4 if row == 1 else 20.0)
        moa_spin.setSuffix(" MOA")
        moa_spin.setDecimals(1)
        moa_spin.setSingleStep(0.1)
        self.input_table.setCellWidget(row, 1, moa_spin)
    
    def remove_input_row(self):
        """Remove the selected row from the input table"""
        selected_rows = self.input_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a row to remove.")
            return
        
        # Remove rows in reverse order to avoid index issues
        for index in sorted([row.row() for row in selected_rows], reverse=True):
            self.input_table.removeRow(index)
        
        # Ensure at least one row remains
        if self.input_table.rowCount() == 0:
            self.add_input_row()
    
    def collect_input_data(self):
        """Collect input data from the table and update the current profile"""
        distances = []
        moa_values = {}
        distance_data_list = []
        
        for row in range(self.input_table.rowCount()):
            distance_widget = self.input_table.cellWidget(row, 0)
            moa_widget = self.input_table.cellWidget(row, 1)
            
            if distance_widget and moa_widget:
                distance = int(distance_widget.value())
                moa = float(moa_widget.value())
                
                # Check for duplicate distances
                if distance in distances:
                    QMessageBox.warning(
                        self, 
                        "Duplicate Distance", 
                        f"Distance {distance}m appears more than once. Please use unique distances."
                    )
                    return None, None
                
                distances.append(distance)
                moa_values[distance] = moa
                distance_data_list.append({"distance": distance, "moa_at_7ms": moa})
        
        # Sort distances
        distances.sort()
        distance_data_list.sort(key=lambda x: x["distance"])
        
        # Update the current profile with the new distance data
        if self.profiles:
            self.profiles[self.current_profile_index]["distances"] = distance_data_list
            self.save_profiles()
        
        return distances, moa_values
    
    def generate_plots(self):
        """Generate wind drift plots for each distance"""
        # Collect input data and update the current profile
        distances, moa_values = self.collect_input_data()
        if not distances or not moa_values:
            return
        
        # Clear existing tabs
        while self.plot_tabs.count() > 0:
            self.plot_tabs.removeTab(0)
        
        # Create a plot for each distance
        for distance in distances:
            moa_drift = moa_values[distance]
            
            # Create a tab for this distance
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Create the plot
            canvas = MatplotlibCanvas(self, width=10, height=6, dpi=100)
            toolbar = NavigationToolbar(canvas, self)
            
            # Draw the wind drift plot
            self.draw_wind_plot(canvas, distance, moa_drift)
            
            # Add toolbar and canvas to the tab
            tab_layout.addWidget(toolbar)
            tab_layout.addWidget(canvas)
            
            # Add the tab to the tab widget
            self.plot_tabs.addTab(tab, f"{distance}m")
        
        # Switch to the first tab
        if self.plot_tabs.count() > 0:
            self.plot_tabs.setCurrentIndex(0)
    
    def draw_wind_plot(self, canvas, distance, moa_drift_at_7ms):
        """Draw the wind drift plot on the given canvas"""
        # Clear the figure
        canvas.fig.clear()
        
        # Create axes
        ax = canvas.fig.add_subplot(111)
        ax.set_aspect('equal')
        
        # === CONFIGURATION ===
        max_speed = 8  # wind speed in m/s (horizontal axis goes from -8 to +8)
        num_circles = 7  # number of concentric wind speed arcs (one per m/s, up to 7 m/s)
        moa_bar_width = 0.25  # MOA increment width for alternating colour bars (4 bars = 1 MOA)
        
        # === DERIVED PARAMETERS ===
        moa_to_x = max_speed / moa_drift_at_7ms  # conversion factor: how many m/s per MOA
        x_to_moa = 1 / moa_to_x  # inverse: how many MOA per m/s
        
        # Calculate the width of one MOA in the x-axis units (m/s)
        one_moa_width = moa_to_x
        
        # Calculate the width of one bar in the x-axis units
        bar_width_x = one_moa_width * moa_bar_width
        
        # === GENERATE MOA GRID POSITIONS ===
        # Calculate the maximum number of MOA ticks needed
        max_moa = int(np.ceil(max_speed * x_to_moa))
        
        # Generate MOA positions for vertical lines (at each full MOA)
        moa_major_ticks = np.arange(-max_moa, max_moa + 1, 1)
        moa_major_positions = moa_major_ticks * moa_to_x
        
        # Generate positions for colored bars (4 bars per MOA)
        # Start with positions for full MOA values
        bar_positions = []
        for moa in np.arange(-max_moa, max_moa + 1, 0.25):
            bar_positions.append(moa * moa_to_x)
        
        # === DRAW COLOURED BACKGROUND BARS ===
        for i in range(len(bar_positions) - 1):
            start_x = bar_positions[i]
            end_x = bar_positions[i + 1]
            color = 'green' if i % 2 == 0 else 'yellow'
            ax.fill_between([start_x, end_x], 0, max_speed, color=color, alpha=0.3)
        
        # === DRAW BOLD LINES FOR EACH FULL MOA ===
        for x in moa_major_positions:
            ax.plot([x, x], [0, max_speed], color='black', lw=1.2)
        
        # === DRAW SEMI-CIRCLES FOR WIND SPEED MAGNITUDES ===
        theta = np.linspace(0, np.pi, 300)
        for r in range(1, num_circles + 1):
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            ax.plot(x, y, color='red', lw=1)
        
        # === DRAW WIND ANGLE LINES AND LABELS (0° to 90° and mirrored) ===
        angles_deg = [0, 15, 30, 45, 60, 75, 90]
        angles_rad = np.deg2rad(angles_deg)
        for angle_deg, angle_rad in zip(angles_deg, angles_rad):
            label = f"{90 - angle_deg}°"
            # Use 7 m/s for the angle lines to match the circles
            angle_line_length = 7
            # Right side
            x_r = angle_line_length * np.cos(angle_rad)
            y_r = angle_line_length * np.sin(angle_rad)
            ax.plot([0, x_r], [0, y_r], color='red', lw=1)
            ax.text(x_r * 1.05, y_r * 1.05, label, ha='left', va='bottom', fontsize=9)
            # Left side (mirror)
            x_l = -x_r
            ax.plot([0, x_l], [0, y_r], color='red', lw=1)
            ax.text(x_l * 1.05, y_r * 1.05, label, ha='right', va='bottom', fontsize=9)
        
        # === DRAW SHORT TICK MARKS EVERY 0.25 MOA ===
        for x in bar_positions:
            ax.plot([x, x], [0, -0.4], color='black', lw=1)
        
        # === LABEL THE MOA SCALE BELOW THE X-AXIS ===
        for moa in moa_major_ticks:
            x = moa * moa_to_x
            ax.text(x, -0.6, f"{moa:.0f}", ha='center', va='top', fontsize=8)
        
        # === AXIS SETTINGS ===
        ax.set_xlim(-max_speed, max_speed)
        ax.set_ylim(-1, max_speed)
        ax.set_xticks(np.arange(-max_speed, max_speed + 1, 1))  # wind speed ticks
        ax.set_yticks(np.arange(0, max_speed + 1, 1))           # wind magnitude (y-axis)
        ax.set_xlabel('Wind Speed (m/s)', fontsize=12)
        ax.set_ylabel('Wind Speed (m/s)', fontsize=12)
        
        # === MAIN AXIS LINES ===
        ax.axhline(0, color='black', lw=1)
        ax.axvline(0, color='black', lw=1)
        
        # === FINAL FORMATTING ===
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title(f'Wind Drift Reference Chart for {distance}m\n7 m/s at 90° = {moa_drift_at_7ms} MOA', fontsize=13)
        
        # Update the canvas
        canvas.fig.tight_layout()
        canvas.draw()
