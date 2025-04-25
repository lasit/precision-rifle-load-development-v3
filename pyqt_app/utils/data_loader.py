"""
Data Loader Utility for the Precision Rifle Load Development App
Handles loading and parsing test data from files.

This module provides functions for:
- Loading test data from YAML files
- Parsing test information from directory names
- Loading chronograph data from CSV files
- Combining all test data into a DataFrame for analysis
"""

import os
import yaml
import pandas as pd
import numpy as np
import re
from datetime import datetime

# Import settings manager
from utils.settings_manager import SettingsManager


def extract_test_info_from_path(test_path):
    """
    Extract test information from the test directory path
    
    Args:
        test_path (str): Path to the test directory
        
    Returns:
        dict: Dictionary containing extracted test information
    """
    # Get the directory name (last part of the path)
    dir_name = os.path.basename(test_path)
    
    # Parse the directory name to extract test information
    # Expected format: YYYY-MM-DD__distance_calibre_rifle_case_bullet-brand_bullet-model_bullet-weight_powder-brand_powder-model_powder-charge_coal_b2o_primer
    try:
        # Split by double underscore to separate date and test info
        date_str, test_info = dir_name.split('__')
        
        # Parse test info parts
        parts = test_info.split('_')
        
        # Extract basic information
        distance = parts[0]  # e.g., "100m"
        calibre = parts[1]   # e.g., "223"
        rifle = parts[2]     # e.g., "Tikka-T3X"
        
        # Extract case brand (if available)
        case_brand_idx = 3
        case_brand = parts[case_brand_idx]  # e.g., "Hornady"
        
        # Extract bullet information
        bullet_brand_idx = 4
        bullet_brand = parts[bullet_brand_idx]  # e.g., "Hornady"
        bullet_model = parts[bullet_brand_idx + 1]  # e.g., "ELD-M"
        bullet_weight = parts[bullet_brand_idx + 2]  # e.g., "75gr"
        
        # Extract powder information
        powder_brand_idx = bullet_brand_idx + 3
        powder_brand = parts[powder_brand_idx]  # e.g., "ADI"
        powder_model = parts[powder_brand_idx + 1]  # e.g., "2208"
        powder_charge = parts[powder_brand_idx + 2]  # e.g., "23.44gr"
        
        # Extract cartridge dimensions
        coal_idx = powder_brand_idx + 3
        coal = parts[coal_idx]  # e.g., "2.410in"
        b2o = parts[coal_idx + 1]  # e.g., "1.784in"
        
        # Extract primer (if available)
        primer_idx = coal_idx + 2
        primer = parts[primer_idx] if len(parts) > primer_idx else "Unknown"
        
        # Extract numeric values
        distance_value = float(re.search(r'(\d+)', distance).group(1))
        bullet_weight_value = float(re.search(r'(\d+\.?\d*)', bullet_weight).group(1))
        powder_charge_value = float(re.search(r'(\d+\.?\d*)', powder_charge).group(1))
        coal_value = float(re.search(r'(\d+\.?\d*)', coal).group(1))
        b2o_value = float(re.search(r'(\d+\.?\d*)', b2o).group(1))
        
        # Create and return the test info dictionary
        return {
            'test_id': dir_name,
            'date': date_str,
            'distance': distance,
            'distance_m': distance_value,
            'calibre': calibre,
            'rifle': rifle.replace('-', ' '),
            'case_brand': case_brand,
            'bullet_brand': bullet_brand,
            'bullet_model': bullet_model,
            'bullet_weight': bullet_weight,
            'bullet_weight_gr': bullet_weight_value,
            'powder_brand': powder_brand,
            'powder_model': powder_model,
            'powder_charge': powder_charge,
            'powder_charge_gr': powder_charge_value,
            'coal': coal,
            'coal_in': coal_value,
            'b2o': b2o,
            'b2o_in': b2o_value,
            'primer': primer
        }
    except (ValueError, IndexError) as e:
        # If parsing fails, return a minimal dictionary with the test_id
        return {
            'test_id': dir_name,
            'date': 'Unknown',
            'distance': 'Unknown',
            'distance_m': 0,
            'calibre': 'Unknown',
            'rifle': 'Unknown',
            'case_brand': 'Unknown',
            'bullet_brand': 'Unknown',
            'bullet_model': 'Unknown',
            'bullet_weight': 'Unknown',
            'bullet_weight_gr': 0,
            'powder_brand': 'Unknown',
            'powder_model': 'Unknown',
            'powder_charge': 'Unknown',
            'powder_charge_gr': 0,
            'coal': 'Unknown',
            'coal_in': 0,
            'b2o': 'Unknown',
            'b2o_in': 0,
            'primer': 'Unknown'
        }


def load_group_data(test_path):
    """
    Load group data from the group.yaml file
    
    Args:
        test_path (str): Path to the test directory
        
    Returns:
        dict: Dictionary containing group data, chrono data, and environment data
    """
    group_file = os.path.join(test_path, 'group.yaml')
    
    if not os.path.exists(group_file):
        return {
            'group_es_mm': 0,
            'group_es_moa': 0,
            'group_es_x_mm': 0,
            'group_es_y_mm': 0,
            'mean_radius_mm': 0,
            'poi_x_mm': 0,
            'poi_y_mm': 0,
            'shots': 0,
            'avg_velocity_fps': 0,
            'sd_fps': 0,
            'es_fps': 0,
            'temperature_c': 0,
            'humidity_pct': 0,
            'pressure_hpa': 0,
            'wind_speed_ms': 0,
            'wind_direction': '',
            'light_conditions': '',
            'barrel_length_in': 0,
            'twist_rate': '',
            'bullet_lot': '',
            'powder_lot': '',
            'case_brand': '',
            'case_lot': '',
            'neck_turned': '',
            'brass_sizing': '',
            'bushing_size': 0,
            'shoulder_bump': 0,
            'primer_brand': '',
            'primer_model': '',
            'primer_lot': ''
        }
    
    try:
        with open(group_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        if not isinstance(yaml_data, dict):
            return {
                'group_es_mm': 0,
                'group_es_moa': 0,
                'group_es_x_mm': 0,
                'group_es_y_mm': 0,
                'mean_radius_mm': 0,
                'poi_x_mm': 0,
                'poi_y_mm': 0,
                'shots': 0,
                'avg_velocity_fps': 0,
                'sd_fps': 0,
                'es_fps': 0,
                'temperature_c': 0,
                'humidity_pct': 0,
                'pressure_hpa': 0,
                'wind_speed_ms': 0,
                'wind_direction': '',
                'light_conditions': '',
                'barrel_length_in': 0,
                'twist_rate': '',
                'bullet_lot': '',
                'powder_lot': '',
                'case_brand': '',
                'case_lot': '',
                'neck_turned': '',
                'brass_sizing': '',
                'bushing_size': 0,
                'shoulder_bump': 0,
                'primer_brand': '',
                'primer_model': '',
                'primer_lot': ''
            }
        
        # Extract relevant group data from the nested structure
        group_data = yaml_data.get('group', {})
        
        # Extract chrono data if available
        chrono_data = yaml_data.get('chrono', {})
        
        # Extract environment data if available
        environment_data = yaml_data.get('environment', {})
        
        # Extract platform data if available
        platform_data = yaml_data.get('platform', {})
        
        # Extract ammunition data if available
        ammo_data = yaml_data.get('ammo', {})
        bullet_data = ammo_data.get('bullet', {})
        powder_data = ammo_data.get('powder', {})
        case_data = ammo_data.get('case', {})
        primer_data = ammo_data.get('primer', {})
        
        return {
            'group_es_mm': group_data.get('group_es_mm', 0),
            'group_es_moa': group_data.get('group_es_moa', 0),
            'group_es_x_mm': group_data.get('group_es_x_mm', 0),
            'group_es_y_mm': group_data.get('group_es_y_mm', 0),
            'mean_radius_mm': group_data.get('mean_radius_mm', 0),
            'poi_x_mm': group_data.get('poi_x_mm', 0),
            'poi_y_mm': group_data.get('poi_y_mm', 0),
            'shots': group_data.get('shots', 0),
            'avg_velocity_fps': chrono_data.get('avg_velocity_fps', 0),
            'sd_fps': chrono_data.get('sd_fps', 0),
            'es_fps': chrono_data.get('es_fps', 0),
            'temperature_c': environment_data.get('temperature_c', 0),
            'humidity_pct': environment_data.get('humidity_percent', 0),
            'pressure_hpa': environment_data.get('pressure_hpa', 0),
            'wind_speed_ms': environment_data.get('wind_speed_mps', 0),
            'wind_direction': environment_data.get('wind_dir_deg', ''),
            'light_conditions': environment_data.get('weather', ''),
            
            # Platform data
            'barrel_length_in': platform_data.get('barrel_length_in', 0),
            'twist_rate': platform_data.get('twist_rate', ''),
            
            # Bullet data
            'bullet_lot': bullet_data.get('lot', ''),
            
            # Powder data
            'powder_lot': powder_data.get('lot', ''),
            
            # Case data
            'case_brand': case_data.get('brand', ''),
            'case_lot': case_data.get('lot', ''),
            'neck_turned': case_data.get('neck_turned', ''),
            'brass_sizing': case_data.get('brass_sizing', ''),
            'bushing_size': case_data.get('bushing_size', 0),
            'shoulder_bump': case_data.get('shoulder_bump', 0),
            
            # Primer data
            'primer_brand': primer_data.get('brand', ''),
            'primer_model': primer_data.get('model', ''),
            'primer_lot': primer_data.get('lot', '')
        }
    except Exception as e:
        return {
            'group_es_mm': 0,
            'group_es_moa': 0,
            'group_es_x_mm': 0,
            'group_es_y_mm': 0,
            'mean_radius_mm': 0,
            'poi_x_mm': 0,
            'poi_y_mm': 0,
            'shots': 0,
            'avg_velocity_fps': 0,
            'sd_fps': 0,
            'es_fps': 0,
            'temperature_c': 0,
            'humidity_pct': 0,
            'pressure_hpa': 0,
            'wind_speed_ms': 0,
            'wind_direction': '',
            'light_conditions': ''
        }


def load_chronograph_data(test_path):
    """
    Load chronograph data from CSV files
    
    Args:
        test_path (str): Path to the test directory
        
    Returns:
        dict: Dictionary containing chronograph data
    """
    # Find CSV files in the test directory
    csv_files = [f for f in os.listdir(test_path) if f.endswith('.csv') and 'Rifle_Cartridge' in f]
    
    if not csv_files:
        return {
            'avg_velocity_fps': 0,
            'sd_fps': 0,
            'es_fps': 0
        }
    
    try:
        # Use the first CSV file found
        csv_file = os.path.join(test_path, csv_files[0])
        
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Extract velocity data
        velocities = df['Velocity(fps)'].dropna().values
        
        if len(velocities) == 0:
            return {
                'avg_velocity_fps': 0,
                'sd_fps': 0,
                'es_fps': 0
            }
        
        # Calculate velocity statistics
        avg_velocity = np.mean(velocities)
        sd_velocity = np.std(velocities)
        es_velocity = np.max(velocities) - np.min(velocities)
        
        return {
            'avg_velocity_fps': avg_velocity,
            'sd_fps': sd_velocity,
            'es_fps': es_velocity
        }
    except Exception as e:
        return {
            'avg_velocity_fps': 0,
            'sd_fps': 0,
            'es_fps': 0
        }


def load_all_test_data(tests_dir=None):
    """
    Load data from all test directories
    
    Args:
        tests_dir (str, optional): Path to the directory containing test directories.
            If None, the path will be obtained from the settings manager.
        
    Returns:
        pandas.DataFrame: DataFrame containing all test data
    """
    # If tests_dir is not provided, get it from the settings manager
    if tests_dir is None:
        settings_manager = SettingsManager.get_instance()
        tests_dir = settings_manager.get_tests_directory()
    
    # Check if the directory exists
    if not os.path.isdir(tests_dir):
        print(f"Warning: Tests directory does not exist: {tests_dir}")
        return pd.DataFrame()
    
    # Get all test directories
    try:
        test_dirs = [os.path.join(tests_dir, d) for d in os.listdir(tests_dir) 
                    if os.path.isdir(os.path.join(tests_dir, d)) and not d.startswith('.')]
    except Exception as e:
        print(f"Error listing test directories: {e}")
        return pd.DataFrame()
    
    # Load data from each test directory
    test_data = []
    for test_dir in test_dirs:
        # Extract test info from the directory path
        test_info = extract_test_info_from_path(test_dir)
        
        # Load group data
        group_data = load_group_data(test_dir)
        
        # We'll use the group.yaml chrono data instead of the CSV data
        # as it's more reliable and consistent with what's shown in the View Test tab
        
        # Combine all data (group_data already contains chrono data)
        test_data.append({**test_info, **group_data})
    
    # Create a DataFrame from the test data
    df = pd.DataFrame(test_data)
    
    # Sort by date and powder charge
    df = df.sort_values(['date', 'powder_charge_gr'])
    
    return df


if __name__ == "__main__":
    # Example usage
    df = load_all_test_data()  # Uses the settings manager to get the tests directory
    print(df.head())
