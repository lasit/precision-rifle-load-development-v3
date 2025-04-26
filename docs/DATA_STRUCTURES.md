# Precision Rifle Load Development Data Structures

This document describes the data schemas and relationships used in the Precision Rifle Load Development application.

## Overview

The application uses YAML files to store test data and component lists. This document outlines the structure of these files and the relationships between different data elements.

## Test Data Structure

Each test is stored in a separate YAML file within a directory named after the test ID. The test ID is generated based on the test parameters and follows this format:

```
YYYY-MM-DD__distance_caliber_rifle_case_bullet_powder_charge_coal_oal_primer
```

For example:
```
2025-04-20__100m_223_Tikka-T3X_Sako_Hornady_ELD-M_75gr_ADI_2208_24.00gr_2.392in_1.850in_RWS_4033
```

### Test Directory Structure

```
tests/
└── 2025-04-20__100m_223_Tikka-T3X_Sako_Hornady_ELD-M_75gr_ADI_2208_24.00gr_2.392in_1.850in_RWS_4033/
    ├── group.yaml       # Test data in YAML format
    ├── target1.jpg      # Target image
    ├── target2.jpg      # Additional target image (optional)
    └── notes.txt        # Additional notes (optional)
```

### Test YAML Structure

The `group.yaml` file contains all the test data and follows this structure:

```yaml
# Test Identification
id: "2025-04-20__100m_223_Tikka-T3X_Sako_Hornady_ELD-M_75gr_ADI_2208_24.00gr_2.392in_1.850in_RWS_4033"
date: "2025-04-20"
name: "Test Name" # Optional

# Platform Details
platform:
  distance: "100m"
  caliber: "223"
  rifle: "Tikka-T3X"
  
# Ammunition Components
components:
  case: "Sako"
  bullet: "Hornady ELD-M 75gr"
  powder: "ADI 2208"
  charge: "24.00gr"
  coal: "2.392in"
  oal: "1.850in"
  primer: "RWS 4033"
  
# Environmental Conditions
environment:
  temperature_c: 22.5 # Celsius
  humidity_percent: 45 # Percentage
  pressure_hpa: 1013.2 # hPa
  wind_speed_mps: 2.5 # m/s
  wind_dir_deg: 45 # Degrees (0-360)
  weather: "Sunny" # Optional
  
# Target Results
results_target:
  group_size: 0.75 # MOA
  mean_radius: 0.32 # MOA
  extreme_spread: 0.82 # inches
  vertical_dispersion: 0.65 # inches
  horizontal_dispersion: 0.45 # inches
  poa_shift_vertical: 0.5 # inches (positive is up)
  poa_shift_horizontal: -0.3 # inches (negative is left)
  target_image: "target1.jpg" # Filename of target image
  shots: 5 # Number of shots in the group
  group_es_x_mm: 33.05 # Extreme spread in X direction (mm)
  group_es_y_mm: 24.63 # Extreme spread in Y direction (mm)
  poi_x_mm: 2.6 # Point of impact X coordinate (mm)
  poi_y_mm: 17.47 # Point of impact Y coordinate (mm)
  
# Velocity Results
results_velocity:
  average: 2950 # fps
  standard_deviation: 12.5 # fps
  extreme_spread: 35 # fps
  shots:
    - 2945 # fps
    - 2960 # fps
    - 2955 # fps
    - 2940 # fps
    - 2950 # fps
    
# Notes
notes: "This load performed well with minimal vertical dispersion."
```

## Lists Structure

The lists are stored in a single YAML file (`Lists.yaml`) in the application's root directory. This file contains lists of available options for various dropdown menus in the application.

```yaml
# Rifles
rifles:
  - "Tikka-T3X"
  - "Remington 700"
  - "Bergara B14"
  - "Savage 110"
  
# Calibers
calibers:
  - "223"
  - "308"
  - "6.5 Creedmoor"
  - "300 Win Mag"
  
# Cases
cases:
  - "Sako"
  - "Lapua"
  - "Hornady"
  - "Winchester"
  
# Bullets
bullets:
  - "Hornady ELD-M 75gr"
  - "Sierra MatchKing 69gr"
  - "Berger Hybrid 73gr"
  - "Nosler RDF 70gr"
  
# Powders
powders:
  - "ADI 2208"
  - "Hodgdon Varget"
  - "IMR 4895"
  - "Vihtavuori N140"
  
# Primers
primers:
  - "RWS 4033"
  - "CCI BR4"
  - "Federal 205M"
  - "Winchester Small Rifle"
  
# Distances
distances:
  - "100m"
  - "200m"
  - "300m"
  - "500m"
```

## Wind Plot Profiles Structure

The wind plot profiles are stored in a YAML file in a platform-specific location:

- Windows: `%APPDATA%\PrecisionRifleLoadDevelopment\wind_plot_profiles.yaml`
- macOS: `~/Library/Application Support/PrecisionRifleLoadDevelopment/wind_plot_profiles.yaml`
- Linux: `~/.config/precision-rifle-load-development/wind_plot_profiles.yaml`

The wind plot profiles file has the following structure:

```yaml
profiles:
  - name: ".223 Rem 75gr @ 2700fps"
    description: "Wind drift profile for .223 Remington with 75gr bullets at 2700fps"
    distances:
      - distance: 300
        moa_at_7ms: 3.7
      - distance: 500
        moa_at_7ms: 7.8
      - distance: 700
        moa_at_7ms: 12.4
      - distance: 1000
        moa_at_7ms: 20.0
  - name: "6.5 Creedmoor 140gr @ 2800fps"
    description: "Wind drift profile for 6.5 Creedmoor with 140gr bullets at 2800fps"
    distances:
      - distance: 300
        moa_at_7ms: 2.8
      - distance: 500
        moa_at_7ms: 5.9
      - distance: 700
        moa_at_7ms: 9.2
      - distance: 1000
        moa_at_7ms: 15.3
```

Each profile contains:
- `name`: A descriptive name for the profile, typically including caliber, bullet weight, and velocity
- `description`: A longer description of the profile
- `distances`: A list of distance/MOA pairs, each containing:
  - `distance`: The distance in meters
  - `moa_at_7ms`: The MOA drift at 7 m/s wind speed at 90 degrees

The profiles can be exported to PDF format, with plots arranged in a 2×4 grid per page (2 columns, 4 rows). The PDF export functionality uses matplotlib's PdfPages to create multi-page PDFs with consistent formatting.

## Settings Structure

The application settings are stored in a YAML file in a platform-specific location:

- Windows: `%APPDATA%\PrecisionRifleLoadDevelopment\config.yaml`
- macOS: `~/Library/Application Support/PrecisionRifleLoadDevelopment/config.yaml`
- Linux: `~/.config/precision-rifle-load-development/config.yaml`

The settings file has the following structure:

```yaml
# Active database
active_database: "Default"

# Database pointers
databases:
  - label: "Default"
    path: "/path/to/tests"
  - label: "Competition Loads"
    path: "/path/to/google/drive/competition_tests"
  - label: "Development Loads"
    path: "/path/to/google/drive/development_tests"
```

## Data Relationships

The application maintains several relationships between different data elements:

1. **Test ID and Test Data**: Each test ID uniquely identifies a test and its associated data.
2. **Component Lists and Test Data**: The component lists provide options for creating and editing tests.
3. **Database Pointers and Test Directories**: Each database pointer points to a directory containing test data.
4. **Active Database and Test Loading**: The active database determines which tests are loaded and displayed.

## Data Validation

The application performs validation on various data elements:

1. **Test ID**: Must follow the specified format and be unique.
2. **Component Values**: Should match values from the component lists, but custom values are allowed.
3. **Numeric Values**: Must be within reasonable ranges (e.g., powder charge, velocity).
4. **Directory Paths**: Must exist and be writable.
5. **Database Labels**: Must be unique.

## Data Migration

The application includes support for migrating data from older formats:

1. **Settings Migration**: Automatically migrates from single tests directory to multiple database pointers.
2. **Test Data Migration**: Can update test data files to include new fields as the application evolves.

## Conclusion

The data structures used in the Precision Rifle Load Development application are designed to be flexible, extensible, and human-readable. By using YAML files for storage, the data can be easily inspected and modified if necessary, while still providing a structured format for the application to work with.
