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
