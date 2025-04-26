# Precision Rifle Load Development

A PyQt application for tracking and analyzing precision rifle load development data.

## Features

- Create and manage test data for different rifle loads
- Track important parameters like:
  - Platform details (caliber, rifle)
  - Ammunition components (case, bullet, powder, primer)
  - Environmental conditions (temperature, humidity, pressure, wind)
  - Target results (group size, mean radius, POA)
  - Velocity data (average, SD, ES)
- Generate unique test IDs based on load components
- Form validation to ensure complete data entry
- Search and filter existing tests
- Data visualization with interactive charts
- Component list management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/lasit/Reloading.git
   cd Reloading
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python run.py
   ```
   
   Or directly:
   ```
   ./run.py
   ```

## Usage

The application has four main tabs:

1. **View Test**: Browse and edit existing test data
   - Select a test from the dropdown
   - Edit test details in the form
   - Save changes back to the YAML file

2. **Data Analysis**: Analyze and visualize test data
   - Filter tests by various parameters
   - View test data in a table
   - Visualize data with interactive charts

3. **Create Test**: Create new test data
   - Fill in all required fields
   - Generate a unique test ID
   - Save the test data

4. **Admin**: Manage component lists
   - Add, edit, and delete component options
   - Organize components by type

## Project Structure

- `pyqt_app/`: PyQt application directory
  - `main.py`: Main application window and tab management
  - `run.py`: Entry point script with dependency checking
  - `modules/`: Application modules
    - `view_test.py`: View and edit test data
    - `data_analysis.py`: Data analysis and visualization
    - `create_test.py`: Create new tests
    - `admin.py`: Component list management
  - `utils/`: Utility functions
    - `data_loader.py`: Data loading and processing functions
- `Lists.yaml`: Dropdown lists for various options
- `run.py`: Convenience script to start the application
- `tests/`: Directory containing test data folders

## License

[MIT License](LICENSE)
