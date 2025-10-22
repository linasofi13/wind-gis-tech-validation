"""
Command Line Interface for Vento Wind GIS Technology Validation.

This module provides a CLI interface using Typer for running
wind suitability analysis and report generation.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    from typer import Typer, Option, Argument
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    typer = None
    Typer = None
    Option = None
    Argument = None

from ..domain.entities import (
    AOI, Criterion, WeightScheme, ReportSpec, ProcessingConfig, EngineType
)
from ..use_cases.compute_wsi import ComputeWSIUseCase
from ..use_cases.generate_report import GenerateReportUseCase
from ..infrastructure.rasterio_adapter import RasterioAdapter
from ..infrastructure.pyqgis_adapter import PyQGISAdapter
from ..infrastructure.arcpy_adapter import ArcPyAdapter
from ..infrastructure.metrics import MetricsCollector
from ..infrastructure.folium_map import FoliumMapGenerator


# Initialize Typer app
if TYPER_AVAILABLE:
    app = Typer(
        name="vento",
        help="Vento Wind GIS Technology Validation - Wind Suitability Analysis",
        add_completion=False
    )
else:
    app = None


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('vento.log')
        ]
    )


def load_config(config_path: str) -> ProcessingConfig:
    """
    Load processing configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Processing configuration object
    """
    import yaml
    
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Parse AOI
        aoi = AOI(
            geometry=config_data['aoi'],
            crs=config_data['crs'],
            name=config_data.get('aoi_name', 'Unnamed AOI')
        )
        
        # Parse criteria
        criteria = []
        for layer_name, layer_config in config_data['layers'].items():
            if layer_name in ['wind', 'slope', 'grid']:
                criterion = Criterion(
                    name=layer_name,
                    weight=config_data['weights'].get(layer_name, 0.0),
                    file_path=layer_config,
                    is_benefit=layer_name == 'wind',  # Wind is benefit, others are cost
                    normalization_method='minmax'
                )
                criteria.append(criterion)
        
        # Parse weight scheme
        weight_scheme = WeightScheme(
            wind=config_data['weights']['wind'],
            slope=config_data['weights']['slope'],
            grid_distance=config_data['weights']['grid_distance']
        )
        
        # Parse report spec
        report_spec = ReportSpec(
            output_format=config_data.get('output_format', 'html'),
            include_metrics=True,
            include_map=True,
            include_charts=True,
            language=config_data.get('language', 'en')
        )
        
        # Parse engine
        engine = EngineType(config_data.get('engine', 'python'))
        
        # Create processing config
        config = ProcessingConfig(
            aoi=aoi,
            criteria=criteria,
            weight_scheme=weight_scheme,
            report_spec=report_spec,
            engine=engine,
            resolution_m=config_data.get('resolution_m', 100),
            top_percent=config_data.get('thresholds', {}).get('top_percent', 0.15),
            output_dir=config_data.get('output_dir', 'outputs')
        )
        
        return config
        
    except Exception as e:
        raise ValueError(f"Failed to load configuration from {config_path}: {e}")


def create_adapters(engine: EngineType) -> tuple:
    """
    Create appropriate adapters based on engine type.
    
    Args:
        engine: GIS engine type
        
    Returns:
        Tuple of (rasterio_adapter, pyqgis_adapter, arcpy_adapter, metrics_collector)
    """
    # Always create rasterio adapter
    rasterio_adapter = RasterioAdapter()
    
    # Create engine-specific adapters
    pyqgis_adapter = None
    arcpy_adapter = None
    
    if engine == EngineType.PYQGIS:
        pyqgis_adapter = PyQGISAdapter()
        if not pyqgis_adapter.is_available():
            raise RuntimeError("PyQGIS not available")
    elif engine == EngineType.ARCPY:
        arcpy_adapter = ArcPyAdapter()
        if not arcpy_adapter.is_available():
            raise RuntimeError("ArcPy not available")
    
    # Create metrics collector
    metrics_collector = MetricsCollector()
    
    return rasterio_adapter, pyqgis_adapter, arcpy_adapter, metrics_collector


if TYPER_AVAILABLE:
    @app.command()
    def compute_wsi(
        config_path: str = Argument(..., help="Path to configuration YAML file"),
        verbose: bool = Option(False, "--verbose", "-v", help="Enable verbose logging"),
        output_dir: Optional[str] = Option(None, "--output-dir", "-o", help="Override output directory")
    ):
        """
        Compute Wind Suitability Index (WSI) using multicriteria analysis.
        
        This command performs the complete WSI computation workflow including:
        - Loading and validating input data
        - Normalizing criteria
        - Calculating WSI using weighted sum
        - Generating outputs (raster, vector, interactive map)
        - Collecting performance metrics
        """
        setup_logging(verbose)
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Starting WSI computation...")
            
            # Load configuration
            config = load_config(config_path)
            
            # Override output directory if provided
            if output_dir:
                config.output_dir = output_dir
            
            # Create adapters
            rasterio_adapter, pyqgis_adapter, arcpy_adapter, metrics_collector = create_adapters(config.engine)
            
            # Create use case
            compute_wsi_use_case = ComputeWSIUseCase(
                rasterio_adapter=rasterio_adapter,
                pyqgis_adapter=pyqgis_adapter,
                arcpy_adapter=arcpy_adapter,
                metrics_collector=metrics_collector
            )
            
            # Start monitoring
            metrics_collector.start_monitoring()
            
            # Execute WSI computation
            result = compute_wsi_use_case.execute(config)
            
            # Stop monitoring
            metrics_collector.stop_monitoring()
            
            # Save metrics
            metrics_path = f"{config.output_dir}/reports/metrics.json"
            metrics_collector.save_metrics(metrics_path)
            
            # Print results
            print(f"\n✅ WSI computation completed successfully!")
            print(f"📊 Processing time: {result.processing_time:.2f} seconds")
            print(f"💾 Memory usage: {result.memory_usage:.1f} MB")
            print(f"🗺️  WSI raster: {result.wsi_raster_path}")
            print(f"📍 Candidate sites: {result.candidate_sites_path}")
            print(f"🌐 Interactive map: {result.interactive_map_path}")
            print(f"📈 Metrics: {metrics_path}")
            
        except Exception as e:
            logger.error(f"WSI computation failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
        finally:
            # Cleanup adapters
            if pyqgis_adapter:
                pyqgis_adapter.cleanup()
            if arcpy_adapter:
                arcpy_adapter.cleanup()


    @app.command()
    def generate_report(
        config_path: str = Argument(..., help="Path to configuration YAML file"),
        wsi_result_path: Optional[str] = Option(None, "--wsi-result", help="Path to WSI result JSON file"),
        verbose: bool = Option(False, "--verbose", "-v", help="Enable verbose logging")
    ):
        """
        Generate wind viability report from WSI results.
        
        This command creates HTML/PDF reports with:
        - Viability analysis and statistics
        - Interactive map integration
        - Performance metrics
        - Report history tracking
        """
        setup_logging(verbose)
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Starting report generation...")
            
            # Load configuration
            config = load_config(config_path)
            
            # Create adapters
            rasterio_adapter, pyqgis_adapter, arcpy_adapter, metrics_collector = create_adapters(config.engine)
            
            # Create use case
            generate_report_use_case = GenerateReportUseCase(
                rasterio_adapter=rasterio_adapter,
                metrics_collector=metrics_collector
            )
            
            # For now, we'll create a mock WSI result
            # In practice, you'd load this from the WSI computation result
            from ..domain.entities import WindSuitabilityResult
            
            wsi_result = WindSuitabilityResult(
                wsi_raster_path=f"{config.output_dir}/rasters/wsi.tif",
                candidate_sites_path=f"{config.output_dir}/vectors/candidate_sites.gpkg",
                interactive_map_path=f"{config.output_dir}/maps/wsi_map.html",
                metrics={},
                processing_time=0.0,
                memory_usage=0.0
            )
            
            # Execute report generation
            report = generate_report_use_case.execute(config, wsi_result)
            
            # Print results
            print(f"\n✅ Report generation completed successfully!")
            print(f"📋 Report ID: {report.report_id}")
            print(f"📊 Viability: {report.viability_percentage:.1f}%")
            print(f"📏 Total area: {report.total_area:.1f} km²")
            print(f"🎯 Suitable area: {report.suitable_area:.1f} km²")
            print(f"📍 Top sites: {report.top_sites_count:,} cells")
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)


    @app.command()
    def validate_config(
        config_path: str = Argument(..., help="Path to configuration YAML file"),
        verbose: bool = Option(False, "--verbose", "-v", help="Enable verbose logging")
    ):
        """
        Validate configuration file and check data availability.
        
        This command validates:
        - Configuration file syntax and structure
        - Data file existence and accessibility
        - GIS engine availability
        - Output directory permissions
        """
        setup_logging(verbose)
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Validating configuration...")
            
            # Load configuration
            config = load_config(config_path)
            
            print(f"\n✅ Configuration validation completed!")
            print(f"🗺️  AOI: {config.aoi.name}")
            print(f"🔧 Engine: {config.engine.value}")
            print(f"📏 Resolution: {config.resolution_m} meters")
            print(f"📊 Top percent: {config.top_percent:.1%}")
            
            # Check data files
            print(f"\n📁 Data files:")
            for criterion in config.criteria:
                file_path = Path(criterion.file_path)
                if file_path.exists():
                    print(f"  ✅ {criterion.name}: {criterion.file_path}")
                else:
                    print(f"  ❌ {criterion.name}: {criterion.file_path} (not found)")
            
            # Check engine availability
            print(f"\n🔧 Engine availability:")
            if config.engine == EngineType.PYQGIS:
                pyqgis_adapter = PyQGISAdapter()
                if pyqgis_adapter.is_available():
                    print(f"  ✅ PyQGIS: Available")
                else:
                    print(f"  ❌ PyQGIS: Not available")
            elif config.engine == EngineType.ARCPY:
                arcpy_adapter = ArcPyAdapter()
                if arcpy_adapter.is_available():
                    print(f"  ✅ ArcPy: Available")
                else:
                    print(f"  ❌ ArcPy: Not available")
            else:
                print(f"  ✅ Python: Available (rasterio)")
            
            # Check output directory
            output_dir = Path(config.output_dir)
            if output_dir.exists() or output_dir.parent.exists():
                print(f"  ✅ Output directory: {config.output_dir}")
            else:
                print(f"  ❌ Output directory: {config.output_dir} (cannot create)")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)


    @app.command()
    def info():
        """
        Display information about the Vento system.
        
        Shows version, available engines, and system information.
        """
        print("🌬️  Vento Wind GIS Technology Validation")
        print("=" * 50)
        print(f"Version: 0.1.0")
        print(f"Purpose: Wind suitability analysis using multicriteria decision making")
        print(f"Architecture: Clean Architecture with domain-driven design")
        print()
        
        print("🔧 Available Engines:")
        print("  • Python (rasterio) - Always available")
        
        # Check PyQGIS
        try:
            pyqgis_adapter = PyQGISAdapter()
            if pyqgis_adapter.is_available():
                print("  • PyQGIS - Available")
            else:
                print("  • PyQGIS - Not available")
        except:
            print("  • PyQGIS - Not available")
        
        # Check ArcPy
        try:
            arcpy_adapter = ArcPyAdapter()
            if arcpy_adapter.is_available():
                print("  • ArcPy - Available")
            else:
                print("  • ArcPy - Not available")
        except:
            print("  • ArcPy - Not available")
        
        print()
        print("📚 Commands:")
        print("  • compute-wsi    - Run wind suitability analysis")
        print("  • generate-report - Generate viability reports")
        print("  • validate-config - Validate configuration and data")
        print("  • info           - Show this information")
        print()
        print("📖 For more information, see the documentation in docs/")


    def main():
        """Main entry point for the CLI."""
        if not TYPER_AVAILABLE:
            print("❌ Error: Typer is not available. Please install it with: pip install typer")
            sys.exit(1)
        
        app()


if __name__ == "__main__":
    main()



