# Precision Rifle Load Development Code Standards

This document outlines the code documentation standards for the Precision Rifle Load Development application. Following these standards ensures that the codebase remains maintainable, readable, and well-documented.

## Python Code Documentation

### Docstrings

All modules, classes, and methods should have docstrings following the Google style:

```python
def function_with_types_in_docstring(param1, param2):
    """Example function with types documented in the docstring.
    
    This function does something useful.
    
    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.
        
    Returns:
        bool: The return value. True for success, False otherwise.
        
    Raises:
        ValueError: If param1 is negative.
        TypeError: If param2 is not a string.
    """
    if param1 < 0:
        raise ValueError("param1 must be positive")
    if not isinstance(param2, str):
        raise TypeError("param2 must be a string")
    return True
```

### Module Docstrings

Each module should have a docstring at the top of the file that describes the purpose of the module:

```python
"""
Data Loader Module for the Precision Rifle Load Development App
Handles loading, saving, and processing test data.

This module provides functions for:
- Loading test data from YAML files
- Saving test data to YAML files
- Validating test data
- Processing test data for analysis
"""
```

### Class Docstrings

Each class should have a docstring that describes the purpose of the class:

```python
class DataLoader:
    """Class for loading and processing test data.
    
    This class handles loading test data from YAML files,
    validating the data, and processing it for analysis.
    It also provides methods for saving test data back to
    YAML files.
    """
```

### Method Docstrings

Each method should have a docstring that describes the purpose of the method, its parameters, return values, and any exceptions it may raise:

```python
def load_test(self, test_id):
    """Load a test from a file.
    
    Args:
        test_id (str): The ID of the test to load.
        
    Returns:
        dict: The test data as a dictionary.
        
    Raises:
        FileNotFoundError: If the test file does not exist.
        ValueError: If the test data is invalid.
    """
```

### Type Hints

Use type hints for function parameters and return values:

```python
def load_test(self, test_id: str) -> dict:
    """Load a test from a file."""
    # ...
```

## PyQt Code Documentation

### Widget Classes

Widget classes should have docstrings that describe the purpose of the widget:

```python
class ViewTestWidget(QWidget):
    """Widget for viewing and editing test data.
    
    This widget displays a list of available tests and allows
    the user to view and edit the details of a selected test.
    It also provides functionality for saving changes back to
    the test file.
    """
```

### Signal Documentation

Document signals in the class docstring:

```python
class CreateTestWidget(QWidget):
    """Widget for creating new tests.
    
    This widget provides a form for entering test parameters
    and creating a new test file.
    
    Signals:
        testCreated (str): Emitted when a new test is created.
            The signal includes the ID of the new test.
    """
    
    # Define the signal
    testCreated = pyqtSignal(str)
```

### UI Setup Methods

Document UI setup methods:

```python
def setup_ui(self):
    """Set up the UI components.
    
    This method creates and configures all the UI components
    for the widget, including layouts, labels, input fields,
    and buttons.
    """
```

## Code Comments

### General Guidelines

- Use comments to explain **why** code is doing something, not **what** it's doing
- Keep comments up to date when changing code
- Use clear and concise language
- Avoid redundant comments that just repeat the code

### Good Comments

```python
# Calculate the mean radius using the distance formula
mean_radius = sum(math.sqrt((x - center_x)**2 + (y - center_y)**2) for x, y in points) / len(points)

# Convert from inches to MOA based on the distance
moa_factor = 1.047 * (100 / distance_yards)
mean_radius_moa = mean_radius * moa_factor
```

### Bad Comments

```python
# Set x to 5
x = 5

# Loop through the list
for item in items:
    # Print the item
    print(item)
```

## File Organization

### Python Files

Python files should be organized in the following order:

1. Module docstring
2. Imports (grouped by standard library, third-party, and local)
3. Constants
4. Global variables
5. Classes
6. Functions
7. Main execution code (if applicable)

Example:

```python
"""
Data Loader Module for the Precision Rifle Load Development App
Handles loading, saving, and processing test data.
"""

# Standard library imports
import os
import sys
import yaml

# Third-party imports
from PyQt6.QtWidgets import QMessageBox

# Local application imports
from utils.settings_manager import SettingsManager

# Constants
DEFAULT_TEST_DIR = "tests"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Classes
class DataLoader:
    """Class for loading and processing test data."""
    # ...

# Functions
def validate_test_data(data):
    """Validate test data."""
    # ...

# Main execution code (if applicable)
if __name__ == "__main__":
    # ...
```

### Class Organization

Classes should be organized in the following order:

1. Class docstring
2. Class attributes
3. Constructor
4. Properties
5. Public methods
6. Protected methods (prefixed with `_`)
7. Private methods (prefixed with `__`)
8. Static methods
9. Class methods

Example:

```python
class DataLoader:
    """Class for loading and processing test data."""
    
    # Class attributes
    DEFAULT_ENCODING = "utf-8"
    
    def __init__(self):
        """Initialize the data loader."""
        self.settings_manager = SettingsManager.get_instance()
        self.tests_directory = self.settings_manager.get_tests_directory()
        self._cache = {}
    
    # Properties
    @property
    def tests_directory(self):
        """Get the tests directory."""
        return self._tests_directory
    
    @tests_directory.setter
    def tests_directory(self, value):
        """Set the tests directory."""
        self._tests_directory = value
    
    # Public methods
    def load_test(self, test_id):
        """Load a test from a file."""
        # ...
    
    def save_test(self, test_id, data):
        """Save a test to a file."""
        # ...
    
    # Protected methods
    def _validate_test_id(self, test_id):
        """Validate a test ID."""
        # ...
    
    # Private methods
    def __parse_yaml(self, content):
        """Parse YAML content."""
        # ...
    
    # Static methods
    @staticmethod
    def is_valid_test_id(test_id):
        """Check if a test ID is valid."""
        # ...
    
    # Class methods
    @classmethod
    def from_config(cls, config):
        """Create a data loader from a configuration."""
        # ...
```

## Conclusion

Following these code documentation standards will help maintain a high-quality codebase that is easy to understand, maintain, and extend. Consistent documentation makes it easier for new developers to join the project and for existing developers to work with code they didn't write.
