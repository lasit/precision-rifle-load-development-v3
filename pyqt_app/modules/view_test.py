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
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QFormLayout, QLineEdit, QGroupBox, QScrollArea,
                             QMessageBox, QStyle, QDoubleSpinBox, QDateEdit, QTextEdit,
                             QSlider, QToolBar, QSizePolicy, QTabWidget, QSplitter,
                             QTableView)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QPoint, QRect, QSize, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent, QTransform, QCursor

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import settings manager and data loader
from utils.settings_manager import SettingsManager
from utils.data_loader import load_all_test_data
# Import TestDataModel from data_analysis module
from .data_analysis import TestDataModel

# Path to the Lists.yaml file (relative to the project root)
COMPONENT_LIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Lists.yaml"
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
        
        # Initialize data
        self.all_data = pd.DataFrame()
        self.filtered_data = pd.DataFrame()
        
        # Variable to store copied environment data
        self.copied_env_data = None
        
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
        
        # Load component lists
        self.component_lists = self.load_component_lists()

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout) # Set the layout for the widget
        
        # Create a splitter for the filter/table section and details section
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(self.main_splitter)
        
        # Top section: Filters and Table
        filter_table_widget = QWidget()
        filter_table_layout = QVBoxLayout(filter_table_widget)
        
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
        
        filter_table_layout.addLayout(filter_header)
        
        # Filter groups in horizontal layout
        filter_groups = QHBoxLayout()
        
        # Test Info filters
        test_info_group = QGroupBox("Test Info")
        test_info_layout = QFormLayout(test_info_group)
        
        # Date range filter with calendar popups
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        # We'll set the actual date range after loading data
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        # We'll set the actual date range after loading data
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.date_to)
        test_info_layout.addRow("Date Range:", date_layout)
        
        # Distance filter
        self.distance_filter_combo = QComboBox()
        self.distance_filter_combo.addItems(["All", "100m", "200m", "300m"])
        test_info_layout.addRow("Distance:", self.distance_filter_combo)
        
        filter_groups.addWidget(test_info_group)
        
        # Platform filters
        platform_group = QGroupBox("Platform")
        platform_layout = QFormLayout(platform_group)
        
        # Calibre filter
        self.calibre_filter_combo = QComboBox()
        self.calibre_filter_combo.addItem("All")
        platform_layout.addRow("Calibre:", self.calibre_filter_combo)
        
        # Rifle filter
        self.rifle_filter_combo = QComboBox()
        self.rifle_filter_combo.addItem("All")
        platform_layout.addRow("Rifle:", self.rifle_filter_combo)
        
        filter_groups.addWidget(platform_group)
        
        # Ammunition filters
        ammo_group = QGroupBox("Ammunition")
        ammo_layout = QFormLayout(ammo_group)
        
        # Bullet brand filter
        self.bullet_brand_filter_combo = QComboBox()
        self.bullet_brand_filter_combo.addItem("All")
        ammo_layout.addRow("Bullet Brand:", self.bullet_brand_filter_combo)
        
        # Bullet weight filter
        self.bullet_weight_min = QLineEdit()
        self.bullet_weight_max = QLineEdit()
        bullet_weight_layout = QHBoxLayout()
        bullet_weight_layout.addWidget(self.bullet_weight_min)
        bullet_weight_layout.addWidget(QLabel("to"))
        bullet_weight_layout.addWidget(self.bullet_weight_max)
        ammo_layout.addRow("Bullet Weight (gr):", bullet_weight_layout)
        
        # Powder brand filter
        self.powder_brand_filter_combo = QComboBox()
        self.powder_brand_filter_combo.addItem("All")
        ammo_layout.addRow("Powder Brand:", self.powder_brand_filter_combo)
        
        # Powder model filter
        self.powder_model_filter_combo = QComboBox()
        self.powder_model_filter_combo.addItem("All")
        ammo_layout.addRow("Powder Model:", self.powder_model_filter_combo)
        
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
        
        # Results Target filters
        results_target_group = QGroupBox("Results Target")
        results_target_layout = QFormLayout(results_target_group)
        
        # Number of shots filter
        self.shots_min = QLineEdit()
        self.shots_max = QLineEdit()
        shots_layout = QHBoxLayout()
        shots_layout.addWidget(self.shots_min)
        shots_layout.addWidget(QLabel("to"))
        shots_layout.addWidget(self.shots_max)
        results_target_layout.addRow("Number of shots:", shots_layout)
        
        # Group size range filter
        self.group_es_min = QLineEdit()
        self.group_es_max = QLineEdit()
        group_es_layout = QHBoxLayout()
        group_es_layout.addWidget(self.group_es_min)
        group_es_layout.addWidget(QLabel("to"))
        group_es_layout.addWidget(self.group_es_max)
        results_target_layout.addRow("Group ES (mm):", group_es_layout)
        
        # Group ES MOA filter
        self.group_es_moa_min = QLineEdit()
        self.group_es_moa_max = QLineEdit()
        group_es_moa_layout = QHBoxLayout()
        group_es_moa_layout.addWidget(self.group_es_moa_min)
        group_es_moa_layout.addWidget(QLabel("to"))
        group_es_moa_layout.addWidget(self.group_es_moa_max)
        results_target_layout.addRow("Group ES (MOA):", group_es_moa_layout)
        
        # Mean Radius filter
        self.mean_radius_min = QLineEdit()
        self.mean_radius_max = QLineEdit()
        mean_radius_layout = QHBoxLayout()
        mean_radius_layout.addWidget(self.mean_radius_min)
        mean_radius_layout.addWidget(QLabel("to"))
        mean_radius_layout.addWidget(self.mean_radius_max)
        results_target_layout.addRow("Mean Radius (mm):", mean_radius_layout)
        
        filter_groups.addWidget(results_target_group)
        
        # Results Velocity filters
        results_velocity_group = QGroupBox("Results Velocity")
        results_velocity_layout = QFormLayout(results_velocity_group)
        
        # Avg Velocity filter
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
        
        filter_table_layout.addLayout(filter_groups)
        
        # Apply filters button
        apply_button = QPushButton("Apply Filters")
        apply_button.clicked.connect(self.apply_filters)
        filter_table_layout.addWidget(apply_button)
        
        # Table header
        table_header = QHBoxLayout()
        table_label = QLabel("Filtered Tests")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.result_count_label = QLabel("0 tests found")
        table_header.addWidget(table_label)
        table_header.addStretch()
        table_header.addWidget(self.result_count_label)
        
        filter_table_layout.addLayout(table_header)
        
        # Test table
        self.test_table = QTableView()
        self.test_model = TestDataModel()
        self.test_table.setModel(self.test_model)
        
        # Enable sorting
        self.test_table.setSortingEnabled(True)
        
        # Enable selection
        self.test_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.test_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # Connect selection to load test
        self.test_table.selectionModel().selectionChanged.connect(self.on_table_selection_changed)
        
        filter_table_layout.addWidget(self.test_table)
        
        # Add the filter/table widget to the splitter
        self.main_splitter.addWidget(filter_table_widget)
        
        # Bottom section: Test details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        # Scroll Area for test details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        details_layout.addWidget(scroll_area)

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
        
        details_layout.addLayout(buttons_layout)
        
        # Add the details widget to the splitter
        self.main_splitter.addWidget(details_widget)
        
        # Set initial splitter sizes
        self.main_splitter.setSizes([300, 700])
        
        # Load test data
        self.load_data()

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
        
        # Sky (Weather)
        current_weather = self.weather_combo.currentText()
        self.weather_combo.clear()
        sky_list = self.component_lists.get('sky', [])
        if sky_list:
            self.weather_combo.addItems(sky_list)
            index = self.weather_combo.findText(current_weather)
            if index >= 0:
                self.weather_combo.setCurrentIndex(index)
            elif current_weather:
                self.weather_combo.addItem(current_weather)
                self.weather_combo.setCurrentText(current_weather)
        else:
            # Fallback to hardcoded values if list is empty
            self.weather_combo.addItems(["Clear", "Partly Cloudy", "Cloudy", "Overcast", "Rain", "Snow"])
    
    def refresh(self):
        """Refresh the widget data (test IDs list)"""
        # Update tests directory from settings manager
        self.tests_dir = self.settings_manager.get_tests_directory()
        self.populate_test_ids()
        self.refresh_component_lists()
        
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
    
    def load_data(self):
        """Load test data from files"""
        try:
            # Load all test data
            self.all_data = load_all_test_data(self.tests_dir)
            
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
        
        # Print debug info about date range in the data
        if 'date' in self.all_data.columns:
            min_date = self.all_data['date'].min()
            max_date = self.all_data['date'].max()
            print(f"DEBUG: All data date range: {min_date} to {max_date}")
        
        # Make a copy of the data for filtering
        self.filtered_data = self.all_data.copy()
        
        # Register auto-range filters BEFORE updating the UI
        self.register_auto_range_filter('date', 'date', self.date_from, self.date_to, True)
        
        # Update filter ranges based on the FULL dataset
        # This ensures the date range reflects ALL available data
        self.disable_auto_range = False  # Make sure auto-range is enabled
        self.update_filter_ranges(self.all_data)  # Use all_data, not filtered_data
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update result count
        self.result_count_label.setText(f"{len(self.filtered_data)} tests found")
        
        # Populate filter dropdowns
        self.populate_filters()
    
    def populate_filters(self):
        """Populate filter dropdowns with values from the data"""
        # Calibre filter
        calibres = sorted(self.all_data["calibre"].unique())
        self.calibre_filter_combo.clear()
        self.calibre_filter_combo.addItem("All")
        self.calibre_filter_combo.addItems([str(c) for c in calibres if pd.notna(c)])
        
        # Rifle filter
        rifles = sorted(self.all_data["rifle"].unique())
        self.rifle_filter_combo.clear()
        self.rifle_filter_combo.addItem("All")
        self.rifle_filter_combo.addItems([str(r) for r in rifles if pd.notna(r)])
        
        # Bullet brand filter
        bullet_brands = sorted(self.all_data["bullet_brand"].unique())
        self.bullet_brand_filter_combo.clear()
        self.bullet_brand_filter_combo.addItem("All")
        self.bullet_brand_filter_combo.addItems([str(b) for b in bullet_brands if pd.notna(b)])
        
        # Powder brand filter
        powder_brands = sorted(self.all_data["powder_brand"].unique())
        self.powder_brand_filter_combo.clear()
        self.powder_brand_filter_combo.addItem("All")
        self.powder_brand_filter_combo.addItems([str(p) for p in powder_brands if pd.notna(p)])
        
        # Powder model filter
        powder_models = sorted(self.all_data["powder_model"].unique())
        self.powder_model_filter_combo.clear()
        self.powder_model_filter_combo.addItem("All")
        self.powder_model_filter_combo.addItems([str(p) for p in powder_models if pd.notna(p)])
        
        # Distance filter
        distances = sorted(self.all_data["distance_m"].unique())
        self.distance_filter_combo.clear()
        self.distance_filter_combo.addItem("All")
        self.distance_filter_combo.addItems([f"{int(d)}m" for d in distances if pd.notna(d)])
    
    def apply_filters(self):
        """Apply filters to the data"""
        filtered_df = self.all_data.copy()
        
        # Flag to track if we should apply date filter
        apply_date_filter = True
        
        # Store date filter values for later use
        try:
            from_date = self.date_from.date().toString("yyyy-MM-dd")
            to_date = self.date_to.date().toString("yyyy-MM-dd")
        except Exception as e:
            print(f"Error getting date filter values: {e}")
            apply_date_filter = False
        
        # Apply distance filter
        if self.distance_filter_combo.currentText() != "All":
            distance_text = self.distance_filter_combo.currentText()
            distance_value = int(distance_text.replace('m', ''))
            filtered_df = filtered_df[filtered_df["distance_m"] == distance_value]
        
        # Apply calibre filter
        if self.calibre_filter_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["calibre"] == self.calibre_filter_combo.currentText()]
        
        # Apply rifle filter
        if self.rifle_filter_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["rifle"] == self.rifle_filter_combo.currentText()]
        
        # Apply bullet brand filter
        if self.bullet_brand_filter_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["bullet_brand"] == self.bullet_brand_filter_combo.currentText()]
        
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
        if self.powder_brand_filter_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["powder_brand"] == self.powder_brand_filter_combo.currentText()]
        
        # Apply powder model filter
        if self.powder_model_filter_combo.currentText() != "All":
            filtered_df = filtered_df[filtered_df["powder_model"] == self.powder_model_filter_combo.currentText()]
        
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
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["shots"].notna()
                    mask = mask & (filtered_df["shots"] >= min_shots)
                    mask = mask & (filtered_df["shots"] <= max_shots)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'shots' column not found in the data")
            except ValueError as e:
                print(f"Error converting Number of shots filter values: {e}")
            except Exception as e:
                print(f"Error applying Number of shots filter: {e}")
        
        # Group ES (mm) filter
        if self.group_es_min.text() and self.group_es_max.text():
            try:
                min_group_es = float(self.group_es_min.text())
                max_group_es = float(self.group_es_max.text())
                
                # Check if the column exists in the dataframe
                if "group_es_mm" in filtered_df.columns:
                    # Handle NaN values by creating a mask that excludes them
                    mask = filtered_df["group_es_mm"].notna()
                    mask = mask & (filtered_df["group_es_mm"] >= min_group_es)
                    mask = mask & (filtered_df["group_es_mm"] <= max_group_es)
                    
                    # Apply the mask to filter the dataframe
                    filtered_df = filtered_df[mask]
                else:
                    print("Warning: 'group_es_mm' column not found in the data")
            except ValueError as e:
                print(f"Error converting Group ES (mm) filter values: {e}")
            except Exception as e:
                print(f"Error applying Group ES (mm) filter: {e}")
        
        # Group ES MOA filter
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
        
        # At this point, all non-date filters have been applied
        # Update the auto-range filters based on the current filtered data
        # This will update the date range filter to show the min/max dates in the filtered data
        self.disable_auto_range = True
        self.update_filter_ranges(filtered_df)
        self.disable_auto_range = False
        
        # Now apply the date filter if needed
        if apply_date_filter and "date" in filtered_df.columns:
            try:
                # Handle NaN values by creating a mask that excludes them
                mask = filtered_df["date"].notna()
                mask = mask & (filtered_df["date"] >= from_date)
                mask = mask & (filtered_df["date"] <= to_date)
                
                # Apply the mask to filter the dataframe
                filtered_df = filtered_df[mask]
            except Exception as e:
                print(f"Error applying date filter: {e}")
        
        # Update filtered data
        self.filtered_data = filtered_df
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update result count
        self.result_count_label.setText(f"{len(self.filtered_data)} tests found")
        
        # Update auto-range filters based on the filtered data
        # Temporarily disable auto-ranging to prevent infinite recursion
        self.disable_auto_range = True
        self.update_filter_ranges(self.filtered_data)
        self.disable_auto_range = False
    
    def _save_current_filters(self):
        """Save current filter values to a dictionary"""
        filters = {
            # Dropdowns
            'calibre': self.calibre_filter_combo.currentText(),
            'rifle': self.rifle_filter_combo.currentText(),
            'bullet_brand': self.bullet_brand_filter_combo.currentText(),
            'powder_brand': self.powder_brand_filter_combo.currentText(),
            'powder_model': self.powder_model_filter_combo.currentText(),
            'distance': self.distance_filter_combo.currentText(),
            
            # Date range
            'date_from': self.date_from.date(),
            'date_to': self.date_to.date(),
            
            # Ammunition filters
            'bullet_weight_min': self.bullet_weight_min.text(),
            'bullet_weight_max': self.bullet_weight_max.text(),
            'charge_min': self.charge_min.text(),
            'charge_max': self.charge_max.text(),
            'coal_min': self.coal_min.text(),
            'coal_max': self.coal_max.text(),
            'b2o_min': self.b2o_min.text(),
            'b2o_max': self.b2o_max.text(),
            
            # Results Target filters
            'shots_min': self.shots_min.text(),
            'shots_max': self.shots_max.text(),
            'group_es_min': self.group_es_min.text(),
            'group_es_max': self.group_es_max.text(),
            'group_es_moa_min': self.group_es_moa_min.text(),
            'group_es_moa_max': self.group_es_moa_max.text(),
            'mean_radius_min': self.mean_radius_min.text(),
            'mean_radius_max': self.mean_radius_max.text(),
            
            # Results Velocity filters
            'avg_velocity_min': self.avg_velocity_min.text(),
            'avg_velocity_max': self.avg_velocity_max.text(),
            'sd_velocity_min': self.sd_velocity_min.text(),
            'sd_velocity_max': self.sd_velocity_max.text(),
            'es_velocity_min': self.es_velocity_min.text(),
            'es_velocity_max': self.es_velocity_max.text()
        }
        return filters
    
    def _restore_filters(self, filters):
        """Restore filter values from a dictionary"""
        # Dropdowns
        index = self.calibre_filter_combo.findText(filters['calibre'])
        if index >= 0:
            self.calibre_filter_combo.setCurrentIndex(index)
            
        index = self.rifle_filter_combo.findText(filters['rifle'])
        if index >= 0:
            self.rifle_filter_combo.setCurrentIndex(index)
            
        index = self.bullet_brand_filter_combo.findText(filters['bullet_brand'])
        if index >= 0:
            self.bullet_brand_filter_combo.setCurrentIndex(index)
            
        index = self.powder_brand_filter_combo.findText(filters['powder_brand'])
        if index >= 0:
            self.powder_brand_filter_combo.setCurrentIndex(index)
            
        index = self.powder_model_filter_combo.findText(filters['powder_model'])
        if index >= 0:
            self.powder_model_filter_combo.setCurrentIndex(index)
            
        index = self.distance_filter_combo.findText(filters['distance'])
        if index >= 0:
            self.distance_filter_combo.setCurrentIndex(index)
        
        # Date range
        self.date_from.setDate(filters['date_from'])
        self.date_to.setDate(filters['date_to'])
        
        # Ammunition filters
        self.bullet_weight_min.setText(filters['bullet_weight_min'])
        self.bullet_weight_max.setText(filters['bullet_weight_max'])
        self.charge_min.setText(filters['charge_min'])
        self.charge_max.setText(filters['charge_max'])
        self.coal_min.setText(filters['coal_min'])
        self.coal_max.setText(filters['coal_max'])
        self.b2o_min.setText(filters['b2o_min'])
        self.b2o_max.setText(filters['b2o_max'])
        
        # Results Target filters
        self.shots_min.setText(filters['shots_min'])
        self.shots_max.setText(filters['shots_max'])
        self.group_es_min.setText(filters['group_es_min'])
        self.group_es_max.setText(filters['group_es_max'])
        self.group_es_moa_min.setText(filters['group_es_moa_min'])
        self.group_es_moa_max.setText(filters['group_es_moa_max'])
        self.mean_radius_min.setText(filters['mean_radius_min'])
        self.mean_radius_max.setText(filters['mean_radius_max'])
        
        # Results Velocity filters
        self.avg_velocity_min.setText(filters['avg_velocity_min'])
        self.avg_velocity_max.setText(filters['avg_velocity_max'])
        self.sd_velocity_min.setText(filters['sd_velocity_min'])
        self.sd_velocity_max.setText(filters['sd_velocity_max'])
        self.es_velocity_min.setText(filters['es_velocity_min'])
        self.es_velocity_max.setText(filters['es_velocity_max'])
    
    def reset_filters(self):
        """Reset all filters to their default values"""
        # Print debug info before reset
        if 'date' in self.all_data.columns:
            min_date = self.all_data['date'].min()
            max_date = self.all_data['date'].max()
            print(f"DEBUG: Before reset - All data date range: {min_date} to {max_date}")
        
        # Reset dropdowns
        self.calibre_filter_combo.setCurrentIndex(0)
        self.rifle_filter_combo.setCurrentIndex(0)
        self.bullet_brand_filter_combo.setCurrentIndex(0)
        self.powder_brand_filter_combo.setCurrentIndex(0)
        self.powder_model_filter_combo.setCurrentIndex(0)
        self.distance_filter_combo.setCurrentIndex(0)
        
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
        
        # Reset Results Velocity filters
        self.avg_velocity_min.clear()
        self.avg_velocity_max.clear()
        self.sd_velocity_min.clear()
        self.sd_velocity_max.clear()
        self.es_velocity_min.clear()
        self.es_velocity_max.clear()
        
        # Reset filtered data to all data
        self.filtered_data = self.all_data.copy()
        
        # Update the table model
        self.test_model.update_data(self.filtered_data)
        
        # Update result count
        self.result_count_label.setText(f"{len(self.filtered_data)} tests found")
        
        # Update date range based on the FULL dataset
        # This ensures the date range reflects ALL available data
        self.disable_auto_range = False  # Make sure auto-range is enabled
        self.update_filter_ranges(self.all_data)  # Use all_data, not filtered_data
        
        # Print debug info after reset
        if 'date' in self.all_data.columns:
            min_date = self.date_from.date().toString("yyyy-MM-dd")
            max_date = self.date_to.date().toString("yyyy-MM-dd")
            print(f"DEBUG: After reset - Date filter set to: {min_date} to {max_date}")
    
    def on_table_selection_changed(self, selected, deselected):
        """Handle selection changes in the table view"""
        # Get the selected row
        indexes = self.test_table.selectionModel().selectedRows()
        if not indexes:
            return
        
        # Get the test_id from the selected row
        row_index = indexes[0].row()
        test_id = self.filtered_data.iloc[row_index]['test_id']
        
        # Load the selected test
        self.current_test_id = test_id
        test_dir = os.path.join(self.tests_dir, self.current_test_id)
        group_yaml_path = os.path.join(test_dir, "group.yaml")
        
        print(f"Loading test from table selection: {self.current_test_id} from {group_yaml_path}")
        
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
    
    def populate_test_ids(self):
        """Refresh the test data and update the table model"""
        try:
            # Load all test data
            self.all_data = load_all_test_data(self.tests_dir)
            
            # Make a copy of the data for filtering
            self.filtered_data = self.all_data.copy()
            
            # Update the table model
            self.test_model.update_data(self.filtered_data)
            
            # Update result count
            self.result_count_label.setText(f"{len(self.filtered_data)} tests found")
            
            # Populate filter dropdowns
            self.populate_filters()
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
        
        # Barrel length (numeric input)
        self.barrel_length_spin = QDoubleSpinBox()
        self.barrel_length_spin.setRange(0, 99.9)
        self.barrel_length_spin.setDecimals(1)
        self.barrel_length_spin.setSingleStep(0.5)
        layout.addRow("Barrel Length (in):", self.barrel_length_spin)
        
        # Twist rate (text input)
        self.twist_rate_edit = QLineEdit()
        self.twist_rate_edit.setPlaceholderText("e.g., 1:8 or 1:10")
        layout.addRow("Twist Rate:", self.twist_rate_edit)
        
        return group

    def _create_ammunition_group(self):
        group = QGroupBox("Ammunition")
        layout = QFormLayout(group)
        
        # Create a tabbed layout for better organization
        ammo_tabs = QTabWidget()
        
        # Case Tab
        case_tab = QWidget()
        case_layout = QFormLayout(case_tab)
        
        # Case Brand (dropdown)
        self.case_brand_combo = QComboBox()
        case_brand_list = self.component_lists.get('case_brand', [])
        if case_brand_list:
            self.case_brand_combo.addItems(case_brand_list)
        case_layout.addRow("Case Brand:", self.case_brand_combo)
        
        # Case Lot (text input)
        self.case_lot_edit = QLineEdit()
        case_layout.addRow("Case Lot:", self.case_lot_edit)
        
        # Neck Turned (dropdown)
        self.neck_turned_combo = QComboBox()
        self.neck_turned_combo.addItems(["No", "Yes"])
        case_layout.addRow("Neck Turned:", self.neck_turned_combo)
        
        # Brass Sizing (dropdown)
        self.brass_sizing_combo = QComboBox()
        brass_sizing_list = self.component_lists.get('brass_sizing', [])
        if brass_sizing_list:
            self.brass_sizing_combo.addItems(brass_sizing_list)
        else:
            self.brass_sizing_combo.addItems(["Neck Only with Bushing", "Neck Only - no bushing", "Full"])
        case_layout.addRow("Brass Sizing:", self.brass_sizing_combo)
        
        # Bushing Size (numeric input)
        self.bushing_size_spin = QDoubleSpinBox()
        self.bushing_size_spin.setRange(0.000, 9.999)
        self.bushing_size_spin.setDecimals(3)
        self.bushing_size_spin.setSingleStep(0.001)
        case_layout.addRow("Bushing Size:", self.bushing_size_spin)
        
        # Shoulder Bump (numeric input)
        self.shoulder_bump_spin = QDoubleSpinBox()
        self.shoulder_bump_spin.setRange(0.0, 9.9)
        self.shoulder_bump_spin.setDecimals(1)
        self.shoulder_bump_spin.setSingleStep(0.1)
        case_layout.addRow("Shoulder Bump (thou):", self.shoulder_bump_spin)
        
        # Bullet Tab
        bullet_tab = QWidget()
        bullet_layout = QFormLayout(bullet_tab)
        
        # Bullet Brand (dropdown)
        self.bullet_brand_combo = QComboBox()
        bullet_brand_list = self.component_lists.get('bullet_brand', [])
        if bullet_brand_list:
            self.bullet_brand_combo.addItems(bullet_brand_list)
        bullet_layout.addRow("Bullet Brand:", self.bullet_brand_combo)
        
        # Bullet Model (dropdown)
        self.bullet_model_combo = QComboBox()
        bullet_model_list = self.component_lists.get('bullet_model', [])
        if bullet_model_list:
            self.bullet_model_combo.addItems(bullet_model_list)
        bullet_layout.addRow("Bullet Model:", self.bullet_model_combo)
        
        # Bullet Weight (numeric input)
        self.bullet_weight_spin = QDoubleSpinBox()
        self.bullet_weight_spin.setRange(0.01, 999.99)
        self.bullet_weight_spin.setDecimals(2)
        self.bullet_weight_spin.setSingleStep(0.1)
        bullet_layout.addRow("Bullet Weight (gr):", self.bullet_weight_spin)
        
        # Bullet Lot (text input)
        self.bullet_lot_edit = QLineEdit()
        bullet_layout.addRow("Bullet Lot:", self.bullet_lot_edit)
        
        # Powder Tab
        powder_tab = QWidget()
        powder_layout = QFormLayout(powder_tab)
        
        # Powder Brand (dropdown)
        self.powder_brand_combo = QComboBox()
        powder_brand_list = self.component_lists.get('powder_brand', [])
        if powder_brand_list:
            self.powder_brand_combo.addItems(powder_brand_list)
        powder_layout.addRow("Powder Brand:", self.powder_brand_combo)
        
        # Powder Model (dropdown)
        self.powder_model_combo = QComboBox()
        powder_model_list = self.component_lists.get('powder_model', [])
        if powder_model_list:
            self.powder_model_combo.addItems(powder_model_list)
        powder_layout.addRow("Powder Model:", self.powder_model_combo)
        
        # Powder Charge (numeric input)
        self.powder_charge_spin = QDoubleSpinBox()
        self.powder_charge_spin.setRange(0.01, 999.99)
        self.powder_charge_spin.setDecimals(2)
        self.powder_charge_spin.setSingleStep(0.1)
        powder_layout.addRow("Powder Charge (gr):", self.powder_charge_spin)
        
        # Powder Lot (text input)
        self.powder_lot_edit = QLineEdit()
        powder_layout.addRow("Powder Lot:", self.powder_lot_edit)
        
        # Cartridge Tab
        cartridge_tab = QWidget()
        cartridge_layout = QFormLayout(cartridge_tab)
        
        # Cartridge OAL (numeric input)
        self.cartridge_oal_spin = QDoubleSpinBox()
        self.cartridge_oal_spin.setRange(0.001, 9.999)
        self.cartridge_oal_spin.setDecimals(3)
        self.cartridge_oal_spin.setSingleStep(0.001)
        cartridge_layout.addRow("Cartridge OAL (in):", self.cartridge_oal_spin)
        
        # Cartridge BTO (numeric input)
        self.cartridge_bto_spin = QDoubleSpinBox()
        self.cartridge_bto_spin.setRange(0.001, 9.999)
        self.cartridge_bto_spin.setDecimals(3)
        self.cartridge_bto_spin.setSingleStep(0.001)
        cartridge_layout.addRow("Cartridge BTO (in):", self.cartridge_bto_spin)
        
        # Primer Tab
        primer_tab = QWidget()
        primer_layout = QFormLayout(primer_tab)
        
        # Primer Brand (dropdown)
        self.primer_brand_combo = QComboBox()
        primer_brand_list = self.component_lists.get('primer_brand', [])
        if primer_brand_list:
            self.primer_brand_combo.addItems(primer_brand_list)
        primer_layout.addRow("Primer Brand:", self.primer_brand_combo)
        
        # Primer Model (dropdown)
        self.primer_model_combo = QComboBox()
        primer_model_list = self.component_lists.get('primer_model', [])
        if primer_model_list:
            self.primer_model_combo.addItems(primer_model_list)
        primer_layout.addRow("Primer Model:", self.primer_model_combo)
        
        # Primer Lot (text input)
        self.primer_lot_edit = QLineEdit()
        primer_layout.addRow("Primer Lot:", self.primer_lot_edit)
        
        # Add tabs to the tab widget
        ammo_tabs.addTab(case_tab, "Case")
        ammo_tabs.addTab(bullet_tab, "Bullet")
        ammo_tabs.addTab(powder_tab, "Powder")
        ammo_tabs.addTab(cartridge_tab, "Cartridge")
        ammo_tabs.addTab(primer_tab, "Primer")
        
        # Add the tab widget to the main layout
        layout.addRow(ammo_tabs)
        
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
    
    def _mm_to_moa(self, mm_value, distance_m):
        """Convert a measurement from mm to MOA based on distance
        
        Args:
            mm_value (float): The measurement in millimeters
            distance_m (int/float): The distance in meters
            
        Returns:
            float: The measurement in MOA, or None if inputs are invalid
        """
        try:
            if mm_value is None or distance_m is None or distance_m <= 0:
                return None
            
            # Convert mm to MOA using the formula: MOA = (mm * 3438) / (distance_in_meters * 1000)
            moa_value = (float(mm_value) * 3438) / (float(distance_m) * 1000)
            return moa_value
        except (ValueError, TypeError, ZeroDivisionError):
            return None
    
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
        self.mean_radius_moa_edit = QLineEdit()
        target_layout.addRow("Group ES (mm):", self.group_es_mm_edit)
        target_layout.addRow("Group ES (MOA):", self.group_es_moa_edit)
        target_layout.addRow("Mean Radius (mm):", self.mean_radius_mm_edit)
        target_layout.addRow("Mean Radius (MOA):", self.mean_radius_moa_edit)
        
        # Group dimensions
        self.group_es_x_mm_edit = QLineEdit()
        self.group_es_x_moa_edit = QLineEdit()
        self.group_es_y_mm_edit = QLineEdit()
        self.group_es_y_moa_edit = QLineEdit()
        target_layout.addRow("Group ES Width-X (mm):", self.group_es_x_mm_edit)
        target_layout.addRow("Group ES Width-X (MOA):", self.group_es_x_moa_edit)
        target_layout.addRow("Group ES Height-Y (mm):", self.group_es_y_mm_edit)
        target_layout.addRow("Group ES Height-Y (MOA):", self.group_es_y_moa_edit)
        
        # Point of impact
        self.poi_x_mm_edit = QLineEdit()
        self.poi_x_moa_edit = QLineEdit()
        self.poi_y_mm_edit = QLineEdit()
        self.poi_y_moa_edit = QLineEdit()
        target_layout.addRow("POA Horizontal-X (mm):", self.poi_x_mm_edit)
        target_layout.addRow("POA Horizontal-X (MOA):", self.poi_x_moa_edit)
        target_layout.addRow("POA Vertical-Y (mm):", self.poi_y_mm_edit)
        target_layout.addRow("POA Vertical-Y (MOA):", self.poi_y_moa_edit)
        
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
        sky_list = self.component_lists.get('sky', [])
        if sky_list:
            self.weather_combo.addItems(sky_list)
        else:
            # Fallback to hardcoded values if list is empty
            self.weather_combo.addItems(["Clear", "Partly Cloudy", "Cloudy", "Overcast", "Rain", "Snow"])
        layout.addRow("Sky:", self.weather_combo)
        
        # Add Copy/Paste buttons
        buttons_layout = QHBoxLayout()
        
        # Copy button
        self.copy_env_button = QPushButton("Copy Environment Data")
        self.copy_env_button.clicked.connect(self.copy_environment_data)
        buttons_layout.addWidget(self.copy_env_button)
        
        # Paste button (initially disabled)
        self.paste_env_button = QPushButton("Paste Environment Data")
        self.paste_env_button.clicked.connect(self.paste_environment_data)
        self.paste_env_button.setEnabled(False)  # Disabled until data is copied
        buttons_layout.addWidget(self.paste_env_button)
        
        # Add buttons to layout
        layout.addRow("", buttons_layout)
        
        return group
    
    def copy_environment_data(self):
        """Copy the current environment data to the clipboard"""
        if not self.current_test_id:
            QMessageBox.warning(self, "No Test Selected", "Please select a test to copy environment data from.")
            return
        
        # Create a dictionary to store the environment data
        self.copied_env_data = {
            'temperature_c': self.temperature_c_edit.text(),
            'humidity_percent': self.humidity_percent_edit.text(),
            'pressure_hpa': self.pressure_hpa_edit.text(),
            'wind_speed_mps': self.wind_speed_mps_edit.text(),
            'wind_dir_deg': self.wind_dir_deg_edit.text(),
            'weather': self.weather_combo.currentText()
        }
        
        # Enable the paste button
        self.paste_env_button.setEnabled(True)
        
        # Show a confirmation message
        QMessageBox.information(self, "Environment Data Copied", 
                               f"Environment data copied from test: {self.current_test_id}\n\n"
                               f"Temperature: {self.copied_env_data['temperature_c']} °C\n"
                               f"Humidity: {self.copied_env_data['humidity_percent']} %\n"
                               f"Pressure: {self.copied_env_data['pressure_hpa']} hpa\n"
                               f"Wind Speed: {self.copied_env_data['wind_speed_mps']} m/s\n"
                               f"Wind Direction: {self.copied_env_data['wind_dir_deg']} deg\n"
                               f"Sky: {self.copied_env_data['weather']}")
    
    def paste_environment_data(self):
        """Paste the copied environment data into the current test"""
        if not self.current_test_id:
            QMessageBox.warning(self, "No Test Selected", "Please select a test to paste environment data to.")
            return
        
        if not self.copied_env_data:
            QMessageBox.warning(self, "No Data to Paste", "Please copy environment data from a test first.")
            return
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Paste",
            f"Are you sure you want to paste environment data to test:\n{self.current_test_id}?\n\n"
            f"Temperature: {self.copied_env_data['temperature_c']} °C\n"
            f"Humidity: {self.copied_env_data['humidity_percent']} %\n"
            f"Pressure: {self.copied_env_data['pressure_hpa']} hpa\n"
            f"Wind Speed: {self.copied_env_data['wind_speed_mps']} m/s\n"
            f"Wind Direction: {self.copied_env_data['wind_dir_deg']} deg\n"
            f"Sky: {self.copied_env_data['weather']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Default is No to prevent accidental paste
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Paste the environment data
            self.temperature_c_edit.setText(self.copied_env_data['temperature_c'])
            self.humidity_percent_edit.setText(self.copied_env_data['humidity_percent'])
            self.pressure_hpa_edit.setText(self.copied_env_data['pressure_hpa'])
            self.wind_speed_mps_edit.setText(self.copied_env_data['wind_speed_mps'])
            self.wind_dir_deg_edit.setText(self.copied_env_data['wind_dir_deg'])
            
            # Set weather in dropdown
            weather = self.copied_env_data['weather']
            if weather:
                index = self.weather_combo.findText(weather)
                if index >= 0:
                    self.weather_combo.setCurrentIndex(index)
                elif weather:
                    # If not found in the list but has a value, add it
                    self.weather_combo.addItem(weather)
                    self.weather_combo.setCurrentText(weather)
            
            # Show a confirmation message
            QMessageBox.information(self, "Environment Data Pasted", 
                                   f"Environment data pasted to test: {self.current_test_id}\n\n"
                                   "Remember to click 'Save Changes' to save the updated data.")
        
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
        
        # Set barrel length in spinner
        barrel_length = platform_data.get('barrel_length_in')
        if barrel_length is not None:
            try:
                self.barrel_length_spin.setValue(float(barrel_length))
            except (ValueError, TypeError):
                pass
        
        # Set twist rate in text field
        self.twist_rate_edit.setText(str(platform_data.get('twist_rate', '')))

        # Ammunition - Case
        ammo_data = data.get('ammo', {}) # Access nested ammo data
        case_data = ammo_data.get('case', {})
        
        # Set case brand in dropdown
        case_brand = str(case_data.get('brand', ''))
        index = self.case_brand_combo.findText(case_brand)
        if index >= 0:
            self.case_brand_combo.setCurrentIndex(index)
        elif case_brand:
            # If not found in the list but has a value, add it
            self.case_brand_combo.addItem(case_brand)
            self.case_brand_combo.setCurrentText(case_brand)
        
        # Set case lot
        self.case_lot_edit.setText(str(case_data.get('lot', '')))
        
        # Set neck turned
        neck_turned = str(case_data.get('neck_turned', 'No'))
        index = self.neck_turned_combo.findText(neck_turned)
        if index >= 0:
            self.neck_turned_combo.setCurrentIndex(index)
        
        # Set brass sizing
        brass_sizing = str(case_data.get('brass_sizing', 'Full'))
        index = self.brass_sizing_combo.findText(brass_sizing)
        if index >= 0:
            self.brass_sizing_combo.setCurrentIndex(index)
        
        # Set bushing size
        bushing_size = case_data.get('bushing_size')
        if bushing_size is not None:
            try:
                self.bushing_size_spin.setValue(float(bushing_size))
            except (ValueError, TypeError):
                pass
        
        # Set shoulder bump
        shoulder_bump = case_data.get('shoulder_bump')
        if shoulder_bump is not None:
            try:
                self.shoulder_bump_spin.setValue(float(shoulder_bump))
            except (ValueError, TypeError):
                pass
        
        # Ammunition - Bullet
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
        
        # Set bullet lot
        self.bullet_lot_edit.setText(str(bullet_data.get('lot', '')))

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
        
        # Get distance for MOA calculations
        distance_m = data.get('distance_m')
        
        # Helper function to format MOA values with 2 decimal places
        def format_moa(moa_value):
            if moa_value == '':
                return ''
            try:
                return f"{float(moa_value):.2f}"
            except (ValueError, TypeError):
                return str(moa_value)
        
        # Group ES
        group_es_mm = group_data.get('group_es_mm', '')
        group_es_moa = group_data.get('group_es_moa', '')
        # If mm value is provided but MOA is not, calculate MOA
        if group_es_mm and not group_es_moa and distance_m:
            try:
                moa_value = self._mm_to_moa(float(group_es_mm), float(distance_m))
                group_es_moa = f"{moa_value:.2f}" if moa_value is not None else ''
            except (ValueError, TypeError):
                group_es_moa = ''
        else:
            group_es_moa = format_moa(group_es_moa)
        self.group_es_mm_edit.setText(str(group_es_mm))
        self.group_es_moa_edit.setText(group_es_moa)
        
        # Mean Radius
        mean_radius_mm = group_data.get('mean_radius_mm', '')
        mean_radius_moa = group_data.get('mean_radius_moa', '')
        # If mm value is provided but MOA is not, calculate MOA
        if mean_radius_mm and not mean_radius_moa and distance_m:
            try:
                moa_value = self._mm_to_moa(float(mean_radius_mm), float(distance_m))
                mean_radius_moa = f"{moa_value:.2f}" if moa_value is not None else ''
            except (ValueError, TypeError):
                mean_radius_moa = ''
        else:
            mean_radius_moa = format_moa(mean_radius_moa)
        self.mean_radius_mm_edit.setText(str(mean_radius_mm))
        self.mean_radius_moa_edit.setText(mean_radius_moa)
        
        # Group ES X and Y
        group_es_x_mm = group_data.get('group_es_x_mm', '')
        group_es_x_moa = group_data.get('group_es_x_moa', '')
        # If mm value is provided but MOA is not, calculate MOA
        if group_es_x_mm and not group_es_x_moa and distance_m:
            try:
                moa_value = self._mm_to_moa(float(group_es_x_mm), float(distance_m))
                group_es_x_moa = f"{moa_value:.2f}" if moa_value is not None else ''
            except (ValueError, TypeError):
                group_es_x_moa = ''
        else:
            group_es_x_moa = format_moa(group_es_x_moa)
        self.group_es_x_mm_edit.setText(str(group_es_x_mm))
        self.group_es_x_moa_edit.setText(group_es_x_moa)
        
        group_es_y_mm = group_data.get('group_es_y_mm', '')
        group_es_y_moa = group_data.get('group_es_y_moa', '')
        # If mm value is provided but MOA is not, calculate MOA
        if group_es_y_mm and not group_es_y_moa and distance_m:
            try:
                moa_value = self._mm_to_moa(float(group_es_y_mm), float(distance_m))
                group_es_y_moa = f"{moa_value:.2f}" if moa_value is not None else ''
            except (ValueError, TypeError):
                group_es_y_moa = ''
        else:
            group_es_y_moa = format_moa(group_es_y_moa)
        self.group_es_y_mm_edit.setText(str(group_es_y_mm))
        self.group_es_y_moa_edit.setText(group_es_y_moa)
        
        # POI X and Y
        poi_x_mm = group_data.get('poi_x_mm', '')
        poi_x_moa = group_data.get('poi_x_moa', '')
        # If mm value is provided but MOA is not, calculate MOA
        if poi_x_mm and not poi_x_moa and distance_m:
            try:
                moa_value = self._mm_to_moa(float(poi_x_mm), float(distance_m))
                poi_x_moa = f"{moa_value:.2f}" if moa_value is not None else ''
            except (ValueError, TypeError):
                poi_x_moa = ''
        else:
            poi_x_moa = format_moa(poi_x_moa)
        self.poi_x_mm_edit.setText(str(poi_x_mm))
        self.poi_x_moa_edit.setText(poi_x_moa)
        
        poi_y_mm = group_data.get('poi_y_mm', '')
        poi_y_moa = group_data.get('poi_y_moa', '')
        # If mm value is provided but MOA is not, calculate MOA
        if poi_y_mm and not poi_y_moa and distance_m:
            try:
                moa_value = self._mm_to_moa(float(poi_y_mm), float(distance_m))
                poi_y_moa = f"{moa_value:.2f}" if moa_value is not None else ''
            except (ValueError, TypeError):
                poi_y_moa = ''
        else:
            poi_y_moa = format_moa(poi_y_moa)
        self.poi_y_mm_edit.setText(str(poi_y_mm))
        self.poi_y_moa_edit.setText(poi_y_moa)

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
        platform_data['barrel_length_in'] = self.barrel_length_spin.value() if self.barrel_length_spin.value() > 0 else None
        platform_data['twist_rate'] = self.twist_rate_edit.text() or None
        if any(platform_data.values()): updated_data['platform'] = platform_data

        # --- Ammunition (Main Key) ---
        ammo_data = {}

        # Ammunition - Bullet
        bullet_data = {}
        bullet_data['brand'] = self.bullet_brand_combo.currentText() or None
        bullet_data['model'] = self.bullet_model_combo.currentText() or None
        bullet_data['weight_gr'] = self.bullet_weight_spin.value() if self.bullet_weight_spin.value() > 0 else None
        bullet_data['lot'] = self.bullet_lot_edit.text() or None
        if any(bullet_data.values()): ammo_data['bullet'] = bullet_data

        # Ammunition - Powder
        powder_data = {}
        powder_data['brand'] = self.powder_brand_combo.currentText() or None
        powder_data['model'] = self.powder_model_combo.currentText() or None
        powder_data['charge_gr'] = self.powder_charge_spin.value() if self.powder_charge_spin.value() > 0 else None
        powder_data['lot'] = self.powder_lot_edit.text() or None
        if any(powder_data.values()): ammo_data['powder'] = powder_data

        # Ammunition - Cartridge/Case/Primer
        oal_val = self.cartridge_oal_spin.value() if self.cartridge_oal_spin.value() > 0 else None
        bto_val = self.cartridge_bto_spin.value() if self.cartridge_bto_spin.value() > 0 else None
        if oal_val is not None: ammo_data['coal_in'] = oal_val # Use correct key
        if bto_val is not None: ammo_data['b2o_in'] = bto_val # Use correct key
        
        case_data = {}
        case_data['brand'] = self.case_brand_combo.currentText() or None
        case_data['lot'] = self.case_lot_edit.text() or None
        case_data['neck_turned'] = self.neck_turned_combo.currentText() or None
        case_data['brass_sizing'] = self.brass_sizing_combo.currentText() or None
        # For bushing size, we need to ensure it's saved even if it's 0
        bushing_size_value = self.bushing_size_spin.value()
        case_data['bushing_size'] = bushing_size_value
        case_data['shoulder_bump'] = self.shoulder_bump_spin.value() if self.shoulder_bump_spin.value() > 0 else None
        if any(case_data.values()): ammo_data['case'] = case_data
        
        primer_data = {}
        primer_data['brand'] = self.primer_brand_combo.currentText() or None
        primer_data['model'] = self.primer_model_combo.currentText() or None
        primer_data['lot'] = self.primer_lot_edit.text() or None
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
        
        # Get distance for MOA calculations
        distance_m = updated_data.get('distance_m')
        
        # Helper function to format MOA values with 2 decimal places
        def format_moa_value(moa_val):
            if moa_val is not None and moa_val != "INVALID_INPUT":
                try:
                    # Round to 2 decimal places
                    return round(float(moa_val), 2)
                except (ValueError, TypeError):
                    return moa_val
            return moa_val
        
        # Group ES
        es_mm_val = safe_convert(self.group_es_mm_edit.text(), float)
        es_moa_val = safe_convert(self.group_es_moa_edit.text(), float)
        # If mm value is provided but MOA is not, calculate MOA
        if es_mm_val is not None and es_moa_val is None and distance_m is not None:
            es_moa_val = self._mm_to_moa(es_mm_val, distance_m)
            if es_moa_val is not None:
                es_moa_val = round(es_moa_val, 2)
        else:
            es_moa_val = format_moa_value(es_moa_val)
        
        # Mean Radius
        mean_rad_val = safe_convert(self.mean_radius_mm_edit.text(), float)
        mean_rad_moa_val = safe_convert(self.mean_radius_moa_edit.text(), float)
        # If mm value is provided but MOA is not, calculate MOA
        if mean_rad_val is not None and mean_rad_moa_val is None and distance_m is not None:
            mean_rad_moa_val = self._mm_to_moa(mean_rad_val, distance_m)
            if mean_rad_moa_val is not None:
                mean_rad_moa_val = round(mean_rad_moa_val, 2)
        else:
            mean_rad_moa_val = format_moa_value(mean_rad_moa_val)
        
        # Group ES X and Y
        es_x_val = safe_convert(self.group_es_x_mm_edit.text(), float)
        es_x_moa_val = safe_convert(self.group_es_x_moa_edit.text(), float)
        # If mm value is provided but MOA is not, calculate MOA
        if es_x_val is not None and es_x_moa_val is None and distance_m is not None:
            es_x_moa_val = self._mm_to_moa(es_x_val, distance_m)
            if es_x_moa_val is not None:
                es_x_moa_val = round(es_x_moa_val, 2)
        else:
            es_x_moa_val = format_moa_value(es_x_moa_val)
        
        es_y_val = safe_convert(self.group_es_y_mm_edit.text(), float)
        es_y_moa_val = safe_convert(self.group_es_y_moa_edit.text(), float)
        # If mm value is provided but MOA is not, calculate MOA
        if es_y_val is not None and es_y_moa_val is None and distance_m is not None:
            es_y_moa_val = self._mm_to_moa(es_y_val, distance_m)
            if es_y_moa_val is not None:
                es_y_moa_val = round(es_y_moa_val, 2)
        else:
            es_y_moa_val = format_moa_value(es_y_moa_val)
        
        # POI X and Y
        poi_x_val = safe_convert(self.poi_x_mm_edit.text(), float)
        poi_x_moa_val = safe_convert(self.poi_x_moa_edit.text(), float)
        # If mm value is provided but MOA is not, calculate MOA
        if poi_x_val is not None and poi_x_moa_val is None and distance_m is not None:
            poi_x_moa_val = self._mm_to_moa(poi_x_val, distance_m)
            if poi_x_moa_val is not None:
                poi_x_moa_val = round(poi_x_moa_val, 2)
        else:
            poi_x_moa_val = format_moa_value(poi_x_moa_val)
        
        poi_y_val = safe_convert(self.poi_y_mm_edit.text(), float)
        poi_y_moa_val = safe_convert(self.poi_y_moa_edit.text(), float)
        # If mm value is provided but MOA is not, calculate MOA
        if poi_y_val is not None and poi_y_moa_val is None and distance_m is not None:
            poi_y_moa_val = self._mm_to_moa(poi_y_val, distance_m)
            if poi_y_moa_val is not None:
                poi_y_moa_val = round(poi_y_moa_val, 2)
        else:
            poi_y_moa_val = format_moa_value(poi_y_moa_val)
        
        # Check for invalid inputs
        if (shots_val == "INVALID_INPUT" or 
            es_mm_val == "INVALID_INPUT" or es_moa_val == "INVALID_INPUT" or 
            mean_rad_val == "INVALID_INPUT" or mean_rad_moa_val == "INVALID_INPUT" or 
            es_x_val == "INVALID_INPUT" or es_x_moa_val == "INVALID_INPUT" or 
            es_y_val == "INVALID_INPUT" or es_y_moa_val == "INVALID_INPUT" or 
            poi_x_val == "INVALID_INPUT" or poi_x_moa_val == "INVALID_INPUT" or 
            poi_y_val == "INVALID_INPUT" or poi_y_moa_val == "INVALID_INPUT"):
            error_occurred = True
        
        # Use correct keys from YAML when saving
        group_data['shots'] = shots_val
        
        # Group ES
        group_data['group_es_mm'] = es_mm_val 
        group_data['group_es_moa'] = es_moa_val 
        
        # Mean Radius
        group_data['mean_radius_mm'] = mean_rad_val
        group_data['mean_radius_moa'] = mean_rad_moa_val
        
        # Group ES X and Y
        group_data['group_es_x_mm'] = es_x_val
        group_data['group_es_x_moa'] = es_x_moa_val
        group_data['group_es_y_mm'] = es_y_val
        group_data['group_es_y_moa'] = es_y_moa_val
        
        # POI X and Y
        group_data['poi_x_mm'] = poi_x_val
        group_data['poi_x_moa'] = poi_x_moa_val
        group_data['poi_y_mm'] = poi_y_val
        group_data['poi_y_moa'] = poi_y_moa_val
        
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
            
            # Save current filter values
            current_filters = self._save_current_filters()
            
            # Reload the data to update the filtered table
            self.load_data()
            
            # Restore filter values and reapply filters
            self._restore_filters(current_filters)
            self.apply_filters()
            
            # Reselect the current test in the table
            if self.current_test_id:
                for row in range(self.filtered_data.shape[0]):
                    if self.filtered_data.iloc[row]['test_id'] == self.current_test_id:
                        self.test_table.selectRow(row)
                        break
            
            QMessageBox.information(self, "Save Successful", f"Changes saved successfully for {self.current_test_id}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save changes for {self.current_test_id}:\n{e}")

        # TODO: Consider if CSV needs updating (might be complex if structure changes)
