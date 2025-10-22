"""
ArcPy adapter for ArcGIS operations.

This module provides a clean interface for ArcGIS operations
using the ArcPy library, implementing the adapter pattern.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import os

try:
    import arcpy
    from arcpy import env
    from arcpy.sa import *
    ARCPY_AVAILABLE = True
except ImportError:
    ARCPY_AVAILABLE = False
    arcpy = None
    env = None


class ArcPyAdapter:
    """Adapter for ArcGIS operations using ArcPy."""
    
    def __init__(self):
        """Initialize the ArcPy adapter."""
        self.logger = logging.getLogger(__name__)
        self._initialize_arcpy()
    
    def _initialize_arcpy(self) -> None:
        """Initialize ArcPy environment."""
        if not ARCPY_AVAILABLE:
            self.logger.warning("ArcPy not available. ArcGIS operations will not work.")
            return
        
        try:
            # Set up ArcPy environment
            env.overwriteOutput = True
            env.parallelProcessingFactor = "100%"
            
            self.logger.info("ArcPy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ArcPy: {e}")
    
    def is_available(self) -> bool:
        """
        Check if ArcPy is available and initialized.
        
        Returns:
            True if ArcPy is available and initialized
        """
        return ARCPY_AVAILABLE
    
    def load_raster(self, file_path: str) -> np.ndarray:
        """
        Load raster data using ArcPy.
        
        Args:
            file_path: Path to raster file
            
        Returns:
            Raster data as numpy array
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Load raster using ArcPy
            raster = Raster(file_path)
            
            # Convert to numpy array
            data = arcpy.RasterToNumPyArray(raster)
            
            self.logger.info(f"Raster loaded using ArcPy: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load raster with ArcPy: {e}")
            raise
    
    def save_raster(self, 
                   data: np.ndarray, 
                   file_path: str, 
                   crs: str, 
                   resolution: int,
                   extent: Optional[Tuple[float, float, float, float]] = None) -> None:
        """
        Save raster data using ArcPy.
        
        Args:
            data: Raster data as numpy array
            file_path: Output file path
            crs: Coordinate reference system
            resolution: Resolution in meters
            extent: Optional extent (minx, miny, maxx, maxy)
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Create spatial reference
            sr = arcpy.SpatialReference(crs)
            
            # Set extent if provided
            if extent:
                env.extent = arcpy.Extent(extent[0], extent[1], extent[2], extent[3])
            
            # Convert numpy array to raster
            raster = arcpy.NumPyArrayToRaster(data, sr)
            
            # Save raster
            raster.save(file_path)
            
            self.logger.info(f"Raster saved using ArcPy: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save raster with ArcPy: {e}")
            raise
    
    def calculate_slope(self, dem_path: str, output_path: str) -> None:
        """
        Calculate slope from DEM using ArcPy.
        
        Args:
            dem_path: Path to DEM file
            output_path: Output slope file path
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Calculate slope using ArcPy
            slope_raster = Slope(dem_path, "DEGREE", 1)
            slope_raster.save(output_path)
            
            self.logger.info(f"Slope calculated using ArcPy: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to calculate slope with ArcPy: {e}")
            raise
    
    def calculate_distance_to_features(self, 
                                    raster_path: str, 
                                    features_path: str, 
                                    output_path: str) -> None:
        """
        Calculate distance to features using ArcPy.
        
        Args:
            raster_path: Reference raster path
            features_path: Path to features file
            output_path: Output distance raster path
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Calculate distance using ArcPy
            distance_raster = EucDistance(features_path)
            distance_raster.save(output_path)
            
            self.logger.info(f"Distance calculated using ArcPy: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to calculate distance with ArcPy: {e}")
            raise
    
    def raster_to_vector(self, 
                        raster_path: str, 
                        output_path: str, 
                        crs: str,
                        threshold: float = 0.5) -> None:
        """
        Convert raster to vector using ArcPy.
        
        Args:
            raster_path: Input raster path
            output_path: Output vector path
            crs: Coordinate reference system
            threshold: Threshold for binary conversion
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Convert raster to polygon
            arcpy.RasterToPolygon_conversion(
                raster_path,
                output_path,
                "NO_SIMPLIFY",
                "VALUE"
            )
            
            self.logger.info(f"Raster to vector conversion using ArcPy: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to convert raster to vector with ArcPy: {e}")
            raise
    
    def reproject_layer(self, 
                       input_path: str, 
                       output_path: str, 
                       target_crs: str) -> None:
        """
        Reproject layer using ArcPy.
        
        Args:
            input_path: Input layer path
            output_path: Output layer path
            target_crs: Target coordinate reference system
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Create spatial reference
            sr = arcpy.SpatialReference(target_crs)
            
            # Determine if input is raster or vector
            if input_path.endswith(('.tif', '.tiff', '.img')):
                # Raster reprojection
                arcpy.ProjectRaster_management(input_path, output_path, sr)
            else:
                # Vector reprojection
                arcpy.Project_management(input_path, output_path, sr)
            
            self.logger.info(f"Layer reprojected using ArcPy: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to reproject layer with ArcPy: {e}")
            raise
    
    def clip_layer(self, 
                  input_path: str, 
                  clip_path: str, 
                  output_path: str) -> None:
        """
        Clip layer using ArcPy.
        
        Args:
            input_path: Input layer path
            clip_path: Clip geometry path
            output_path: Output layer path
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Determine if input is raster or vector
            if input_path.endswith(('.tif', '.tiff', '.img')):
                # Raster clipping
                arcpy.Clip_management(input_path, "", output_path, clip_path)
            else:
                # Vector clipping
                arcpy.Clip_analysis(input_path, clip_path, output_path)
            
            self.logger.info(f"Layer clipped using ArcPy: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to clip layer with ArcPy: {e}")
            raise
    
    def calculate_statistics(self, raster_path: str) -> Dict[str, float]:
        """
        Calculate raster statistics using ArcPy.
        
        Args:
            raster_path: Path to raster file
            
        Returns:
            Dictionary with statistics
        """
        if not self.is_available():
            raise RuntimeError("ArcPy not available")
        
        try:
            # Get raster properties
            raster = Raster(raster_path)
            
            # Calculate statistics
            stats = arcpy.GetRasterProperties_management(
                raster_path, 
                "ALL"
            )
            
            return {
                "minimum": float(stats.getOutput(0)),
                "maximum": float(stats.getOutput(1)),
                "mean": float(stats.getOutput(2)),
                "std": float(stats.getOutput(3))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics with ArcPy: {e}")
            raise
    
    def cleanup(self) -> None:
        """Clean up ArcPy resources."""
        if self.is_available():
            try:
                # Clear ArcPy environment
                env.overwriteOutput = False
                self.logger.info("ArcPy cleanup completed")
            except Exception as e:
                self.logger.warning(f"Error during ArcPy cleanup: {e}")



