"""
Script to create test data for Vento Wind GIS Technology Validation.
This creates sample wind, elevation, and grid data for testing.
"""

import numpy as np
import rasterio
from rasterio.transform import from_bounds
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import os
from pathlib import Path

def create_directories():
    """Create necessary directories."""
    dirs = [
        "data/raw", "data/interim", "data/processed",
        "outputs/rasters", "outputs/vectors", "outputs/maps", "outputs/reports"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f" Created directory: {dir_path}")

def create_wind_data():
    """Create sample wind speed data."""
    print("Creating wind speed data...")
    
    west, south, east, north = -73.0, 10.5, -71.0, 12.5
    width, height = 200, 200
    
    x = np.linspace(west, east, width)
    y = np.linspace(south, north, height)
    X, Y = np.meshgrid(x, y)
    
    wind_speed = 6 + 3 * np.sin((Y - south) / (north - south) * np.pi) + np.random.normal(0, 0.8, (height, width))
    wind_speed = np.clip(wind_speed, 4, 12)
    
    transform = from_bounds(west, south, east, north, width, height)
    
    with rasterio.open(
        "data/raw/wind_100m.tif",
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=wind_speed.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(wind_speed, 1)
    
    print(" Wind data created: data/raw/wind_100m.tif")

def create_elevation_data():
    """Create sample elevation data."""
    print("Creating elevation data...")
    
    west, south, east, north = -73.0, 10.5, -71.0, 12.5
    width, height = 200, 200
    
    x = np.linspace(west, east, width)
    y = np.linspace(south, north, height)
    X, Y = np.meshgrid(x, y)
    
    elevation = 50 + 200 * np.sin((X - west) / (east - west) * np.pi) * np.cos((Y - south) / (north - south) * np.pi) + np.random.normal(0, 30, (height, width))
    elevation = np.clip(elevation, 0, 500)
    
    transform = from_bounds(west, south, east, north, width, height)
    
    with rasterio.open(
        "data/raw/dem.tif",
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=elevation.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(elevation, 1)
    
    print(" Elevation data created: data/raw/dem.tif")

def create_grid_data():
    """Create sample electrical grid data."""
    print("Creating electrical grid data...")
    
    grid_lines = [
        LineString([(-72.8, 11.2), (-72.2, 11.8)]),
        LineString([(-72.5, 11.1), (-72.3, 11.3)]),
        LineString([(-72.7, 11.5), (-72.1, 11.7)]),
        LineString([(-72.9, 10.8), (-72.4, 11.0)]),
    ]
    
    gdf = gpd.GeoDataFrame({
        'id': range(len(grid_lines)),
        'voltage': ['400kV', '132kV', '132kV', '230kV'],
        'type': ['transmission', 'distribution', 'distribution', 'transmission'],
        'name': ['Riohacha-Maicao', 'Riohacha Local', 'Maicao Local', 'Coastal Line'],
        'geometry': grid_lines
    }, crs="EPSG:4326")
    
    gdf.to_file("data/raw/grid_lines.gpkg", driver="GPKG")
    print(" Grid data created: data/raw/grid_lines.gpkg")

def create_restrictions_data():
    """Create sample restrictions data."""
    print("Creating restrictions data...")
    
    restrictions = [
        Polygon([(-72.9, 11.1), (-72.8, 11.1), (-72.8, 11.2), (-72.9, 11.2)]),
        Polygon([(-72.4, 11.6), (-72.3, 11.6), (-72.3, 11.7), (-72.4, 11.7)]),
        Polygon([(-72.6, 10.8), (-72.5, 10.8), (-72.5, 10.9), (-72.6, 10.9)]),
        Polygon([(-72.2, 11.3), (-72.1, 11.3), (-72.1, 11.4), (-72.2, 11.4)]),
    ]
    
    gdf = gpd.GeoDataFrame({
        'id': range(len(restrictions)),
        'type': ['protected', 'urban', 'water', 'indigenous'],
        'name': ['Sierra Nevada Park', 'Maicao City', 'Laguna de Taroa', 'Wayuu Territory'],
        'geometry': restrictions
    }, crs="EPSG:4326")
    
    gdf.to_file("data/raw/restrictions.gpkg", driver="GPKG")
    print(" Restrictions data created: data/raw/restrictions.gpkg")

def create_aoi():
    """Create Area of Interest."""
    print(" Creating Area of Interest...")
    
    aoi_polygon = Polygon([
        (-73.0, 10.5), (-71.0, 10.5), (-71.0, 12.5), (-73.0, 12.5), (-73.0, 10.5)
    ])
    
    gdf = gpd.GeoDataFrame({
        'id': [1],
        'name': ['La Guajira, Colombia'],
        'description': ['Wind energy suitability analysis for La Guajira region, Colombia'],
        'geometry': [aoi_polygon]
    }, crs="EPSG:4326")
    
    gdf.to_file("data/interim/aoi.geojson", driver="GeoJSON")
    print(" AOI created: data/interim/aoi.geojson")

def main():
    """Main function to create all test data."""
    print("Creating Test Data for Vento Wind GIS")
    print("=" * 50)
    
    create_directories()
    create_wind_data()
    create_elevation_data()
    create_grid_data()
    create_restrictions_data()
    create_aoi()
    
    print("\nTest data creation completed!")
    print("\nCreated files:")
    print("  • data/raw/wind_100m.tif - Wind speed data")
    print("  • data/raw/dem.tif - Elevation data")
    print("  • data/raw/grid_lines.gpkg - Electrical grid")
    print("  • data/raw/restrictions.gpkg - Restricted areas")
    print("  • data/interim/aoi.geojson - Area of Interest")
    
    print("\nNext steps:")
    print("  1. python -m src.interface.cli validate-config configs/wsi.yaml")
    print("  2. python -m src.interface.cli compute-wsi configs/wsi.yaml")

if __name__ == "__main__":
    main()
