"""
Settings Manager for the Precision Rifle Load Development App
Handles loading, saving, and managing application settings.

This module provides a singleton SettingsManager class that:
- Stores settings in a platform-specific location
- Provides default settings for first-time users
- Validates settings before saving
- Ensures consistent settings across the application
- Manages multiple test database pointers
"""

# Standard library imports
import os
import sys
import yaml

class SettingsManager:
    """Singleton class for managing application settings.
    
    This class handles loading, saving, and accessing application settings.
    It uses the singleton pattern to ensure that only one instance exists
    throughout the application.
    
    It also manages multiple test database pointers, allowing the user to
    switch between different test databases.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the SettingsManager.
        
        Returns:
            SettingsManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = SettingsManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the SettingsManager.
        
        Sets up the configuration file path and loads settings.
        """
        self.config_file = self._get_config_file_path()
        self.settings = self._load_settings()
    
    def _get_config_file_path(self):
        """Get the platform-specific path for the configuration file.
        
        Returns:
            str: Path to the configuration file
        """
        # Platform-specific config directory
        if sys.platform == 'win32':
            config_dir = os.path.join(os.environ['APPDATA'], 'PrecisionRifleLoadDevelopment')
        elif sys.platform == 'darwin':
            config_dir = os.path.expanduser('~/Library/Application Support/PrecisionRifleLoadDevelopment')
        else:
            config_dir = os.path.expanduser('~/.config/precision-rifle-load-development')
        
        # Create directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, 'config.yaml')
    
    def _load_settings(self):
        """Load settings from the configuration file.
        
        If the file doesn't exist or can't be loaded, returns default settings.
        If the settings file exists but uses the old format (single tests_directory),
        it will be migrated to the new format (multiple databases).
        
        Returns:
            dict: Dictionary containing application settings
        """
        # Default tests directory path
        default_tests_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tests')
        
        # Default settings with multiple database support
        default_settings = {
            'active_database': 'Default',
            'databases': [
                {
                    'label': 'Default',
                    'path': default_tests_dir
                }
            ]
        }
        
        # Try to load existing settings
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    settings = yaml.safe_load(f)
                
                if settings and isinstance(settings, dict):
                    # Check if we need to migrate from old format to new format
                    if 'tests_directory' in settings and 'databases' not in settings:
                        # Migrate from old format to new format
                        old_path = settings['tests_directory']
                        settings = {
                            'active_database': 'Default',
                            'databases': [
                                {
                                    'label': 'Default',
                                    'path': old_path
                                }
                            ]
                        }
                    
                    # Merge with defaults to ensure all keys exist
                    return {**default_settings, **settings}
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save settings to the configuration file.
        
        Returns:
            bool: True if settings were saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.settings, f)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_tests_directory(self):
        """Get the tests directory path for the active database.
        
        Returns:
            str: Path to the tests directory for the active database
        """
        active_db = self.get_active_database()
        for db in self.settings.get('databases', []):
            if db.get('label') == active_db:
                return db.get('path')
        
        # Fallback to the first database if active database not found
        if self.settings.get('databases'):
            return self.settings['databases'][0].get('path')
        
        # Ultimate fallback to default path
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tests')
    
    def get_active_database(self):
        """Get the label of the active database.
        
        Returns:
            str: Label of the active database
        """
        return self.settings.get('active_database', 'Default')
    
    def set_active_database(self, label):
        """Set the active database by label.
        
        Args:
            label (str): Label of the database to set as active
            
        Returns:
            bool: True if the database was found and set as active, False otherwise
        """
        # Check if the database exists
        for db in self.settings.get('databases', []):
            if db.get('label') == label:
                self.settings['active_database'] = label
                return True
        return False
    
    def get_databases(self):
        """Get the list of database pointers.
        
        Returns:
            list: List of dictionaries containing database pointers
        """
        return self.settings.get('databases', [])
    
    def add_database(self, label, path):
        """Add a new database pointer.
        
        Args:
            label (str): Label for the database
            path (str): Path to the tests directory
            
        Returns:
            bool: True if the database was added successfully, False otherwise
        """
        # Check if the path is valid
        if not os.path.isdir(path) or not os.access(path, os.W_OK):
            return False
        
        # Check if the label already exists
        for db in self.settings.get('databases', []):
            if db.get('label') == label:
                return False
        
        # Add the database
        if 'databases' not in self.settings:
            self.settings['databases'] = []
        
        self.settings['databases'].append({
            'label': label,
            'path': path
        })
        
        return True
    
    def update_database(self, old_label, new_label, path):
        """Update an existing database pointer.
        
        Args:
            old_label (str): Current label of the database
            new_label (str): New label for the database
            path (str): New path for the database
            
        Returns:
            bool: True if the database was updated successfully, False otherwise
        """
        # Check if the path is valid
        if not os.path.isdir(path) or not os.access(path, os.W_OK):
            return False
        
        # Check if the new label already exists (unless it's the same as the old label)
        if old_label != new_label:
            for db in self.settings.get('databases', []):
                if db.get('label') == new_label:
                    return False
        
        # Update the database
        for db in self.settings.get('databases', []):
            if db.get('label') == old_label:
                db['label'] = new_label
                db['path'] = path
                
                # If this was the active database, update the active database label
                if self.settings.get('active_database') == old_label:
                    self.settings['active_database'] = new_label
                
                return True
        
        return False
    
    def delete_database(self, label):
        """Delete a database pointer.
        
        Args:
            label (str): Label of the database to delete
            
        Returns:
            bool: True if the database was deleted successfully, False otherwise
        """
        # Don't allow deleting the last database
        if len(self.settings.get('databases', [])) <= 1:
            return False
        
        # Find the database
        for i, db in enumerate(self.settings.get('databases', [])):
            if db.get('label') == label:
                # Remove the database
                del self.settings['databases'][i]
                
                # If this was the active database, set the first database as active
                if self.settings.get('active_database') == label:
                    self.settings['active_database'] = self.settings['databases'][0].get('label')
                
                return True
        
        return False
    
    def set_tests_directory(self, path):
        """Set the tests directory path for the active database.
        
        This method is maintained for backward compatibility.
        
        Args:
            path (str): Path to the tests directory
            
        Returns:
            bool: True if the path is valid and was set, False otherwise
        """
        if os.path.isdir(path) and os.access(path, os.W_OK):
            active_db = self.get_active_database()
            
            # Update the active database
            for db in self.settings.get('databases', []):
                if db.get('label') == active_db:
                    db['path'] = path
                    return True
            
            # If the active database wasn't found, add it
            return self.add_database(active_db, path)
        
        return False
