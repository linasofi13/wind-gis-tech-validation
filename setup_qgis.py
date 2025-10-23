"""
Script to configure PyQGIS in the current Python environment.
"""

import sys
import os

QGIS_PATH = r"C:\Program Files\QGIS 3.40.11"
QGIS_APP_PATH = os.path.join(QGIS_PATH, "apps", "qgis-ltr")
QGIS_PYTHON_PATH = os.path.join(QGIS_APP_PATH, "python")

if os.path.exists(QGIS_PATH):
    if QGIS_PYTHON_PATH not in sys.path:
        sys.path.insert(0, QGIS_PYTHON_PATH)
    
    plugins_path = os.path.join(QGIS_PYTHON_PATH, "plugins")
    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)
    
    os.environ['QGIS_PREFIX_PATH'] = QGIS_APP_PATH
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(QGIS_APP_PATH, "qtplugins")
    
    qgis_bin = os.path.join(QGIS_APP_PATH, "bin")
    if qgis_bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = qgis_bin + os.pathsep + os.environ.get('PATH', '')
    
    qt_bin = os.path.join(QGIS_APP_PATH, "bin")
    if qt_bin not in os.environ.get('PATH', ''):
        os.environ['PATH'] = qt_bin + os.pathsep + os.environ.get('PATH', '')
    
    print(" QGIS paths configured successfully!")
    print(f"QGIS Path: {QGIS_PATH}")
    print(f"QGIS App Path: {QGIS_APP_PATH}")
    print(f"QGIS Python Path: {QGIS_PYTHON_PATH}")
    
    try:
        import qgis
        from qgis.core import QgsApplication
        print(" PyQGIS imported successfully!")
        print(" QGIS core modules available!")
    except ImportError as e:
        print(f"PyQGIS import failed: {e}")
        
else:
    print(f"QGIS not found at {QGIS_PATH}")
    print("Please check your QGIS installation path.")
