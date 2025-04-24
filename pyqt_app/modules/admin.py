"""
Admin Module for the Reloading App
Provides administration interface for component lists
"""

import os
import sys
import yaml
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QScrollArea, QFormLayout,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Path to the Component_List.yaml file (relative to the project root)
COMPONENT_LIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Component_List.yaml"
)

class ComponentListEditor(QWidget):
    """Widget for editing a single component list"""
    
    itemsChanged = pyqtSignal()  # Signal emitted when items are changed
    
    def __init__(self, component_key, component_name, parent=None):
        super().__init__(parent)
        self.component_key = component_key
        self.component_name = component_name
        self.items = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # List widget for displaying items
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.currentRowChanged.connect(self.on_item_selected)
        main_layout.addWidget(self.list_widget)
        
        # Form for adding/editing items
        form_group = QGroupBox("Edit Item")
        form_layout = QFormLayout(form_group)
        
        # Item input
        self.item_input = QLineEdit()
        form_layout.addRow(f"{self.component_name}:", self.item_input)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add button
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_item)
        buttons_layout.addWidget(self.add_button)
        
        # Update button
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_item)
        self.update_button.setEnabled(False)
        buttons_layout.addWidget(self.update_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_item)
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        form_layout.addRow("", buttons_layout)
        main_layout.addWidget(form_group)
    
    def load_items(self, items):
        """Load items into the list widget"""
        self.items = items.copy()
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the list widget with current items"""
        self.list_widget.clear()
        for item in self.items:
            self.list_widget.addItem(item)
    
    def on_item_selected(self, row):
        """Handle item selection"""
        if row >= 0 and row < len(self.items):
            self.item_input.setText(self.items[row])
            self.update_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.item_input.clear()
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def add_item(self):
        """Add a new item to the list"""
        item_text = self.item_input.text().strip()
        if not item_text:
            QMessageBox.warning(self, "Input Error", "Please enter a value.")
            return
        
        if item_text in self.items:
            QMessageBox.warning(self, "Duplicate Item", f"'{item_text}' already exists in the list.")
            return
        
        self.items.append(item_text)
        self.refresh_list()
        self.item_input.clear()
        self.itemsChanged.emit()
    
    def update_item(self):
        """Update the selected item"""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
        
        item_text = self.item_input.text().strip()
        if not item_text:
            QMessageBox.warning(self, "Input Error", "Please enter a value.")
            return
        
        if item_text != self.items[current_row] and item_text in self.items:
            QMessageBox.warning(self, "Duplicate Item", f"'{item_text}' already exists in the list.")
            return
        
        self.items[current_row] = item_text
        self.refresh_list()
        self.list_widget.setCurrentRow(current_row)
        self.itemsChanged.emit()
    
    def delete_item(self):
        """Delete the selected item"""
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
        
        item_text = self.items[current_row]
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete '{item_text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.items.pop(current_row)
            self.refresh_list()
            self.item_input.clear()
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.itemsChanged.emit()
    
    def get_items(self):
        """Get the current items"""
        return self.items.copy()


class AdminWidget(QWidget):
    """Widget for administration interface"""
    
    # Signal emitted when component lists are updated
    componentListsUpdated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Component lists
        self.component_lists = {}
        
        # Component info
        self.component_info = [
            {"key": "distance", "name": "Distance"},
            {"key": "calibre", "name": "Calibre"},
            {"key": "rifle", "name": "Rifle"},
            {"key": "case_brand", "name": "Case Brand"},
            {"key": "powder_brand", "name": "Powder Brand"},
            {"key": "powder_model", "name": "Powder Model"},
            {"key": "bullet_brand", "name": "Bullet Brand"},
            {"key": "bullet_model", "name": "Bullet Model"},
            {"key": "primer_brand", "name": "Primer Brand"},
            {"key": "primer_model", "name": "Primer Model"},
            {"key": "brass_sizing", "name": "Brass Sizing"}
        ]
        
        # Component editors
        self.component_editors = {}
        
        # Set up the UI
        self.setup_ui()
        
        # Load component lists
        self.load_component_lists()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Component List Administration")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(header_label)
        
        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs for each component type
        for component in self.component_info:
            component_key = component["key"]
            component_name = component["name"]
            
            # Create editor widget
            editor = ComponentListEditor(component_key, component_name)
            editor.itemsChanged.connect(self.save_component_lists)
            self.component_editors[component_key] = editor
            
            # Create scroll area for the editor
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(editor)
            
            # Add tab
            self.tabs.addTab(scroll_area, component_name)
        
        # Save button
        self.save_button = QPushButton("Save All Changes")
        self.save_button.clicked.connect(self.save_component_lists)
        main_layout.addWidget(self.save_button)
    
    def load_component_lists(self):
        """Load component lists from the YAML file"""
        try:
            if os.path.exists(COMPONENT_LIST_PATH):
                with open(COMPONENT_LIST_PATH, 'r') as file:
                    data = yaml.safe_load(file)
                    if data:
                        self.component_lists = data
            else:
                # Create default component lists if file doesn't exist
                self.component_lists = {
                    "calibre": ["223", "308", "6.5CM"],
                    "rifle": ["Tikka T3X"],
                    "case_brand": ["Hornady", "Sako", "Lapua"],
                    "powder_brand": ["ADI"],
                    "powder_model": ["2208", "2206H"],
                    "bullet_brand": ["Hornady", "Berger"],
                    "bullet_model": ["ELD-M"],
                    "primer_brand": ["CCI", "RWS"],
                    "primer_model": ["BR-4", "4033"],
                    "brass_sizing": ["Full", "Neck Only with Bushing", "Neck Only - no bushing"]
                }
                self.save_component_lists()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load component lists: {e}")
            return
        
        # Update editor widgets
        for component_key, editor in self.component_editors.items():
            items = self.component_lists.get(component_key, [])
            editor.load_items(items)
    
    def save_component_lists(self):
        """Save component lists to the YAML file"""
        try:
            # Update component lists from editors
            for component_key, editor in self.component_editors.items():
                self.component_lists[component_key] = editor.get_items()
            
            # Save to file
            with open(COMPONENT_LIST_PATH, 'w') as file:
                yaml.dump(self.component_lists, file, default_flow_style=False, sort_keys=False)
            
            # Emit signal to notify other widgets that component lists have been updated
            self.componentListsUpdated.emit()
            
            # Show success message (only when explicitly clicked save button)
            if self.sender() == self.save_button:
                QMessageBox.information(self, "Success", "Component lists saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save component lists: {e}")
