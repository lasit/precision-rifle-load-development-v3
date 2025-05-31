# Precision Rifle Load Development Components

This document provides detailed documentation for the main components of the Precision Rifle Load Development application.

## Main Window

The main window (`pyqt_app/main.py`) is the central component of the application. It:

- Creates and manages the tab-based interface
- Sets up the menu bar with File and Help menus
- Provides a dedicated "Database Settings" button for cross-platform access to database configuration
- Coordinates communication between modules
- Handles settings and database management
- Displays the active database in both the window title and status bar

### Key Methods

- `__init__()`: Initializes the main window and sets up the UI
- `setup_ui()`: Sets up the UI components and tab widget
- `setup_menu()`: Sets up the menu bar with File and Help menus
- `show_settings_dialog()`: Shows the settings dialog
- `refresh_after_settings_change()`: Refreshes the application after settings changes
- `update_active_database()`: Updates the active database indicator

## View Test Module

The View Test module (`pyqt_app/modules/view_test.py`) allows users to view and edit existing tests. It:

- Displays a comprehensive filtering system similar to the Data Analysis tab
- Shows filtered tests in a sortable table view
- Allows selection of tests from the table to view and edit details
- Shows test details in a two-column layout
- Allows editing of test parameters
- Provides interactive target image viewing with zoom and pan capabilities
- Saves changes back to the test file
- Preserves filter settings when saving changes
- Uses component lists from Lists.yaml for dropdown options
- Supports copying and pasting of environment data between tests
- Includes "Powder Model" filter in the ammunition filtering section, positioned below "Powder Brand"
- Preserves powder model filter state when saving changes to ensure table updates correctly

### Key Classes

- `ViewTestWidget`: Main widget for viewing and editing tests
- `ZoomableImageLabel`: Custom QLabel that supports zooming and panning of target images
- `TestDataModel`: Reused from Data Analysis module for displaying test data in a table

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `load_data()`: Loads all tests from the active database
- `apply_filters()`: Filters tests based on user criteria with robust error handling
- `reset_filters()`: Resets all filters to their default values
- `_save_current_filters()`: Saves current filter values to a dictionary
- `_restore_filters()`: Restores filter values from a dictionary
- `on_table_selection_changed()`: Handles selection changes in the table view
- `load_selected_test()`: Loads a test from a file
- `save_changes()`: Saves changes to a test file with intelligent folder renaming
- `refresh()`: Refreshes the list of available tests
- `populate_test_ids()`: Refreshes the test data and updates the table model
- `refresh_component_lists()`: Refreshes the component dropdown lists
- `copy_environment_data()`: Copies environment data from the current test
- `paste_environment_data()`: Pastes copied environment data into the current test
- `_create_image_group()`: Creates the target image group with zoom and pan capabilities
- `_create_results_target_group()`: Creates the Results Target group
- `_create_results_velocity_group()`: Creates the Results Velocity group

### Folder Renaming System

The View Test module includes a comprehensive folder renaming system that automatically maintains consistency between test data and folder names:

#### Key Folder Renaming Methods

- `extract_folder_name_data()`: Extracts only the fields that affect folder naming from test data
- `generate_folder_name_from_data()`: Generates folder name using the same logic as create_test.py
- `detect_folder_name_changes()`: Compares old and new data to detect changes in folder-name-determining fields
- `show_folder_rename_dialog()`: Shows detailed confirmation dialog for folder renaming with change summary
- `get_unique_folder_name()`: Generates unique folder names by appending version suffixes when conflicts exist
- `rename_test_folder()`: Safely renames test folders with comprehensive error handling and verification

#### Monitored Fields for Folder Renaming

The system monitors changes to all fields that affect the folder name structure:
- **Test Information**: Date, Distance
- **Platform**: Calibre, Rifle
- **Ammunition Components**: Case Brand, Bullet Brand/Model/Weight, Powder Brand/Model/Charge, Cartridge OAL/BTO, Primer Brand/Model

#### Folder Renaming Workflow

1. **Change Detection**: When saving changes, the system compares old vs new data for folder-affecting fields
2. **User Confirmation**: If changes are detected, a detailed dialog shows what changed and asks for confirmation
3. **Safe Renaming**: If approved, the system safely renames the folder with conflict resolution
4. **Data Integrity**: All test files (YAML, images, notes) are moved together to maintain data integrity
5. **UI Updates**: The interface is immediately updated to reflect the new folder name

## Data Analysis Module

The Data Analysis module (`pyqt_app/modules/data_analysis.py`) provides tools for analyzing and visualizing test data. It:

- Displays test data in a table with comprehensive columns including environment data and MOA measurements
- Provides filtering options for test data with calendar widgets for date selection
- Generates charts and visualizations for accuracy, velocity, and seating depth metrics
- Allows filtering by various parameters including group size, velocity, shot count, and MOA values
- Features updated Accuracy and Combined plots that use Group ES Vertical (MOA) instead of Mean Radius (mm)
- Includes a dedicated Seating Depth tab that plots Group Size (MOA) against Bullet to Ogive (mm) distance
- Enables selective inclusion/exclusion of specific tests from analysis via checkboxes
- Provides bulk selection controls (Select All, Deselect All, Toggle Selection)
- Preserves selection state when applying filters
- Displays only selected tests in visualizations
- Features a reorganized filter layout with logical grouping of related filters
- Includes a scrollable visualization area for larger graph displays
- Handles missing data gracefully with comprehensive error handling
- Validates column existence before filtering
- Handles NaN values in filter operations
- Provides detailed error messages for troubleshooting
- Features a dynamic custom plot tab that allows users to:
  - Select any parameter for the X-axis (powder charge, COAL, B2O, bullet weight, etc.)
  - Select up to three different parameters for the Y-axes with distinct colors
  - Generate trend lines with equations for each parameter
  - Create custom visualizations to explore relationships between any data points
- Includes "Powder Model" filter in the ammunition filtering section, positioned below "Powder Brand"
- Enhanced data loader to properly extract powder model information from YAML files for accurate table display

### Key Classes

- `TestDataModel`: Custom table model for displaying test data with selection capabilities
  - Adds a checkbox column for selecting/unselecting tests
  - Emits signals when selection state changes
  - Preserves selection state during filtering operations
- `MatplotlibCanvas`: Custom canvas for embedding Matplotlib plots in PyQt with enhanced size

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components with filter groups and visualization tabs
- `load_data()`: Loads all tests from the active database
- `apply_filters()`: Filters tests based on user criteria with robust error handling
- `update_plots()`: Updates the accuracy, velocity, and combined plots based on selected tests
- `refresh()`: Refreshes the test data
- `select_all_tests()`: Selects all tests in the filtered data
- `deselect_all_tests()`: Deselects all tests in the filtered data
- `toggle_test_selection()`: Toggles the selection state of all tests
- `update_selected_count()`: Updates the selected count label
- `clear_plots()`: Clears all plots when not enough data is available

## Create Test Module

The Create Test module (`pyqt_app/modules/create_test.py`) allows users to create new tests. It:

- Provides a form for entering test parameters with user-friendly default values (Barrel Length: 20, Twist Rate: "1:8")
- Displays empty fields for Bushing size, Powder Charge, Cartridge OAL, and Cartridge B2O
- Preserves field values between test creations for faster creation of multiple similar tests
- Validates input data
- Generates a unique test ID
- Automatically handles duplicate test IDs by appending a suffix (e.g., " - 1", " - 2")
- Creates a new test file
- Emits a signal when a test is created

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components
- `validate_form()`: Validates the form input
- `generate_test_id()`: Generates a unique test ID
- `create_test()`: Creates a new test file
- `refresh()`: Refreshes the component dropdown lists

## Wind Plots Module

The Wind Plots module (`pyqt_app/modules/wind_plot.py`) provides tools for creating precision wind drift reference charts. It:

- Creates visual representations of wind drift based on wind speed and direction
- Supports multiple profiles for different calibers and bullet configurations
- Allows users to create, edit, and delete profiles
- Saves profiles to a YAML file for persistence between sessions
- Generates plots for multiple distances within a profile
- Visualizes wind drift using colored bars, concentric circles, and angle lines
- Provides a comprehensive UI for managing profiles and distance/MOA pairs
- Displays wind drift in Minutes of Angle (MOA) based on wind speed and direction
- Supports customization of distance/MOA pairs for each profile
- Handles profile data persistence in a platform-specific location
- Features a two-column layout with profile management and distance parameters on the left, and plots on the right
- Provides PDF export functionality that generates PDFs with plots arranged in either 2×4 grid (8 per page) or 1×2 grid (2 per page)
- Displays intuitive clock time labels (03:00, 09:00, etc.) for wind direction reference
- Features enhanced axis labels with increased font sizes for better readability
- Provides a clean interface with optimized label placement and no redundant information

### Key Classes

- `WindPlotWidget`: Main widget for creating and displaying wind plots
- `ProfileDialog`: Dialog for creating and editing wind plot profiles
- `MatplotlibCanvas`: Custom canvas for embedding Matplotlib plots in PyQt

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components with profile management and plot tabs
- `get_profiles_file_path()`: Gets the platform-specific path for the profiles file
- `load_profiles()`: Loads profiles from the YAML file
- `save_profiles()`: Saves profiles to the YAML file
- `populate_profile_dropdown()`: Populates the profile dropdown with available profiles
- `on_profile_selected()`: Handles profile selection changes
- `load_current_profile()`: Loads the currently selected profile data
- `create_new_profile()`: Creates a new profile
- `edit_current_profile()`: Edits the current profile
- `delete_current_profile()`: Deletes the current profile
- `add_input_row()`: Adds a new distance/MOA pair to the input table
- `remove_input_row()`: Removes a selected distance/MOA pair from the input table
- `collect_input_data()`: Collects input data from the table and updates the current profile
- `generate_plots()`: Generates wind drift plots for each distance
- `draw_wind_plot()`: Draws the wind drift plot on the given canvas

## Admin Module

The Admin module (`pyqt_app/modules/admin.py`) allows users to manage component lists. It:

- Displays the current component lists from Lists.yaml
- Allows adding, editing, and deleting components for all component types
- Manages all component types including: distance, calibre, rifle, case_brand, powder_brand, powder_model, bullet_brand, bullet_model, primer_brand, primer_model, brass_sizing, neck_turned, and sky conditions
- Saves changes to the Lists.yaml file
- Emits a signal when component lists are updated to refresh all dependent modules
- Provides centralized management for all dropdown options used throughout the application

### Key Methods

- `__init__()`: Initializes the widget and sets up the UI
- `setup_ui()`: Sets up the UI components
- `load_component_lists()`: Loads the component lists from the file
- `save_component_lists()`: Saves changes to the component list file
- `add_component()`: Adds a new component
- `edit_component()`: Edits an existing component
- `delete_component()`: Deletes a component

## Settings Dialog

The Settings dialog (`pyqt_app/modules/settings.py`) allows users to configure application settings. It:

- Displays the current database pointers
- Allows adding, editing, and deleting database pointers
- Provides a way to set the active database
- Validates directory paths
- Saves settings to the configuration file

### Key Classes

- `DatabaseItem`: Custom list widget item for displaying database pointers
- `SettingsDialog`: Dialog for configuring application settings

### Key Methods

- `__init__()`: Initializes the dialog and sets up the UI
- `populate_database_list()`: Populates the database list with current databases
- `on_database_selected()`: Handles database selection
- `validate_directory()`: Validates a directory path
- `validate_label()`: Validates a database label
- `add_database()`: Adds a new database pointer
- `update_database()`: Updates an existing database pointer
- `delete_database()`: Deletes a database pointer
- `set_active_database()`: Sets the active database

## Settings Manager

The Settings Manager (`pyqt_app/utils/settings_manager.py`) handles application settings. It:

- Uses the singleton pattern to ensure consistent settings
- Stores settings in a platform-specific location
- Provides methods for accessing and modifying settings
- Supports multiple database pointers
- Handles migration from older settings formats

### Key Methods

- `get_instance()`: Gets the singleton instance of the SettingsManager
- `_get_config_file_path()`: Gets the platform-specific path for the configuration file
- `_load_settings()`: Loads settings from the configuration file
- `save_settings()`: Saves settings to the configuration file
- `get_tests_directory()`: Gets the tests directory path for the active database
- `get_active_database()`: Gets the label of the active database
- `set_active_database()`: Sets the active database by label
- `get_databases()`: Gets the list of database pointers
- `add_database()`: Adds a new database pointer
- `update_database()`: Updates an existing database pointer
- `delete_database()`: Deletes a database pointer

## Data Loader

The Data Loader (`pyqt_app/utils/data_loader.py`) handles loading and processing test data. It:

- Loads test data from YAML files
- Validates test data
- Provides error handling for missing or invalid files
- Supports loading from different database directories
- Properly extracts powder model information from YAML files to ensure accurate table display

### Key Methods

- `load_test()`: Loads a test from a file
- `load_all_tests()`: Loads all tests from the active database
- `save_test()`: Saves a test to a file
- `validate_test()`: Validates test data
- `get_test_list()`: Gets a list of available tests

## Conclusion

This document provides an overview of the main components of the Precision Rifle Load Development application. Each component is designed to handle a specific aspect of the application's functionality, with clear interfaces for communication between components.
