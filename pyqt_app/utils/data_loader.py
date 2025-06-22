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
        
        # Extract numeric values with proper null checking
        distance_match = re.search(r'(\d+)', distance)
        distance_value = float(distance_match.group(1)) if distance_match else 0
        
        bullet_weight_match = re.search(r'(\d+\.?\d*)', bullet_weight)
        bullet_weight_value = float(bullet_weight_match.group(1)) if bullet_weight_match else 0
        
        powder_charge_match = re.search(r'(\d+\.?\d*)', powder_charge)
        powder_charge_value = float(powder_charge_match.group(1)) if powder_charge_match else 0
        
        coal_match = re.search(r'(\d+\.?\d*)', coal)
        coal_value = float(coal_match.group(1)) if coal_match else 0
        
        b2o_match = re.search(r'(\d+\.?\d*)', b2o)
        b2o_value = float(b2o_match.group(1)) if b2o_match else 0
        
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
    except (ValueError, IndexError, AttributeError) as e:
        # If parsing fails, return a minimal dictionary with the test_id
        print(f"Warning: Failed to parse test directory name: {dir_name}, error: {e}")
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
            'group_es_mm': None,
            'group_es_moa': None,
            'group_es_x_mm': None,
            'group_es_x_moa': None,
            'group_es_y_mm': None,
            'group_es_y_moa': None,
            'mean_radius_mm': None,
            'mean_radius_moa': None,
            'poi_x_mm': None,
            'poi_x_moa': None,
            'poi_y_mm': None,
            'poi_y_moa': None,
            'shots': None,
            'avg_velocity_fps': None,
            'sd_fps': None,
            'es_fps': None,
            'temperature_c': None,
            'humidity_pct': None,
            'pressure_hpa': None,
            'wind_speed_ms': None,
            'wind_direction': None,
            'light_conditions': None,
            'barrel_length_in': None,
            'twist_rate': None,
            'bullet_lot': None,
            'powder_lot': None,
            'powder_model': None,
            'case_brand': None,
            'case_lot': None,
            'neck_turned': None,
            'brass_sizing': None,
            'bushing_size': None,
            'shoulder_bump': None,
            'mandrel': None,
            'mandrel_size': None,
            'primer_brand': None,
            'primer_model': None,
            'primer_lot': None
        }
    
    try:
        with open(group_file, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # Check if yaml_data is None (empty file) or not a dictionary
        if yaml_data is None or not isinstance(yaml_data, dict):
            print(f"Warning: Invalid or empty YAML file: {group_file}")
            return {
                'group_es_mm': None,
                'group_es_moa': None,
                'group_es_x_mm': None,
                'group_es_x_moa': None,
                'group_es_y_mm': None,
                'group_es_y_moa': None,
                'mean_radius_mm': None,
                'mean_radius_moa': None,
                'poi_x_mm': None,
                'poi_x_moa': None,
                'poi_y_mm': None,
                'poi_y_moa': None,
                'shots': None,
                'avg_velocity_fps': None,
                'sd_fps': None,
                'es_fps': None,
                'temperature_c': None,
                'humidity_pct': None,
                'pressure_hpa': None,
                'wind_speed_ms': None,
                'wind_direction': None,
                'light_conditions': None,
                'barrel_length_in': None,
                'twist_rate': None,
                'bullet_lot': None,
                'powder_lot': None,
                'powder_model': None,
                'case_brand': None,
                'case_lot': None,
                'neck_turned': None,
                'brass_sizing': None,
                'bushing_size': None,
                'shoulder_bump': None,
                'primer_brand': None,
                'primer_model': None,
                'primer_lot': None
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
            # Main test parameters from YAML (override directory parsing)
            'date': yaml_data.get('date'),
            'distance_m': yaml_data.get('distance_m'),
            'calibre': platform_data.get('calibre'),
            'rifle': platform_data.get('rifle'),
            'bullet_brand': bullet_data.get('brand'),
            'bullet_model': bullet_data.get('model'),
            'bullet_weight_gr': bullet_data.get('weight_gr'),
            'powder_brand': powder_data.get('brand'),
            'powder_model': powder_data.get('model'),
            'powder_charge_gr': powder_data.get('charge_gr'),
            'coal_in': ammo_data.get('coal_in'),
            'b2o_in': ammo_data.get('b2o_in'),
            
            # Group/target results
            'group_es_mm': group_data.get('group_es_mm'),
            'group_es_moa': group_data.get('group_es_moa'),
            'group_es_x_mm': group_data.get('group_es_x_mm'),
            'group_es_x_moa': group_data.get('group_es_x_moa'),
            'group_es_y_mm': group_data.get('group_es_y_mm'),
            'group_es_y_moa': group_data.get('group_es_y_moa'),
            'mean_radius_mm': group_data.get('mean_radius_mm'),
            'mean_radius_moa': group_data.get('mean_radius_moa'),
            'poi_x_mm': group_data.get('poi_x_mm'),
            'poi_x_moa': group_data.get('poi_x_moa'),
            'poi_y_mm': group_data.get('poi_y_mm'),
            'poi_y_moa': group_data.get('poi_y_moa'),
            'shots': group_data.get('shots'),
            
            # Velocity/chrono results
            'avg_velocity_fps': chrono_data.get('avg_velocity_fps'),
            'sd_fps': chrono_data.get('sd_fps'),
            'es_fps': chrono_data.get('es_fps'),
            
            # Environment data
            'temperature_c': environment_data.get('temperature_c'),
            'humidity_pct': environment_data.get('humidity_percent'),
            'pressure_hpa': environment_data.get('pressure_hpa'),
            'wind_speed_ms': environment_data.get('wind_speed_mps'),
            'wind_direction': environment_data.get('wind_dir_deg'),
            'light_conditions': environment_data.get('weather'),
            
            # Platform data
            'barrel_length_in': platform_data.get('barrel_length_in'),
            'twist_rate': platform_data.get('twist_rate'),
            
            # Bullet data
            'bullet_lot': bullet_data.get('lot'),
            
            # Powder data
            'powder_lot': powder_data.get('lot'),
            
            # Case data
            'case_brand': case_data.get('brand'),
            'case_lot': case_data.get('lot'),
            'neck_turned': case_data.get('neck_turned'),
            'brass_sizing': case_data.get('brass_sizing'),
            'bushing_size': case_data.get('bushing_size'),
            'shoulder_bump': case_data.get('shoulder_bump'),
            'mandrel': case_data.get('mandrel'),
            'mandrel_size': case_data.get('mandrel_size'),
            
            # Primer data
            'primer_brand': primer_data.get('brand'),
            'primer_model': primer_data.get('model'),
            'primer_lot': primer_data.get('lot')
        }
    except Exception as e:
        print(f"Error loading group data from {group_file}: {e}")
        return {
            'group_es_mm': None,
            'group_es_moa': None,
            'group_es_x_mm': None,
            'group_es_x_moa': None,
            'group_es_y_mm': None,
            'group_es_y_moa': None,
            'mean_radius_mm': None,
            'mean_radius_moa': None,
            'poi_x_mm': None,
            'poi_x_moa': None,
            'poi_y_mm': None,
            'poi_y_moa': None,
            'shots': None,
            'avg_velocity_fps': None,
            'sd_fps': None,
            'es_fps': None,
            'temperature_c': None,
            'humidity_pct': None,
            'pressure_hpa': None,
            'wind_speed_ms': None,
            'wind_direction': None,
            'light_conditions': None,
            'barrel_length_in': None,
            'twist_rate': None,
            'bullet_lot': None,
            'powder_lot': None,
            'powder_model': None,
            'case_brand': None,
            'case_lot': None,
            'neck_turned': None,
            'brass_sizing': None,
            'bushing_size': None,
            'shoulder_bump': None,
            'primer_brand': None,
            'primer_model': None,
            'primer_lot': None
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
            'avg_velocity_fps': None,
            'sd_fps': None,
            'es_fps': None
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
                'avg_velocity_fps': None,
                'sd_fps': None,
                'es_fps': None
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
            'avg_velocity_fps': None,
            'sd_fps': None,
            'es_fps': None
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
    
    print(f"DEBUG: Loading test data from directory: {tests_dir}")
    
    # Check if the directory exists
    if not os.path.isdir(tests_dir):
        print(f"Warning: Tests directory does not exist: {tests_dir}")
        return pd.DataFrame()
    
    # Get all test directories
    try:
        test_dirs = [os.path.join(tests_dir, d) for d in os.listdir(tests_dir) 
                    if os.path.isdir(os.path.join(tests_dir, d)) and not d.startswith('.')]
        print(f"DEBUG: Found {len(test_dirs)} test directories")
    except Exception as e:
        print(f"Error listing test directories: {e}")
        return pd.DataFrame()
    
    # Load data from each test directory
    test_data = []
    successful_loads = 0
    failed_loads = 0
    
    for test_dir in test_dirs:
        try:
            # Extract test info from the directory path
            test_info = extract_test_info_from_path(test_dir)
            test_id = test_info['test_id']
            
            # Load group data
            group_data = load_group_data(test_dir)
            
            # Merge data with proper fallback logic
            # Start with directory-parsed data as base
            merged_data = test_info.copy()
            
            # Override with YAML data where available, but keep directory data as fallback
            for key, value in group_data.items():
                if value is not None:
                    merged_data[key] = value
                # If YAML value is None but we have a directory-parsed value, keep the directory value
                elif key in test_info and test_info[key] is not None:
                    merged_data[key] = test_info[key]
            
            # Ensure test_id is always preserved
            merged_data['test_id'] = test_id
            
            print(f"DEBUG: Successfully loaded test: {test_id}")
            test_data.append(merged_data)
            successful_loads += 1
            
        except Exception as e:
            print(f"Error loading test data from {test_dir}: {e}")
            failed_loads += 1
            continue
    
    print(f"DEBUG: Successfully loaded {successful_loads} tests, failed to load {failed_loads} tests")
    
    # Create a DataFrame from the test data
    if test_data:
        df = pd.DataFrame(test_data)
        
        # Sort by date and powder charge, handling None values properly
        try:
            # Fill NaN values for sorting
            df_sorted = df.copy()
            df_sorted['date'] = df_sorted['date'].fillna('1900-01-01')
            df_sorted['powder_charge_gr'] = pd.to_numeric(df_sorted['powder_charge_gr'], errors='coerce').fillna(0)
            df_sorted = df_sorted.sort_values(['date', 'powder_charge_gr'])
            
            # Use the sorted index to reorder the original dataframe
            df = df.loc[df_sorted.index]
        except Exception as e:
            print(f"Warning: Could not sort DataFrame: {e}")
        
        print(f"DEBUG: Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df
    else:
        print("DEBUG: No test data loaded, returning empty DataFrame")
        return pd.DataFrame()


if __name__ == "__main__":
    # Example usage
    df = load_all_test_data()  # Uses the settings manager to get the tests directory
    print(df.head())
