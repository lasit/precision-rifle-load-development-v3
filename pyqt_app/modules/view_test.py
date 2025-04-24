"""
View Test Module for the Precision Rifle Load Development App
Provides detailed view of a single selected test, allowing editing.

This module defines the ViewTestWidget class, which displays and allows editing
of test data. It includes fields for test information, platform details,
ammunition components, environmental conditions, and results.
"""

import os
import sys
import yaml
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QFormLayout, QLineEdit, QGroupBox, QScrollArea,
                             QMessageBox, QStyle, QDoubleSpinBox, QDateEdit, QTextEdit,
                             QSlider, QToolBar, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QPoint, QRect, QSize, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent, QTransform, QCursor

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import settings manager and data loader
from utils.settings_manager import SettingsManager

# Path to the Component_List.yaml file (relative to the project root)
COMPONENT_LIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Component_List.yaml"
)

class ZoomableImageLabel(QLabel):
    """A QLabel that supports zooming and panning of its pixmap."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(560, 420)  # 40% larger than original 400x300
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid gray;")
        
        # Enable mouse tracking for panning
        self.setMouseTracking(True)
        
        # Initialize variables
        self._pixmap = QPixmap()
        self._zoom_factor = 1.0
        self._pan_start_pos = QPoint()
        self._panning = False
        self._offset = QPoint(0, 0)
        
        # Set focus policy to accept wheel events
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        
        # Set cursor to indicate the image is pannable
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
    
    def setPixmap(self, pixmap):
        """Set the pixmap and reset zoom and pan."""
        self._pixmap = pixmap
        self._zoom_factor = 1.0
        self._offset = QPoint(0, 0)
        self._update_pixmap()
    
    def _update_pixmap(self):
        """Update the displayed pixmap based on zoom and pan."""
        if self._pixmap.isNull():
            super().setPixmap(QPixmap())
            return
        
        # Calculate the scaled size
        scaled_size = self._pixmap.size() * self._zoom_factor
        
        # Create a new pixmap with the scaled size
        scaled_pixmap = self._pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Calculate the visible area
        visible_rect = QRect(self._offset, self.size())
        
        # Create a new pixmap for the visible area
        visible_pixmap = QPixmap(self.size())
        visible_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Paint the scaled pixmap onto the visible pixmap
        painter = QPainter(visible_pixmap)
        
        # Calculate the position to center the image
        x = (self.width() - scaled_pixmap.width()) // 2 - self._offset.x()
        y = (self.height() - scaled_pixmap.height()) // 2 - self._offset.y()
        
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        # Set the visible pixmap to the label
        super().setPixmap(visible_pixmap)
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if self._pixmap.isNull():
            return
        
        # Get the mouse position
        pos = event.position().toPoint()
        
        # Calculate zoom factor
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        
        # Adjust zoom factor
        if zoom_in:
            self._zoom_factor *= 1.2
        else:
            self._zoom_factor /= 1.2
        
        # Limit zoom factor
        self._zoom_factor = max(0.1, min(10.0, self._zoom_factor))
        
        # Update the pixmap
        self._update_pixmap()
    
    def mousePressEvent(self, event):
        """Handle mouse press events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = False
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning."""
        if self._panning:
            # Calculate the offset
            delta = event.pos() - self._pan_start_pos
            self._offset -= delta
            self._pan_start_pos = event.pos()
            
            # Update the pixmap
            self._update_pixmap()
    
    def resizeEvent(self, event):
        """Handle resize events."""
        self._update_pixmap()

class ViewTestWidget(QWidget):
    """Widget for displaying and editing details of a single test"""
    
    # Signals emitted when a test is updated or deleted
    testUpdated = pyqtSignal()
    testDeleted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get settings manager
        self.settings_manager = SettingsManager.get_instance()
        
        # Get tests directory from settings manager
        self.tests_dir = self.settings_manager.get_tests_directory()
        self.current_test_id = None
        self.test_data = {} # To hold loaded test data (from group.yaml)
        
        # Load component lists
        self.component_lists = self.load_component_lists()

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout) # Set the layout for the widget
        
        # Top section: Test Selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Test ID:"))
        self.test_id_combo = QComboBox()
        self.test_id_combo.setMinimumWidth(400)
        self.test_id_combo.currentIndexChanged.connect(self.load_selected_test)
        selection_layout.addWidget(self.test_id_combo)
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)

        # Scroll Area for test details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # Widget inside scroll area to hold the form layouts
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # Create a horizontal layout for the two columns
        two_column_layout = QHBoxLayout(scroll_content)
        
        # Left column layout
        left_column = QVBoxLayout()
        left_column.addWidget(self._create_test_info_group())
        left_column.addWidget(self._create_platform_group())
        left_column.addWidget(self._create_ammunition_group())
        left_column.addWidget(self._create_environment_group())
        left_column.addStretch() # Push groups to the top
        
        # Right column layout
        right_column = QVBoxLayout()
        right_column.addWidget(self._create_image_group())
        right_column.addWidget(self._create_results_group())
        right_column.addStretch() # Push groups to the top
        
        # Add columns to the two-column layout
        two_column_layout.addLayout(left_column, 1)  # 1:1 ratio
        two_column_layout.addLayout(right_column, 1)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Delete Button
        delete_button = QPushButton("Delete Test")
        delete_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        delete_button.setIcon(delete_icon)
        delete_button.clicked.connect(self.delete_test)
        buttons_layout.addWidget(delete_button)
        
        buttons_layout.addStretch()  # Push buttons apart
        
        # Save Button
        save_button = QPushButton("Save Changes")
        save_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        save_button.setIcon(save_icon) 
        save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_button)
        
        main_layout.addLayout(buttons_layout)

        self.populate_test_ids()

    def load_component_lists(self):
        """Load component lists from the YAML file"""
        try:
            if os.path.exists(COMPONENT_LIST_PATH):
                with open(COMPONENT_LIST_PATH, 'r') as file:
                    data = yaml.safe_load(file)
                    if data:
                        return data
            return {}
        except Exception as e:
            print(f"Error loading component lists: {e}")
            return {}
    
    def refresh_component_lists(self):
        """Refresh component lists when they are updated in the Admin tab"""
        self.component_lists = self.load_component_lists()
        
        # Update dropdown contents
        # Calibre
        current_calibre = self.calibre_combo.currentText()
        self.calibre_combo.clear()
        calibre_list = self.component_lists.get('calibre', [])
        if calibre_list:
            self.calibre_combo.addItems(calibre_list)
            index = self.calibre_combo.findText(current_calibre)
            if index >= 0:
                self.calibre_combo.setCurrentIndex(index)
            elif current_calibre:
                self.calibre_combo.addItem(current_calibre)
                self.calibre_combo.setCurrentText(current_calibre)
        
        # Rifle
        current_rifle = self.rifle_combo.currentText()
        self.rifle_combo.clear()
        rifle_list = self.component_lists.get('rifle', [])
        if rifle_list:
            self.rifle_combo.addItems(rifle_list)
            index = self.rifle_combo.findText(current_rifle)
            if index >= 0:
                self.rifle_combo.setCurrentIndex(index)
            elif current_rifle:
                self.rifle_combo.addItem(current_rifle)
                self.rifle_combo.setCurrentText(current_rifle)
        
        # Bullet Brand
        current_bullet_brand = self.bullet_brand_combo.currentText()
        self.bullet_brand_combo.clear()
        bullet_brand_list = self.component_lists.get('bullet_brand', [])
        if bullet_brand_list:
            self.bullet_brand_combo.addItems(bullet_brand_list)
            index = self.bullet_brand_combo.findText(current_bullet_brand)
            if index >= 0:
                self.bullet_brand_combo.setCurrentIndex(index)
            elif current_bullet_brand:
                self.bullet_brand_combo.addItem(current_bullet_brand)
                self.bullet_brand_combo.setCurrentText(current_bullet_brand)
        
        # Bullet Model
        current_bullet_model = self.bullet_model_combo.currentText()
        self.bullet_model_combo.clear()
        bullet_model_list = self.component_lists.get('bullet_model', [])
        if bullet_model_list:
            self.bullet_model_combo.addItems(bullet_model_list)
            index = self.bullet_model_combo.findText(current_bullet_model)
            if index >= 0:
                self.bullet_model_combo.setCurrentIndex(index)
            elif current_bullet_model:
                self.bullet_model_combo.addItem(current_bullet_model)
                self.bullet_model_combo.setCurrentText(current_bullet_model)
        
        # Powder Brand
        current_powder_brand = self.powder_brand_combo.currentText()
        self.powder_brand_combo.clear()
        powder_brand_list = self.component_lists.get('powder_brand', [])
        if powder_brand_list:
            self.powder_brand_combo.addItems(powder_brand_list)
            index = self.powder_brand_combo.findText(current_powder_brand)
            if index >= 0:
                self.powder_brand_combo.setCurrentIndex(index)
            elif current_powder_brand:
                self.powder_brand_combo.addItem(current_powder_brand)
                self.powder_brand_combo.setCurrentText(current_powder_brand)
        
        # Powder Model
        current_powder_model = self.powder_model_combo.currentText()
        self.powder_model_combo.clear()
        powder_model_list = self.component_lists.get('powder_model', [])
        if powder_model_list:
            self.powder_model_combo.addItems(powder_model_list)
            index = self.powder_model_combo.findText(current_powder_model)
            if index >= 0:
                self.powder_model_combo.setCurrentIndex(index)
            elif current_powder_model:
                self.powder_model_combo.addItem(current_powder_model)
                self.powder_model_combo.setCurrentText(current_powder_model)
        
        # Case Brand
        current_case_brand = self.case_brand_combo.currentText()
        self.case_brand_combo.clear()
        case_brand_list = self.component_lists.get('case_brand', [])
        if case_brand_list:
            self.case_brand_combo.addItems(case_brand_list)
            index = self.case_brand_combo.findText(current_case_brand)
            if index >= 0:
                self.case_brand_combo.setCurrentIndex(index)
            elif current_case_brand:
                self.case_brand_combo.addItem(current_case_brand)
                self.case_brand_combo.setCurrentText(current_case_brand)
        
        # Primer Brand
        current_primer_brand = self.primer_brand_combo.currentText()
        self.primer_brand_combo.clear()
        primer_brand_list = self.component_lists.get('primer_brand', [])
        if primer_brand_list:
            self.primer_brand_combo.addItems(primer_brand_list)
            index = self.primer_brand_combo.findText(current_primer_brand)
            if index >= 0:
                self.primer_brand_combo.setCurrentIndex(index)
            elif current_primer_brand:
                self.primer_brand_combo.addItem(current_primer_brand)
                self.primer_brand_combo.setCurrentText(current_primer_brand)
        
        # Primer Model
        current_primer_model = self.primer_model_combo.currentText()
        self.primer_model_combo.clear()
        primer_model_list = self.component_lists.get('primer_model', [])
        if primer_model_list:
            self.primer_model_combo.addItems(primer_model_list)
            index = self.primer_model_combo.findText(current_primer_model)
            if index >= 0:
                self.primer_model_combo.setCurrentIndex(index)
            elif current_primer_model:
                self.primer_model_combo.addItem(current_primer_model)
                self.primer_model_combo.setCurrentText(current_primer_model)
    
    def refresh(self):
        """Refresh the widget data (test IDs list)"""
        # Update tests directory from settings manager
        self.tests_dir = self.settings_manager.get_tests_directory()
        self.populate_test_ids()
        self.refresh_component_lists()
        
    def populate_test_ids(self):
        """Populate the ComboBox with test IDs from the tests directory"""
        self.test_id_combo.clear()
        self.test_id_combo.addItem("Select a test...")
        try:
            if os.path.exists(self.tests_dir):
                # Filter out non-directory items like .DS_Store
                test_ids = sorted([d for d in os.listdir(self.tests_dir) if os.path.isdir(os.path.join(self.tests_dir, d))])
                self.test_id_combo.addItems(test_ids)
        except Exception as e:
            print(f"Error populating test IDs: {e}")

    def load_selected_test(self):
        """Load data for the selected test ID"""
        selected_index = self.test_id_combo.currentIndex()
        if selected_index <= 0: # Ignore the "Select a test..." item
            self.clear_details()
            return

        self.current_test_id = self.test_id_combo.currentText()
        test_dir = os.path.join(self.tests_dir, self.current_test_id)
        group_yaml_path = os.path.join(test_dir, "group.yaml")

        print(f"Loading test: {self.current_test_id} from {group_yaml_path}") # Debug print

        if not os.path.exists(group_yaml_path):
            QMessageBox.warning(self, "Error", f"group.yaml not found for test: {self.current_test_id}")
            self.clear_details()
            return

        try:
            with open(group_yaml_path, 'r') as f:
                # Use safe_load and ensure it's a dict even if file is empty/malformed
                loaded_content = yaml.safe_load(f)
                self.test_data = loaded_content if isinstance(loaded_content, dict) else {} 
            self.populate_details()
            self.load_image()
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", f"Failed to load data for {self.current_test_id}:\n{e}")
            self.clear_details()

    def _create_test_info_group(self):
        group = QGroupBox("Test Information")
        layout = QFormLayout(group)
        
        # Date field with calendar popup
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Date:", self.date_edit)
        
        # Distance field (dropdown)
        self.distance_combo = QComboBox()
        distance_list = self.component_lists.get('distance', [])
        if distance_list:
            self.distance_combo.addItems(distance_list)
        layout.addRow("Distance:", self.distance_combo)
        
        # Notes field (multi-line)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)  # Limit height
        layout.addRow("Notes:", self.notes_edit)
        
        return group

    def _create_platform_group(self):
        group = QGroupBox("Platform")
        layout = QFormLayout(group)
        
        # Calibre field (dropdown)
        self.calibre_combo = QComboBox()
        calibre_list = self.component_lists.get('calibre', [])
        if calibre_list:
            self.calibre_combo.addItems(calibre_list)
        layout.addRow("Calibre:", self.calibre_combo)
        
        # Rifle field (dropdown)
        self.rifle_combo = QComboBox()
        rifle_list = self.component_lists.get('rifle', [])
        if rifle_list:
            self.rifle_combo.addItems(rifle_list)
        layout.addRow("Rifle:", self.rifle_combo)
        
        return group

    def _create_ammunition_group(self):
        group = QGroupBox("Ammunition")
        layout = QFormLayout(group)
        
        # Bullet section
        # Bullet Brand (dropdown)
        self.bullet_brand_combo = QComboBox()
        bullet_brand_list = self.component_lists.get('bullet_brand', [])
        if bullet_brand_list:
            self.bullet_brand_combo.addItems(bullet_brand_list)
        layout.addRow("Bullet Brand:", self.bullet_brand_combo)
        
        # Bullet Model (dropdown)
        self.bullet_model_combo = QComboBox()
        bullet_model_list = self.component_lists.get('bullet_model', [])
        if bullet_model_list:
            self.bullet_model_combo.addItems(bullet_model_list)
        layout.addRow("Bullet Model:", self.bullet_model_combo)
        
        # Bullet Weight (numeric input)
        self.bullet_weight_spin = QDoubleSpinBox()
        self.bullet_weight_spin.setRange(0.01, 999.99)
        self.bullet_weight_spin.setDecimals(2)
        self.bullet_weight_spin.setSingleStep(0.1)
        layout.addRow("Bullet Weight (gr):", self.bullet_weight_spin)
        
        # Powder section
        # Powder Brand (dropdown)
        self.powder_brand_combo = QComboBox()
        powder_brand_list = self.component_lists.get('powder_brand', [])
        if powder_brand_list:
            self.powder_brand_combo.addItems(powder_brand_list)
        layout.addRow("Powder Brand:", self.powder_brand_combo)
        
        # Powder Model (dropdown)
        self.powder_model_combo = QComboBox()
        powder_model_list = self.component_lists.get('powder_model', [])
        if powder_model_list:
            self.powder_model_combo.addItems(powder_model_list)
        layout.addRow("Powder Model:", self.powder_model_combo)
        
        # Powder Charge (numeric input)
        self.powder_charge_spin = QDoubleSpinBox()
        self.powder_charge_spin.setRange(0.01, 999.99)
        self.powder_charge_spin.setDecimals(2)
        self.powder_charge_spin.setSingleStep(0.1)
        layout.addRow("Powder Charge (gr):", self.powder_charge_spin)
        
        # Cartridge section
        # Cartridge OAL (numeric input)
        self.cartridge_oal_spin = QDoubleSpinBox()
        self.cartridge_oal_spin.setRange(0.001, 9.999)
        self.cartridge_oal_spin.setDecimals(3)
        self.cartridge_oal_spin.setSingleStep(0.001)
        layout.addRow("Cartridge OAL (in):", self.cartridge_oal_spin)
        
        # Cartridge BTO (numeric input)
        self.cartridge_bto_spin = QDoubleSpinBox()
        self.cartridge_bto_spin.setRange(0.001, 9.999)
        self.cartridge_bto_spin.setDecimals(3)
        self.cartridge_bto_spin.setSingleStep(0.001)
        layout.addRow("Cartridge BTO (in):", self.cartridge_bto_spin)
        
        # Case Brand (dropdown)
        self.case_brand_combo = QComboBox()
        case_brand_list = self.component_lists.get('case_brand', [])
        if case_brand_list:
            self.case_brand_combo.addItems(case_brand_list)
        layout.addRow("Case Brand:", self.case_brand_combo)
        
        # Primer Brand (dropdown)
        self.primer_brand_combo = QComboBox()
        primer_brand_list = self.component_lists.get('primer_brand', [])
        if primer_brand_list:
            self.primer_brand_combo.addItems(primer_brand_list)
        layout.addRow("Primer Brand:", self.primer_brand_combo)
        
        # Primer Model (dropdown)
        self.primer_model_combo = QComboBox()
        primer_model_list = self.component_lists.get('primer_model', [])
        if primer_model_list:
            self.primer_model_combo.addItems(primer_model_list)
        layout.addRow("Primer Model:", self.primer_model_combo)
        
        return group

    def _create_results_group(self):
        # Create a container widget with vertical layout to hold both result groups
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Results Target group
        target_group = self._create_results_target_group()
        container_layout.addWidget(target_group)
        
        # Results Velocity group
        velocity_group = self._create_results_velocity_group()
        container_layout.addWidget(velocity_group)
        
        return container
    
    def _create_results_target_group(self):
        """Create the Results Target group"""
        target_group = QGroupBox("Results Target")
        target_layout = QFormLayout(target_group)
        
        # Number of shots
        self.shots_edit = QLineEdit()
        target_layout.addRow("Number of shots:", self.shots_edit)
        
        # Group measurements
        self.group_es_mm_edit = QLineEdit()
        self.group_es_moa_edit = QLineEdit()
        self.mean_radius_mm_edit = QLineEdit()
        target_layout.addRow("Group ES (mm):", self.group_es_mm_edit)
        target_layout.addRow("Group ES (MOA):", self.group_es_moa_edit)
        target_layout.addRow("Mean Radius (mm):", self.mean_radius_mm_edit)
        
        # Group dimensions
        self.group_es_x_mm_edit = QLineEdit()
        self.group_es_y_mm_edit = QLineEdit()
        target_layout.addRow("Group ES Width-X (mm):", self.group_es_x_mm_edit)
        target_layout.addRow("Group ES Height-Y (mm):", self.group_es_y_mm_edit)
        
        # Point of impact
        self.poi_x_mm_edit = QLineEdit()
        self.poi_y_mm_edit = QLineEdit()
        target_layout.addRow("POA Horizontal-X (mm):", self.poi_x_mm_edit)
        target_layout.addRow("POA Vertical-Y (mm):", self.poi_y_mm_edit)
        
        return target_group
    
    def _create_results_velocity_group(self):
        """Create the Results Velocity group"""
        velocity_group = QGroupBox("Results Velocity")
        velocity_layout = QFormLayout(velocity_group)
        
        # Velocity measurements
        self.avg_velocity_edit = QLineEdit()
        self.sd_velocity_edit = QLineEdit()
        self.es_velocity_edit = QLineEdit()
        velocity_layout.addRow("Avg Velocity (f/s):", self.avg_velocity_edit)
        velocity_layout.addRow("SD Velocity (f/s):", self.sd_velocity_edit)
        velocity_layout.addRow("ES Velocity (f/s):", self.es_velocity_edit)
        
        return velocity_group
        
    def _create_environment_group(self):
        group = QGroupBox("Environment")
        layout = QFormLayout(group)
        
        # Temperature
        self.temperature_c_edit = QLineEdit()
        layout.addRow("Temperature (C):", self.temperature_c_edit)
        
        # Humidity
        self.humidity_percent_edit = QLineEdit()
        layout.addRow("Humidity (%):", self.humidity_percent_edit)
        
        # Pressure
        self.pressure_hpa_edit = QLineEdit()
        layout.addRow("Pressure (hpa):", self.pressure_hpa_edit)
        
        # Wind
        self.wind_speed_mps_edit = QLineEdit()
        self.wind_dir_deg_edit = QLineEdit()
        layout.addRow("Wind Speed (m/s):", self.wind_speed_mps_edit)
        layout.addRow("Wind Direction (deg):", self.wind_dir_deg_edit)
        
        # Sky condition
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["Clear", "Partly Cloudy", "Cloudy", "Overcast", "Rain", "Snow"])
        layout.addRow("Sky:", self.weather_combo)
        
        return group
        
    def _create_image_group(self):
        group = QGroupBox("Target Image")
        layout = QVBoxLayout(group)
        
        # Use the zoomable image label instead of a regular QLabel
        self.image_label = ZoomableImageLabel()
        self.image_label.setText("Image will be displayed here")
        
        # Add instructions label
        instructions = QLabel("Use mouse wheel to zoom, click and drag to pan")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("font-style: italic; color: gray;")
        
        layout.addWidget(self.image_label)
        layout.addWidget(instructions)
        
        return group

    def populate_details(self):
        """Populate the form fields with loaded test data"""
        data = self.test_data
        
        # Test Info
        # Set date in date edit
        date_str = str(data.get('date', ''))
        if date_str:
            try:
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():
                    self.date_edit.setDate(date)
            except Exception as e:
                print(f"Error setting date: {e}")
        
        # Set distance in dropdown
        distance = str(data.get('distance_m', ''))
        if distance:
            # Try to find the distance in the dropdown
            distance_text = f"{distance}m"
            index = self.distance_combo.findText(distance_text)
            if index >= 0:
                self.distance_combo.setCurrentIndex(index)
            else:
                # If not found, add it
                self.distance_combo.addItem(distance_text)
                self.distance_combo.setCurrentText(distance_text)
        
        # Set notes in text edit
        self.notes_edit.setText(str(data.get('notes', '')))

        # Platform
        platform_data = data.get('platform', {}) # Access nested platform data
        
        # Set calibre in dropdown
        calibre = str(platform_data.get('calibre', ''))
        index = self.calibre_combo.findText(calibre)
        if index >= 0:
            self.calibre_combo.setCurrentIndex(index)
        elif calibre:
            # If not found in the list but has a value, add it
            self.calibre_combo.addItem(calibre)
            self.calibre_combo.setCurrentText(calibre)
        
        # Set rifle in dropdown
        rifle = str(platform_data.get('rifle', ''))
        index = self.rifle_combo.findText(rifle)
        if index >= 0:
            self.rifle_combo.setCurrentIndex(index)
        elif rifle:
            # If not found in the list but has a value, add it
            self.rifle_combo.addItem(rifle)
            self.rifle_combo.setCurrentText(rifle)

        # Ammunition - Bullet
        ammo_data = data.get('ammo', {}) # Access nested ammo data
        bullet_data = ammo_data.get('bullet', {})
        
        # Set bullet brand in dropdown
        bullet_brand = str(bullet_data.get('brand', ''))
        index = self.bullet_brand_combo.findText(bullet_brand)
        if index >= 0:
            self.bullet_brand_combo.setCurrentIndex(index)
        elif bullet_brand:
            # If not found in the list but has a value, add it
            self.bullet_brand_combo.addItem(bullet_brand)
            self.bullet_brand_combo.setCurrentText(bullet_brand)
        
        # Set bullet model in dropdown
        bullet_model = str(bullet_data.get('model', ''))
        index = self.bullet_model_combo.findText(bullet_model)
        if index >= 0:
            self.bullet_model_combo.setCurrentIndex(index)
        elif bullet_model:
            # If not found in the list but has a value, add it
            self.bullet_model_combo.addItem(bullet_model)
            self.bullet_model_combo.setCurrentText(bullet_model)
        
        # Set bullet weight in spinner
        bullet_weight = bullet_data.get('weight_gr')
        if bullet_weight is not None:
            try:
                self.bullet_weight_spin.setValue(float(bullet_weight))
            except (ValueError, TypeError):
                pass

        # Ammunition - Powder
        powder_data = ammo_data.get('powder', {})
        
        # Set powder brand in dropdown
        powder_brand = str(powder_data.get('brand', ''))
        index = self.powder_brand_combo.findText(powder_brand)
        if index >= 0:
            self.powder_brand_combo.setCurrentIndex(index)
        elif powder_brand:
            # If not found in the list but has a value, add it
            self.powder_brand_combo.addItem(powder_brand)
            self.powder_brand_combo.setCurrentText(powder_brand)
        
        # Set powder model in dropdown
        powder_model = str(powder_data.get('model', ''))
        index = self.powder_model_combo.findText(powder_model)
        if index >= 0:
            self.powder_model_combo.setCurrentIndex(index)
        elif powder_model:
            # If not found in the list but has a value, add it
            self.powder_model_combo.addItem(powder_model)
            self.powder_model_combo.setCurrentText(powder_model)
        
        # Set powder charge in spinner
        powder_charge = powder_data.get('charge_gr')
        if powder_charge is not None:
            try:
                self.powder_charge_spin.setValue(float(powder_charge))
            except (ValueError, TypeError):
                pass

        # Ammunition - Cartridge/Case/Primer
        # Set cartridge OAL in spinner
        coal = ammo_data.get('coal_in')
        if coal is not None:
            try:
                self.cartridge_oal_spin.setValue(float(coal))
            except (ValueError, TypeError):
                pass
        
        # Set cartridge BTO in spinner
        b2o = ammo_data.get('b2o_in')
        if b2o is not None:
            try:
                self.cartridge_bto_spin.setValue(float(b2o))
            except (ValueError, TypeError):
                pass
        
        # Set case brand in dropdown
        case_data = ammo_data.get('case', {})
        case_brand = str(case_data.get('brand', ''))
        index = self.case_brand_combo.findText(case_brand)
        if index >= 0:
            self.case_brand_combo.setCurrentIndex(index)
        elif case_brand:
            # If not found in the list but has a value, add it
            self.case_brand_combo.addItem(case_brand)
            self.case_brand_combo.setCurrentText(case_brand)
        
        # Set primer brand in dropdown
        primer_data = ammo_data.get('primer', {})
        primer_brand = str(primer_data.get('brand', ''))
        index = self.primer_brand_combo.findText(primer_brand)
        if index >= 0:
            self.primer_brand_combo.setCurrentIndex(index)
        elif primer_brand:
            # If not found in the list but has a value, add it
            self.primer_brand_combo.addItem(primer_brand)
            self.primer_brand_combo.setCurrentText(primer_brand)
        
        # Set primer model in dropdown
        primer_model = str(primer_data.get('model', ''))
        index = self.primer_model_combo.findText(primer_model)
        if index >= 0:
            self.primer_model_combo.setCurrentIndex(index)
        elif primer_model:
            # If not found in the list but has a value, add it
            self.primer_model_combo.addItem(primer_model)
            self.primer_model_combo.setCurrentText(primer_model)

        # Environment data
        env_data = data.get('environment', {})
        self.temperature_c_edit.setText(str(env_data.get('temperature_c', '')))
        self.humidity_percent_edit.setText(str(env_data.get('humidity_percent', '')))
        self.pressure_hpa_edit.setText(str(env_data.get('pressure_hpa', '')))
        self.wind_speed_mps_edit.setText(str(env_data.get('wind_speed_mps', '')))
        self.wind_dir_deg_edit.setText(str(env_data.get('wind_dir_deg', '')))
        
        # Set weather in dropdown
        weather = str(env_data.get('weather', ''))
        if weather:
            index = self.weather_combo.findText(weather)
            if index >= 0:
                self.weather_combo.setCurrentIndex(index)
            elif weather:
                # If not found in the list but has a value, add it
                self.weather_combo.addItem(weather)
                self.weather_combo.setCurrentText(weather)

        # Results - Group
        group_data = data.get('group', {}) # Get the nested group dictionary
        self.shots_edit.setText(str(group_data.get('shots', '')))
        self.group_es_mm_edit.setText(str(group_data.get('group_es_mm', '')))
        self.group_es_moa_edit.setText(str(group_data.get('group_es_moa', '')))
        self.mean_radius_mm_edit.setText(str(group_data.get('mean_radius_mm', '')))
        self.group_es_x_mm_edit.setText(str(group_data.get('group_es_x_mm', '')))
        self.group_es_y_mm_edit.setText(str(group_data.get('group_es_y_mm', '')))
        self.poi_x_mm_edit.setText(str(group_data.get('poi_x_mm', '')))
        self.poi_y_mm_edit.setText(str(group_data.get('poi_y_mm', '')))

        # Results - Velocity (Corrected to chrono)
        chrono_data = data.get('chrono', {})
        self.avg_velocity_edit.setText(str(chrono_data.get('avg_velocity_fps', '')))
        self.sd_velocity_edit.setText(str(chrono_data.get('sd_fps', '')))
        self.es_velocity_edit.setText(str(chrono_data.get('es_fps', '')))

    def load_image(self):
        """Load and display the target image"""
        if not self.current_test_id:
            self.image_label.setText("Select a test to view image")
            self.image_label.setPixmap(QPixmap()) # Clear previous image
            return

        test_dir = os.path.join(self.tests_dir, self.current_test_id)
        image_path = None

        try:
            if not os.path.isdir(test_dir):
                 self.image_label.setText(f"Directory not found:\n{self.current_test_id}")
                 self.image_label.setPixmap(QPixmap())
                 return
                 
            # Only look for PNG files
            for fname in os.listdir(test_dir):
                if fname.lower().endswith('.png'):
                    image_path = os.path.join(test_dir, fname)
                    break 
            
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                # Scale pixmap to fit the label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText(f"No image found for\n{self.current_test_id}")
                self.image_label.setPixmap(QPixmap()) # Clear previous image

        except Exception as e:
            print(f"Error loading image for {self.current_test_id}: {e}")
            self.image_label.setText(f"Error loading image for\n{self.current_test_id}")
            self.image_label.setPixmap(QPixmap())

    def clear_details(self):
        """Clear all detail fields"""
        self.current_test_id = None
        self.test_data = {}
        
        # Reset date to current date
        self.date_edit.setDate(QDate.currentDate())
        
        # Clear notes
        self.notes_edit.clear()
        
        # Reset dropdowns to first item if they have items
        if self.distance_combo.count() > 0:
            self.distance_combo.setCurrentIndex(0)
        if self.calibre_combo.count() > 0:
            self.calibre_combo.setCurrentIndex(0)
        if self.rifle_combo.count() > 0:
            self.rifle_combo.setCurrentIndex(0)
        if self.bullet_brand_combo.count() > 0:
            self.bullet_brand_combo.setCurrentIndex(0)
        if self.bullet_model_combo.count() > 0:
            self.bullet_model_combo.setCurrentIndex(0)
        if self.powder_brand_combo.count() > 0:
            self.powder_brand_combo.setCurrentIndex(0)
        if self.powder_model_combo.count() > 0:
            self.powder_model_combo.setCurrentIndex(0)
        if self.case_brand_combo.count() > 0:
            self.case_brand_combo.setCurrentIndex(0)
        if self.primer_brand_combo.count() > 0:
            self.primer_brand_combo.setCurrentIndex(0)
        if self.primer_model_combo.count() > 0:
            self.primer_model_combo.setCurrentIndex(0)
        
        # Reset spinners to minimum values
        self.bullet_weight_spin.setValue(self.bullet_weight_spin.minimum())
        self.powder_charge_spin.setValue(self.powder_charge_spin.minimum())
        self.cartridge_oal_spin.setValue(self.cartridge_oal_spin.minimum())
        self.cartridge_bto_spin.setValue(self.cartridge_bto_spin.minimum())
        
        # Clear all QLineEdit fields (for results)
        for group_box in self.findChildren(QGroupBox):
            # Check if it's the image group, skip clearing label
            if group_box.title() != "Target Image": 
                for line_edit in group_box.findChildren(QLineEdit):
                    line_edit.clear()
        
        # Clear image
        self.image_label.setText("Select a test to view details")
        self.image_label.setPixmap(QPixmap())

    def delete_test(self):
        """Delete the currently selected test"""
        if not self.current_test_id:
            QMessageBox.warning(self, "No Test Selected", "Please select a test to delete.")
            return
        
        # Confirm deletion with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the test:\n{self.current_test_id}?\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default is No to prevent accidental deletion
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            test_dir = os.path.join(self.tests_dir, self.current_test_id)
            
            try:
                # Delete all files in the directory
                for filename in os.listdir(test_dir):
                    file_path = os.path.join(test_dir, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                
                # Delete the directory
                os.rmdir(test_dir)
                
                # Clear the form
                self.clear_details()
                
                # Refresh the test ID list
                self.populate_test_ids()
                
                # Emit signal to notify other widgets that a test has been deleted
                self.testDeleted.emit()
                
                QMessageBox.information(self, "Test Deleted", f"Test {self.current_test_id} has been deleted successfully.")
                
                # Reset current_test_id after successful deletion
                self.current_test_id = None
                
            except Exception as e:
                QMessageBox.critical(self, "Deletion Error", f"Failed to delete test {self.current_test_id}:\n{e}")
    
    def save_changes(self):
        """Save the modified test data back to group.yaml"""
        if not self.current_test_id:
            QMessageBox.warning(self, "No Test Selected", "Please select a test before saving.")
            return
            
        print(f"Saving changes for test: {self.current_test_id}") # Debug print
        
        # --- Create a new dictionary to hold updated data ---
        # This avoids modifying self.test_data directly until saving is confirmed
        updated_data = {} 
        
        # Helper function to safely convert text to float/int or return None
        def safe_convert(text, type_func):
            stripped_text = text.strip()
            if not stripped_text:
                return None
            try:
                return type_func(stripped_text)
            except ValueError:
                 QMessageBox.warning(self, "Input Error", f"Invalid number format: '{text}'")
                 return "INVALID_INPUT" # Special marker for error

        error_occurred = False

        # Test Info
        # Get date from QDateEdit
        updated_data['date'] = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Get distance from QComboBox
        distance_text = self.distance_combo.currentText()
        if distance_text:
            # Extract numeric part from "100m" format
            distance_val = distance_text.replace('m', '')
            try:
                updated_data['distance_m'] = int(distance_val)
            except ValueError:
                QMessageBox.warning(self, "Input Error", f"Invalid distance format: '{distance_text}'")
                error_occurred = True
        
        # Get notes from QTextEdit
        updated_data['notes'] = self.notes_edit.toPlainText() or None

        # Platform (Corrected nesting)
        platform_data = {}
        platform_data['calibre'] = self.calibre_combo.currentText() or None
        platform_data['rifle'] = self.rifle_combo.currentText() or None
        if any(platform_data.values()): updated_data['platform'] = platform_data

        # --- Ammunition (Main Key) ---
        ammo_data = {}

        # Ammunition - Bullet
        bullet_data = {}
        bullet_data['brand'] = self.bullet_brand_combo.currentText() or None
        bullet_data['model'] = self.bullet_model_combo.currentText() or None
        bullet_data['weight_gr'] = self.bullet_weight_spin.value() if self.bullet_weight_spin.value() > 0 else None
        if any(bullet_data.values()): ammo_data['bullet'] = bullet_data

        # Ammunition - Powder
        powder_data = {}
        powder_data['brand'] = self.powder_brand_combo.currentText() or None
        powder_data['model'] = self.powder_model_combo.currentText() or None
        powder_data['charge_gr'] = self.powder_charge_spin.value() if self.powder_charge_spin.value() > 0 else None
        if any(powder_data.values()): ammo_data['powder'] = powder_data

        # Ammunition - Cartridge/Case/Primer
        oal_val = self.cartridge_oal_spin.value() if self.cartridge_oal_spin.value() > 0 else None
        bto_val = self.cartridge_bto_spin.value() if self.cartridge_bto_spin.value() > 0 else None
        if oal_val is not None: ammo_data['coal_in'] = oal_val # Use correct key
        if bto_val is not None: ammo_data['b2o_in'] = bto_val # Use correct key
        
        case_data = {}
        case_data['brand'] = self.case_brand_combo.currentText() or None
        # Add other case fields if they exist in UI
        if any(case_data.values()): ammo_data['case'] = case_data
        
        primer_data = {}
        primer_data['brand'] = self.primer_brand_combo.currentText() or None
        primer_data['model'] = self.primer_model_combo.currentText() or None
        if any(primer_data.values()): ammo_data['primer'] = primer_data
        
        # Add ammo_data to updated_data if it's not empty
        if ammo_data: updated_data['ammo'] = ammo_data

        # --- Results ---
        # Environment data
        env_data = {}
        temp_val = safe_convert(self.temperature_c_edit.text(), float)
        humidity_val = safe_convert(self.humidity_percent_edit.text(), float)
        pressure_val = safe_convert(self.pressure_hpa_edit.text(), float)
        wind_speed_val = safe_convert(self.wind_speed_mps_edit.text(), float)
        wind_dir_val = safe_convert(self.wind_dir_deg_edit.text(), float)
        
        if temp_val == "INVALID_INPUT" or humidity_val == "INVALID_INPUT" or pressure_val == "INVALID_INPUT" or wind_speed_val == "INVALID_INPUT" or wind_dir_val == "INVALID_INPUT": 
            error_occurred = True
        
        env_data['temperature_c'] = temp_val
        env_data['humidity_percent'] = humidity_val
        env_data['pressure_hpa'] = pressure_val
        env_data['wind_speed_mps'] = wind_speed_val
        env_data['wind_dir_deg'] = wind_dir_val
        env_data['weather'] = self.weather_combo.currentText() or None
        
        if any(v is not None for v in env_data.values()): 
            updated_data['environment'] = env_data

        # Results - Group
        group_data = {}
        shots_val = safe_convert(self.shots_edit.text(), int)
        es_mm_val = safe_convert(self.group_es_mm_edit.text(), float)
        es_moa_val = safe_convert(self.group_es_moa_edit.text(), float)
        mean_rad_val = safe_convert(self.mean_radius_mm_edit.text(), float)
        es_x_val = safe_convert(self.group_es_x_mm_edit.text(), float)
        es_y_val = safe_convert(self.group_es_y_mm_edit.text(), float)
        poi_x_val = safe_convert(self.poi_x_mm_edit.text(), float)
        poi_y_val = safe_convert(self.poi_y_mm_edit.text(), float)
        
        if shots_val == "INVALID_INPUT" or es_mm_val == "INVALID_INPUT" or es_moa_val == "INVALID_INPUT" or mean_rad_val == "INVALID_INPUT" or es_x_val == "INVALID_INPUT" or es_y_val == "INVALID_INPUT" or poi_x_val == "INVALID_INPUT" or poi_y_val == "INVALID_INPUT":
            error_occurred = True
        
        # Use correct keys from YAML when saving
        group_data['shots'] = shots_val
        group_data['group_es_mm'] = es_mm_val 
        group_data['group_es_moa'] = es_moa_val 
        group_data['mean_radius_mm'] = mean_rad_val
        group_data['group_es_x_mm'] = es_x_val
        group_data['group_es_y_mm'] = es_y_val
        group_data['poi_x_mm'] = poi_x_val
        group_data['poi_y_mm'] = poi_y_val
        
        if any(v is not None for v in group_data.values()): 
            updated_data['group'] = group_data

        # Results - Velocity (Chrono)
        chrono_data = {}
        avg_v_val = safe_convert(self.avg_velocity_edit.text(), float)
        sd_v_val = safe_convert(self.sd_velocity_edit.text(), float)
        es_v_val = safe_convert(self.es_velocity_edit.text(), float)
        
        if avg_v_val == "INVALID_INPUT" or sd_v_val == "INVALID_INPUT" or es_v_val == "INVALID_INPUT": 
            error_occurred = True
        
        # Use correct keys from YAML when saving
        chrono_data['avg_velocity_fps'] = avg_v_val 
        chrono_data['sd_fps'] = sd_v_val
        chrono_data['es_fps'] = es_v_val
        
        if any(v is not None for v in chrono_data.values()): 
            updated_data['chrono'] = chrono_data

        if error_occurred:
            return # Stop if there was a conversion error

        # --- Final cleanup of None values before saving ---
        # This recursive function removes keys with None values
        def remove_none_values(d):
            if not isinstance(d, dict):
                return d
            # Process dictionary items, ensuring nested dictionaries are also cleaned
            cleaned_dict = {}
            for k, v in d.items():
                cleaned_v = remove_none_values(v)
                # Keep key if value is not None, or if it's a non-empty dictionary after cleaning
                if cleaned_v is not None and not (isinstance(cleaned_v, dict) and not cleaned_v):
                    cleaned_dict[k] = cleaned_v
            return cleaned_dict

        final_data_to_save = remove_none_values(updated_data)

        # --- Write updated data back to group.yaml ---
        test_dir = os.path.join(self.tests_dir, self.current_test_id)
        group_yaml_path = os.path.join(test_dir, "group.yaml")

        try:
            with open(group_yaml_path, 'w') as f:
                yaml.dump(final_data_to_save, f, default_flow_style=False, sort_keys=False, indent=2) # Added indent
            self.test_data = final_data_to_save # Update internal data state after successful save
            
            # Emit signal to notify other widgets that a test has been updated
            self.testUpdated.emit()
            
            QMessageBox.information(self, "Save Successful", f"Changes saved successfully for {self.current_test_id}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save changes for {self.current_test_id}:\n{e}")

        # TODO: Consider if CSV needs updating (might be complex if structure changes)
