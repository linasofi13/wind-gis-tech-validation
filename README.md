# Vento Wind GIS Technology Validation

🌬️ **A clean architecture implementation for wind energy suitability analysis using multicriteria decision making (MCDM) with Python, QGIS, and ArcGIS integration.**

## 🎯 Purpose

This proof-of-concept (PoC) validates the integration of Python with QGIS and ArcGIS for wind energy suitability analysis. The system applies multicriteria spatial analysis to generate a Wind Suitability Index (WSI) and provides a foundation for the future development of the Vento software application.

## 🏗️ Architecture

The project follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├─ domain/                # Pure business logic
│  ├─ entities.py         # Core business entities
│  └─ policies.py         # Business rules and policies
├─ use_cases/             # Application business logic
│  ├─ compute_wsi.py      # WSI computation workflow
│  └─ generate_report.py   # Report generation workflow
├─ infrastructure/        # External adapters
│  ├─ rasterio_adapter.py # Raster I/O operations
│  ├─ pyqgis_adapter.py   # QGIS integration
│  ├─ arcpy_adapter.py    # ArcGIS integration
│  ├─ folium_map.py       # Interactive map generation
│  └─ metrics.py          # Performance monitoring
└─ interface/
   └─ cli.py              # Command-line interface
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda (recommended) or pip
- Optional: QGIS or ArcGIS for advanced operations

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd wind-gis-tech-validation
   ```

2. **Create environment:**
   ```bash
   # Using conda (recommended)
   conda env create -f env/environment.yml
   conda activate vento-wind-gis
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -m src.interface.cli info
   ```

### Basic Usage

1. **Prepare your data:**
   - Place wind speed data in `data/raw/wind_100m.tif`
   - Place elevation data in `data/raw/dem.tif`
   - Place electrical grid data in `data/raw/grid_lines.gpkg`
   - Create AOI in `data/interim/aoi.geojson`

2. **Configure analysis:**
   - Edit `configs/wsi.yaml` with your parameters
   - Adjust weights, thresholds, and output settings

3. **Run analysis:**
   ```bash
   # Compute Wind Suitability Index
   python -m src.interface.cli compute-wsi configs/wsi.yaml
   
   # Generate viability report
   python -m src.interface.cli generate-report configs/wsi.yaml
   
   # Validate configuration
   python -m src.interface.cli validate-config configs/wsi.yaml
   ```

## 📊 Features

### Core Functionality

- **Multicriteria Analysis**: Weighted sum of normalized criteria
- **Multiple GIS Engines**: Python (rasterio), QGIS (PyQGIS), ArcGIS (ArcPy)
- **Interactive Visualization**: Folium maps with WSI visualization
- **Performance Monitoring**: Metrics collection and analysis
- **Report Generation**: HTML/PDF reports with statistics

### Supported Criteria

- **Wind Speed**: Primary factor for wind energy potential
- **Terrain Slope**: Affects turbine installation feasibility
- **Grid Distance**: Proximity to electrical infrastructure
- **Restrictions**: Protected areas, water bodies, urban zones

### Output Formats

- **Raster**: WSI as GeoTIFF (`wsi.tif`)
- **Vector**: Candidate sites as GeoPackage (`candidate_sites.gpkg`)
- **Interactive Map**: HTML with Folium (`wsi_map.html`)
- **Reports**: HTML/PDF with analysis results
- **Metrics**: JSON with performance data

## 🔧 Configuration

The system uses YAML configuration files for easy parameter adjustment:

```yaml
# configs/wsi.yaml
aoi: "data/interim/aoi.geojson"
crs: "EPSG:3857"
resolution_m: 100

layers:
  wind: "data/raw/wind_100m.tif"
  dem: "data/raw/dem.tif"
  grid: "data/raw/grid_lines.gpkg"

weights:
  wind: 0.6
  slope: 0.2
  grid_distance: 0.2

engine: "python"  # python, pyqgis, or arcpy
```

## 📈 Outputs

### Generated Files

- `outputs/rasters/wsi.tif` - Wind Suitability Index raster
- `outputs/vectors/candidate_sites.gpkg` - Top suitable sites
- `outputs/maps/wsi_map.html` - Interactive visualization
- `outputs/reports/viability_report.html` - Analysis report
- `outputs/reports/metrics.json` - Performance metrics
- `outputs/reports/history.csv` - Report history

### Metrics Collected

- Processing time and memory usage
- Data coverage and quality
- WSI statistics (mean, std, min, max)
- Viability percentages
- File sizes and formats

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_mcdm.py -v
```

## 📚 Documentation

- **[Methodology](docs/methodology.md)**: Detailed analysis methodology
- **[Vento Criteria](docs/vento-criteria.md)**: Technology comparison matrix
- **[Architecture Decision Records](docs/adr/)**: Design decisions and rationale

## 🔬 Research Context

This PoC supports wind energy technology surveillance by:

1. **Validating GIS Integration**: Comparing Python, QGIS, and ArcGIS performance
2. **Assessing Usability**: Evaluating ease of integration and deployment
3. **Measuring Accuracy**: Validating spatial analysis precision
4. **Documenting Workflows**: Creating reproducible analysis pipelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is part of the Vento initiative for wind energy technology surveillance.

## 🆘 Support

For questions or issues:

1. Check the documentation in `docs/`
2. Review the test cases in `tests/`
3. Open an issue on the repository
4. Contact the Vento team

---

**Vento Team** - Wind Energy Technology Surveillance Initiative