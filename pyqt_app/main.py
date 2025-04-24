#!/usr/bin/env python3
"""
Reloading App - PyQt Implementation
Main entry point for the application
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

# Import application modules
from modules.create_test import CreateTestWidget # Import the create test widget
from modules.data_analysis import DataAnalysisWidget
from modules.view_test import ViewTestWidget # Import the view test widget
from modules.admin import AdminWidget # Import the admin widget


class MainWindow(QMainWindow):
    """Main application window with tab-based interface"""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Precision Rifle Load Development")
        self.setMinimumSize(1200, 800)
        
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
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show the application's About box")
        # about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
