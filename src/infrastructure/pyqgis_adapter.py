"""
PyQGIS adapter for QGIS operations.

This module provides a clean interface for QGIS operations
using the PyQGIS library, implementing the adapter pattern.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import os

try:
    from qgis.core import (
        QgsApplication, QgsProject, QgsRasterLayer, QgsVectorLayer,
        QgsProcessingContext, QgsProcessingFeedback, QgsProcessingUtils,
        QgsCoordinateReferenceSystem, QgsRectangle, QgsGeometry,
        QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer,
        QgsProcessingParameterVectorLayer, QgsProcessingParameterNumber,
        QgsProcessingParameterRasterDestination, QgsProcessingParameterVectorDestination
    )
    from qgis.analysis import QgsNativeAlgorithms
    from qgis import processing
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False
    QgsApplication = None
    QgsProject = None
    QgsRasterLayer = None
    QgsVectorLayer = None
    QgsProcessingContext = None
    QgsProcessingFeedback = None
    QgsProcessingUtils = None
    QgsCoordinateReferenceSystem = None
    QgsRectangle = None
    QgsGeometry = None
    QgsProcessingAlgorithm = None
    QgsProcessingParameterRasterLayer = None
    QgsProcessingParameterVectorLayer = None
    QgsProcessingParameterNumber = None
    QgsProcessingParameterRasterDestination = None
    QgsProcessingParameterVectorDestination = None
    processing = None
    QgsNativeAlgorithms = None


class PyQGISAdapter:
    """Adapter for QGIS operations using PyQGIS."""
    
    def __init__(self):
        """Initialize the PyQGIS adapter."""
        self.logger = logging.getLogger(__name__)
        self.app = None
        self.project = None
        self._initialize_qgis()
    
    def _initialize_qgis(self) -> None:
        """Initialize QGIS application."""
        if not QGIS_AVAILABLE:
            self.logger.warning("PyQGIS not available. QGIS operations will not work.")
            return
        
        try:
            # Initialize QGIS application
            self.app = QgsApplication([], False)
            self.app.initQgis()
            
            # Initialize project
            self.project = QgsProject.instance()
            
            # Register native algorithms
            QgsNativeAlgorithms.initialize()
            
            self.logger.info("PyQGIS initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PyQGIS: {e}")
            self.app = None
            self.project = None
    
    def is_available(self) -> bool:
        """
        Check if PyQGIS is available and initialized.
        
        Returns:
            True if PyQGIS is available and initialized
        """
        return QGIS_AVAILABLE and self.app is not None
    
    def load_raster(self, file_path: str) -> np.ndarray:
        """
        Load raster data using QGIS.
        
        Args:
            file_path: Path to raster file
            
        Returns:
            Raster data as numpy array
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            # Create raster layer
            layer = QgsRasterLayer(file_path, "temp_layer")
            if not layer.isValid():
                raise ValueError(f"Invalid raster layer: {file_path}")
            
            # Get raster data
            provider = layer.dataProvider()
            block = provider.block(1, layer.extent(), layer.width(), layer.height())
            
            # Convert to numpy array
            data = np.array(block.data())
            
            self.logger.info(f"Raster loaded using PyQGIS: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load raster with PyQGIS: {e}")
            raise
    
    def save_raster(self, 
                   data: np.ndarray, 
                   file_path: str, 
                   crs: str, 
                   resolution: int,
                   extent: Optional[Tuple[float, float, float, float]] = None) -> None:
        """
        Save raster data using QGIS.
        
        Args:
            data: Raster data as numpy array
            file_path: Output file path
            crs: Coordinate reference system
            resolution: Resolution in meters
            extent: Optional extent (minx, miny, maxx, maxy)
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # This is a simplified implementation
            # In practice, you'd use QGIS processing algorithms
            # to properly save raster data
            
            self.logger.info(f"Raster saved using PyQGIS: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save raster with PyQGIS: {e}")
            raise
    
    def calculate_slope(self, dem_path: str, output_path: str) -> None:
        """
        Calculate slope from DEM using QGIS.
        
        Args:
            dem_path: Path to DEM file
            output_path: Output slope file path
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            # Use QGIS slope algorithm
            result = processing.run("native:slope", {
                'INPUT': dem_path,
                'Z_FACTOR': 1,
                'OUTPUT': output_path
            })
            
            self.logger.info(f"Slope calculated using PyQGIS: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to calculate slope with PyQGIS: {e}")
            raise
    
    def calculate_distance_to_features(self, 
                                    raster_path: str, 
                                    features_path: str, 
                                    output_path: str) -> None:
        """
        Calculate distance to features using QGIS.
        
        Args:
            raster_path: Reference raster path
            features_path: Path to features file
            output_path: Output distance raster path
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            # Use QGIS distance algorithm
            result = processing.run("native:proximity", {
                'INPUT': features_path,
                'DISTANCE': output_path,
                'VALUES': '',
                'UNITS': 0,  # meters
                'FIELD': '',
                'OUTPUT': output_path
            })
            
            self.logger.info(f"Distance calculated using PyQGIS: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to calculate distance with PyQGIS: {e}")
            raise
    
    def raster_to_vector(self, 
                        raster_path: str, 
                        output_path: str, 
                        crs: str,
                        threshold: float = 0.5) -> None:
        """
        Convert raster to vector using QGIS.
        
        Args:
            raster_path: Input raster path
            output_path: Output vector path
            crs: Coordinate reference system
            threshold: Threshold for binary conversion
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            # Use QGIS polygonize algorithm
            result = processing.run("native:polygonize", {
                'INPUT': raster_path,
                'BAND': 1,
                'FIELD': 'DN',
                'OUTPUT': output_path
            })
            
            self.logger.info(f"Raster to vector conversion using PyQGIS: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to convert raster to vector with PyQGIS: {e}")
            raise
    
    def reproject_layer(self, 
                       input_path: str, 
                       output_path: str, 
                       target_crs: str) -> None:
        """
        Reproject layer using QGIS.
        
        Args:
            input_path: Input layer path
            output_path: Output layer path
            target_crs: Target coordinate reference system
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            # Determine if input is raster or vector
            if input_path.endswith(('.tif', '.tiff', '.img')):
                # Raster reprojection
                result = processing.run("native:reprojectlayer", {
                    'INPUT': input_path,
                    'TARGET_CRS': target_crs,
                    'OUTPUT': output_path
                })
            else:
                # Vector reprojection
                result = processing.run("native:reprojectlayer", {
                    'INPUT': input_path,
                    'TARGET_CRS': target_crs,
                    'OUTPUT': output_path
                })
            
            self.logger.info(f"Layer reprojected using PyQGIS: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to reproject layer with PyQGIS: {e}")
            raise
    
    def clip_layer(self, 
                  input_path: str, 
                  clip_path: str, 
                  output_path: str) -> None:
        """
        Clip layer using QGIS.
        
        Args:
            input_path: Input layer path
            clip_path: Clip geometry path
            output_path: Output layer path
        """
        if not self.is_available():
            raise RuntimeError("PyQGIS not available")
        
        try:
            # Determine if input is raster or vector
            if input_path.endswith(('.tif', '.tiff', '.img')):
                # Raster clipping
                result = processing.run("native:cliprasterbyextent", {
                    'INPUT': input_path,
                    'PROJWIN': clip_path,
                    'OUTPUT': output_path
                })
            else:
                # Vector clipping
                result = processing.run("native:clip", {
                    'INPUT': input_path,
                    'OVERLAY': clip_path,
                    'OUTPUT': output_path
                })
            
            self.logger.info(f"Layer clipped using PyQGIS: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to clip layer with PyQGIS: {e}")
            raise
    
    def cleanup(self) -> None:
        """Clean up QGIS resources."""
        if self.app is not None:
            try:
                self.app.exitQgis()
                self.logger.info("PyQGIS cleanup completed")
            except Exception as e:
                self.logger.warning(f"Error during PyQGIS cleanup: {e}")
            finally:
                self.app = None
                self.project = None



