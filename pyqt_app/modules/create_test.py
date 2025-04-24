"""
Create Test Module for the Reloading App
Allows users to input data for a new test and creates the corresponding folder and files.
"""

import os
import sys
import yaml
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFormLayout, QLineEdit, QGroupBox, QMessageBox, QDateEdit,
                             QComboBox, QDoubleSpinBox, QTextEdit)
from PyQt6.QtCore import Qt, QDate, pyqtSignal

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.settings_manager import SettingsManager

# Path to the Component_List.yaml file (relative to the project root)
COMPONENT_LIST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Component_List.yaml"
)

class CreateTestWidget(QWidget):
    """Widget for creating new test entries"""
    
    # Signal emitted when a new test is created
    testCreated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get settings manager
        self.settings_manager = SettingsManager.get_instance()
        
        # Get tests directory from settings manager
        self.tests_dir = self.settings_manager.get_tests_directory()
        
        # Load component lists
        self.component_lists = self.load_component_lists()

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # --- Form for Test Details ---
        # Using GroupBoxes similar to ViewTestWidget for consistency
        main_layout.addWidget(self._create_test_info_group())
        main_layout.addWidget(self._create_platform_group())
        main_layout.addWidget(self._create_ammunition_group())
        # Results are typically added after the test, so not included in creation form
        
        main_layout.addStretch() # Push form elements up

        # Create Button
        create_button = QPushButton("Create New Test")
        # Find a suitable icon if desired, e.g., SP_DialogApplyButton or SP_FileIcon
        # create_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_...) 
        # create_button.setIcon(create_icon) 
        create_button.clicked.connect(self.create_test)
        main_layout.addWidget(create_button, alignment=Qt.AlignmentFlag.AlignRight)

    def refresh(self):
        """Refresh the widget data (reload component lists)"""
        # Update tests directory from settings manager
        self.tests_dir = self.settings_manager.get_tests_directory()
        
        # Reload component lists
        self.component_lists = self.load_component_lists()
        
        # Update dropdowns with new component lists
        # Distance
        self.distance_combo.clear()
        distance_list = self.component_lists.get('distance', [])
        if distance_list:
            self.distance_combo.addItems(distance_list)
        else:
            self.distance_combo.addItems(["100m", "200m", "300m"])
            
        # Calibre
        self.calibre_combo.clear()
        calibre_list = self.component_lists.get('calibre', [])
        if calibre_list:
            self.calibre_combo.addItems(calibre_list)
            
        # Rifle
        self.rifle_combo.clear()
        rifle_list = self.component_lists.get('rifle', [])
        if rifle_list:
            self.rifle_combo.addItems(rifle_list)
            
        # Bullet Brand
        self.bullet_brand_combo.clear()
        bullet_brand_list = self.component_lists.get('bullet_brand', [])
        if bullet_brand_list:
            self.bullet_brand_combo.addItems(bullet_brand_list)
            
        # Bullet Model
        self.bullet_model_combo.clear()
        bullet_model_list = self.component_lists.get('bullet_model', [])
        if bullet_model_list:
            self.bullet_model_combo.addItems(bullet_model_list)
            
        # Powder Brand
        self.powder_brand_combo.clear()
        powder_brand_list = self.component_lists.get('powder_brand', [])
        if powder_brand_list:
            self.powder_brand_combo.addItems(powder_brand_list)
            
        # Powder Model
        self.powder_model_combo.clear()
        powder_model_list = self.component_lists.get('powder_model', [])
        if powder_model_list:
            self.powder_model_combo.addItems(powder_model_list)
            
        # Case Brand
        self.case_brand_combo.clear()
        case_brand_list = self.component_lists.get('case_brand', [])
        if case_brand_list:
            self.case_brand_combo.addItems(case_brand_list)
            
        # Primer Brand
        self.primer_brand_combo.clear()
        primer_brand_list = self.component_lists.get('primer_brand', [])
        if primer_brand_list:
            self.primer_brand_combo.addItems(primer_brand_list)
            
        # Primer Model
        self.primer_model_combo.clear()
        primer_model_list = self.component_lists.get('primer_model', [])
        if primer_model_list:
            self.primer_model_combo.addItems(primer_model_list)
    
    def load_component_lists(self):
        """Load component lists from the YAML file"""
        try:
            if os.path.exists(COMPONENT_LIST_PATH):
                with open(COMPONENT_LIST_PATH, 'r') as file:
                    data = yaml.safe_load(file)
                    if data:
                        return data
            return {}
        except Exception as e:
            print(f"Error loading component lists: {e}")
            return {}

    def _create_test_info_group(self):
        group = QGroupBox("Test Information")
        layout = QFormLayout(group)
        
        # Date field
        self.date_edit = QDateEdit(QDate.currentDate()) # Default to today
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("Date:", self.date_edit)
        
        # Distance field (dropdown)
        self.distance_combo = QComboBox()
        distance_list = self.component_lists.get('distance', [])
        if distance_list:
            self.distance_combo.addItems(distance_list)
        else:
            self.distance_combo.addItems(["100m", "200m", "300m"])
        layout.addRow("Distance:", self.distance_combo)
        
        # Notes field (multi-line)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)  # Limit height
        layout.addRow("Notes:", self.notes_edit)
        
        return group

    def _create_platform_group(self):
        group = QGroupBox("Platform")
        layout = QFormLayout(group)
        
        # Calibre field (dropdown)
        self.calibre_combo = QComboBox()
        calibre_list = self.component_lists.get('calibre', [])
        if calibre_list:
            self.calibre_combo.addItems(calibre_list)
        layout.addRow("Calibre:", self.calibre_combo)
        
        # Rifle field (dropdown)
        self.rifle_combo = QComboBox()
        rifle_list = self.component_lists.get('rifle', [])
        if rifle_list:
            self.rifle_combo.addItems(rifle_list)
        layout.addRow("Rifle:", self.rifle_combo)
        
        return group

    def _create_ammunition_group(self):
        group = QGroupBox("Ammunition")
        layout = QFormLayout(group)
        
        # Bullet section
        # Bullet Brand (dropdown)
        self.bullet_brand_combo = QComboBox()
        bullet_brand_list = self.component_lists.get('bullet_brand', [])
        if bullet_brand_list:
            self.bullet_brand_combo.addItems(bullet_brand_list)
        layout.addRow("Bullet Brand:", self.bullet_brand_combo)
        
        # Bullet Model (dropdown)
        self.bullet_model_combo = QComboBox()
        bullet_model_list = self.component_lists.get('bullet_model', [])
        if bullet_model_list:
            self.bullet_model_combo.addItems(bullet_model_list)
        layout.addRow("Bullet Model:", self.bullet_model_combo)
        
        # Bullet Weight (numeric input)
        self.bullet_weight_spin = QDoubleSpinBox()
        self.bullet_weight_spin.setRange(0.01, 999.99)
        self.bullet_weight_spin.setDecimals(2)
        self.bullet_weight_spin.setSingleStep(0.1)
        self.bullet_weight_spin.setValue(75.0)  # Default value
        layout.addRow("Bullet Weight (gr):", self.bullet_weight_spin)
        
        # Powder section
        # Powder Brand (dropdown)
        self.powder_brand_combo = QComboBox()
        powder_brand_list = self.component_lists.get('powder_brand', [])
        if powder_brand_list:
            self.powder_brand_combo.addItems(powder_brand_list)
        layout.addRow("Powder Brand:", self.powder_brand_combo)
        
        # Powder Model (dropdown)
        self.powder_model_combo = QComboBox()
        powder_model_list = self.component_lists.get('powder_model', [])
        if powder_model_list:
            self.powder_model_combo.addItems(powder_model_list)
        layout.addRow("Powder Model:", self.powder_model_combo)
        
        # Powder Charge (numeric input)
        self.powder_charge_spin = QDoubleSpinBox()
        self.powder_charge_spin.setRange(0.01, 999.99)
        self.powder_charge_spin.setDecimals(2)
        self.powder_charge_spin.setSingleStep(0.1)
        self.powder_charge_spin.setValue(23.5)  # Default value
        layout.addRow("Powder Charge (gr):", self.powder_charge_spin)
        
        # Cartridge section
        # Cartridge OAL (numeric input)
        self.cartridge_oal_spin = QDoubleSpinBox()
        self.cartridge_oal_spin.setRange(0.001, 9.999)
        self.cartridge_oal_spin.setDecimals(3)
        self.cartridge_oal_spin.setSingleStep(0.001)
        self.cartridge_oal_spin.setValue(2.410)  # Default value
        layout.addRow("Cartridge OAL (in):", self.cartridge_oal_spin)
        
        # Cartridge BTO (numeric input)
        self.cartridge_bto_spin = QDoubleSpinBox()
        self.cartridge_bto_spin.setRange(0.001, 9.999)
        self.cartridge_bto_spin.setDecimals(3)
        self.cartridge_bto_spin.setSingleStep(0.001)
        self.cartridge_bto_spin.setValue(1.784)  # Default value
        layout.addRow("Cartridge BTO (in):", self.cartridge_bto_spin)
        
        # Case Brand (dropdown)
        self.case_brand_combo = QComboBox()
        case_brand_list = self.component_lists.get('case_brand', [])
        if case_brand_list:
            self.case_brand_combo.addItems(case_brand_list)
        layout.addRow("Case Brand:", self.case_brand_combo)
        
        # Primer Brand (dropdown)
        self.primer_brand_combo = QComboBox()
        primer_brand_list = self.component_lists.get('primer_brand', [])
        if primer_brand_list:
            self.primer_brand_combo.addItems(primer_brand_list)
        layout.addRow("Primer Brand:", self.primer_brand_combo)
        
        # Primer Model (dropdown)
        self.primer_model_combo = QComboBox()
        primer_model_list = self.component_lists.get('primer_model', [])
        if primer_model_list:
            self.primer_model_combo.addItems(primer_model_list)
        layout.addRow("Primer Model:", self.primer_model_combo)
        
        return group

    def generate_test_id(self, data):
        """Generates a unique folder name based on test data."""
        # Similar logic to the Streamlit app's generate_test_id
        date_str = data.get('date', datetime.date.today().strftime('%Y-%m-%d'))
        dist = data.get('distance_m', 'Dist')
        cal = data.get('calibre', 'Cal').replace('.', '') # Remove dots from calibre
        rifle = data.get('rifle', 'Rifle').replace(' ', '-')
        case = data.get('case_brand', 'Case')
        bullet_brand = data.get('bullet_brand', 'BulletBrand')
        bullet_model = data.get('bullet_model', 'BulletModel').replace(' ', '-')
        bullet_wt = data.get('bullet_weight_gr', 'Wt')
        powder_brand = data.get('powder_brand', 'PowderBrand')
        powder_model = data.get('powder_model', 'PowderModel').replace(' ', '-')
        powder_chg = data.get('powder_charge_gr', 'Chg')
        oal = data.get('coal_in', 'OAL')
        bto = data.get('b2o_in', 'BTO')
        primer_brand = data.get('primer_brand', 'PrimerBrand')
        primer_model = data.get('primer_model', 'PrimerModel')

        # Construct the folder name (adjust formatting as needed)
        folder_name = (
            f"{date_str}__{dist}_{cal}_{rifle}_{case}_{bullet_brand}_{bullet_model}_{bullet_wt}gr_"
            f"{powder_brand}_{powder_model}_{powder_chg}gr_{oal}in_{bto}in_"
            f"{primer_brand}_{primer_model}"
        )
        
        # Basic sanitization (replace invalid chars, although above logic might handle most)
        folder_name = "".join(c if c.isalnum() or c in ['-', '_', '.'] else '_' for c in folder_name)
        
        return folder_name

    def create_test(self):
        """Gathers data, creates folder, and saves initial group.yaml"""
        
        # --- Gather data from UI fields ---
        test_data = {}
        
        # Test Info
        test_data['date'] = self.date_edit.date().toString("yyyy-MM-dd")
        distance_text = self.distance_combo.currentText()
        test_data['distance_m'] = int(distance_text.replace('m', ''))  # Extract numeric part
        test_data['notes'] = self.notes_edit.toPlainText() or None

        # Platform
        test_data['calibre'] = self.calibre_combo.currentText()
        test_data['rifle'] = self.rifle_combo.currentText()
        
        # Ammunition
        test_data['bullet_brand'] = self.bullet_brand_combo.currentText()
        test_data['bullet_model'] = self.bullet_model_combo.currentText()
        test_data['bullet_weight_gr'] = self.bullet_weight_spin.value()
        
        test_data['powder_brand'] = self.powder_brand_combo.currentText()
        test_data['powder_model'] = self.powder_model_combo.currentText()
        test_data['powder_charge_gr'] = self.powder_charge_spin.value()
        
        test_data['coal_in'] = self.cartridge_oal_spin.value()
        test_data['b2o_in'] = self.cartridge_bto_spin.value()
        test_data['case_brand'] = self.case_brand_combo.currentText()
        
        test_data['primer_brand'] = self.primer_brand_combo.currentText()
        test_data['primer_model'] = self.primer_model_combo.currentText()
        
        # Validate required fields
        required_fields = [
            'date', 'distance_m', 'calibre', 'rifle', 
            'bullet_brand', 'bullet_model', 'bullet_weight_gr',
            'powder_brand', 'powder_model', 'powder_charge_gr',
            'coal_in', 'b2o_in', 'case_brand',
            'primer_brand', 'primer_model'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not test_data.get(field):
                missing_fields.append(field.replace('_', ' ').title())
        
        if missing_fields:
            QMessageBox.warning(
                self, 
                "Missing Required Fields", 
                f"The following fields are required:\n{', '.join(missing_fields)}"
            )
            return

        # --- Generate Test ID and Create Folder ---
        test_id = self.generate_test_id(test_data)
        new_test_dir = os.path.join(self.tests_dir, test_id)

        if os.path.exists(new_test_dir):
            QMessageBox.warning(self, "Directory Exists", f"A test directory already exists for:\n{test_id}\nPlease modify inputs or delete the existing directory.")
            return

        try:
            os.makedirs(new_test_dir)
        except Exception as e:
            QMessageBox.critical(self, "Directory Creation Error", f"Failed to create directory:\n{new_test_dir}\nError: {e}")
            return

        # --- Save initial group.yaml ---
        group_yaml_path = os.path.join(new_test_dir, "group.yaml")
        try:
            # Restructure data for YAML format
            yaml_data = {
                'date': test_data['date'],
                'distance_m': test_data['distance_m'],
                'notes': test_data['notes'],
                'platform': {
                    'calibre': test_data['calibre'],
                    'rifle': test_data['rifle']
                },
                'ammo': {
                    'bullet': {
                        'brand': test_data['bullet_brand'],
                        'model': test_data['bullet_model'],
                        'weight_gr': test_data['bullet_weight_gr']
                    },
                    'powder': {
                        'brand': test_data['powder_brand'],
                        'model': test_data['powder_model'],
                        'charge_gr': test_data['powder_charge_gr']
                    },
                    'coal_in': test_data['coal_in'],
                    'b2o_in': test_data['b2o_in'],
                    'case': {
                        'brand': test_data['case_brand']
                    },
                    'primer': {
                        'brand': test_data['primer_brand'],
                        'model': test_data['primer_model']
                    }
                },
                'group': {
                    'group_es_mm': None,
                    'group_es_moa': None,
                    'mean_radius_mm': None
                },
                'chrono': {
                    'avg_velocity_fps': None,
                    'sd_fps': None,
                    'es_fps': None
                }
            }
            
            # Clean up None values before saving for a cleaner YAML
            def remove_none_values(d):
                if not isinstance(d, dict):
                    return d
                cleaned_dict = {}
                for k, v in d.items():
                    cleaned_v = remove_none_values(v)
                    if cleaned_v is not None and not (isinstance(cleaned_v, dict) and not cleaned_v):
                        cleaned_dict[k] = cleaned_v
                return cleaned_dict
            
            cleaned_data = remove_none_values(yaml_data)

            with open(group_yaml_path, 'w') as f:
                yaml.dump(cleaned_data, f, default_flow_style=False, sort_keys=False)
            
            # Emit signal to notify other widgets that a new test has been created
            self.testCreated.emit()
            
            QMessageBox.information(self, "Test Created", f"Successfully created test:\n{test_id}")
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "File Save Error", f"Failed to save group.yaml for {test_id}:\n{e}")
            # Consider deleting the created directory if the file save fails
            try:
                os.rmdir(new_test_dir) 
            except OSError:
                pass # Ignore error if directory couldn't be removed

    def clear_form(self):
        """Clear the form after successful creation"""
        self.date_edit.setDate(QDate.currentDate())
        self.notes_edit.clear()  # This works for QTextEdit too
        
        # Reset numeric fields to defaults
        self.bullet_weight_spin.setValue(75.0)
        self.powder_charge_spin.setValue(23.5)
        self.cartridge_oal_spin.setValue(2.410)
        self.cartridge_bto_spin.setValue(1.784)
