# Precision Rifle Load Development Changelog

This document records all notable changes to the Precision Rifle Load Development application.

## [Unreleased]

### Added
- Multiple database support allowing users to switch between different test databases
- Settings dialog for managing database pointers
- Google Drive integration for storing test data
- Status bar showing the active database
- Window title showing the active database
- Automatic refresh of test lists when switching databases
- Migration support for existing settings
- Kill scripts for properly terminating the application on all platforms
- Improved application startup with automatic cleanup of previous instances
- Two-column layout in the View Test tab for better organization
- Zoomable and pannable target images
- Calendar widget for date filtering in the Data Analysis tab
- Additional columns in the Data Analysis tab (Group ES Width-X, Group ES Height-Y, POA Horizontal-X, POA Vertical-Y, Number of shots)
- MOA equivalents for all measurements in the Results Target section (Mean Radius, Group ES Width-X, Group ES Height-Y, POA Horizontal-X, POA Vertical-Y)
- Added MOA fields to the Data Analysis tab filters and visualization
- Updated Accuracy and Combined plots to use Group ES Vertical (MOA) instead of Mean Radius (mm)
- Changed default values in Create Test tab (Barrel Length: 20, Twist Rate: "1:8", empty fields for Bushing size, Powder Charge, Cartridge OAL, and Cartridge B2O)
- Modified Create Test tab to preserve field values between test creations for faster creation of multiple similar tests
- Added automatic handling of duplicate test IDs by appending a suffix (e.g., " - 1", " - 2") to create unique folder names
- Added new "Seating Depth" tab in Data Analysis that plots Group Size (MOA) against Bullet to Ogive (mm) distance
- Added a dedicated "Database Settings" button to the main window for easier access to database configuration on all platforms
- Test selection feature in Data Analysis module allowing users to include/exclude specific tests from analysis
- Improved filter layout with reorganized sections for better usability
- Scrollable visualization area for larger graph displays
- Dynamic custom plot feature allowing users to select any parameter for X and Y axes
- Support for up to three Y-axis parameters with distinct colors in custom plots
- Trend line generation with equations for each parameter in custom plots
- Environment data display in the test table (temperature, humidity, pressure, wind)
- Support for COAL, B2O, and bullet weight parameters in custom plots and filters
- Comprehensive filtering system in the View Test tab, similar to the Data Analysis tab
- Table view in the View Test tab for displaying filtered tests
- Filter persistence when saving changes in the View Test tab
- Environment data copy/paste feature allowing users to copy environment data from one test and paste it into another
- Renamed Component_List.yaml to Lists.yaml for better organization
- Added Sky (weather) conditions list to Lists.yaml
- Wind Plots tab for creating precision wind drift reference charts
- Profile management system for storing multiple wind plot configurations
- Support for different calibers and bullet configurations in wind plots
- Persistent storage of wind plot profiles in YAML format
- Visual representation of wind drift based on wind speed and direction
- Customizable distance/MOA pairs for each wind plot profile
- Two-column layout in Wind Plots tab for better organization
- PDF export functionality for wind plots with 2×4 grid layout per page
- Improved Wind Plots with correct clock time labels (03:00, 09:00, etc.)
- Enhanced axis labels and removed redundant Y-axis label in Wind Plots
- Increased font sizes for better readability in Wind Plots
- Added "Powder Model" filter to both View Test and Data Analysis tabs, positioned below "Powder Brand" filter
- Fixed data loading issue where powder model changes weren't reflected in the filtered tests table
- **Intelligent Folder Renaming System**: Comprehensive folder renaming functionality that automatically detects changes to folder-name-determining fields and offers to rename test folders accordingly
- **Smart Change Detection**: Monitors changes to all key test parameters (Date, Distance, Calibre, Rifle, Case Brand, Bullet Brand/Model/Weight, Powder Brand/Model/Charge, Cartridge OAL/BTO, Primer Brand/Model)
- **User-Controlled Renaming**: Always asks for user confirmation before renaming folders with detailed change summary and three options (Yes/No/Cancel)
- **Conflict Resolution**: Automatically handles naming conflicts by appending version suffixes (_v2, _v3, etc.) when target folders already exist
- **Data Integrity Protection**: Ensures all test files (YAML, images, notes) stay together during folder rename operations
- **Real-time Feedback**: Provides clear success/failure messages and updates the UI immediately after folder operations
- **Component List Consistency**: Fixed hardcoded values throughout the application to use centralized Lists.yaml configuration
- **Brass Sizing Synchronization**: Resolved mismatch between admin tab and create test form brass sizing options
- **Neck Turned Component**: Added neck_turned component to Lists.yaml and updated all forms to use it consistently
- **Distance Filter Integration**: Updated distance filters in all modules to use Lists.yaml instead of hardcoded values
- **Weather Conditions Consistency**: Ensured all weather/sky condition dropdowns use the centralized Lists.yaml configuration
- **Dynamic Component Loading**: All dropdown fields now dynamically load from Lists.yaml with proper fallback mechanisms
- **Admin Interface Enhancement**: Added neck_turned component management to the admin interface
- **Mandrel Attributes**: Added mandrel and mandrel_size fields to case data
  - New "Mandrel" dropdown (Yes/No) with default "Yes" in Create Test
  - New "Mandrel Size" numeric input with 4 decimal precision (0.0000-0.9999)
  - Added mandrel columns to filtered tests table (positioned after Shoulder Bump)
  - Integrated mandrel management in Admin interface
  - Updated data loader and YAML structure to support mandrel fields
- **List Reordering in Admin**: Added "Move Up" and "Move Down" buttons
  - Users can now reorder items in all component lists (Distance, Calibre, Rifle, etc.)
  - Smart button states (disabled when at boundaries or no selection)
  - Selection follows moved items for better UX
  - Auto-save functionality preserves order in Lists.yaml
  - Order is maintained across all dropdown menus in the application
- **Smart Date Filter Management**: Fixed issue where newly created tests would disappear from the View Test table after editing and saving
  - Implemented intelligent date range expansion that automatically includes saved test dates in the filter range
  - Enhanced data loading logic with robust fallback handling for newly created tests
  - Added comprehensive debugging system to track data loading and filtering processes
  - Tests now remain visible in the table after editing without requiring application restart

### Changed
- Improved settings management with platform-specific storage locations
- Enhanced data loader to support multiple database directories
- Updated documentation with Google Drive setup instructions
- Refactored code for better maintainability
- Fixed menu bar visibility on macOS
- Improved platform-specific startup and shutdown scripts
- Increased main window size for better usability
- Enhanced graph size and visualization for better data analysis
- Reorganized filter layout in Data Analysis module for improved workflow

### Fixed
- Issue with test list not refreshing after settings changes
- Path handling on different operating systems
- Improved error handling in Data Analysis module filters
- Fixed NoneType errors in filter application
- Fixed selection state preservation when applying filters
- Improved checkbox behavior in the test table
- Fixed graph rendering issues to prevent duplicate lines
- Fixed error in ViewTestWidget when trying to create a new test (AttributeError: 'ViewTestWidget' object has no attribute 'test_id_combo')

## [1.2.0] - 2025-03-15

### Added
- Two-column layout in the View Test tab for better organization
- Zoomable and pannable target images
- Comprehensive environment data display
- Separate Results Target and Results Velocity sections

### Changed
- Improved UI responsiveness
- Enhanced data visualization in the Data Analysis tab
- Updated component list management in the Admin tab

### Fixed
- Issue with large target images not displaying correctly
- Bug in velocity data calculation
- Form validation in the Create Test tab

## [1.1.0] - 2025-02-01

### Added
- Data visualization with interactive charts
- Search and filter functionality for existing tests
- Component list management in the Admin tab
- Form validation to ensure complete data entry

### Changed
- Improved test data storage format
- Enhanced user interface with better layouts
- Updated documentation

### Fixed
- Issue with test IDs containing special characters
- Bug in date handling
- Performance issues with large datasets

## [1.0.0] - 2025-01-01

### Added
- Initial release of the Precision Rifle Load Development application
- Create and manage test data for different rifle loads
- Track platform details, ammunition components, and results
- Generate unique test IDs based on load components
- Basic data visualization
- YAML-based data storage

## Version Numbering

The project follows [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for added functionality in a backward-compatible manner
- PATCH version for backward-compatible bug fixes

## Release Process

1. Update the version number in the code
2. Update this changelog with the new version
3. Create a release branch
4. Create a pull request to merge the release branch into main
5. After the pull request is approved and merged, create a tag
6. Create a release on GitHub with release notes

## Future Plans

- Mobile companion app
- Cloud synchronization beyond Google Drive
- Advanced statistical analysis
- PDF report generation
- Barcode/QR code scanning for quick test lookup
- Integration with chronographs and other measurement devices
