# Precision Rifle Load Development App (PyQt)

## Project Overview
This PyQt application manages precision rifle load development test data. It allows users to browse test folders, load and edit YAML files, display them in a structured form, and save changes back. The application includes dropdown lists for common components and an admin interface for managing these lists.

## Application Structure
The application is built as a single PyQt window with a tabbed interface, each tab serving a specific purpose:

1. **View Test**
   - For viewing and updating existing test data
   - Includes detailed form for editing test parameters
   - Displays target images
   - Saves changes back to YAML files

2. **Data Analysis**
   - For analyzing and visualizing test data
   - Interactive charts and filtering capabilities
   - Comprehensive filtering system for all test parameters
   - Multiple visualization options for accuracy and velocity metrics

3. **Create Test**
   - Dedicated tab for creating new tests
   - Streamlined interface for entering test parameters
   - Generates test IDs and creates test folders

4. **Admin**
   - For managing component lists and options
   - Add, edit, and delete component options

All tabs are integrated into a single application window, with signals and slots connecting the different components to ensure data consistency.

## Project Structure
```
Reloading/
├── pyqt_app/                ← PyQt application directory
│   ├── __init__.py          ← Package initialization
│   ├── main.py              ← Main application window and tab management
│   ├── run.py               ← Entry point script with dependency checking
│   ├── requirements.txt     ← PyQt-specific dependencies
│   ├── modules/             ← Application modules
│   │   ├── __init__.py      ← Package initialization
│   │   ├── view_test.py     ← View and edit test data
│   │   ├── data_analysis.py ← Data analysis and visualization
│   │   ├── create_test.py   ← Create new tests
│   │   └── admin.py         ← Component list management
│   └── utils/               ← Utility functions
│       ├── __init__.py      ← Package initialization
│       └── data_loader.py   ← Data loading and processing functions
├── Component_List.yaml      ← Dropdown list data
├── requirements.txt         ← Project dependencies
└── tests/                   ← Test data folders
    └── [test-folders]/      ← Individual test folders
        ├── group.yaml       ← Test data in YAML format
        ├── chrono.csv       ← Chronograph data
        └── [target images]  ← Target images in various formats
```

## Features Implemented

### 1. Test Data Management
- Browse existing tests via dropdown
- Search and filter tests by test ID
- Create new tests with auto-generated IDs
- Load and save YAML data with correct structure
- Parse test ID components automatically
- Form validation with required fields
- Immediate data saving after test ID generation

### 2. User Interface
- Tabbed interface with intuitive organization
- Form validation and error handling
- Responsive layout with proper sizing
- Dropdown lists for common components
- Custom value option for all dropdown lists
- Image display for target photos

### 3. Data Processing
- Automatic MOA calculation
- Test ID generation from components
- File existence checking
- Component list management

### 4. Data Analysis and Visualization
- Comprehensive filtering system for all test parameters
- Interactive data tables for comparing test results
- Multiple visualization options:
  - **Results Target Section**:
    - Group ES (mm)
    - Group ES (MOA)
    - Mean Radius (mm)
    - Group ES Width-X (mm)
    - Group ES Height-Y (mm)
    - POA Horizontal-X (mm)
    - POA Vertical-Y (mm)
    - Number of shots
  - **Results Velocity Section**:
    - Average Velocity (f/s)
    - SD Velocity (f/s)
    - ES Velocity (f/s)
  - Separate charts for accuracy metrics
  - Separate charts for velocity metrics
  - Combined multi-axis chart showing all key metrics together

### 5. Admin Interface
- Dedicated admin tab for managing component lists
- Add, edit, and delete items in component lists
- Organized by component type

## Technical Details

### Data Structure
The app uses a consistent data structure for all test data, including:
- Test metadata (date, distance)
- Platform configuration (rifle, calibre)
- Ammunition configuration (bullet, powder, primer, case)
- Environmental conditions:
  - Temperature (C)
  - Humidity (%)
  - Pressure (hpa)
  - Wind Speed (m/s)
  - Wind Direction (deg)
  - Sky conditions
- Results Target:
  - Number of shots
  - Group ES (mm)
  - Group ES (MOA)
  - Mean Radius (mm)
  - Group ES Width-X (mm)
  - Group ES Height-Y (mm)
  - POA Horizontal-X (mm)
  - POA Vertical-Y (mm)
- Results Velocity:
  - Average Velocity (f/s)
  - SD Velocity (f/s)
  - ES Velocity (f/s)
- File paths
- Notes

### Component Lists
The app maintains lists of common components in Component_List.yaml:
- Calibre options
- Rifle options
- Case brand options
- Powder brand and model options
- Bullet brand and model options
- Primer brand and model options

### File Naming Convention
Test folders follow this format:
`[Date]__[Distance]_[Calibre]_[Rifle]_[CaseBrand]_[BulletBrand]_[BulletModel]_[BulletWeight]_[PowderBrand]_[Powder]_[Charge]_[COAL]_[B2O]_[PrimerBrand]_[Primer]`

### Dependencies
- PyQt6: GUI framework
- matplotlib: Data visualization
- pandas: Data manipulation
- numpy: Numerical operations
- pyyaml: YAML file handling
- plotly (optional): Enhanced visualizations
- pyqtgraph (optional): Fast plotting
- pillow: Image handling
- pyinstaller: Application packaging

### Application Startup
The application can be started using:
- `python3 pyqt_app/run.py`: Runs the application with dependency checking
- Direct execution of the run.py script if it's made executable

## Recent Updates
- Split the "Results" section into "Results Target" and "Results Velocity" sections in both Data Analysis and View Test modules
- Added new filters in the Data Analysis module:
  - **Results Target**:
    - Number of shots
    - Group ES (mm) - renamed from Group size (mm)
    - Group ES (MOA)
    - Mean Radius (mm)
    - Group ES Width-X (mm)
    - Group ES Height-Y (mm)
    - POA Horizontal-X (mm)
    - POA Vertical-Y (mm)
  - **Results Velocity**:
    - Avg Velocity (f/s) - renamed from Velocity (fps)
    - SD Velocity (f/s)
    - ES Velocity (f/s)
- Added Environment data display in the View Test module:
  - Temperature (C)
  - Humidity (%)
  - Pressure (hpa)
  - Wind Speed (m/s)
  - Wind Direction (deg)
  - Sky conditions
- Updated the View Test module to display the same split sections for Results Target and Results Velocity
