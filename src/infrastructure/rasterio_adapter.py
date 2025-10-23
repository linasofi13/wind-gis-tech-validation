"""
Rasterio adapter for raster operations.

This module provides a clean interface for raster operations
using the rasterio library, implementing the adapter pattern.
"""

import rasterio
import rasterio.mask
import rasterio.warp
import rasterio.features
import numpy as np
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import geopandas as gpd
from shapely.geometry import shape
import os


class RasterioAdapter:
    """Adapter for raster operations using rasterio."""
    
    def __init__(self):
        """Initialize the rasterio adapter."""
        self.logger = logging.getLogger(__name__)
        self.processing_extent = None
        self.processing_crs = None
    
    def load_raster(self, file_path: str) -> np.ndarray:
        """
        Load raster data from file.
        
        Args:
            file_path: Path to raster file
            
        Returns:
            Raster data as numpy array
        """
        try:
            with rasterio.open(file_path) as src:
                # If processing extent is set, crop to extent
                if self.processing_extent is not None:
                    data, _ = rasterio.mask.mask(src, [self.processing_extent], crop=True)
                    return data[0]  # Remove band dimension
                else:
                    return src.read(1)  # Read first band
        except Exception as e:
            self.logger.error(f"Failed to load raster {file_path}: {e}")
            raise
    
    def save_raster(self, 
                   data: np.ndarray, 
                   file_path: str, 
                   crs: str, 
                   resolution: int,
                   transform: Optional[rasterio.transform.Affine] = None) -> None:
        """
        Save raster data to file.
        
        Args:
            data: Raster data as numpy array
            file_path: Output file path
            crs: Coordinate reference system
            resolution: Resolution in meters
            transform: Optional transform (will be calculated if not provided)
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Calculate transform if not provided
            if transform is None:
                transform = rasterio.transform.from_bounds(
                    *self._get_bounds_from_extent(), 
                    data.shape[1], 
                    data.shape[0]
                )
            
            # Get CRS object
            if isinstance(crs, str):
                crs_obj = rasterio.crs.CRS.from_string(crs)
            else:
                crs_obj = crs
            
            with rasterio.open(
                file_path,
                'w',
                driver='GTiff',
                height=data.shape[0],
                width=data.shape[1],
                count=1,
                dtype=data.dtype,
                crs=crs_obj,
                transform=transform,
                compress='lzw'
            ) as dst:
                dst.write(data, 1)
            
            self.logger.info(f"Raster saved to: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save raster {file_path}: {e}")
            raise
    
    def load_geometry(self, geometry_input: Union[str, dict]) -> dict:
        """
        Load geometry from file or dictionary.
        
        Args:
            geometry_input: Path to geometry file or geometry dictionary
            
        Returns:
            Geometry as dictionary
        """
        try:
            if isinstance(geometry_input, str):
                # Load from file
                if geometry_input.endswith('.geojson'):
                    gdf = gpd.read_file(geometry_input)
                    if len(gdf) == 0:
                        raise ValueError("Geometry file is empty")
                    return gdf.geometry.iloc[0].__geo_interface__
                else:
                    raise ValueError(f"Unsupported geometry file format: {geometry_input}")
            else:
                # Already a geometry dictionary
                return geometry_input
                
        except Exception as e:
            self.logger.error(f"Failed to load geometry: {e}")
            raise
    
    def set_processing_extent(self, geometry: dict, crs: str) -> None:
        """
        Set processing extent from geometry.
        
        Args:
            geometry: Geometry dictionary
            crs: Coordinate reference system
        """
        try:
            self.processing_extent = shape(geometry)
            self.processing_crs = crs
            self.logger.info(f"Processing extent set with CRS: {crs}")
        except Exception as e:
            self.logger.error(f"Failed to set processing extent: {e}")
            raise
    
    def _get_bounds_from_extent(self) -> Tuple[float, float, float, float]:
        """
        Get bounds from processing extent.
        
        Returns:
            Tuple of (minx, miny, maxx, maxy)
        """
        if self.processing_extent is None:
            raise ValueError("Processing extent not set")
        
        return self.processing_extent.bounds
    
    def raster_to_vector(self, 
                        raster_data: np.ndarray, 
                        output_path: str, 
                        crs: str,
                        threshold: float = 0.5) -> None:
        """
        Convert raster to vector format.
        
        Args:
            raster_data: Raster data array
            output_path: Output vector file path
            crs: Coordinate reference system
            threshold: Threshold for binary conversion
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create binary mask
            binary_mask = (raster_data >= threshold).astype(np.uint8)
            
            # Convert to vector
            shapes = rasterio.features.shapes(
                binary_mask,
                transform=rasterio.transform.from_bounds(
                    *self._get_bounds_from_extent(),
                    raster_data.shape[1],
                    raster_data.shape[0]
                )
            )
            
            # Create GeoDataFrame
            geometries = []
            properties = []
            
            for geom, value in shapes:
                if value == 1:  # Only keep areas above threshold
                    geometries.append(shape(geom))
                    properties.append({'value': int(value)})
            
            if geometries:
                gdf = gpd.GeoDataFrame(properties, geometry=geometries, crs=crs)
                gdf.to_file(output_path, driver='GPKG')
                self.logger.info(f"Vector saved to: {output_path}")
            else:
                self.logger.warning("No geometries found above threshold")
                
        except Exception as e:
            self.logger.error(f"Failed to convert raster to vector: {e}")
            raise
    
    def get_raster_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get raster information.
        
        Args:
            file_path: Path to raster file
            
        Returns:
            Dictionary with raster information
        """
        try:
            with rasterio.open(file_path) as src:
                return {
                    "width": src.width,
                    "height": src.height,
                    "crs": src.crs.to_string(),
                    "transform": src.transform,
                    "bounds": src.bounds,
                    "dtype": src.dtypes[0],
                    "nodata": src.nodata,
                    "count": src.count
                }
        except Exception as e:
            self.logger.error(f"Failed to get raster info for {file_path}: {e}")
            raise
    
    def reproject_raster(self, 
                        input_path: str, 
                        output_path: str, 
                        target_crs: str) -> None:
        """
        Reproject raster to target CRS.
        
        Args:
            input_path: Input raster path
            output_path: Output raster path
            target_crs: Target coordinate reference system
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with rasterio.open(input_path) as src:
                # Calculate transform and dimensions
                transform, width, height = rasterio.warp.calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds
                )
                
                # Create output profile
                profile = src.profile.copy()
                profile.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })
                
                with rasterio.open(output_path, 'w', **profile) as dst:
                    for i in range(1, src.count + 1):
                        rasterio.warp.reproject(
                            source=rasterio.band(src, i),
                            destination=rasterio.band(dst, i),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=rasterio.warp.Resampling.bilinear
                        )
            
            self.logger.info(f"Raster reprojected to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to reproject raster: {e}")
            raise
    
    def calculate_distance_to_features(self, 
                                    raster_data: np.ndarray, 
                                    features_path: str) -> np.ndarray:
        """
        Calculate distance to features for each raster cell.
        
        Args:
            raster_data: Reference raster data
            features_path: Path to features file
            
        Returns:
            Distance raster array
        """
        try:
            # Load features
            gdf = gpd.read_file(features_path)
            
            # Create distance raster
            # This is a simplified implementation
            # In practice, you'd use more sophisticated distance calculation
            distance_raster = np.full_like(raster_data, np.inf, dtype=np.float32)
            
            # For each feature, calculate distance
            for idx, row in gdf.iterrows():
                # This is a placeholder - actual implementation would use
                # proper distance calculation algorithms
                pass
            
            return distance_raster
            
        except Exception as e:
            self.logger.error(f"Failed to calculate distance to features: {e}")
            raise



