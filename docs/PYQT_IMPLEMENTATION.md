# Precision Rifle Load Development PyQt Implementation

This document provides details about the PyQt implementation in the Precision Rifle Load Development application. It covers the UI architecture, widget hierarchy, signal/slot connections, and best practices.

## PyQt Overview

The application uses PyQt6, a set of Python bindings for Qt, which is a cross-platform application framework. PyQt provides a rich set of widgets, layouts, and other UI components that are used to build the application's user interface.

## UI Architecture

The application follows a modular UI architecture with a main window that contains a tab widget. Each tab represents a different module of the application:

1. **View Test**: For viewing and editing existing tests
2. **Data Analysis**: For analyzing and visualizing test data
3. **Create Test**: For creating new tests
4. **Admin**: For managing component lists

### Main Window

The main window (`pyqt_app/main.py`) is a subclass of `QMainWindow` and serves as the container for all other UI components. It:

- Sets up the menu bar with File and Help menus
- Creates the central widget with a tab widget
- Manages communication between tabs using signals and slots
- Handles settings and database management

### Module Widgets

Each module is implemented as a separate widget class that extends `QWidget`. These widgets are added as tabs to the main window's tab widget:

- **ViewTestWidget** (`pyqt_app/modules/view_test.py`): Displays and allows editing of test data
- **DataAnalysisWidget** (`pyqt_app/modules/data_analysis.py`): Provides data analysis and visualization
- **CreateTestWidget** (`pyqt_app/modules/create_test.py`): Allows creation of new tests
- **AdminWidget** (`pyqt_app/modules/admin.py`): Manages component lists

### Settings Dialog

The settings dialog (`pyqt_app/modules/settings.py`) is a subclass of `QDialog` and provides a UI for configuring application settings, including database management.

## Widget Hierarchy

The application uses a hierarchical structure of widgets and layouts to create the UI:

```
QMainWindow (MainWindow)
└── QWidget (central_widget)
    └── QVBoxLayout
        └── QTabWidget (tabs)
            ├── QWidget (ViewTestWidget)
            │   └── QVBoxLayout
            │       ├── QHBoxLayout (selection_layout)
            │       │   ├── QLabel ("Select Test ID:")
            │       │   └── QComboBox (test_id_combo)
            │       └── QScrollArea
            │           └── QWidget (scroll_content)
            │               └── QHBoxLayout (two_column_layout)
            │                   ├── QVBoxLayout (left_column)
            │                   │   ├── QGroupBox ("Test Information")
            │                   │   │   └── QFormLayout
            │                   │   │       ├── QDateEdit (date_edit)
            │                   │   │       ├── QComboBox (distance_combo)
            │                   │   │       └── QTextEdit (notes_edit)
            │                   │   ├── QGroupBox ("Platform")
            │                   │   │   └── QFormLayout
            │                   │   │       ├── QComboBox (calibre_combo)
            │                   │   │       └── QComboBox (rifle_combo)
            │                   │   ├── QGroupBox ("Ammunition")
            │                   │   │   └── QFormLayout
            │                   │   │       ├── QComboBox (bullet_brand_combo)
            │                   │   │       ├── QComboBox (bullet_model_combo)
            │                   │   │       └── ...
            │                   │   └── QGroupBox ("Environment")
            │                   │       └── QFormLayout
            │                   │           ├── QLineEdit (temperature_c_edit)
            │                   │           ├── QLineEdit (humidity_percent_edit)
            │                   │           └── ...
            │                   └── QVBoxLayout (right_column)
            │                       ├── QGroupBox ("Target Image")
            │                       │   └── QVBoxLayout
            │                       │       ├── ZoomableImageLabel (image_label)
            │                       │       └── QLabel (instructions)
            │                       └── QWidget (results_container)
            │                           └── QVBoxLayout
            │                               ├── QGroupBox ("Results Target")
            │                               │   └── QFormLayout
            │                               │       ├── QLineEdit (shots_edit)
            │                               │       ├── QLineEdit (group_es_mm_edit)
            │                               │       └── ...
            │                               └── QGroupBox ("Results Velocity")
            │                                   └── QFormLayout
            │                                       ├── QLineEdit (avg_velocity_edit)
            │                                       ├── QLineEdit (sd_velocity_edit)
            │                                       └── ...
            ├── QWidget (DataAnalysisWidget)
            │   └── ...
            ├── QWidget (CreateTestWidget)
            │   └── ...
            └── QWidget (AdminWidget)
                └── ...
```

## Signal/Slot Connections

The application uses Qt's signal/slot mechanism for communication between components. This allows for loose coupling between components and makes the code more maintainable.

### Main Window Connections

The main window sets up connections between the different modules:

```python
# When component lists are updated in Admin tab, refresh Create Test and View Test tabs
self.admin_widget.componentListsUpdated.connect(self.create_test_widget.refresh)
self.admin_widget.componentListsUpdated.connect(self.view_test_widget.refresh_component_lists)

# When a new test is created in Create Test tab, refresh View Test and Data Analysis tabs
self.create_test_widget.testCreated.connect(self.view_test_widget.refresh)
self.create_test_widget.testCreated.connect(self.data_analysis_widget.refresh)

# When a test is updated or deleted in View Test tab, refresh Data Analysis tab
self.view_test_widget.testUpdated.connect(self.data_analysis_widget.refresh)
self.view_test_widget.testDeleted.connect(self.data_analysis_widget.refresh)
```

### Settings Dialog Connections

The settings dialog emits signals when settings are changed:

```python
# Connect the settingsChanged signal to refresh the test lists
dialog.settingsChanged.connect(self.refresh_after_settings_change)

# Connect the databaseSwitched signal to update the active database
dialog.databaseSwitched.connect(self.update_active_database)
```

### Widget Internal Connections

Each widget sets up internal connections between its UI components:

```python
# Connect the test selector to the load_test method
self.test_selector.currentIndexChanged.connect(self.load_test)

# Connect the save button to the save_test method
self.save_button.clicked.connect(self.save_test)
```

## Custom Widgets

The application includes several custom widgets to provide specialized functionality:

### ZoomableImageLabel

A custom widget for displaying and interacting with target images:

```python
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
        # ...
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        # ...
    
    def mousePressEvent(self, event):
        """Handle mouse press events for panning."""
        # ...
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events for panning."""
        # ...
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning."""
        # ...
    
    def resizeEvent(self, event):
        """Handle resize events."""
        # ...
```

### Database Item

A custom list widget item for displaying database pointers:

```python
class DatabaseItem(QListWidgetItem):
    """Custom list widget item for displaying database pointers.
    
    This class extends QListWidgetItem to store additional data about
    the database pointer, such as the label and path.
    """
    
    def __init__(self, label, path, is_active=False):
        """Initialize the database item."""
        super().__init__(label)
        self.label = label
        self.path = path
        self.is_active = is_active
        
        # Set font and color based on active status
        font = QFont()
        if is_active:
            font.setBold(True)
            self.setForeground(QColor(0, 0, 255))  # Blue for active database
        
        self.setFont(font)
        
        # Set tooltip to show the path
        self.setToolTip(f"Path: {path}")
```

## Layout Management

The application uses a combination of layout managers to create a flexible and responsive UI:

- **QVBoxLayout**: For vertical arrangement of widgets
- **QHBoxLayout**: For horizontal arrangement of widgets
- **QFormLayout**: For form-like layouts with labels and input fields
- **QGridLayout**: For grid-like arrangements of widgets
- **QSplitter**: For resizable split views

Example of a complex layout:

```python
# Create a splitter for the main content
self.splitter = QSplitter(Qt.Orientation.Horizontal)

# Left panel with form layout
self.left_panel = QScrollArea()
self.left_panel.setWidgetResizable(True)
left_widget = QWidget()
left_layout = QFormLayout(left_widget)

# Add form fields
left_layout.addRow("Date:", self.date_edit)
left_layout.addRow("Caliber:", self.caliber_combo)
# ...

self.left_panel.setWidget(left_widget)

# Right panel with target and velocity data
self.right_panel = QScrollArea()
self.right_panel.setWidgetResizable(True)
right_widget = QWidget()
right_layout = QVBoxLayout(right_widget)

# Target group
target_group = QGroupBox("Target")
target_layout = QVBoxLayout(target_group)
target_layout.addWidget(self.target_image)
# ...

# Velocity group
velocity_group = QGroupBox("Velocity")
velocity_layout = QVBoxLayout(velocity_group)
velocity_layout.addWidget(self.velocity_label)
# ...

right_layout.addWidget(target_group)
right_layout.addWidget(velocity_group)
self.right_panel.setWidget(right_widget)

# Add panels to splitter
self.splitter.addWidget(self.left_panel)
self.splitter.addWidget(self.right_panel)

# Add splitter to main layout
self.layout.addWidget(self.splitter)
```

## Styling and Theming

The application uses the Fusion style for a consistent appearance across platforms:

```python
app = QApplication(sys.argv)
app.setStyle("Fusion")
```

Custom styling is applied using stylesheets:

```python
# Set stylesheet for the validation label
self.validation_label.setStyleSheet("color: red;")

# Set stylesheet for the active database label
self.db_label.setStyleSheet("font-weight: bold; color: blue;")
```

## Best Practices

### Widget Creation

Widgets are created in the `__init__` method and configured in a separate `setup_ui` method:

```python
def __init__(self, parent=None):
    """Initialize the widget."""
    super().__init__(parent)
    self.setup_ui()

def setup_ui(self):
    """Set up the UI components."""
    # Create layout
    self.layout = QVBoxLayout(self)
    
    # Create widgets
    self.label = QLabel("Hello, World!")
    self.button = QPushButton("Click Me")
    
    # Add widgets to layout
    self.layout.addWidget(self.label)
    self.layout.addWidget(self.button)
    
    # Connect signals
    self.button.clicked.connect(self.on_button_clicked)
```

### Signal/Slot Connections

Signal/slot connections are made after the widgets are created:

```python
# Connect the button's clicked signal to the on_button_clicked slot
self.button.clicked.connect(self.on_button_clicked)
```

### Error Handling

Error handling is done using try/except blocks with user feedback:

```python
try:
    # Try to load the test
    test_data = self.load_test(test_id)
except FileNotFoundError:
    # Show an error message if the file is not found
    QMessageBox.critical(self, "Error", f"Test file not found: {test_id}")
    return
except ValueError as e:
    # Show an error message if the test data is invalid
    QMessageBox.critical(self, "Error", f"Invalid test data: {e}")
    return
```

## Conclusion

The PyQt implementation in the Precision Rifle Load Development application follows best practices for creating a maintainable and user-friendly UI. By using a modular architecture, proper signal/slot connections, and appropriate layout management, the application provides a responsive and intuitive user experience.
