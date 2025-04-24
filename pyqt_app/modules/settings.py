"""
Settings Module for the Precision Rifle Load Development App
Provides a dialog for configuring application settings.

This module contains the SettingsDialog class, which allows users to:
- View and modify application settings
- Manage multiple test database pointers
- Set the active database
- Browse for test directories
- Validate settings before saving
"""

# Standard library imports
import os

# Third-party imports
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLineEdit, QPushButton, QDialogButtonBox, QFileDialog,
                            QLabel, QMessageBox, QListWidget, QListWidgetItem,
                            QFormLayout, QFrame, QSplitter, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Local application imports
from utils.settings_manager import SettingsManager

class DatabaseItem(QListWidgetItem):
    """Custom list widget item for displaying database pointers.
    
    This class extends QListWidgetItem to store additional data about
    the database pointer, such as the label and path.
    """
    
    def __init__(self, label, path, is_active=False):
        """Initialize the database item.
        
        Args:
            label (str): Label for the database
            path (str): Path to the tests directory
            is_active (bool, optional): Whether this is the active database. Defaults to False.
        """
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

class SettingsDialog(QDialog):
    """Dialog for configuring application settings.
    
    This dialog allows users to view and modify application settings,
    manage multiple test database pointers, and set the active database.
    """
    
    # Signal emitted when settings are saved
    settingsChanged = pyqtSignal()
    
    # Signal emitted when the active database is changed
    databaseSwitched = pyqtSignal(str)  # Emits the label of the new active database
    
    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        # Get settings manager
        self.settings_manager = SettingsManager.get_instance()
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create a splitter for the database list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Database list section
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add description label
        description_label = QLabel(
            "Manage multiple test databases. Each database points to a directory "
            "containing test data, which can be on your local drive or in Google Drive."
        )
        description_label.setWordWrap(True)
        list_layout.addWidget(description_label)
        
        # Database list
        self.database_list = QListWidget()
        self.database_list.setMinimumWidth(200)
        self.database_list.currentItemChanged.connect(self.on_database_selected)
        list_layout.addWidget(self.database_list)
        
        # Database list buttons
        list_buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_database)
        list_buttons_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_database)
        self.delete_button.setEnabled(False)
        list_buttons_layout.addWidget(self.delete_button)
        
        self.set_active_button = QPushButton("Set as Active")
        self.set_active_button.clicked.connect(self.set_active_database)
        self.set_active_button.setEnabled(False)
        list_buttons_layout.addWidget(self.set_active_button)
        
        list_layout.addLayout(list_buttons_layout)
        
        # Database editor section
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Database editor group
        editor_group = QGroupBox("Database Details")
        editor_form = QFormLayout(editor_group)
        
        # Label input
        self.label_edit = QLineEdit()
        editor_form.addRow("Label:", self.label_edit)
        
        # Path input with browse button
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        
        self.path_edit = QLineEdit()
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_directory)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)
        
        editor_form.addRow("Path:", path_widget)
        
        # Add validation label
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red;")
        editor_form.addRow("", self.validation_label)
        
        # Editor buttons
        editor_buttons_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_database)
        self.update_button.setEnabled(False)
        editor_buttons_layout.addWidget(self.update_button)
        
        editor_form.addRow("", editor_buttons_layout)
        
        editor_layout.addWidget(editor_group)
        editor_layout.addStretch()
        
        # Add widgets to splitter
        splitter.addWidget(list_widget)
        splitter.addWidget(editor_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 400])
        
        # Add splitter to main layout
        layout.addWidget(splitter)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Populate the database list
        self.populate_database_list()
    
    def populate_database_list(self):
        """Populate the database list with the current databases."""
        self.database_list.clear()
        
        active_db = self.settings_manager.get_active_database()
        
        for db in self.settings_manager.get_databases():
            label = db.get('label', '')
            path = db.get('path', '')
            is_active = (label == active_db)
            
            item = DatabaseItem(label, path, is_active)
            self.database_list.addItem(item)
    
    def on_database_selected(self, current, previous):
        """Handle database selection.
        
        Args:
            current (QListWidgetItem): The currently selected item
            previous (QListWidgetItem): The previously selected item
        """
        if current is None:
            # Clear the editor
            self.label_edit.clear()
            self.path_edit.clear()
            self.validation_label.clear()
            
            # Disable buttons
            self.delete_button.setEnabled(False)
            self.set_active_button.setEnabled(False)
            self.update_button.setEnabled(False)
            return
        
        # Get the selected database
        db_item = current
        
        # Update the editor
        self.label_edit.setText(db_item.label)
        self.path_edit.setText(db_item.path)
        self.validation_label.clear()
        
        # Enable buttons
        self.delete_button.setEnabled(True)
        self.update_button.setEnabled(True)
        
        # Only enable "Set as Active" if this is not already the active database
        self.set_active_button.setEnabled(not db_item.is_active)
    
    def browse_directory(self):
        """Open a file dialog to browse for a directory."""
        current_dir = self.path_edit.text()
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", current_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )
        
        if directory:
            self.path_edit.setText(directory)
            self.validate_directory(directory)
    
    def validate_directory(self, directory):
        """Validate the selected directory.
        
        Args:
            directory (str): Path to the directory to validate
            
        Returns:
            bool: True if the directory is valid, False otherwise
        """
        if not os.path.isdir(directory):
            self.validation_label.setText("Error: Directory does not exist")
            return False
        
        if not os.access(directory, os.W_OK):
            self.validation_label.setText("Error: Directory is not writable")
            return False
        
        self.validation_label.setText("")
        return True
    
    def validate_label(self, label, current_label=None):
        """Validate the database label.
        
        Args:
            label (str): Label to validate
            current_label (str, optional): Current label for updates. Defaults to None.
            
        Returns:
            bool: True if the label is valid, False otherwise
        """
        if not label:
            self.validation_label.setText("Error: Label cannot be empty")
            return False
        
        # Check if the label already exists (unless it's the same as the current label)
        if label != current_label:
            for db in self.settings_manager.get_databases():
                if db.get('label') == label:
                    self.validation_label.setText("Error: Label already exists")
                    return False
        
        self.validation_label.setText("")
        return True
    
    def add_database(self):
        """Add a new database."""
        # Clear the editor
        self.label_edit.clear()
        self.path_edit.clear()
        self.validation_label.clear()
        
        # Deselect any selected item
        self.database_list.clearSelection()
        
        # Disable buttons that require selection
        self.delete_button.setEnabled(False)
        self.set_active_button.setEnabled(False)
        
        # Enable the update button for adding
        self.update_button.setEnabled(True)
    
    def update_database(self):
        """Update the selected database or add a new one."""
        label = self.label_edit.text().strip()
        path = self.path_edit.text().strip()
        
        # Validate inputs
        if not self.validate_directory(path):
            return
        
        # Check if we're in "add mode" (no item selected) or "update mode" (item selected)
        current_item = self.database_list.currentItem()
        is_add_mode = (current_item is None or not self.database_list.selectedItems())
        
        if is_add_mode:
            # Adding a new database
            if not self.validate_label(label):
                return
            
            if self.settings_manager.add_database(label, path):
                if self.settings_manager.save_settings():
                    self.populate_database_list()
                    self.settingsChanged.emit()
                    
                    # Select the newly added database in the list
                    for i in range(self.database_list.count()):
                        item = self.database_list.item(i)
                        if item.label == label:
                            self.database_list.setCurrentItem(item)
                            break
                    
                    QMessageBox.information(self, "Database Added", 
                                          f"Database '{label}' has been added successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save settings")
            else:
                QMessageBox.warning(self, "Error", "Failed to add database")
        else:
            # Updating an existing database
            old_label = current_item.label
            
            if not self.validate_label(label, old_label):
                return
            
            if self.settings_manager.update_database(old_label, label, path):
                if self.settings_manager.save_settings():
                    # Check if this was the active database
                    was_active = current_item.is_active
                    
                    self.populate_database_list()
                    self.settingsChanged.emit()
                    
                    # If this was the active database, emit the databaseSwitched signal
                    if was_active:
                        self.databaseSwitched.emit(label)
                    
                    QMessageBox.information(self, "Database Updated", 
                                          f"Database '{label}' has been updated successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save settings")
            else:
                QMessageBox.warning(self, "Error", "Failed to update database")
    
    def delete_database(self):
        """Delete the selected database."""
        current_item = self.database_list.currentItem()
        
        if current_item is None:
            return
        
        label = current_item.label
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the database '{label}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Check if this is the last database
        if len(self.settings_manager.get_databases()) <= 1:
            QMessageBox.warning(self, "Cannot Delete", 
                               "Cannot delete the last database. At least one database must exist.")
            return
        
        # Check if this is the active database
        was_active = current_item.is_active
        
        if self.settings_manager.delete_database(label):
            if self.settings_manager.save_settings():
                self.populate_database_list()
                self.settingsChanged.emit()
                
                # If this was the active database, emit the databaseSwitched signal
                if was_active:
                    self.databaseSwitched.emit(self.settings_manager.get_active_database())
                
                QMessageBox.information(self, "Database Deleted", 
                                      f"Database '{label}' has been deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings")
        else:
            QMessageBox.warning(self, "Error", "Failed to delete database")
    
    def set_active_database(self):
        """Set the selected database as active."""
        current_item = self.database_list.currentItem()
        
        if current_item is None or current_item.is_active:
            return
        
        label = current_item.label
        
        if self.settings_manager.set_active_database(label):
            if self.settings_manager.save_settings():
                self.populate_database_list()
                
                # Emit both signals
                self.settingsChanged.emit()
                self.databaseSwitched.emit(label)
                
                QMessageBox.information(self, "Active Database Changed", 
                                      f"Database '{label}' is now the active database.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings")
        else:
            QMessageBox.warning(self, "Error", "Failed to set active database")
