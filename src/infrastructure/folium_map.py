"""
Folium map generation infrastructure.

This module provides utilities for creating interactive maps
using the Folium library for wind suitability visualization.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import folium
import folium.plugins
from folium import plugins
import json
import os

try:
    import rasterio
    from rasterio.transform import from_bounds
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    rasterio = None
    from_bounds = None


class FoliumMapGenerator:
    """Generator for interactive Folium maps."""
    
    def __init__(self):
        """Initialize the Folium map generator."""
        self.logger = logging.getLogger(__name__)
    
    def create_wsi_map(self, 
                      wsi_data: np.ndarray,
                      aoi_geometry: Union[str, dict],
                      crs: str,
                      output_path: str,
                      title: str = "Wind Suitability Index",
                      center: Optional[Tuple[float, float]] = None,
                      zoom_start: int = 10) -> None:
        """
        Create interactive WSI map using Folium.
        
        Args:
            wsi_data: WSI raster data
            aoi_geometry: AOI geometry (file path or dict)
            crs: Coordinate reference system
            output_path: Output HTML file path
            title: Map title
            center: Optional map center (lat, lon)
            zoom_start: Initial zoom level
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get map center
            if center is None:
                center = self._get_geometry_center(aoi_geometry)
            
            # Create base map with default tile
            m = folium.Map(
                location=center,
                zoom_start=zoom_start,
                tiles='OpenStreetMap'
            )
            
            # Add different tile layers
            self._add_tile_layers(m)
            
            # Add satellite layer
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Satelital',
                overlay=False,
                control=True
            ).add_to(m)
            
            # Add terrain layer
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Terreno',
                overlay=False,
                control=True
            ).add_to(m)
            
            
            # Add WSI visualization
            self._add_wsi_layer(m, wsi_data, aoi_geometry, crs)
            
            # Add AOI boundary
            self._add_aoi_boundary(m, aoi_geometry)
            
            # Add custom markers for important locations
            self._add_custom_markers(m)
            
            # Add legend
            self._add_wsi_legend(m)
            
            # Add title
            self._add_title(m, title)
            
            # Add plugins
            self._add_plugins(m)
            
            # Add layer control
            folium.LayerControl(
                position='topright',
                collapsed=True,
                autoZIndex=True
            ).add_to(m)
            
            # Save map
            m.save(output_path)
            
            self.logger.info(f"Interactive map saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create WSI map: {e}")
            raise
    
    def _get_geometry_center(self, geometry_input: Union[str, dict]) -> Tuple[float, float]:
        """Get center point of geometry."""
        try:
            if isinstance(geometry_input, str):
                import geopandas as gpd
                gdf = gpd.read_file(geometry_input)
                if gdf.crs and gdf.crs.is_geographic:
                    gdf_projected = gdf.to_crs('EPSG:3857')
                    centroid = gdf_projected.geometry.centroid.iloc[0]
                    centroid_geo = gdf_projected.to_crs('EPSG:4326').geometry.centroid.iloc[0]
                    return (centroid_geo.y, centroid_geo.x)
                else:
                    centroid = gdf.geometry.centroid.iloc[0]
                    return (centroid.y, centroid.x)
            else:
                from shapely.geometry import shape
                geom = shape(geometry_input)
                centroid = geom.centroid
                return (centroid.y, centroid.x)
                
        except Exception as e:
            self.logger.warning(f"Could not get geometry center: {e}")
            return (11.5, -72.0)
    
    def _add_wsi_layer(self, 
                      map_obj: folium.Map, 
                      wsi_data: np.ndarray,
                      aoi_geometry: Union[str, dict],
                      crs: str) -> None:
        """Add WSI layer to map."""
        try:
            bounds = self._get_geometry_bounds(aoi_geometry)
            sample_points = self._sample_wsi_points(wsi_data, bounds)
            
            for point in sample_points:
                lat, lon, wsi_value = point
                color = self._get_wsi_color(wsi_value)
                radius = self._get_wsi_radius(wsi_value)
                
                popup_text = f"""
                <div style="font-family: Arial, sans-serif; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #333;">Punto de Idoneidad Eólica</h4>
                    <p style="margin: 5px 0;"><strong>WSI:</strong> {wsi_value:.3f}</p>
                    <p style="margin: 5px 0;"><strong>Latitud:</strong> {lat:.4f}°</p>
                    <p style="margin: 5px 0;"><strong>Longitud:</strong> {lon:.4f}°</p>
                    <p style="margin: 5px 0;"><strong>Clasificación:</strong> {self._get_wsi_classification(wsi_value)}</p>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">
                        Área terrestre de Colombia - La Guajira
                    </p>
                </div>
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    popup=folium.Popup(popup_text, max_width=250),
                    color='white',
                    weight=3,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.9
                ).add_to(map_obj)
                
        except Exception as e:
            self.logger.error(f"Failed to add WSI layer: {e}")
    
    def _get_geometry_bounds(self, geometry_input: Union[str, dict]) -> Tuple[float, float, float, float]:
        """Get bounds from geometry."""
        try:
            if isinstance(geometry_input, str):
                import geopandas as gpd
                gdf = gpd.read_file(geometry_input)
                return gdf.total_bounds
            else:
                from shapely.geometry import shape
                geom = shape(geometry_input)
                return geom.bounds
                
        except Exception as e:
            self.logger.warning(f"Could not get geometry bounds: {e}")
            return (-180, -90, 180, 90)
    
    def _sample_wsi_points(self, 
                          wsi_data: np.ndarray, 
                          bounds: Tuple[float, float, float, float]) -> List[Tuple[float, float, float]]:
        """Sample points from WSI data, filtering for terrestrial areas only."""
        points = []
        minx, miny, maxx, maxy = bounds
        height, width = wsi_data.shape
        max_points = 1000
        
        if height * width <= max_points:
            step = 1
        else:
            step = max(1, int(np.sqrt(height * width / max_points)))
        
        for i in range(0, height, step):
            for j in range(0, width, step):
                wsi_value = wsi_data[i, j]
                if not np.isnan(wsi_value) and wsi_value > 0:
                    lat = miny + (maxy - miny) * (i / height)
                    lon = minx + (maxx - minx) * (j / width)
                    
                    if self._is_terrestrial_point(lat, lon):
                        points.append((lat, lon, float(wsi_value)))
        
        if len(points) > max_points:
            import random
            points = random.sample(points, max_points)
        
        return points
    
    def _is_terrestrial_point(self, lat: float, lon: float) -> bool:
        """Check if a point is on land (terrestrial) based on Colombia's geography."""
        colombia_bounds = {
            'north': 15.5, 'south': 4.0, 'east': -66.0, 'west': -82.0
        }
        
        if not (colombia_bounds['south'] <= lat <= colombia_bounds['north'] and
                colombia_bounds['west'] <= lon <= colombia_bounds['east']):
            return False
        
        if lat > 12.0 and lon > -75.0:
            return False
        
        if lon < -78.0:
            return False
        
        if 10.5 <= lat <= 12.5 and -73.0 <= lon <= -71.0:
            return True
        
        return True
    
    def _get_wsi_color(self, wsi_value: float) -> str:
        """Get color for WSI value."""
        if wsi_value < 0.2:
            return '#FF0000'
        elif wsi_value < 0.4:
            return '#FFA500'
        elif wsi_value < 0.6:
            return '#FFFF00'
        elif wsi_value < 0.8:
            return '#90EE90'
        else:
            return '#006400'
    
    def _get_wsi_radius(self, wsi_value: float) -> int:
        """Get radius for WSI value."""
        return int(4 + wsi_value * 8)
    
    def _get_wsi_classification(self, wsi_value: float) -> str:
        """Get Spanish classification for WSI value."""
        if wsi_value < 0.2:
            return "Bajo"
        elif wsi_value < 0.4:
            return "Regular"
        elif wsi_value < 0.6:
            return "Bueno"
        elif wsi_value < 0.8:
            return "Alto"
        else:
            return "Excelente"
    
    def _add_aoi_boundary(self, map_obj: folium.Map, aoi_geometry: Union[str, dict]) -> None:
        """
        Add AOI boundary to map.
        
        Args:
            map_obj: Folium map object
            aoi_geometry: AOI geometry
        """
        try:
            if isinstance(aoi_geometry, str):
                import geopandas as gpd
                gdf = gpd.read_file(aoi_geometry)
                geom = gdf.geometry.iloc[0]
            else:
                from shapely.geometry import shape
                geom = shape(aoi_geometry)
            
            # Convert geometry to GeoJSON
            geojson = geom.__geo_interface__
            
            # Add to map
            folium.GeoJson(
                geojson,
                style_function=lambda x: {
                    'fillColor': 'transparent',
                    'color': 'blue',
                    'weight': 3,
                    'opacity': 0.8
                }
            ).add_to(map_obj)
            
        except Exception as e:
            self.logger.warning(f"Could not add AOI boundary: {e}")
    
    def _add_wsi_legend(self, map_obj: folium.Map) -> None:
        """
        Add WSI legend to map.
        
        Args:
            map_obj: Folium map object
        """
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 300px; height: 220px; 
                    background-color: white; border:2px solid #333; z-index:9999; 
                    font-size:14px; padding: 15px; border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3); overflow: visible;">
        <p style="margin: 0 0 10px 0; font-weight: bold; text-align: center; color: #333;">
            Índice de Idoneidad Eólica
        </p>
        <div style="display: flex; align-items: center; margin: 6px 0;">
            <span style="color:#FF0000; font-size:16px; margin-right: 8px;">●</span>
            <span>0.0 - 0.2 (Bajo)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 6px 0;">
            <span style="color:#FFA500; font-size:16px; margin-right: 8px;">●</span>
            <span>0.2 - 0.4 (Regular)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 6px 0;">
            <span style="color:#FFFF00; font-size:16px; margin-right: 8px;">●</span>
            <span>0.4 - 0.6 (Bueno)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 6px 0;">
            <span style="color:#90EE90; font-size:16px; margin-right: 8px;">●</span>
            <span>0.6 - 0.8 (Alto)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 6px 0;">
            <span style="color:#006400; font-size:16px; margin-right: 8px;">●</span>
            <span>0.8 - 1.0 (Excelente)</span>
        </div>
        </div>
        '''
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def _add_tile_layers(self, map_obj: folium.Map) -> None:
        """
        Add multiple tile layers to the map.
        
        Args:
            map_obj: Folium map object
        """
        # OpenStreetMap (default)
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(map_obj)
        
        # Add additional useful layers
        folium.TileLayer(
            tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            attr='OpenTopoMap',
            name='Topográfico',
            overlay=False,
            control=True
        ).add_to(map_obj)
        
    
    def _add_title(self, map_obj: folium.Map, title: str) -> None:
        """
        Add title to map with Vento logo.
        
        Args:
            map_obj: Folium map object
            title: Map title
        """
        # Default to Spanish title if not provided
        if title == "Wind Suitability Index":
            title = "Índice de Idoneidad Eólica"
        
        title_html = f'''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 400px; height: 80px; 
                    background-color: #f8f9fa; color: #333; border:2px solid #dee2e6; z-index:9999; 
                    font-size:18px; padding: 15px; text-align: center;
                    border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1)">
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
            <div style="width: 50px; height: 50px; background: white; border: 2px solid #dee2e6; 
                        border-radius: 8px; display: flex; align-items: center; justify-content: center; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <img src="./img/image.png" style="width: 40px; height: 40px; object-fit: contain;" 
                     alt="Logo Vento" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                <div style="display: none; width: 40px; height: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 50%; align-items: center; justify-content: center; color: white; 
                            font-weight: bold; font-size: 18px;">V</div>
            </div>
            <div>
                <b>{title}</b><br>
                <small style="color: #666;">Vento</small>
            </div>
        </div>
        </div>
        '''
        
        map_obj.get_root().html.add_child(folium.Element(title_html))
    
    def _add_plugins(self, map_obj: folium.Map) -> None:
        """
        Add useful GIS plugins to map.
        
        Args:
            map_obj: Folium map object
        """
        try:
        # Add fullscreen plugin
            plugins.Fullscreen(
                position='topright',
                title='Pantalla Completa',
                title_cancel='Salir de Pantalla Completa',
                force_separate_button=True
            ).add_to(map_obj)
        except Exception as e:
            self.logger.warning(f"Could not add fullscreen plugin: {e}")
        
        try:
            # Add measure plugin
            plugins.MeasureControl(
                position='topright',
                primary_length_unit='meters',
                primary_area_unit='sqmeters',
                active_color='#3b5998',
                completed_color='#3b5998'
            ).add_to(map_obj)
        except Exception as e:
            self.logger.warning(f"Could not add measure plugin: {e}")
        
        try:
            # Add draw plugin for GIS editing
            plugins.Draw(
                position='topleft',
                export=False,
                filename='vento_gis_data',
                show_geometry_on_click=True,
                draw_options={
                    'polyline': {
                        'allowIntersection': False,
                        'drawError': {'color': '#e1e100', 'message': '<strong>Error:</strong> Las líneas no pueden cruzarse!'},
                        'shapeOptions': {'color': '#bada55'}
                    },
                    'polygon': {
                        'allowIntersection': False,
                        'drawError': {'color': '#e1e100', 'message': '<strong>Error:</strong> Los polígonos no pueden cruzarse!'},
                        'shapeOptions': {'color': '#bada55'}
                    },
                    'circle': False,
                    'rectangle': {
                        'shapeOptions': {'color': '#bada55'}
                    },
                    'marker': {
                        'shapeOptions': {'color': '#bada55'}
                    }
                },
                edit_options={
                    'featureGroup': None,
                    'edit': True,
                    'remove': True
                }
            ).add_to(map_obj)
        except Exception as e:
            self.logger.warning(f"Could not add draw plugin: {e}")
        
        try:
            # Add export plugin for PNG export
            self._add_export_plugin(map_obj)
        except Exception as e:
            self.logger.warning(f"Could not add export plugin: {e}")
        
        try:
            # Add minimap
            plugins.MiniMap(
                position='bottomright',
                width=200,
                height=150,
                collapsed_width=25,
                collapsed_height=25,
                zoom_level_offset=-5,
                zoom_level_fixed=False,
                center_fixed=False,
                zoom_control=True,
                auto_toggle=False
            ).add_to(map_obj)
        except Exception as e:
            self.logger.warning(f"Could not add minimap plugin: {e}")
        
        try:
            # Add mouse position
            plugins.MousePosition(
                position='bottomleft',
                separator=' | ',
                empty_string='Coordenadas no disponibles',
                lng_first=True,
                num_digits=5,
                prefix='',
                lat_formatter=None,
                lng_formatter=None
            ).add_to(map_obj)
        except Exception as e:
            self.logger.warning(f"Could not add mouse position plugin: {e}")
    
    def _add_export_plugin(self, map_obj: folium.Map) -> None:
        """
        Add custom export plugin for PNG export.
        
        Args:
            map_obj: Folium map object
        """
        export_html = '''
        <div id="export-control" style="position: fixed; 
                    top: 10px; right: 10px; z-index: 1000;">
            <button id="export-png-btn" style="
                background: #6c757d;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(0,0,0,0.3)'; this.style.background='#5a6268'" 
               onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.2)'; this.style.background='#6c757d'"
               onclick="exportMapAsPNG()">
                Exportar PNG
            </button>
        </div>
        
        <script>
        function exportMapAsPNG() {
            const button = document.getElementById('export-png-btn');
            const originalText = button.innerHTML;
            
            // Show loading state
            button.innerHTML = 'Generando...';
            button.disabled = true;
            
            // Get map container
            const mapContainer = document.querySelector('.folium-map');
            if (!mapContainer) {
                alert('Error: No se pudo encontrar el mapa');
                button.innerHTML = originalText;
                button.disabled = false;
                return;
            }
            
            // Use html2canvas to capture the map
            if (typeof html2canvas === 'undefined') {
                // Load html2canvas if not available
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
                script.onload = function() {
                    captureMap();
                };
                script.onerror = function() {
                    alert('Error: No se pudo cargar la librería de captura');
                    button.innerHTML = originalText;
                    button.disabled = false;
                };
                document.head.appendChild(script);
            } else {
                captureMap();
            }
            
            function captureMap() {
                try {
                    html2canvas(mapContainer, {
                        useCORS: true,
                        allowTaint: true,
                        backgroundColor: '#ffffff',
                        scale: 2,
                        logging: false,
                        width: mapContainer.offsetWidth,
                        height: mapContainer.offsetHeight
                    }).then(function(canvas) {
                        // Create download link
                        const link = document.createElement('a');
                        link.download = 'vento_wsi_map_' + new Date().toISOString().slice(0,19).replace(/:/g, '-') + '.png';
                        link.href = canvas.toDataURL('image/png');
                        
                        // Trigger download
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        // Reset button
                        button.innerHTML = 'Exportado';
                        setTimeout(() => {
                            button.innerHTML = originalText;
                            button.disabled = false;
                        }, 2000);
                        
                    }).catch(function(error) {
                        console.error('Error al capturar el mapa:', error);
                        alert('Error al generar la imagen PNG. Intente de nuevo.');
                        button.innerHTML = originalText;
                        button.disabled = false;
                    });
                } catch (error) {
                    console.error('Error en la captura:', error);
                    alert('Error al generar la imagen PNG. Intente de nuevo.');
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            }
        }
        </script>
        '''
        
        map_obj.get_root().html.add_child(folium.Element(export_html))
    
    def _add_custom_markers(self, map_obj: folium.Map) -> None:
        """
        Add custom markers for important locations in La Guajira.
        
        Args:
            map_obj: Folium map object
        """
        # Important locations in La Guajira, Colombia
        important_locations = [
            {
                'name': 'Riohacha',
                'lat': 11.5444,
                'lon': -72.9072,
                'type': 'city',
                'icon': 'building',
                'description': 'Capital de La Guajira'
            },
            {
                'name': 'Maicao',
                'lat': 11.3833,
                'lon': -72.2333,
                'type': 'city',
                'icon': 'home',
                'description': 'Ciudad fronteriza'
            },
            {
                'name': 'Uribia',
                'lat': 11.7167,
                'lon': -72.2667,
                'type': 'city',
                'icon': 'home',
                'description': 'Capital indígena'
            },
            {
                'name': 'Punta Gallinas',
                'lat': 12.4333,
                'lon': -71.6667,
                'type': 'landmark',
                'icon': 'map',
                'description': 'Punto más septentrional de Colombia'
            },
            {
                'name': 'Cabo de la Vela',
                'lat': 12.2167,
                'lon': -72.1167,
                'type': 'landmark',
                'icon': 'beach',
                'description': 'Destino turístico importante'
            },
            {
                'name': 'Parque Nacional Natural Macuira',
                'lat': 12.1667,
                'lon': -71.4167,
                'type': 'protected',
                'icon': '🌿',
                'description': 'Área protegida nacional'
            }
        ]
        
        # Create feature groups for different types of markers
        cities_group = folium.FeatureGroup(name='Ciudades')
        landmarks_group = folium.FeatureGroup(name='Puntos de Interés')
        protected_group = folium.FeatureGroup(name='Áreas Protegidas')
        
        for location in important_locations:
            # Create custom icon
            if location['type'] == 'city':
                icon_color = 'blue'
                icon_symbol = 'city'
            elif location['type'] == 'landmark':
                icon_color = 'orange'
                icon_symbol = 'star'
            elif location['type'] == 'protected':
                icon_color = 'green'
                icon_symbol = 'leaf'
            else:
                icon_color = 'red'
                icon_symbol = 'info'
            
            # Create popup content
            popup_content = f"""
            <div style="font-family: Arial, sans-serif; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">
                    {location['icon']} {location['name']}
                </h4>
                <p style="margin: 5px 0;"><strong>Tipo:</strong> {location['type'].title()}</p>
                <p style="margin: 5px 0;"><strong>Descripción:</strong> {location['description']}</p>
                <p style="margin: 5px 0;"><strong>Coordenadas:</strong> {location['lat']:.4f}, {location['lon']:.4f}</p>
                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                    La Guajira, Colombia
                </p>
            </div>
            """
            
            # Create marker
            marker = folium.Marker(
                location=[location['lat'], location['lon']],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=location['name'],
                icon=folium.Icon(
                    color=icon_color,
                    icon=icon_symbol,
                    prefix='fa'
                )
            )
            
            # Add to appropriate group
            if location['type'] == 'city':
                marker.add_to(cities_group)
            elif location['type'] == 'landmark':
                marker.add_to(landmarks_group)
            elif location['type'] == 'protected':
                marker.add_to(protected_group)
        
        # Add groups to map
        cities_group.add_to(map_obj)
        landmarks_group.add_to(map_obj)
        protected_group.add_to(map_obj)
    
    def create_heatmap(self, 
                       wsi_data: np.ndarray,
                       aoi_geometry: Union[str, dict],
                       crs: str,
                       output_path: str,
                       title: str = "Índice de Idoneidad Eólica") -> None:
        """
        Create heatmap visualization of WSI data.
        
        Args:
            wsi_data: WSI raster data
            aoi_geometry: AOI geometry
            crs: Coordinate reference system
            output_path: Output HTML file path
            title: Map title
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get map center
            center = self._get_geometry_center(aoi_geometry)
            
            # Create base map with multiple tile layers
            m = folium.Map(
                location=center,
                zoom_start=10,
                tiles=None  # We'll add tiles manually
            )
            
            # Add different tile layers
            self._add_tile_layers(m)
            
            # Get bounds and sample points
            bounds = self._get_geometry_bounds(aoi_geometry)
            sample_points = self._sample_wsi_points(wsi_data, bounds)
            
            # Prepare heatmap data
            heat_data = []
            for lat, lon, wsi_value in sample_points:
                heat_data.append([lat, lon, wsi_value])
            
            # Add heatmap layer
            plugins.HeatMap(
                heat_data,
                name='WSI Heatmap',
                min_opacity=0.4,
                max_zoom=18,
                radius=25,
                blur=15,
                gradient={0.0: 'red', 0.2: 'orange', 0.4: 'yellow', 0.6: 'lightgreen', 0.8: 'green', 1.0: 'darkgreen'}
            ).add_to(m)
            
            # Add AOI boundary
            self._add_aoi_boundary(m, aoi_geometry)
            
            # Add legend
            self._add_wsi_legend(m)
            
            # Add title
            self._add_title(m, title)
            
            # Add plugins
            self._add_plugins(m)
            
            # Save map
            m.save(output_path)
            
            self.logger.info(f"Heatmap saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create heatmap: {e}")
            raise
    
    def create_static_map(self, 
                         wsi_data: np.ndarray,
                         output_path: str,
                         title: str = "Wind Suitability Index") -> None:
        """
        Create static map visualization.
        
        Args:
            wsi_data: WSI raster data
            output_path: Output PNG file path
            title: Map title
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.colors as mcolors
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create colormap
            colors = ['red', 'orange', 'yellow', 'lightgreen', 'darkgreen']
            n_bins = 5
            cmap = mcolors.LinearSegmentedColormap.from_list('wsi', colors, N=n_bins)
            
            # Plot WSI data
            im = ax.imshow(wsi_data, cmap=cmap, vmin=0, vmax=1)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Wind Suitability Index', rotation=270, labelpad=20)
            
            # Set title
            ax.set_title(title, fontsize=16, fontweight='bold')
            
            # Remove axes
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Save figure
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Static map saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create static map: {e}")
            raise



