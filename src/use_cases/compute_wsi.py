"""
Use case for computing Wind Suitability Index (WSI).

This module orchestrates the multicriteria analysis workflow
to calculate wind suitability and generate outputs.
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np

from ..domain.entities import (
    ProcessingConfig, WindSuitabilityResult, Criterion, EngineType
)
from ..domain.policies import (
    NormalizationPolicy, ScoringPolicy, ThresholdPolicy, ValidationPolicy
)
from ..infrastructure.metrics import MetricsCollector
from ..infrastructure.rasterio_adapter import RasterioAdapter
from ..infrastructure.pyqgis_adapter import PyQGISAdapter
from ..infrastructure.arcpy_adapter import ArcPyAdapter
from ..infrastructure.folium_map import FoliumMapGenerator


class ComputeWSIUseCase:
    """Use case for computing Wind Suitability Index."""
    
    def __init__(self, 
                 rasterio_adapter: RasterioAdapter,
                 pyqgis_adapter: Optional[PyQGISAdapter] = None,
                 arcpy_adapter: Optional[ArcPyAdapter] = None,
                 metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize the compute WSI use case.
        
        Args:
            rasterio_adapter: Rasterio adapter for basic raster operations
            pyqgis_adapter: Optional PyQGIS adapter for QGIS operations
            arcpy_adapter: Optional ArcPy adapter for ArcGIS operations
            metrics_collector: Optional metrics collector for performance monitoring
        """
        self.rasterio_adapter = rasterio_adapter
        self.pyqgis_adapter = pyqgis_adapter
        self.arcpy_adapter = arcpy_adapter
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, config: ProcessingConfig) -> WindSuitabilityResult:
        """
        Execute the WSI computation workflow.
        
        Args:
            config: Processing configuration
            
        Returns:
            Wind suitability analysis result
        """
        start_time = time.time()
        self.logger.info(f"Starting WSI computation with engine: {config.engine.value}")
        
        try:
            # Step 1: Load and validate input data
            self.logger.info("Loading input data...")
            input_data = self._load_input_data(config)
            
            # Step 2: Normalize criteria
            self.logger.info("Normalizing criteria...")
            normalized_layers = self._normalize_criteria(input_data, config.criteria)
            
            # Step 3: Calculate WSI
            self.logger.info("Calculating WSI...")
            wsi_array = self._calculate_wsi(normalized_layers, config.weight_scheme)
            
            # Step 4: Validate results
            self.logger.info("Validating results...")
            self._validate_results(wsi_array, input_data)
            
            # Step 5: Generate outputs
            self.logger.info("Generating outputs...")
            result = self._generate_outputs(wsi_array, config, start_time)
            
            self.logger.info("WSI computation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"WSI computation failed: {str(e)}")
            raise
    
    def _load_input_data(self, config: ProcessingConfig) -> Dict[str, np.ndarray]:
        """
        Load and prepare input data for analysis.
        
        Args:
            config: Processing configuration
            
        Returns:
            Dictionary of loaded data arrays
        """
        input_data = {}
        
        # Load AOI and set up processing extent
        aoi_geom = self.rasterio_adapter.load_geometry(config.aoi.geometry)
        self.rasterio_adapter.set_processing_extent(aoi_geom, config.aoi.crs)
        
        # Load each criterion
        for criterion in config.criteria:
            self.logger.info(f"Loading criterion: {criterion.name}")
            data = self.rasterio_adapter.load_raster(criterion.file_path)
            input_data[criterion.name] = data
        
        return input_data
    
    def _normalize_criteria(self, 
                          input_data: Dict[str, np.ndarray], 
                          criteria: List[Criterion]) -> Dict[str, np.ndarray]:
        """
        Normalize all criteria according to their specifications.
        
        Args:
            input_data: Raw input data arrays
            criteria: List of criterion specifications
            
        Returns:
            Dictionary of normalized arrays
        """
        normalized_layers = {}
        
        for criterion in criteria:
            if criterion.name not in input_data:
                raise ValueError(f"Criterion {criterion.name} not found in input data")
            
            raw_data = input_data[criterion.name]
            normalized_data = NormalizationPolicy.normalize_criterion(raw_data, criterion)
            normalized_layers[criterion.name] = normalized_data
            
            self.logger.info(f"Normalized {criterion.name} using {criterion.normalization_method}")
        
        return normalized_layers
    
    def _calculate_wsi(self, 
                      normalized_layers: Dict[str, np.ndarray], 
                      weight_scheme) -> np.ndarray:
        """
        Calculate Wind Suitability Index using weighted sum.
        
        Args:
            normalized_layers: Normalized criterion arrays
            weight_scheme: Weight scheme for criteria
            
        Returns:
            WSI array
        """
        weights = weight_scheme.get_all_weights()
        wsi_array = ScoringPolicy.weighted_sum(normalized_layers, weights)
        
        # Validate WSI result
        is_valid, error_msg = ValidationPolicy.validate_wsi_result(wsi_array)
        if not is_valid:
            raise ValueError(f"WSI validation failed: {error_msg}")
        
        return wsi_array
    
    def _validate_results(self, 
                         wsi_array: np.ndarray, 
                         input_data: Dict[str, np.ndarray]) -> None:
        """
        Validate the computed results.
        
        Args:
            wsi_array: Computed WSI array
            input_data: Original input data for validation
        """
        # Validate WSI
        is_valid, error_msg = ValidationPolicy.validate_wsi_result(wsi_array)
        if not is_valid:
            raise ValueError(f"WSI validation failed: {error_msg}")
        
        # Validate input data if available
        if "wind" in input_data:
            is_valid, error_msg = ValidationPolicy.validate_wind_data(input_data["wind"])
            if not is_valid:
                self.logger.warning(f"Wind data validation warning: {error_msg}")
        
        if "slope" in input_data:
            is_valid, error_msg = ValidationPolicy.validate_slope_data(input_data["slope"])
            if not is_valid:
                self.logger.warning(f"Slope data validation warning: {error_msg}")
    
    def _generate_outputs(self, 
                         wsi_array: np.ndarray, 
                         config: ProcessingConfig, 
                         start_time: float) -> WindSuitabilityResult:
        """
        Generate all output files and results.
        
        Args:
            wsi_array: Computed WSI array
            config: Processing configuration
            start_time: Start time for performance calculation
            
        Returns:
            Wind suitability result with all outputs
        """
        processing_time = time.time() - start_time
        memory_usage = self.metrics_collector.get_memory_usage()
        
        # Generate output paths
        output_dir = config.output_dir
        wsi_raster_path = f"{output_dir}/rasters/wsi.tif"
        candidate_sites_path = f"{output_dir}/vectors/candidate_sites.gpkg"
        interactive_map_path = f"{output_dir}/maps/wsi_map.html"
        
        # Save WSI raster
        self.logger.info("Saving WSI raster...")
        self.rasterio_adapter.save_raster(wsi_array, wsi_raster_path, 
                                         config.aoi.crs, config.resolution_m)
        
        # Generate candidate sites
        self.logger.info("Generating candidate sites...")
        self._generate_candidate_sites(wsi_array, config, candidate_sites_path)
        
        # Generate interactive map
        self.logger.info("Generating interactive map...")
        self._generate_interactive_map(wsi_raster_path, config, interactive_map_path)
        
        # Calculate metrics
        metrics = self._calculate_metrics(wsi_array, processing_time, memory_usage)
        
        return WindSuitabilityResult(
            wsi_raster_path=wsi_raster_path,
            candidate_sites_path=candidate_sites_path,
            interactive_map_path=interactive_map_path,
            metrics=metrics,
            processing_time=processing_time,
            memory_usage=memory_usage
        )
    
    def _generate_candidate_sites(self, 
                               wsi_array: np.ndarray, 
                               config: ProcessingConfig, 
                               output_path: str) -> None:
        """
        Generate candidate sites from top percentage of WSI values.
        
        Args:
            wsi_array: WSI array
            config: Processing configuration
            output_path: Output path for candidate sites
        """
        # Get top sites mask
        top_sites_mask = ThresholdPolicy.get_top_sites_mask(
            wsi_array, config.top_percent
        )
        
        # Convert to vector format
        if config.engine == EngineType.PYQGIS and self.pyqgis_adapter:
            self.pyqgis_adapter.raster_to_vector(
                top_sites_mask, output_path, config.aoi.crs
            )
        elif config.engine == EngineType.ARCPY and self.arcpy_adapter:
            self.arcpy_adapter.raster_to_vector(
                top_sites_mask, output_path, config.aoi.crs
            )
        else:
            # Use rasterio for basic vectorization
            self.rasterio_adapter.raster_to_vector(
                top_sites_mask, output_path, config.aoi.crs
            )
    
    def _generate_interactive_map(self, 
                                wsi_raster_path: str, 
                                config: ProcessingConfig, 
                                output_path: str) -> None:
        """
        Generate interactive map using Folium.
        
        Args:
            wsi_raster_path: Path to WSI raster
            config: Processing configuration
            output_path: Output path for interactive map
        """
        map_generator = FoliumMapGenerator()
        
        # Load WSI data for visualization
        wsi_data = self.rasterio_adapter.load_raster(wsi_raster_path)
        
        # Generate map
        map_generator.create_wsi_map(
            wsi_data=wsi_data,
            aoi_geometry=config.aoi.geometry,
            crs=config.aoi.crs,
            output_path=output_path,
            title="Wind Suitability Index"
        )
    
    def _calculate_metrics(self, 
                          wsi_array: np.ndarray, 
                          processing_time: float, 
                          memory_usage: float) -> Dict[str, float]:
        """
        Calculate performance and quality metrics.
        
        Args:
            wsi_array: WSI array
            processing_time: Processing time in seconds
            memory_usage: Memory usage in MB
            
        Returns:
            Dictionary of metrics
        """
        valid_values = wsi_array[~np.isnan(wsi_array)]
        
        metrics = {
            "processing_time_seconds": processing_time,
            "memory_usage_mb": memory_usage,
            "total_cells": len(wsi_array.flatten()),
            "valid_cells": len(valid_values),
            "nodata_percentage": (1 - len(valid_values) / len(wsi_array.flatten())) * 100,
            "wsi_mean": float(np.mean(valid_values)) if len(valid_values) > 0 else 0.0,
            "wsi_std": float(np.std(valid_values)) if len(valid_values) > 0 else 0.0,
            "wsi_min": float(np.min(valid_values)) if len(valid_values) > 0 else 0.0,
            "wsi_max": float(np.max(valid_values)) if len(valid_values) > 0 else 0.0,
            "viability_percentage": ScoringPolicy.calculate_viability_percentage(valid_values)
        }
        
        return metrics


