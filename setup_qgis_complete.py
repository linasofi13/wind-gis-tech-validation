"""
Complete QGIS environment setup for PyQGIS integration.
This script configures all necessary paths and environment variables.
"""

import sys
import os
from pathlib import Path

def setup_qgis_environment():
    """Setup complete QGIS environment for PyQGIS."""
    
    # QGIS installation path
    QGIS_PATH = r"C:\Program Files\QGIS 3.40.11"
    QGIS_APP_PATH = os.path.join(QGIS_PATH, "apps", "qgis-ltr")
    QGIS_PYTHON_PATH = os.path.join(QGIS_APP_PATH, "python")
    
    if not os.path.exists(QGIS_PATH):
        print(f"❌ QGIS not found at {QGIS_PATH}")
        return False
    
    print("🔧 Setting up QGIS environment...")
    
    # 1. Add QGIS Python path
    if QGIS_PYTHON_PATH not in sys.path:
        sys.path.insert(0, QGIS_PYTHON_PATH)
        print(f"✅ Added QGIS Python path: {QGIS_PYTHON_PATH}")
    
    # 2. Add QGIS plugins path
    plugins_path = os.path.join(QGIS_PYTHON_PATH, "plugins")
    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)
        print(f"✅ Added QGIS plugins path: {plugins_path}")
    
    # 3. Set QGIS environment variables
    os.environ['QGIS_PREFIX_PATH'] = QGIS_APP_PATH
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(QGIS_APP_PATH, "qtplugins")
    os.environ['QGIS_PLUGINPATH'] = plugins_path
    
    # 4. Add all necessary bin directories to PATH
    bin_dirs = [
        os.path.join(QGIS_APP_PATH, "bin"),
        os.path.join(QGIS_PATH, "bin"),
        os.path.join(QGIS_APP_PATH, "qtplugins"),
    ]
    
    current_path = os.environ.get('PATH', '')
    for bin_dir in bin_dirs:
        if os.path.exists(bin_dir) and bin_dir not in current_path:
            os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']
            print(f"✅ Added to PATH: {bin_dir}")
    
    # 5. Set Qt environment variables
    os.environ['QT_PLUGIN_PATH'] = os.path.join(QGIS_APP_PATH, "qtplugins")
    os.environ['QML2_IMPORT_PATH'] = os.path.join(QGIS_APP_PATH, "qml")
    
    print("✅ QGIS environment configured!")
    return True

def test_pyqgis():
    """Test PyQGIS import and functionality."""
    print("\n🧪 Testing PyQGIS...")
    
    try:
        # Test basic import
        import qgis
        print("✅ qgis module imported")
        
        # Test core import
        from qgis.core import QgsApplication
        print("✅ QgsApplication imported")
        
        # Test processing import
        from qgis import processing
        print("✅ processing module imported")
        
        # Test analysis import
        from qgis.analysis import QgsNativeAlgorithms
        print("✅ QgsNativeAlgorithms imported")
        
        print("🎉 PyQGIS is working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ PyQGIS import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PyQGIS error: {e}")
        return False

def main():
    """Main setup function."""
    print("🌬️  Complete QGIS Environment Setup")
    print("=" * 40)
    
    # Setup environment
    if not setup_qgis_environment():
        print("❌ Failed to setup QGIS environment")
        return False
    
    # Test PyQGIS
    if test_pyqgis():
        print("\n🎉 QGIS integration successful!")
        print("You can now use PyQGIS in your Python scripts.")
        return True
    else:
        print("\n⚠️  QGIS integration failed.")
        print("You can still use the project with Python (rasterio) engine.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
