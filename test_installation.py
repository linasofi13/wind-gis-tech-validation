"""
Test script to verify Vento installation and dependencies.

This script checks if all required packages are installed correctly
and the basic functionality is working.
"""

import sys
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} is not compatible. Requires Python 3.8+")
        return False

def test_core_dependencies():
    """Test core scientific computing dependencies."""
    print("\n📊 Testing core dependencies...")
    core_packages = [
        'numpy', 'scipy', 'pandas', 'geopandas',
        'rasterio', 'shapely', 'fiona', 'pyproj',
        'folium', 'matplotlib', 'seaborn'
    ]
    
    success = True
    for package in core_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            success = False
    
    return success

def test_cli_dependencies():
    """Test CLI and utility dependencies."""
    print("\n🖥️  Testing CLI dependencies...")
    cli_packages = [
        'typer', 'yaml', 'psutil', 'jinja2', 'reportlab'
    ]
    
    success = True
    for package in cli_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            success = False
    
    return success

def test_development_dependencies():
    """Test development and testing dependencies."""
    print("\n🧪 Testing development dependencies...")
    dev_packages = [
        'pytest', 'pytest_cov', 'black', 'flake8'
    ]
    
    success = True
    for package in dev_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} - not installed (optional)")
    
    return True  # Development packages are optional

def test_optional_dependencies():
    """Test optional dependencies."""
    print("\n🔧 Testing optional dependencies...")
    optional_packages = [
        'pydeck', 'streamlit'
    ]
    
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} - not installed (optional)")

def test_vento_imports():
    """Test Vento project imports."""
    print("\n🌬️  Testing Vento project imports...")
    
    try:
        from src.domain.entities import AOI, Criterion, WeightScheme
        print("✅ Domain entities")
    except ImportError as e:
        print(f"❌ Domain entities: {e}")
        return False
    
    try:
        from src.domain.policies import NormalizationPolicy, ScoringPolicy
        print("✅ Domain policies")
    except ImportError as e:
        print(f"❌ Domain policies: {e}")
        return False
    
    try:
        from src.use_cases.compute_wsi import ComputeWSIUseCase
        print("✅ Use cases")
    except ImportError as e:
        print(f"❌ Use cases: {e}")
        return False
    
    try:
        from src.infrastructure.rasterio_adapter import RasterioAdapter
        print("✅ Infrastructure adapters")
    except ImportError as e:
        print(f"❌ Infrastructure adapters: {e}")
        return False
    
    try:
        from src.interface.cli import app
        print("✅ CLI interface")
    except ImportError as e:
        print(f"❌ CLI interface: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from src.domain.entities import AOI, Criterion, WeightScheme
        from src.domain.policies import NormalizationPolicy
        import numpy as np
        
        # Test AOI creation
        aoi = AOI(geometry="test.geojson", crs="EPSG:4326")
        print("✅ AOI entity creation")
        
        # Test criterion creation
        criterion = Criterion(
            name="wind",
            weight=0.6,
            file_path="wind.tif"
        )
        print("✅ Criterion entity creation")
        
        # Test weight scheme creation
        weights = WeightScheme(wind=0.6, slope=0.2, grid_distance=0.2)
        print("✅ Weight scheme creation")
        
        # Test normalization
        values = np.array([1, 2, 3, 4, 5])
        normalized = NormalizationPolicy.minmax_normalize(values, is_benefit=True)
        expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        if np.allclose(normalized, expected):
            print("✅ Normalization policy")
        else:
            print("❌ Normalization policy - values don't match")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_file_structure():
    """Test project file structure."""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "src/__init__.py",
        "src/domain/__init__.py",
        "src/use_cases/__init__.py",
        "src/infrastructure/__init__.py",
        "src/interface/__init__.py",
        "configs/wsi.yaml",
        "requirements.txt",
        "README.md"
    ]
    
    success = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - not found")
            success = False
    
    return success

def main():
    """Main test function."""
    print("🌬️  Vento Installation Verification")
    print("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Dependencies", test_core_dependencies),
        ("CLI Dependencies", test_cli_dependencies),
        ("Development Dependencies", test_development_dependencies),
        ("Optional Dependencies", test_optional_dependencies),
        ("Vento Imports", test_vento_imports),
        ("Basic Functionality", test_basic_functionality),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is successful.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


