#!/usr/bin/env python3
"""
Reloading App - PyQt Implementation
Main entry point for the application
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
                            QLabel, QStatusBar)
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtCore import Qt

# Import application modules
from modules.create_test import CreateTestWidget
from modules.data_analysis import DataAnalysisWidget
from modules.view_test import ViewTestWidget
from modules.admin import AdminWidget
from utils.settings_manager import SettingsManager


class MainWindow(QMainWindow):
    """Main application window with tab-based interface"""
    
    def __init__(self):
        super().__init__()
        
        # Get settings manager
        self.settings_manager = SettingsManager.get_instance()
        
        # Set window properties
        self.update_window_title()
        self.setMinimumSize(1560, 1040)  # Increased by 30%
        self.resize(1560, 1040)  # Set initial size
        
        # Ensure menu bar is visible on all platforms
        self.menuBar().setNativeMenuBar(False)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Initialize UI components
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
    
    def update_window_title(self):
        """Update the window title to include the active database label."""
        active_db = self.settings_manager.get_active_database()
        self.setWindowTitle(f"Precision Rifle Load Development - {active_db}")
    
    def setup_status_bar(self):
        """Set up the status bar with the active database indicator."""
        # Create status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Add active database label
        active_db = self.settings_manager.get_active_database()
        self.db_label = QLabel(f"Active Database: {active_db}")
        
        # Make the label stand out
        font = QFont()
        font.setBold(True)
        self.db_label.setFont(font)
        
        status_bar.addPermanentWidget(self.db_label)
        
    def setup_ui(self):
        """Set up the main UI components"""
        # Instantiate widgets
        self.view_test_widget = ViewTestWidget()
        self.data_analysis_widget = DataAnalysisWidget()
        self.create_test_widget = CreateTestWidget()
        self.admin_widget = AdminWidget()  # Use the actual AdminWidget

        # Add tabs in the desired order
        self.tabs.addTab(self.view_test_widget, "View Test")
        self.tabs.addTab(self.data_analysis_widget, "Data Analysis")
        self.tabs.addTab(self.create_test_widget, "Create Test")
        self.tabs.addTab(self.admin_widget, "Admin")
        
        # Connect signals between widgets
        # When component lists are updated in Admin tab, refresh Create Test and View Test tabs
        self.admin_widget.componentListsUpdated.connect(self.create_test_widget.refresh)
        self.admin_widget.componentListsUpdated.connect(self.view_test_widget.refresh_component_lists)
        
        # When a new test is created in Create Test tab, refresh View Test and Data Analysis tabs
        self.create_test_widget.testCreated.connect(self.view_test_widget.refresh)
        self.create_test_widget.testCreated.connect(self.data_analysis_widget.refresh)
        
        # When a test is updated or deleted in View Test tab, refresh Data Analysis tab
        self.view_test_widget.testUpdated.connect(self.data_analysis_widget.refresh)
        self.view_test_widget.testDeleted.connect(self.data_analysis_widget.refresh)
    
    def setup_menu(self):
        """Set up the application menu"""
        # Create menu bar explicitly
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show the application's About box")
        # about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def show_settings_dialog(self):
        """Show the settings dialog.
        
        This method creates and displays the settings dialog,
        which allows the user to configure application settings.
        When settings are saved, it refreshes the test lists in the
        View Test and Data Analysis tabs.
        """
        try:
            from modules.settings import SettingsDialog
            dialog = SettingsDialog(self)
            
            # Connect the settingsChanged signal to refresh the test lists
            dialog.settingsChanged.connect(self.refresh_after_settings_change)
            
            # Connect the databaseSwitched signal to update the active database
            dialog.databaseSwitched.connect(self.update_active_database)
            
            dialog.exec()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to open settings dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_after_settings_change(self):
        """Refresh the application after settings have changed.
        
        This method refreshes the test lists in the View Test and Data Analysis tabs
        when the tests directory has been changed in the settings.
        """
        print("Refreshing application after settings change...")
        
        # Refresh the View Test tab
        self.view_test_widget.refresh()
        
        # Refresh the Data Analysis tab
        self.data_analysis_widget.refresh()
    
    def update_active_database(self, label):
        """Update the active database indicator.
        
        Args:
            label (str): Label of the new active database
        """
        print(f"Switching to database: {label}")
        
        # Update the window title
        self.update_window_title()
        
        # Update the status bar label
        self.db_label.setText(f"Active Database: {label}")
        
        # Refresh the test lists
        self.refresh_after_settings_change()


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MainWindow()
    window.showMaximized()  # Show maximized instead of normal
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
