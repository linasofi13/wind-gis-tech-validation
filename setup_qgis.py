"""
Script to configure PyQGIS in the current Python environment.
Run this script to enable QGIS integration.
"""

import sys
import os

# QGIS installation path
QGIS_PATH = r"C:\Program Files\QGIS 3.40.11"
QGIS_APP_PATH = os.path.join(QGIS_PATH, "apps", "qgis-ltr")
QGIS_PYTHON_PATH = os.path.join(QGIS_APP_PATH, "python")

# Add QGIS paths to Python path
if os.path.exists(QGIS_PATH):
    # Add QGIS Python path
    if QGIS_PYTHON_PATH not in sys.path:
        sys.path.insert(0, QGIS_PYTHON_PATH)
    
    # Add QGIS plugins path
    plugins_path = os.path.join(QGIS_PYTHON_PATH, "plugins")
    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)
    
    # Set QGIS environment variables
    os.environ['QGIS_PREFIX_PATH'] = QGIS_APP_PATH
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(QGIS_APP_PATH, "qtplugins")
    
    # Add QGIS bin directory to PATH for DLLs
    qgis_bin = os.path.join(QGIS_APP_PATH, "bin")
    if qgis_bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = qgis_bin + os.pathsep + os.environ.get('PATH', '')
    
    # Add Qt bin directory to PATH
    qt_bin = os.path.join(QGIS_APP_PATH, "bin")
    if qt_bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = qt_bin + os.pathsep + os.environ.get('PATH', '')
    
    print("✅ QGIS paths configured successfully!")
    print(f"QGIS Path: {QGIS_PATH}")
    print(f"QGIS App Path: {QGIS_APP_PATH}")
    print(f"QGIS Python Path: {QGIS_PYTHON_PATH}")
    
    # Test PyQGIS import
    try:
        import qgis
        from qgis.core import QgsApplication
        print("✅ PyQGIS imported successfully!")
        print("✅ QGIS core modules available!")
    except ImportError as e:
        print(f"❌ PyQGIS import failed: {e}")
        
else:
    print(f"❌ QGIS not found at {QGIS_PATH}")
    print("Please check your QGIS installation path.")
