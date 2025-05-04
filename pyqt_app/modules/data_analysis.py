"""
Data Analysis Module for the Reloading App
Provides visualization and analysis of test data
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QSlider, QPushButton, QTableView, QSplitter, QTabWidget,
    QGroupBox, QFormLayout, QLineEdit, QCheckBox, QSizePolicy,
    QDateEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QModelIndex, pyqtSignal, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem

import matplotlib
matplotlib.use('QtAgg')  # Use QtAgg which works with both PyQt5 and PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import pandas as pd
import numpy as np
import os
import yaml
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_all_test_data
from utils.settings_manager import SettingsManager


class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding plots in PyQt"""
    
    def __init__(self, parent=None, width=15, height=12, dpi=100):  # Tripled width and height
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


class TestDataModel(QAbstractTableModel):
    """Model for displaying test data in a table view"""
    
    selectionChanged = pyqtSignal()
    
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else pd.DataFrame()
        self._display_columns = [
            # Test identification
            "test_id", "date", "distance_m", 
            
            # Platform
            "calibre", "rifle", "barrel_length_in", "twist_rate",
            
            # Components
            "bullet_brand", "bullet_model", "bullet_weight_gr", "bullet_lot",
            "powder_brand", "powder_model", "powder_charge_gr", "powder_lot",
            "coal_in", "b2o_in", 
            "case_brand", "case_lot", "neck_turned", "brass_sizing", "bushing_size", "shoulder_bump",
            "primer_brand", "primer_model", "primer_lot",
            
            # Results
            "group_es_mm", "group_es_moa", "mean_radius_mm", "mean_radius_moa",
            "group_es_x_mm", "group_es_x_moa", "group_es_y_mm", "group_es_y_moa", 
            "poi_x_mm", "poi_x_moa", "poi_y_mm", "poi_y_moa",
            "avg_velocity_fps", "sd_fps", "es_fps", 
            
            # Environment
            "temperature_c", "humidity_pct", "pressure_hpa", 
            "wind_speed_ms", "wind_direction", "light_conditions",
            
            # Shots count
            "shots"
        ]
        
        # Ensure all columns exist in the dataframe
        for col in self._display_columns:
            if col not in self._data.columns:
                self._data[col] = None
        
        # Add selection column (not displayed in the columns list)
        self._data['selected'] = True
        
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()):
        # Add 1 for the checkbox column
        return len(self._display_columns) + 1
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        # Handle checkbox column (first column)
        if index.column() == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                # Return the checkbox state
                try:
                    return Qt.CheckState.Checked if self._data.iloc[index.row()]['selected'] else Qt.CheckState.Unchecked
                except (KeyError, IndexError):
                    return Qt.CheckState.Checked
            return None
        
        # For other columns, adjust the column index
        actual_column = index.column() - 1
        if actual_column < 0 or actual_column >= len(self._display_columns):
            return None
        
        column_name = self._display_columns[actual_column]
        
        # Handle display role for data columns
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                value = self._data.iloc[index.row()][column_name]
                
                # Format numeric values
                if isinstance(value, (int, float)):
                    if column_name in ["group_es_mm", "group_es_moa", "mean_radius_mm", "group_es_x_mm", "group_es_y_mm", "poi_x_mm", "poi_y_mm"]:
                        return f"{value:.2f}"
                    elif column_name in ["avg_velocity_fps", "sd_fps", "es_fps"]:
                        return f"{value:.1f}"
                    elif column_name == "powder_charge_gr":
                        return f"{value:.2f}"
                    elif column_name in ["b2o_in", "coal_in"]:
                        return f"{value:.3f}"
                    else:
                        return str(value)
                
                return str(value)
            except (KeyError, ValueError, IndexError) as e:
                # If the column doesn't exist or there's an error, return an empty string
                return ""
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "Select"
            
            # Return user-friendly column names for data columns
            column_name = self._display_columns[section - 1]
            # Convert snake_case to Title Case with spaces
            return " ".join(word.capitalize() for word in column_name.split("_"))
        
        return super().headerData(section, orientation, role)
    
    def flags(self, index):
        """Return the item flags for the given index"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        
        # Make the checkbox column editable and user-checkable
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable
        
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Set the data for the given index"""
        if not index.isValid():
            return False
        
        # Handle checkbox state changes
        if index.column() == 0:
            row = index.row()
            
            # Update the selected state in the dataframe
            try:
                # Always toggle the current state when clicked
                current_state = self._data.iloc[row]['selected']
                new_state = not current_state
                
                # Update the dataframe
                self._data.iloc[row, self._data.columns.get_loc('selected')] = new_state
                print(f"Toggling row {row} selection from {current_state} to {new_state}")
                
                # Emit dataChanged signal to update the view
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
                
                # Emit the selectionChanged signal
                self.selectionChanged.emit()
                
                return True
            except (KeyError, IndexError) as e:
                print(f"Error setting selection state: {e}")
                return False
        
        return False
    
    def update_data(self, data):
        """Update the model with new data"""
        self.beginResetModel()
        self._data = data
        self.endResetModel()


class DataAnalysisWidget(QWidget):
    """Widget for data analysis and visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize data
        self.all_data = pd.DataFrame()
        self.filtered_data = pd.DataFrame()
        
        # For backward compatibility with existing code
        self.group_min = None
        self.group_max = None
        self.velocity_min = None
        self.velocity_max = None
        
        # Define plottable parameters
        self.plottable_params = {
            # Load data parameters
            "powder_charge_gr": "Powder Charge (gr)",
            "coal_in": "COAL (in)",
            "b2o_in": "B2O (in)",
            "bullet_weight_gr": "Bullet Weight (gr)",
            
            # Results parameters
            "group_es_mm": "Group ES (mm)",
            "group_es_moa": "Group ES (MOA)",
            "mean_radius_mm": "Mean Radius (mm)",
            "group_es_x_mm": "Group ES Width-X (mm)",
            "group_es_y_mm": "Group ES Height-Y (mm)",
            "poi_x_mm": "POA Horizontal-X (mm)",
            "poi_y_mm": "POA Vertical-Y (mm)",
            "avg_velocity_fps": "Avg Velocity (fps)",
            "sd_fps": "SD Velocity (fps)",
            "es_fps": "ES Velocity (fps)",
            "shots": "Number of Shots"
        }
        
        # Flag to temporarily disable auto-ranging when filters are being applied
        self.disable_auto_range = False
        
        # Configuration for auto-range filters
        # Format: {
        #   'column_name': {
        #     'type': 'date' or 'numeric',
        #     'min_widget': reference to min widget,
        #     'max_widget': reference to max widget,
        #     'enabled': True/False
        #   }
        # }
        self.auto_range_filters = {}
        
        # Set up the UI
        self.setup_ui()
        
        # Load test data
        self.load_data()
    
    def register_auto_range_filter(self, column_name, filter_type, min_widget, max_widget, enabled=True):
        """Register a filter for auto-ranging
        
        Args:
            column_name (str): The name of the column in the dataframe
            filter_type (str): The type of filter ('date' or 'numeric')
            min_widget: The widget for the minimum value
            max_widget: The widget for the maximum value
            enabled (bool): Whether auto-ranging is enabled for this filter
        """
        self.auto_range_filters[column_name] = {
            'type': filter_type,
            'min_widget': min_widget,
            'max_widget': max_widget,
            'enabled': enabled
        }
    
    def update_filter_ranges(self, df):
        """Update filter ranges based on the current filtered data
        
        Args:
            df (DataFrame): The dataframe to use for calculating ranges
        """
        if self.disable_auto_range or df.empty:
            return
        
        for column_name, filter_config in self.auto_range_filters.items():
            if not filter_config['enabled'] or column_name not in df.columns:
                continue
            
            # Get min and max values from the dataframe
            try:
                if filter_config['type'] == 'date':
                    # For date filters
                    min_date = df[column_name].min()
                    max_date = df[column_name].max()
                    
                    if pd.notna(min_date) and pd.notna(max_date):
                        # Convert to QDate
                        min_qdate = QDate.fromString(min_date, "yyyy-MM-dd")
                        max_qdate = QDate.fromString(max_date, "yyyy-MM-dd")
                        
                        # Update the widgets
                        filter_config['min_widget'].setDate(min_qdate)
                        filter_config['max_widget'].setDate(max_qdate)
                
                elif filter_config['type'] == 'numeric':
                    # For numeric filters
                    min_value = df[column_name].min()
                    max_value = df[column_name].max()
                    
                    if pd.notna(min_value) and pd.notna(max_value):
                        # Update the widgets
                        filter_config['min_widget'].setText(str(min_value))
                        filter_config['max_widget'].setText(str(max_value))
            
            except Exception as e:
                print(f"Error updating filter range for {column_name}: {e}")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)
        
        # Top section: Filters
        filter_widget = QWidget()
        filter_layout = QVBoxLayout(filter_widget)
        
        # Filter header
        filter_header = QHBoxLayout()
        filter_label = QLabel("Filter Tests")
        filter_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        filter_header.addWidget(filter_label)
        
        # Reset button
        reset_button = QPushButton("Reset All Filters")
        reset_button.clicked.connect(self.reset_filters)
        filter_header.addStretch()
        filter_header.addWidget(reset_button)
        
        filter_layout.addLayout(filter_header)
        
        # Filter groups in horizontal layout
        filter_groups = QHBoxLayout()
        
        # Left column for Test Info and Platform
        left_column = QVBoxLayout()
        
        # Test Info filters
        test_info_group = QGroupBox("Test Info")
        test_info_layout = QFormLayout(test_info_group)
        
        # Date range filter with calendar popups
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())  # Default to today
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.date_to)
        test_info_layout.addRow("Date Range:", date_layout)
        
        # Distance filter
        self.distance_combo = QComboBox()
        self.distance_combo.addItems(["All", "100m", "200m", "300m"])
        test_info_layout.addRow("Distance:", self.distance_combo)
        
        left_column.addWidget(test_info_group)
        
        # Platform filters
        platform_group = QGroupBox("Platform")
        platform_layout = QFormLayout(platform_group)
        
        # Calibre filter
        self.calibre_combo = QComboBox()
        self.calibre_combo.addItem("All")
        platform_layout.addRow("Calibre:", self.calibre_combo)
        
        # Rifle filter
        self.rifle_combo = QComboBox()
        self.rifle_combo.addItem("All")
        platform_layout.addRow("Rifle:", self.rifle_combo)
        
        left_column.addWidget(platform_group)
        
        filter_groups.addLayout(left_column)
        
        # Ammunition filters
        ammo_group = QGroupBox("Ammunition")
        ammo_layout = QFormLayout(ammo_group)
        
        # Bullet brand filter
        self.bullet_brand_combo = QComboBox()
        self.bullet_brand_combo.addItem("All")
        ammo_layout.addRow("Bullet Brand:", self.bullet_brand_combo)
        
        # Bullet weight filter
        self.bullet_weight_min = QLineEdit()
        self.bullet_weight_max = QLineEdit()
        bullet_weight_layout = QHBoxLayout()
        bullet_weight_layout.addWidget(self.bullet_weight_min)
        bullet_weight_layout.addWidget(QLabel("to"))
        bullet_weight_layout.addWidget(self.bullet_weight_max)
        ammo_layout.addRow("Bullet Weight (gr):", bullet_weight_layout)
        
        # Powder brand filter
        self.powder_brand_combo = QComboBox()
        self.powder_brand_combo.addItem("All")
        ammo_layout.addRow("Powder Brand:", self.powder_brand_combo)
        
        # Powder charge range filter
        self.charge_min = QLineEdit()
        self.charge_max = QLineEdit()
        charge_layout = QHBoxLayout()
        charge_layout.addWidget(self.charge_min)
        charge_layout.addWidget(QLabel("to"))
        charge_layout.addWidget(self.charge_max)
        ammo_layout.addRow("Charge (gr):", charge_layout)
        
        # COAL filter
        self.coal_min = QLineEdit()
        self.coal_max = QLineEdit()
        coal_layout = QHBoxLayout()
        coal_layout.addWidget(self.coal_min)
        coal_layout.addWidget(QLabel("to"))
        coal_layout.addWidget(self.coal_max)
        ammo_layout.addRow("COAL (in):", coal_layout)
        
        # B2O filter
        self.b2o_min = QLineEdit()
        self.b2o_max = QLineEdit()
        b2o_layout = QHBoxLayout()
        b2o_layout.addWidget(self.b2o_min)
        b2o_layout.addWidget(QLabel("to"))
        b2o_layout.addWidget(self.b2o_max)
        ammo_layout.addRow("B2O (in):", b2o_layout)
        
        filter_groups.addWidget(ammo_group)
        
        # Results Target filters - split into two columns
        results_target_container = QWidget()
        results_target_container_layout = QHBoxLayout(results_target_container)
        
        # Left column of Results Target
        results_target_left = QGroupBox("Results Target (1/2)")
        results_target_left_layout = QFormLayout(results_target_left)
        
        # Number of shots filter
        self.shots_min = QLineEdit()
        self.shots_max = QLineEdit()
        shots_layout = QHBoxLayout()
        shots_layout.addWidget(self.shots_min)
        shots_layout.addWidget(QLabel("to"))
        shots_layout.addWidget(self.shots_max)
        results_target_left_layout.addRow("Number of shots:", shots_layout)
        
        # Group size range filter (renamed to Group ES)
        self.group_es_min = QLineEdit()
        self.group_es_max = QLineEdit()
        group_es_layout = QHBoxLayout()
        group_es_layout.addWidget(self.group_es_min)
        group_es_layout.addWidget(QLabel("to"))
        group_es_layout.addWidget(self.group_es_max)
        results_target_left_layout.addRow("Group ES (mm):", group_es_layout)
        
        # Group ES MOA filter
        self.group_es_moa_min = QLineEdit()
        self.group_es_moa_max = QLineEdit()
        group_es_moa_layout = QHBoxLayout()
        group_es_moa_layout.addWidget(self.group_es_moa_min)
        group_es_moa_layout.addWidget(QLabel("to"))
        group_es_moa_layout.addWidget(self.group_es_moa_max)
        results_target_left_layout.addRow("Group ES (MOA):", group_es_moa_layout)
        
        # Mean Radius filter
        self.mean_radius_min = QLineEdit()
        self.mean_radius_max = QLineEdit()
        mean_radius_layout = QHBoxLayout()
        mean_radius_layout.addWidget(self.mean_radius_min)
        mean_radius_layout.addWidget(QLabel("to"))
        mean_radius_layout.addWidget(self.mean_radius_max)
        results_target_left_layout.addRow("Mean Radius (mm):", mean_radius_layout)
        
        results_target_container_layout.addWidget(results_target_left)
        
        # Right column of Results Target
        results_target_right = QGroupBox("Results Target (2/2)")
        results_target_right_layout = QFormLayout(results_target_right)
        
        # Group ES Width-X filter
        self.group_es_x_min = QLineEdit()
        self.group_es_x_max = QLineEdit()
        group_es_x_layout = QHBoxLayout()
        group_es_x_layout.addWidget(self.group_es_x_min)
        group_es_x_layout.addWidget(QLabel("to"))
        group_es_x_layout.addWidget(self.group_es_x_max)
        results_target_right_layout.addRow("Group ES Width-X (mm):", group_es_x_layout)
        
        # Group ES Height-Y filter
        self.group_es_y_min = QLineEdit()
        self.group_es_y_max = QLineEdit()
        group_es_y_layout = QHBoxLayout()
        group_es_y_layout.addWidget(self.group_es_y_min)
        group_es_y_layout.addWidget(QLabel("to"))
        group_es_y_layout.addWidget(self.group_es_y_max)
        results_target_right_layout.addRow("Group ES Height-Y (mm):", group_es_y_layout)
        
        # POA Horizontal-X filter
        self.poi_x_min = QLineEdit()
        self.poi_x_max = QLineEdit()
        poi_x_layout = QHBoxLayout()
        poi_x_layout.addWidget(self.poi_x_min)
        poi_x_layout.addWidget(QLabel("to"))
        poi_x_layout.addWidget(self.poi_x_max)
        results_target_right_layout.addRow("POA Horizontal-X (mm):", poi_x_layout)
        
        # POA Vertical-Y filter
        self.poi_y_min = QLineEdit()
        self.poi_y_max = QLineEdit()
        poi_y_layout = QHBoxLayout()
        poi_y_layout.addWidget(self.poi_y_min)
        poi_y_layout.addWidget(QLabel("to"))
        poi_y_layout.addWidget(self.poi_y_max)
        results_target_right_layout.addRow("POA Vertical-Y (mm):", poi_y_layout)
        
        results_target_container_layout.addWidget(results_target_right)
        
        filter_groups.addWidget(results_target_container)
        
        # Results Velocity filters
        results_velocity_group = QGroupBox("Results Velocity")
        results_velocity_layout = QFormLayout(results_velocity_group)
        
        # Avg Velocity filter (renamed)
        self.avg_velocity_min = QLineEdit()
        self.avg_velocity_max = QLineEdit()
        avg_velocity_layout = QHBoxLayout()
        avg_velocity_layout.addWidget(self.avg_velocity_min)
        avg_velocity_layout.addWidget(QLabel("to"))
        avg_velocity_layout.addWidget(self.avg_velocity_max)
        results_velocity_layout.addRow("Avg Velocity (f/s):", avg_velocity_layout)
        
        # SD Velocity filter
        self.sd_velocity_min = QLineEdit()
        self.sd_velocity_max = QLineEdit()
        sd_velocity_layout = QHBoxLayout()
        sd_velocity_layout.addWidget(self.sd_velocity_min)
        sd_velocity_layout.addWidget(QLabel("to"))
        sd_velocity_layout.addWidget(self.sd_velocity_max)
        results_velocity_layout.addRow("SD Velocity (f/s):", sd_velocity_layout)
        
        # ES Velocity filter
        self.es_velocity_min = QLineEdit()
        self.es_velocity_max = QLineEdit()
        es_velocity_layout = QHBoxLayout()
        es_velocity_layout.addWidget(self.es_velocity_min)
        es_velocity_layout.addWidget(QLabel("to"))
        es_velocity_layout.addWidget(self.es_velocity_max)
        results_velocity_layout.addRow("ES Velocity (f/s):", es_velocity_layout)
        
        filter_groups.addWidget(results_velocity_group)
        
        # Environment filters - split into two columns
        environment_container = QWidget()
        environment_container_layout = QHBoxLayout(environment_container)
        
        # Left column of Environment
        environment_left = QGroupBox("Environment (1/2)")
        environment_left_layout = QFormLayout(environment_left)
        
        # Temperature filter
        self.temperature_min = QLineEdit()
        self.temperature_max = QLineEdit()
        temperature_layout = QHBoxLayout()
        temperature_layout.addWidget(self.temperature_min)
        temperature_layout.addWidget(QLabel("to"))
        temperature_layout.addWidget(self.temperature_max)
        environment_left_layout.addRow("Temperature (°C):", temperature_layout)
        
        # Humidity filter
        self.humidity_min = QLineEdit()
        self.humidity_max = QLineEdit()
        humidity_layout = QHBoxLayout()
        humidity_layout.addWidget(self.humidity_min)
        humidity_layout.addWidget(QLabel("to"))
        humidity_layout.addWidget(self.humidity_max)
        environment_left_layout.addRow("Humidity (%):", humidity_layout)
        
        # Pressure filter
        self.pressure_min = QLineEdit()
        self.pressure_max = QLineEdit()
        pressure_layout = QHBoxLayout()
        pressure_layout.addWidget(self.pressure_min)
        pressure_layout.addWidget(QLabel("to"))
        pressure_layout.addWidget(self.pressure_max)
        environment_left_layout.addRow("Pressure (hPa):", pressure_layout)
        
        # Wind speed filter
        self.wind_speed_min = QLineEdit()
        self.wind_speed_max = QLineEdit()
        wind_speed_layout = QHBoxLayout()
        wind_speed_layout.addWidget(self.wind_speed_min)
        wind_speed_layout.addWidget(QLabel("to"))
        wind_speed_layout.addWidget(self.wind_speed_max)
        environment_left_layout.addRow("Wind Speed (m/s):", wind_speed_layout)
        
        # Wind direction filter
        self.wind_direction_min = QLineEdit()
        self.wind_direction_max = QLineEdit()
        wind_direction_layout = QHBoxLayout()
        wind_direction_layout.addWidget(self.wind_direction_min)
        wind_direction_layout.addWidget(QLabel("to"))
        wind_direction_layout.addWidget(self.wind_direction_max)
        environment_left_layout.addRow("Wind Direction (°):", wind_direction_layout)
        
        environment_container_layout.addWidget(environment_left)
        
        # Right column of Environment
        environment_right = QGroupBox("Environment (2/2)")
        environment_right_layout = QVBoxLayout(environment_right)
        
        # Light conditions filter (multiple selection)
        environment_right_layout.addWidget(QLabel("Light Conditions:"))
        
        light_conditions_layout = QVBoxLayout()
        self.light_conditions_checkboxes = {}
        
        # Get light conditions from Lists.yaml (sky)
        light_conditions = ["Clear", "Partly Cloudy", "Cloudy", "Overcast", "Rain", "Snow", "Stormy"]
        
        for condition in light_conditions:
            checkbox = QCheckBox(condition)
            checkbox.setChecked(False)
            light_conditions_layout.addWidget(checkbox)
            self.light_conditions_checkboxes[condition] = checkbox
        
        environment_right_layout.addLayout(light_conditions_layout)
        
        environment_container_layout.addWidget(environment_right)
        
        filter_groups.addWidget(environment_container)
        
        filter_layout.addLayout(filter_groups)
        
        # Apply filters button
        apply_button = QPushButton("Apply Filters")
        apply_button.clicked.connect(self.apply_filters)
        filter_layout.addWidget(apply_button)
        
        splitter.addWidget(filter_widget)
        
        # Middle section: Test table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # Table header
        table_header = QHBoxLayout()
        table_label = QLabel("Filtered Tests")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.result_count_label = QLabel("0 tests found")
        table_header.addWidget(table_label)
        table_header.addStretch()
        table_header.addWidget(self.result_count_label)
        
        table_layout.addLayout(table_header)
        
        # Selection controls
        selection_controls = QHBoxLayout()
        
        # Select All button
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_tests)
        selection_controls.addWidget(select_all_button)
        
        # Deselect All button
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.clicked.connect(self.deselect_all_tests)
        selection_controls.addWidget(deselect_all_button)
        
        # Toggle Selection button
        toggle_selection_button = QPushButton("Toggle Selection")
        toggle_selection_button.clicked.connect(self.toggle_test_selection)
        selection_controls.addWidget(toggle_selection_button)
        
        # Selected count label
        self.selected_count_label = QLabel("0 tests selected")
        selection_controls.addStretch()
        selection_controls.addWidget(self.selected_count_label)
        
        table_layout.addLayout(selection_controls)
        
        # Test table
        self.test_table = QTableView()
        self.test_model = TestDataModel()
        self.test_table.setModel(self.test_model)
        
        # Connect the selectionChanged signal to update plots
        self.test_model.selectionChanged.connect(self.update_plots)
        
        # Enable sorting
        self.test_table.setSortingEnabled(True)
        
        # Enable selection
        self.test_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        
        table_layout.addWidget(self.test_table)
        
        splitter.addWidget(table_widget)
        
        # Bottom section: Visualization tabs
        # Create a scroll area for the visualization section
        viz_scroll_area = QScrollArea()
        viz_scroll_area.setWidgetResizable(True)
        viz_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        viz_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        viz_widget = QWidget()
        viz_layout = QVBoxLayout(viz_widget)
        
        # Visualization header
        viz_header = QLabel("Data Visualization")
        viz_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        viz_layout.addWidget(viz_header)
        
        # Visualization tabs
        viz_tabs = QTabWidget()
        
        # Accuracy tab
        accuracy_tab = QWidget()
        accuracy_layout = QVBoxLayout(accuracy_tab)
        
        # Accuracy plot
        self.accuracy_canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        accuracy_toolbar = NavigationToolbar(self.accuracy_canvas, self)
        
        accuracy_layout.addWidget(accuracy_toolbar)
        accuracy_layout.addWidget(self.accuracy_canvas)
        
        viz_tabs.addTab(accuracy_tab, "Accuracy")
        
        # Velocity tab
        velocity_tab = QWidget()
        velocity_layout = QVBoxLayout(velocity_tab)
        
        # Velocity plot
        self.velocity_canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        velocity_toolbar = NavigationToolbar(self.velocity_canvas, self)
        
        velocity_layout.addWidget(velocity_toolbar)
        velocity_layout.addWidget(self.velocity_canvas)
        
        viz_tabs.addTab(velocity_tab, "Velocity")
        
        # Combined tab
        combined_tab = QWidget()
        combined_layout = QVBoxLayout(combined_tab)
        
        # Combined plot
        self.combined_canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        combined_toolbar = NavigationToolbar(self.combined_canvas, self)
        
        combined_layout.addWidget(combined_toolbar)
        combined_layout.addWidget(self.combined_canvas)
        
        viz_tabs.addTab(combined_tab, "Combined")
        
        # Custom Plot tab
        custom_tab = QWidget()
        custom_layout = QVBoxLayout(custom_tab)
        
        # Controls for custom plot
        controls_layout = QHBoxLayout()
        
        # X-axis parameter selection
        x_axis_layout = QFormLayout()
        self.x_axis_combo = QComboBox()
        x_axis_layout.addRow("X-Axis:", self.x_axis_combo)
        controls_layout.addLayout(x_axis_layout)
        
        # Y-axis parameter selections (up to 3)
        y_axis_layout = QVBoxLayout()
        y_axis_form = QFormLayout()
        
        # Y-axis 1 (primary)
        self.y_axis1_combo = QComboBox()
        y_axis_form.addRow("Y-Axis 1:", self.y_axis1_combo)
        
        # Y-axis 2 (secondary)
        self.y_axis2_combo = QComboBox()
        self.y_axis2_combo.addItem("None")
        y_axis_form.addRow("Y-Axis 2:", self.y_axis2_combo)
        
        # Y-axis 3 (tertiary)
        self.y_axis3_combo = QComboBox()
        self.y_axis3_combo.addItem("None")
        y_axis_form.addRow("Y-Axis 3:", self.y_axis3_combo)
        
        y_axis_layout.addLayout(y_axis_form)
        controls_layout.addLayout(y_axis_layout)
        
        # Generate plot button
        generate_button = QPushButton("Generate Plot")
        generate_button.clicked.connect(self.generate_custom_plot)
        controls_layout.addWidget(generate_button)
        
        custom_layout.addLayout(controls_layout)
        
        # Custom plot canvas
        self.custom_canvas = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        custom_toolbar = NavigationToolbar(self.custom_canvas, self)
        
        custom_layout.addWidget(custom_toolbar)
        custom_layout.addWidget(self.custom_canvas)
        
        viz_tabs.addTab(custom_tab, "Custom Plot")
        
        viz_layout.addWidget(viz_tabs)
        
        # Set the visualization widget as the content of the scroll area
        viz_widget.setLayout(viz_layout)
        viz_scroll_area.setWidget(viz_widget)
        
        # Add the scroll area to the splitter
        splitter.addWidget(viz_scroll_area)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 300, 400])
    
    def refresh(self):
        """Refresh the widget data (reload test data)"""
        self.load_data()
        
    def load_data(self):
        """Load test data from files"""
        try:
            # Get settings manager
            settings_manager = SettingsManager.get_instance()
            
            # Get the path to the tests directory from settings manager
            tests_dir = settings_manager.get_tests_directory()
            
            # Load all test data
            self.all_data = load_all_test_data(tests_dir)
            
            # If no data was loaded, create a sample DataFrame for demonstration
            if len(self.all_data) == 0:
                self.all_data = pd.DataFrame({
                    "test_id": ["sample_test_1", "sample_test_2"],
                    "date": ["2025-04-15", "2025-04-16"],
                    "distance_m": [100, 100],
                    "calibre": [".223", ".223"],
                    "rifle": ["Tikka T3X", "Tikka T3X"],
                    "bullet_brand": ["Hornady", "Hornady"],
                    "bullet_model": ["ELD-M", "ELD-M"],
                    "bullet_weight_gr": [75.0, 75.0],
                    "powder_brand": ["ADI", "ADI"],
                    "powder_model": ["2208", "2208"],
                    "powder_charge_gr": [23.5, 24.0],
                    "group_es_mm": [15.2, 12.8],
                    "group_es_moa": [0.54, 0.45],
                    "mean_radius_mm": [5.8, 4.9],
                    "avg_velocity_fps": [2850.5, 2875.2],
                    "sd_fps": [8.5, 7.2],
                    "es_fps": [25.0, 22.5]
                })
        except Exception as e:
            # If an error occurs, create a sample DataFrame
            print(f"Error loading test data: {e}")
            self.all_data = pd.DataFrame({
                "test_id": ["sample_test_1", "sample_test_2"],
                "date": ["2025-04-15", "2025-04-16"],
                "distance_m": [100, 100],
                "calibre": [".223", ".223"],
                "rifle": ["Tikka T3X", "Tikka T3X"],
                "bullet_brand": ["Hornady", "Hornady"],
                "bullet_model": ["ELD-M", "ELD-M"],
                "bullet_weight_gr": [75.0, 75.0],
                "powder_brand": ["ADI", "ADI"],
                "powder_model": ["2208", "2208"],
                "powder_charge_gr": [23.5, 24.0],
                "group_es_mm": [15.2, 12.8],
                "group_es_moa": [0.54, 0.45],
                "mean_radius_mm": [5.8, 4.9],
                "avg_velocity_fps": [2850.5, 2875.2],
                "sd_fps": [8.5, 7.2],
                "es_fps": [25.0, 22.5]
            })
        
        self.filtered_data = self.all_data.copy()
        
        # Add selection column if it doesn't exist
        if 'selected' not in self.filtered_data.columns:
            self.filtered_data['selected'] = True
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update result count
        self.result_count_label.setText(f"{len(self.filtered_data)} tests found")
        
        # Populate filter dropdowns
        self.populate_filters()
        
        # Register auto-range filters
        self.register_auto_range_filter('date', 'date', self.date_from, self.date_to, True)
        
        # Update filter ranges based on the current data
        self.update_filter_ranges(self.filtered_data)
        
        # Populate custom plot parameter dropdowns
        self.populate_plot_params()
        
        # Create initial plots
        self.update_plots()
        
    def populate_plot_params(self):
        """Populate the custom plot parameter dropdowns"""
        # Clear the dropdowns
        self.x_axis_combo.clear()
        self.y_axis1_combo.clear()
        self.y_axis2_combo.clear()
        self.y_axis3_combo.clear()
        
        # Add "None" option to secondary and tertiary Y-axis dropdowns
        self.y_axis2_combo.addItem("None")
        self.y_axis3_combo.addItem("None")
        
        # Add all plottable parameters to the dropdowns
        for param_key, param_name in self.plottable_params.items():
            self.x_axis_combo.addItem(param_name, param_key)
            self.y_axis1_combo.addItem(param_name, param_key)
            self.y_axis2_combo.addItem(param_name, param_key)
            self.y_axis3_combo.addItem(param_name, param_key)
        
        # Set default selections
        self.x_axis_combo.setCurrentText(self.plottable_params["powder_charge_gr"])
        self.y_axis1_combo.setCurrentText(self.plottable_params["group_es_moa"])
        self.y_axis2_combo.setCurrentIndex(0)  # "None"
        self.y_axis3_combo.setCurrentIndex(0)  # "None"
    
    def generate_custom_plot(self):
        """Generate a custom plot based on selected parameters"""
        # Get only selected tests
        selected_df = self.filtered_data[self.filtered_data['selected'] == True]
        
        if len(selected_df) < 2:
            # Not enough data for meaningful plots
            self.custom_canvas.fig.clear()
            self.custom_canvas.axes = self.custom_canvas.fig.add_subplot(111)
            self.custom_canvas.axes.set_title('Not enough data for visualization (minimum 2 tests required)')
            self.custom_canvas.draw()
            return
        
        # Get the selected parameters
        x_param = self.x_axis_combo.currentData()
        y1_param = self.y_axis1_combo.currentData()
        y2_param = self.y_axis2_combo.currentData() if self.y_axis2_combo.currentIndex() > 0 else None
        y3_param = self.y_axis3_combo.currentData() if self.y_axis3_combo.currentIndex() > 0 else None
        
        # Check if the parameters exist in the dataframe
        if x_param not in selected_df.columns:
            print(f"Warning: '{x_param}' column not found in the data")
            return
        
        if y1_param not in selected_df.columns:
            print(f"Warning: '{y1_param}' column not found in the data")
            return
        
        if y2_param and y2_param not in selected_df.columns:
            print(f"Warning: '{y2_param}' column not found in the data")
            y2_param = None
            
        if y3_param and y3_param not in selected_df.columns:
            print(f"Warning: '{y3_param}' column not found in the data")
            y3_param = None
        
        # Clear the figure and create a new axes
        self.custom_canvas.fig.clear()
        self.custom_canvas.axes = self.custom_canvas.fig.add_subplot(111)
        
        # Define colors for each Y-axis
        colors = {
            'y1': 'tab:blue',
            'y2': 'tab:red',
            'y3': 'tab:green'
        }
        
        # Sort data by x parameter for line plots
        plot_df = selected_df.sort_values(x_param)
        
        # Primary Y-axis (Y1)
        ax1 = self.custom_canvas.axes
        ax1.set_xlabel(self.plottable_params[x_param])
        ax1.set_ylabel(self.plottable_params[y1_param], color=colors['y1'])
        ax1.scatter(plot_df[x_param], plot_df[y1_param], color=colors['y1'], alpha=0.8, s=100)
        ax1.plot(plot_df[x_param], plot_df[y1_param], '-', color=colors['y1'], alpha=0.6, label=self.plottable_params[y1_param])
        ax1.tick_params(axis='y', labelcolor=colors['y1'])
        
        # Add a grid
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Add trend line for primary Y-axis
        try:
            # Convert to numeric if needed
            x_data = pd.to_numeric(plot_df[x_param], errors='coerce')
            y_data = pd.to_numeric(plot_df[y1_param], errors='coerce')
            
            # Remove NaN values
            mask = ~np.isnan(x_data) & ~np.isnan(y_data)
            x_data = x_data[mask]
            y_data = y_data[mask]
            
            if len(x_data) >= 2:
                # Calculate trend line
                z = np.polyfit(x_data, y_data, 1)
                p = np.poly1d(z)
                
                # Add trend line to plot
                x_range = np.linspace(min(x_data), max(x_data), 100)
                ax1.plot(x_range, p(x_range), "--", color=colors['y1'], alpha=0.8)
                
                # Add trend line equation
                slope, intercept = z
                equation = f"y1 = {slope:.4f}x + {intercept:.4f}"
                ax1.annotate(
                    equation,
                    xy=(0.05, 0.95),
                    xycoords='axes fraction',
                    fontsize=10,
                    color=colors['y1'],
                    backgroundcolor='w',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
                )
        except Exception as e:
            print(f"Error adding trend line for Y1: {e}")
        
        # Secondary Y-axis (Y2) if selected
        if y2_param:
            ax2 = ax1.twinx()
            ax2.set_ylabel(self.plottable_params[y2_param], color=colors['y2'])
            ax2.scatter(plot_df[x_param], plot_df[y2_param], color=colors['y2'], alpha=0.8, s=100)
            ax2.plot(plot_df[x_param], plot_df[y2_param], '-', color=colors['y2'], alpha=0.6, label=self.plottable_params[y2_param])
            ax2.tick_params(axis='y', labelcolor=colors['y2'])
            
            # Add trend line for secondary Y-axis
            try:
                # Convert to numeric if needed
                x_data = pd.to_numeric(plot_df[x_param], errors='coerce')
                y_data = pd.to_numeric(plot_df[y2_param], errors='coerce')
                
                # Remove NaN values
                mask = ~np.isnan(x_data) & ~np.isnan(y_data)
                x_data = x_data[mask]
                y_data = y_data[mask]
                
                if len(x_data) >= 2:
                    # Calculate trend line
                    z = np.polyfit(x_data, y_data, 1)
                    p = np.poly1d(z)
                    
                    # Add trend line to plot
                    x_range = np.linspace(min(x_data), max(x_data), 100)
                    ax2.plot(x_range, p(x_range), "--", color=colors['y2'], alpha=0.8)
                    
                    # Add trend line equation
                    slope, intercept = z
                    equation = f"y2 = {slope:.4f}x + {intercept:.4f}"
                    ax2.annotate(
                        equation,
                        xy=(0.05, 0.85),
                        xycoords='axes fraction',
                        fontsize=10,
                        color=colors['y2'],
                        backgroundcolor='w',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
                    )
            except Exception as e:
                print(f"Error adding trend line for Y2: {e}")
        
        # Tertiary Y-axis (Y3) if selected
        if y3_param:
            ax3 = ax1.twinx()
            # Offset the third y-axis to the right
            ax3.spines['right'].set_position(('outward', 60))
            ax3.set_ylabel(self.plottable_params[y3_param], color=colors['y3'])
            ax3.scatter(plot_df[x_param], plot_df[y3_param], color=colors['y3'], alpha=0.8, s=100)
            ax3.plot(plot_df[x_param], plot_df[y3_param], '-', color=colors['y3'], alpha=0.6, label=self.plottable_params[y3_param])
            ax3.tick_params(axis='y', labelcolor=colors['y3'])
            
            # Add trend line for tertiary Y-axis
            try:
                # Convert to numeric if needed
                x_data = pd.to_numeric(plot_df[x_param], errors='coerce')
                y_data = pd.to_numeric(plot_df[y3_param], errors='coerce')
                
                # Remove NaN values
                mask = ~np.isnan(x_data) & ~np.isnan(y_data)
                x_data = x_data[mask]
                y_data = y_data[mask]
                
                if len(x_data) >= 2:
                    # Calculate trend line
                    z = np.polyfit(x_data, y_data, 1)
                    p = np.poly1d(z)
                    
                    # Add trend line to plot
                    x_range = np.linspace(min(x_data), max(x_data), 100)
                    ax3.plot(x_range, p(x_range), "--", color=colors['y3'], alpha=0.8)
                    
                    # Add trend line equation
                    slope, intercept = z
                    equation = f"y3 = {slope:.4f}x + {intercept:.4f}"
                    ax3.annotate(
                        equation,
                        xy=(0.05, 0.75),
                        xycoords='axes fraction',
                        fontsize=10,
                        color=colors['y3'],
                        backgroundcolor='w',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
                    )
            except Exception as e:
                print(f"Error adding trend line for Y3: {e}")
        
        # Add a title
        title_parts = []
        if y1_param:
            title_parts.append(self.plottable_params[y1_param])
        if y2_param:
            title_parts.append(self.plottable_params[y2_param])
        if y3_param:
            title_parts.append(self.plottable_params[y3_param])
        
        title = f"{', '.join(title_parts)} vs. {self.plottable_params[x_param]}"
        self.custom_canvas.axes.set_title(title)
        
        # Add a legend
        lines = []
        labels = []
        
        # Get lines and labels from each axis
        if y1_param:
            line1, label1 = ax1.get_legend_handles_labels()
            lines.extend(line1)
            labels.extend(label1)
        
        if y2_param:
            line2, label2 = ax2.get_legend_handles_labels()
            lines.extend(line2)
            labels.extend(label2)
        
        if y3_param:
            line3, label3 = ax3.get_legend_handles_labels()
            lines.extend(line3)
            labels.extend(label3)
        
        # Add the legend
        if lines and labels:
            ax1.legend(lines, labels, loc='best')
        
        # Adjust layout
        self.custom_canvas.fig.tight_layout()
        
        # Redraw the canvas
        self.custom_canvas.draw()
    
    def populate_filters(self):
        """Populate filter dropdowns with values from the data"""
        # Calibre filter
        calibres = sorted(self.all_data["calibre"].unique())
        self.calibre_combo.clear()
        self.calibre_combo.addItem("All")
        self.calibre_combo.addItems(calibres)
        
        # Rifle filter
        rifles = sorted(self.all_data["rifle"].unique())
        self.rifle_combo.clear()
        self.rifle_combo.addItem("All")
        self.rifle_combo.addItems(rifles)
        
        # Bullet brand filter
        bullet_brands = sorted(self.all_data["bullet_brand"].unique())
        self.bullet_brand_combo.clear()
        self.bullet_brand_combo.addItem("All")
        self.bullet_brand_combo.addItems(bullet_brands)
        
        # Powder brand filter
        powder_brands = sorted(self.all_data["powder_brand"].unique())
        self.powder_brand_combo.clear()
        self.powder_brand_combo.addItem("All")
        self.powder_brand_combo.addItems(powder_brands)
    
    def apply_filters(self):
        """Apply filters to the data"""
        filtered_df = self.all_data.copy()
        
        # Apply date range filter
        try:
            # Get dates from QDateEdit widgets
            from_date = self.date_from.date().toString("yyyy-MM-dd")
            to_date = self.date_to.date().toString("yyyy-MM-dd")
            
            # Check if the column exists in the dataframe
            if "date" in filtered_df.columns:
                # Handle NaN values by creating a mask that excludes them
                mask = filtered_df["date"].notna()
                mask = mask & (filtered_df["date"] >= from_date)
                mask = mask & (filtered_df["date"] <= to_date)
                
                # Apply the mask to filter the dataframe
                filtered_df = filtered_df[mask]
            else:
                print("Warning: 'date' column not found in the data")
        except Exception as e:
            print(f"Error applying date filter: {e}")
        
        # Apply calibre filter
        if self.calibre_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["calibre"] == self.calibre_combo.currentText()]
        
        # Apply rifle filter
        if self.rifle_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["rifle"] == self.rifle_combo.currentText()]
        
        # Apply bullet brand filter
        if self.bullet_brand_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["bullet_brand"] == self.bullet_brand_combo.currentText()]
        
        # Apply bullet weight filter
        if self.bullet_weight_min.text() and self.bullet_weight_max.text():
            try:
                min_bullet_weight = float(self.bullet_weight_min.text())
                max_bullet_weight = float(self.bullet_weight_max.text())
                
                # Check if the column exists in the dataframe
                if "bullet_weight_gr" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["bullet_weight_gr"].notna()
                    mask = mask & (filtered_df["bullet_weight_gr"] >= min_bullet_weight)
                    mask = mask & (filtered_df["bullet_weight_gr"] <= max_bullet_weight)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'bullet_weight_gr' column not found in the data")
            except ValueError as e:
                print(f"Error converting Bullet Weight filter values: {e}")
            except Exception as e:
                print(f"Error applying Bullet Weight filter: {e}")
        
        # Apply powder brand filter
        if self.powder_brand_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["powder_brand"] == self.powder_brand_combo.currentText()]
        
        # Apply charge range filter
        if self.charge_min.text() and self.charge_max.text():
            try:
                min_charge = float(self.charge_min.text())
                max_charge = float(self.charge_max.text())
                
                # Check if the column exists in the dataframe
                if "powder_charge_gr" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["powder_charge_gr"].notna()
                    mask = mask & (filtered_df["powder_charge_gr"] >= min_charge)
                    mask = mask & (filtered_df["powder_charge_gr"] <= max_charge)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'powder_charge_gr' column not found in the data")
            except ValueError as e:
                print(f"Error converting Charge filter values: {e}")
            except Exception as e:
                print(f"Error applying Charge filter: {e}")
        
        # Apply COAL filter
        if self.coal_min.text() and self.coal_max.text():
            try:
                min_coal = float(self.coal_min.text())
                max_coal = float(self.coal_max.text())
                
                # Check if the column exists in the dataframe
                if "coal_in" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["coal_in"].notna()
                    mask = mask & (filtered_df["coal_in"] >= min_coal)
                    mask = mask & (filtered_df["coal_in"] <= max_coal)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'coal_in' column not found in the data")
            except ValueError as e:
                print(f"Error converting COAL filter values: {e}")
            except Exception as e:
                print(f"Error applying COAL filter: {e}")
        
        # Apply B2O filter
        if self.b2o_min.text() and self.b2o_max.text():
            try:
                min_b2o = float(self.b2o_min.text())
                max_b2o = float(self.b2o_max.text())
                
                # Check if the column exists in the dataframe
                if "b2o_in" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["b2o_in"].notna()
                    mask = mask & (filtered_df["b2o_in"] >= min_b2o)
                    mask = mask & (filtered_df["b2o_in"] <= max_b2o)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'b2o_in' column not found in the data")
            except ValueError as e:
                print(f"Error converting B2O filter values: {e}")
            except Exception as e:
                print(f"Error applying B2O filter: {e}")
        
        # Apply Results Target filters
        
        # Number of shots filter
        if self.shots_min.text() and self.shots_max.text():
            try:
                min_shots = int(self.shots_min.text())
                max_shots = int(self.shots_max.text())
                
                # Check if the column exists in the dataframe
                if "shots" in filtered_df.columns:
                    # Make a copy of the 'selected' column before filtering
                    if 'selected' in filtered_df.columns:
                        selection_state = filtered_df['selected'].copy()
                    
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["shots"].notna()
                    mask = mask & (filtered_df["shots"] >= min_shots)
                    mask = mask & (filtered_df["shots"] <= max_shots)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                    
                    # Restore the selection state for the remaining rows
                    if 'selected' in filtered_df.columns and len(selection_state) > 0:
                        # Create a mapping from index to selection state
                        selection_map = dict(zip(selection_state.index, selection_state))
                        
                        # Apply the selection state to the filtered dataframe
                        filtered_df['selected'] = filtered_df.index.map(lambda x: selection_map.get(x, True))
                else:
                    print("Warning: 'shots' column not found in the data")
            except ValueError as e:
                print(f"Error converting Number of shots filter values: {e}")
            except Exception as e:
                print(f"Error applying Number of shots filter: {e}")
                import traceback
                traceback.print_exc()
        
        # Group ES (mm) filter
        if self.group_es_min.text() and self.group_es_max.text():
            try:
                min_group_es = float(self.group_es_min.text())
                max_group_es = float(self.group_es_max.text())
                
                # Check if the column exists in the dataframe
                if "group_es_mm" in filtered_df.columns:
                    # Make a copy of the 'selected' column before filtering
                    if 'selected' in filtered_df.columns:
                        selection_state = filtered_df['selected'].copy()
                    
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["group_es_mm"].notna()
                    mask = mask & (filtered_df["group_es_mm"] >= min_group_es)
                    mask = mask & (filtered_df["group_es_mm"] <= max_group_es)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                    
                    # Restore the selection state for the remaining rows
                    if 'selected' in filtered_df.columns and len(selection_state) > 0:
                        # Create a mapping from index to selection state
                        selection_map = dict(zip(selection_state.index, selection_state))
                        
                        # Apply the selection state to the filtered dataframe
                        filtered_df['selected'] = filtered_df.index.map(lambda x: selection_map.get(x, True))
                else:
                    print("Warning: 'group_es_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting Group ES (mm) filter values: {e}")
            except Exception as e:
                print(f"Error applying Group ES (mm) filter: {e}")
                import traceback
                traceback.print_exc()
        
        # Group ES (MOA) filter
        if self.group_es_moa_min.text() and self.group_es_moa_max.text():
            try:
                min_group_es_moa = float(self.group_es_moa_min.text())
                max_group_es_moa = float(self.group_es_moa_max.text())
                
                # Check if the column exists in the dataframe
                if "group_es_moa" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["group_es_moa"].notna()
                    mask = mask & (filtered_df["group_es_moa"] >= min_group_es_moa)
                    mask = mask & (filtered_df["group_es_moa"] <= max_group_es_moa)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'group_es_moa' column not found in the data")
            except ValueError as e:
                print(f"Error converting Group ES (MOA) filter values: {e}")
            except Exception as e:
                print(f"Error applying Group ES (MOA) filter: {e}")
        
        # Mean Radius filter
        if self.mean_radius_min.text() and self.mean_radius_max.text():
            try:
                min_mean_radius = float(self.mean_radius_min.text())
                max_mean_radius = float(self.mean_radius_max.text())
                
                # Check if the column exists in the dataframe
                if "mean_radius_mm" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["mean_radius_mm"].notna()
                    mask = mask & (filtered_df["mean_radius_mm"] >= min_mean_radius)
                    mask = mask & (filtered_df["mean_radius_mm"] <= max_mean_radius)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'mean_radius_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting Mean Radius filter values: {e}")
            except Exception as e:
                print(f"Error applying Mean Radius filter: {e}")
        
        # Group ES Width-X filter
        if self.group_es_x_min.text() and self.group_es_x_max.text():
            try:
                min_group_es_x = float(self.group_es_x_min.text())
                max_group_es_x = float(self.group_es_x_max.text())
                
                # Check if the column exists in the dataframe
                if "group_es_x_mm" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["group_es_x_mm"].notna()
                    mask = mask & (filtered_df["group_es_x_mm"] >= min_group_es_x)
                    mask = mask & (filtered_df["group_es_x_mm"] <= max_group_es_x)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'group_es_x_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting Group ES Width-X filter values: {e}")
            except Exception as e:
                print(f"Error applying Group ES Width-X filter: {e}")
        
        # Group ES Height-Y filter
        if self.group_es_y_min.text() and self.group_es_y_max.text():
            try:
                min_group_es_y = float(self.group_es_y_min.text())
                max_group_es_y = float(self.group_es_y_max.text())
                
                # Check if the column exists in the dataframe
                if "group_es_y_mm" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["group_es_y_mm"].notna()
                    mask = mask & (filtered_df["group_es_y_mm"] >= min_group_es_y)
                    mask = mask & (filtered_df["group_es_y_mm"] <= max_group_es_y)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'group_es_y_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting Group ES Height-Y filter values: {e}")
            except Exception as e:
                print(f"Error applying Group ES Height-Y filter: {e}")
        
        # POA Horizontal-X filter
        if self.poi_x_min.text() and self.poi_x_max.text():
            try:
                min_poi_x = float(self.poi_x_min.text())
                max_poi_x = float(self.poi_x_max.text())
                
                # Check if the column exists in the dataframe
                if "poi_x_mm" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["poi_x_mm"].notna()
                    mask = mask & (filtered_df["poi_x_mm"] >= min_poi_x)
                    mask = mask & (filtered_df["poi_x_mm"] <= max_poi_x)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'poi_x_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting POA Horizontal-X filter values: {e}")
            except Exception as e:
                print(f"Error applying POA Horizontal-X filter: {e}")
        
        # POA Vertical-Y filter
        if self.poi_y_min.text() and self.poi_y_max.text():
            try:
                min_poi_y = float(self.poi_y_min.text())
                max_poi_y = float(self.poi_y_max.text())
                
                # Check if the column exists in the dataframe
                if "poi_y_mm" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["poi_y_mm"].notna()
                    mask = mask & (filtered_df["poi_y_mm"] >= min_poi_y)
                    mask = mask & (filtered_df["poi_y_mm"] <= max_poi_y)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'poi_y_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting POA Vertical-Y filter values: {e}")
            except Exception as e:
                print(f"Error applying POA Vertical-Y filter: {e}")
        
        # Apply Results Velocity filters
        
        # Avg Velocity filter
        if self.avg_velocity_min.text() and self.avg_velocity_max.text():
            try:
                min_avg_velocity = float(self.avg_velocity_min.text())
                max_avg_velocity = float(self.avg_velocity_max.text())
                
                # Check if the column exists in the dataframe
                if "avg_velocity_fps" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["avg_velocity_fps"].notna()
                    mask = mask & (filtered_df["avg_velocity_fps"] >= min_avg_velocity)
                    mask = mask & (filtered_df["avg_velocity_fps"] <= max_avg_velocity)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'avg_velocity_fps' column not found in the data")
            except ValueError as e:
                print(f"Error converting Avg Velocity filter values: {e}")
            except Exception as e:
                print(f"Error applying Avg Velocity filter: {e}")
        
        # SD Velocity filter
        if self.sd_velocity_min.text() and self.sd_velocity_max.text():
            try:
                min_sd_velocity = float(self.sd_velocity_min.text())
                max_sd_velocity = float(self.sd_velocity_max.text())
                
                # Check if the column exists in the dataframe
                if "sd_fps" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["sd_fps"].notna()
                    mask = mask & (filtered_df["sd_fps"] >= min_sd_velocity)
                    mask = mask & (filtered_df["sd_fps"] <= max_sd_velocity)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'sd_fps' column not found in the data")
            except ValueError as e:
                print(f"Error converting SD Velocity filter values: {e}")
            except Exception as e:
                print(f"Error applying SD Velocity filter: {e}")
        
        # ES Velocity filter
        if self.es_velocity_min.text() and self.es_velocity_max.text():
            try:
                min_es_velocity = float(self.es_velocity_min.text())
                max_es_velocity = float(self.es_velocity_max.text())
                
                # Check if the column exists in the dataframe
                if "es_fps" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["es_fps"].notna()
                    mask = mask & (filtered_df["es_fps"] >= min_es_velocity)
                    mask = mask & (filtered_df["es_fps"] <= max_es_velocity)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'es_fps' column not found in the data")
            except ValueError as e:
                print(f"Error converting ES Velocity filter values: {e}")
            except Exception as e:
                print(f"Error applying ES Velocity filter: {e}")
        
        # Apply Environment filters
        
        # Temperature filter
        if self.temperature_min.text() and self.temperature_max.text():
            try:
                min_temperature = float(self.temperature_min.text())
                max_temperature = float(self.temperature_max.text())
                
                # Check if the column exists in the dataframe
                if "temperature_c" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["temperature_c"].notna()
                    mask = mask & (filtered_df["temperature_c"] >= min_temperature)
                    mask = mask & (filtered_df["temperature_c"] <= max_temperature)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'temperature_c' column not found in the data")
            except ValueError as e:
                print(f"Error converting Temperature filter values: {e}")
            except Exception as e:
                print(f"Error applying Temperature filter: {e}")
        
        # Humidity filter
        if self.humidity_min.text() and self.humidity_max.text():
            try:
                min_humidity = float(self.humidity_min.text())
                max_humidity = float(self.humidity_max.text())
                
                # Check if the column exists in the dataframe
                if "humidity_pct" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["humidity_pct"].notna()
                    mask = mask & (filtered_df["humidity_pct"] >= min_humidity)
                    mask = mask & (filtered_df["humidity_pct"] <= max_humidity)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'humidity_pct' column not found in the data")
            except ValueError as e:
                print(f"Error converting Humidity filter values: {e}")
            except Exception as e:
                print(f"Error applying Humidity filter: {e}")
        
        # Pressure filter
        if self.pressure_min.text() and self.pressure_max.text():
            try:
                min_pressure = float(self.pressure_min.text())
                max_pressure = float(self.pressure_max.text())
                
                # Check if the column exists in the dataframe
                if "pressure_hpa" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["pressure_hpa"].notna()
                    mask = mask & (filtered_df["pressure_hpa"] >= min_pressure)
                    mask = mask & (filtered_df["pressure_hpa"] <= max_pressure)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'pressure_hpa' column not found in the data")
            except ValueError as e:
                print(f"Error converting Pressure filter values: {e}")
            except Exception as e:
                print(f"Error applying Pressure filter: {e}")
        
        # Wind speed filter
        if self.wind_speed_min.text() and self.wind_speed_max.text():
            try:
                min_wind_speed = float(self.wind_speed_min.text())
                max_wind_speed = float(self.wind_speed_max.text())
                
                # Check if the column exists in the dataframe
                if "wind_speed_ms" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["wind_speed_ms"].notna()
                    mask = mask & (filtered_df["wind_speed_ms"] >= min_wind_speed)
                    mask = mask & (filtered_df["wind_speed_ms"] <= max_wind_speed)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'wind_speed_ms' column not found in the data")
            except ValueError as e:
                print(f"Error converting Wind Speed filter values: {e}")
            except Exception as e:
                print(f"Error applying Wind Speed filter: {e}")
        
        # Wind direction filter
        if self.wind_direction_min.text() and self.wind_direction_max.text():
            try:
                min_wind_direction = float(self.wind_direction_min.text())
                max_wind_direction = float(self.wind_direction_max.text())
                
                # Check if the column exists in the dataframe
                if "wind_direction" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["wind_direction"].notna()
                    mask = mask & (filtered_df["wind_direction"] >= min_wind_direction)
                    mask = mask & (filtered_df["wind_direction"] <= max_wind_direction)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'wind_direction' column not found in the data")
            except ValueError as e:
                print(f"Error converting Wind Direction filter values: {e}")
            except Exception as e:
                print(f"Error applying Wind Direction filter: {e}")
        
        # Light conditions filter (multiple selection)
        selected_light_conditions = [condition for condition, checkbox in self.light_conditions_checkboxes.items() if checkbox.isChecked()]
        if selected_light_conditions:
            # Check if the column exists in the dataframe
            if "light_conditions" in filtered_df.columns:
                # Filter for rows where light_conditions is in the selected list
                filtered_df = filtered_df[filtered_df["light_conditions"].isin(selected_light_conditions)]
            else:
                print("Warning: 'light_conditions' column not found in the data")
                
        # For backward compatibility
        if self.group_min is not None and self.group_max is not None and self.group_min.text() and self.group_max.text():
            try:
                min_group = float(self.group_min.text())
                max_group = float(self.group_max.text())
                filtered_df = filtered_df[
                    (filtered_df["group_es_mm"] >= min_group) & 
                    (filtered_df["group_es_mm"] <= max_group)
                ]
            except ValueError:
                pass
        
        if self.velocity_min is not None and self.velocity_max is not None and self.velocity_min.text() and self.velocity_max.text():
            try:
                min_velocity = float(self.velocity_min.text())
                max_velocity = float(self.velocity_max.text())
                filtered_df = filtered_df[
                    (filtered_df["avg_velocity_fps"] >= min_velocity) & 
                    (filtered_df["avg_velocity_fps"] <= max_velocity)
                ]
            except ValueError:
                pass
        
        # Update filtered data
        self.filtered_data = filtered_df
        
        # Ensure the 'selected' column exists
        if 'selected' not in self.filtered_data.columns:
            self.filtered_data['selected'] = True
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update result count
        self.result_count_label.setText(f"{len(self.filtered_data)} tests found")
        
        # Update auto-range filters based on the filtered data
        # Temporarily disable auto-ranging to prevent infinite recursion
        self.disable_auto_range = True
        self.update_filter_ranges(self.filtered_data)
        self.disable_auto_range = False
        
        # Update plots
        self.update_plots()
    
    def reset_filters(self):
        """Reset all filters to their default values"""
        # Reset dropdowns
        self.calibre_combo.setCurrentIndex(0)
        self.rifle_combo.setCurrentIndex(0)
        self.bullet_brand_combo.setCurrentIndex(0)
        self.powder_brand_combo.setCurrentIndex(0)
        
        # Reset date inputs to default values
        self.date_from.setDate(QDate.currentDate().addMonths(-1))  # Default to 1 month ago
        self.date_to.setDate(QDate.currentDate())  # Default to today
        
        # Reset Ammunition filters
        self.bullet_weight_min.clear()
        self.bullet_weight_max.clear()
        self.charge_min.clear()
        self.charge_max.clear()
        self.coal_min.clear()
        self.coal_max.clear()
        self.b2o_min.clear()
        self.b2o_max.clear()
        
        # Reset Results Target filters
        self.shots_min.clear()
        self.shots_max.clear()
        self.group_es_min.clear()
        self.group_es_max.clear()
        self.group_es_moa_min.clear()
        self.group_es_moa_max.clear()
        self.mean_radius_min.clear()
        self.mean_radius_max.clear()
        self.group_es_x_min.clear()
        self.group_es_x_max.clear()
        self.group_es_y_min.clear()
        self.group_es_y_max.clear()
        self.poi_x_min.clear()
        self.poi_x_max.clear()
        self.poi_y_min.clear()
        self.poi_y_max.clear()
        
        # Reset Results Velocity filters
        self.avg_velocity_min.clear()
        self.avg_velocity_max.clear()
        self.sd_velocity_min.clear()
        self.sd_velocity_max.clear()
        self.es_velocity_min.clear()
        self.es_velocity_max.clear()
        
        # Reset Environment filters
        self.temperature_min.clear()
        self.temperature_max.clear()
        self.humidity_min.clear()
        self.humidity_max.clear()
        self.pressure_min.clear()
        self.pressure_max.clear()
        self.wind_speed_min.clear()
        self.wind_speed_max.clear()
        self.wind_direction_min.clear()
        self.wind_direction_max.clear()
        
        # Reset Light conditions checkboxes
        for checkbox in self.light_conditions_checkboxes.values():
            checkbox.setChecked(False)
        
        # For backward compatibility with existing code
        self.group_min = self.group_es_min
        self.group_max = self.group_es_max
        self.velocity_min = self.avg_velocity_min
        self.velocity_max = self.avg_velocity_max
        
        # Apply filters (which will now show all data)
        self.apply_filters()
    
    def select_all_tests(self):
        """Select all tests in the filtered data"""
        # Set all tests to selected
        self.filtered_data['selected'] = True
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update the selected count label
        self.update_selected_count()
        
        # Update plots
        self.update_plots()
    
    def deselect_all_tests(self):
        """Deselect all tests in the filtered data"""
        # Set all tests to not selected
        self.filtered_data['selected'] = False
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update the selected count label
        self.update_selected_count()
        
        # Update plots
        self.update_plots()
    
    def toggle_test_selection(self):
        """Toggle the selection state of all tests in the filtered data"""
        # Toggle the selection state of all tests
        self.filtered_data['selected'] = ~self.filtered_data['selected']
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update the selected count label
        self.update_selected_count()
        
        # Update plots
        self.update_plots()
    
    def update_selected_count(self):
        """Update the selected count label"""
        # Count the number of selected tests
        selected_count = len(self.filtered_data[self.filtered_data['selected'] == True])
        
        # Update the selected count label
        self.selected_count_label.setText(f"{selected_count} tests selected")
    
    def update_plots(self):
        """Update all plots with the current filtered data"""
        # Get only selected tests
        selected_df = self.filtered_data[self.filtered_data['selected'] == True]
        
        # Update the selected count label
        self.update_selected_count()
        
        if len(selected_df) < 2:
            # Not enough data for meaningful plots
            self.clear_plots()
            return
        
        # Sort data by powder charge for plotting
        plot_df = selected_df.sort_values("powder_charge_gr")
        
        # Update accuracy plot
        self.update_accuracy_plot(plot_df)
        
        # Update velocity plot
        self.update_velocity_plot(plot_df)
        
        # Update combined plot
        self.update_combined_plot(plot_df)
    
    def update_accuracy_plot(self, df):
        """Update the accuracy plot with the given data"""
        # Clear the figure and create a new axes
        self.accuracy_canvas.fig.clear()
        self.accuracy_canvas.axes = self.accuracy_canvas.fig.add_subplot(111)
        
        # Create the plot
        x = range(len(df))
        
        # Plot group size (MOA) on the left y-axis
        color = 'tab:blue'
        self.accuracy_canvas.axes.set_xlabel('Test')
        self.accuracy_canvas.axes.set_ylabel('Group Size (MOA)', color=color)
        self.accuracy_canvas.axes.plot(x, df['group_es_moa'], 'o-', color=color, label='Group Size (MOA)')
        self.accuracy_canvas.axes.tick_params(axis='y', labelcolor=color)
        
        # Create a second y-axis for mean radius
        ax2 = self.accuracy_canvas.axes.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Mean Radius (mm)', color=color)
        ax2.plot(x, df['mean_radius_mm'], 'o-', color=color, label='Mean Radius (mm)')
        ax2.tick_params(axis='y', labelcolor=color)
        
        # Set x-axis labels
        self.accuracy_canvas.axes.set_xticks(x)
        self.accuracy_canvas.axes.set_xticklabels([f"{charge:.2f}gr" for charge in df['powder_charge_gr']], rotation=45)
        
        # Add a title
        self.accuracy_canvas.axes.set_title('Group Size and Mean Radius vs. Powder Charge')
        
        # Add a legend
        lines1, labels1 = self.accuracy_canvas.axes.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.accuracy_canvas.axes.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Adjust layout
        self.accuracy_canvas.fig.tight_layout()
        
        # Redraw the canvas
        self.accuracy_canvas.draw()
    
    def update_velocity_plot(self, df):
        """Update the velocity plot with the given data"""
        # Clear the figure and create a new axes
        self.velocity_canvas.fig.clear()
        self.velocity_canvas.axes = self.velocity_canvas.fig.add_subplot(111)
        
        # Create the plot
        x = range(len(df))
        
        # Plot average velocity on the left y-axis
        color = 'tab:green'
        self.velocity_canvas.axes.set_xlabel('Test')
        self.velocity_canvas.axes.set_ylabel('Average Velocity (fps)', color=color)
        self.velocity_canvas.axes.plot(x, df['avg_velocity_fps'], 'o-', color=color, label='Avg Velocity (fps)')
        self.velocity_canvas.axes.tick_params(axis='y', labelcolor=color)
        
        # Create a second y-axis for ES and SD
        ax2 = self.velocity_canvas.axes.twinx()
        ax2.set_ylabel('Velocity Variation (fps)')
        
        # Plot ES and SD on the right y-axis with different colors
        ax2.plot(x, df['es_fps'], 'o-', color='tab:orange', label='ES (fps)')
        ax2.plot(x, df['sd_fps'], 'o-', color='tab:purple', label='SD (fps)')
        
        # Set x-axis labels
        self.velocity_canvas.axes.set_xticks(x)
        self.velocity_canvas.axes.set_xticklabels([f"{charge:.2f}gr" for charge in df['powder_charge_gr']], rotation=45)
        
        # Add a title
        self.velocity_canvas.axes.set_title('Velocity Metrics vs. Powder Charge')
        
        # Add a legend
        lines1, labels1 = self.velocity_canvas.axes.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        self.velocity_canvas.axes.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Adjust layout
        self.velocity_canvas.fig.tight_layout()
        
        # Redraw the canvas
        self.velocity_canvas.draw()
    
    def update_combined_plot(self, df):
        """Update the combined plot with the given data"""
        # Clear the figure and create a new axes
        self.combined_canvas.fig.clear()
        self.combined_canvas.axes = self.combined_canvas.fig.add_subplot(111)
        
        # Create the plot
        x = range(len(df))
        
        # Define colors for each metric
        colors = {
            'group_es_moa': 'tab:blue',
            'mean_radius_mm': 'tab:red',
            'avg_velocity_fps': 'tab:green',
            'es_fps': 'tab:orange',
            'sd_fps': 'tab:purple'
        }
        
        # Create a figure with 2 subplots sharing the x-axis
        # Top subplot for accuracy metrics
        ax1 = self.combined_canvas.axes
        ax1.set_xlabel('Test')
        ax1.set_ylabel('Group Size (MOA)', color=colors['group_es_moa'])
        ax1.plot(x, df['group_es_moa'], 'o-', color=colors['group_es_moa'], label='Group Size (MOA)')
        ax1.tick_params(axis='y', labelcolor=colors['group_es_moa'])
        
        # Set x-axis labels
        ax1.set_xticks(x)
        ax1.set_xticklabels([f"{charge:.2f}gr" for charge in df['powder_charge_gr']], rotation=45)
        
        # Create a second y-axis for Mean Radius
        ax2 = ax1.twinx()
        ax2.set_ylabel('Mean Radius (mm)', color=colors['mean_radius_mm'])
        ax2.plot(x, df['mean_radius_mm'], 'o-', color=colors['mean_radius_mm'], label='Mean Radius (mm)')
        ax2.tick_params(axis='y', labelcolor=colors['mean_radius_mm'])
        
        # Create a third y-axis for Velocity
        ax3 = ax1.twinx()
        # Offset the third y-axis to the right
        ax3.spines['right'].set_position(('outward', 60))
        ax3.set_ylabel('Velocity (fps)', color=colors['avg_velocity_fps'])
        ax3.plot(x, df['avg_velocity_fps'], 'o-', color=colors['avg_velocity_fps'], label='Avg Velocity (fps)')
        ax3.tick_params(axis='y', labelcolor=colors['avg_velocity_fps'])
        
        # Create a fourth y-axis for ES and SD
        ax4 = ax1.twinx()
        # Offset the fourth y-axis to the right
        ax4.spines['right'].set_position(('outward', 120))
        ax4.set_ylabel('Velocity Variation (fps)')
        ax4.plot(x, df['es_fps'], 'o-', color=colors['es_fps'], label='ES (fps)')
        ax4.plot(x, df['sd_fps'], 'o-', color=colors['sd_fps'], label='SD (fps)')
        
        # Add a title
        ax1.set_title('Accuracy and Velocity Metrics vs. Powder Charge')
        
        # Add a legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        lines4, labels4 = ax4.get_legend_handles_labels()
        ax1.legend(lines1 + lines2 + lines3 + lines4, 
                  labels1 + labels2 + labels3 + labels4, 
                  loc='upper left')
        
        # Adjust layout
        self.combined_canvas.fig.tight_layout()
        
        # Redraw the canvas
        self.combined_canvas.draw()
    
    def clear_plots(self):
        """Clear all plots"""
        # Clear accuracy plot
        self.accuracy_canvas.fig.clear()
        self.accuracy_canvas.axes = self.accuracy_canvas.fig.add_subplot(111)
        self.accuracy_canvas.axes.set_title('Not enough data for visualization')
        self.accuracy_canvas.draw()
        
        # Clear velocity plot
        self.velocity_canvas.fig.clear()
        self.velocity_canvas.axes = self.velocity_canvas.fig.add_subplot(111)
        self.velocity_canvas.axes.set_title('Not enough data for visualization')
        self.velocity_canvas.draw()
        
        # Clear combined plot
        self.combined_canvas.fig.clear()
        self.combined_canvas.axes = self.combined_canvas.fig.add_subplot(111)
        self.combined_canvas.axes.set_title('Not enough data for visualization')
        self.combined_canvas.draw()
