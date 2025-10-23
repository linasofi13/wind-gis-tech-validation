"""
Script to improve the HTML report generation with Spanish translation and better table formatting.
"""

def create_improved_html_content(report, config, wsi_result):
    """Create improved HTML content with Spanish translation and better table formatting."""
    
    # Spanish translations
    translations = {
        'en': {
            'title': 'Wind Viability Report',
            'report_id': 'Report ID',
            'aoi': 'AOI',
            'generated': 'Generated',
            'executive_summary': 'Executive Summary',
            'key_metrics': 'Key Metrics',
            'viability_percentage': 'Viability Percentage',
            'total_area': 'Total Area',
            'suitable_area': 'Suitable Area',
            'top_sites_count': 'Top Sites Count',
            'wsi_statistics': 'WSI Statistics',
            'mean_wsi': 'Mean WSI',
            'standard_deviation': 'Standard Deviation',
            'min_wsi': 'Min WSI',
            'max_wsi': 'Max WSI',
            'processing_info': 'Processing Information',
            'processing_time': 'Processing Time',
            'memory_usage': 'Memory Usage',
            'engine': 'Engine',
            'resolution': 'Resolution',
            'output_files': 'Output Files',
            'wsi_raster': 'WSI Raster',
            'candidate_sites': 'Candidate Sites',
            'interactive_map': 'Interactive Map',
            'summary_text': 'The wind viability analysis for {aoi} shows a viability percentage of {percentage:.1f}% based on the Wind Suitability Index (WSI).'
        },
        'es': {
            'title': 'Reporte de Viabilidad Eólica',
            'report_id': 'ID del Reporte',
            'aoi': 'Área de Interés',
            'generated': 'Generado',
            'executive_summary': 'Resumen Ejecutivo',
            'key_metrics': 'Métricas Clave',
            'viability_percentage': 'Porcentaje de Viabilidad',
            'total_area': 'Área Total',
            'suitable_area': 'Área Adecuada',
            'top_sites_count': 'Número de Sitios Top',
            'wsi_statistics': 'Estadísticas del WSI',
            'mean_wsi': 'WSI Promedio',
            'standard_deviation': 'Desviación Estándar',
            'min_wsi': 'WSI Mínimo',
            'max_wsi': 'WSI Máximo',
            'processing_info': 'Información de Procesamiento',
            'processing_time': 'Tiempo de Procesamiento',
            'memory_usage': 'Uso de Memoria',
            'engine': 'Motor',
            'resolution': 'Resolución',
            'output_files': 'Archivos de Salida',
            'wsi_raster': 'Raster WSI',
            'candidate_sites': 'Sitios Candidatos',
            'interactive_map': 'Mapa Interactivo',
            'summary_text': 'El análisis de viabilidad eólica para {aoi} muestra un porcentaje de viabilidad del {percentage:.1f}% basado en el Índice de Idoneidad Eólica (WSI).'
        }
    }
    
    lang = config.report_spec.language if hasattr(config, 'report_spec') else 'es'
    t = translations.get(lang, translations['es'])
    
    html_content = f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']} - {report.report_id}</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header-info {{
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
        }}
        .header-info p {{
            margin: 5px 0;
            font-size: 1.1em;
        }}
        .section {{ 
            margin: 0;
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .metric:hover {{
            transform: translateY(-5px);
        }}
        .metric strong {{
            display: block;
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stats-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        .stats-table td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .stats-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .stats-table tr:hover {{
            background-color: #e3f2fd;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        .info-item strong {{
            color: #333;
            display: block;
            margin-bottom: 5px;
        }}
        .output-list {{
            list-style: none;
            padding: 0;
        }}
        .output-list li {{
            background: #e8f4f8;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #2196f3;
        }}
        .output-list strong {{
            color: #1976d2;
        }}
        .chart {{
            width: 100%;
            height: 300px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.2em;
            margin: 20px 0;
        }}
        @media (max-width: 768px) {{
            .header-info {{
                flex-direction: column;
                gap: 10px;
            }}
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            .info-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{t['title']}</h1>
            <div class="header-info">
                <p><strong>{t['report_id']}:</strong> {report.report_id}</p>
                <p><strong>{t['aoi']}:</strong> {report.aoi_name}</p>
                <p><strong>{t['generated']}:</strong> {report.generation_date}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>{t['executive_summary']}</h2>
            <p>{t['summary_text'].format(aoi=report.aoi_name, percentage=report.viability_percentage)}</p>
        </div>
        
        <div class="section">
            <h2>{t['key_metrics']}</h2>
            <div class="metrics-grid">
                <div class="metric">
                    <strong>{t['viability_percentage']}</strong>
                    <div class="metric-value">{report.viability_percentage:.1f}%</div>
                </div>
                <div class="metric">
                    <strong>{t['total_area']}</strong>
                    <div class="metric-value">{report.total_area:.1f} km²</div>
                </div>
                <div class="metric">
                    <strong>{t['suitable_area']}</strong>
                    <div class="metric-value">{report.suitable_area:.1f} km²</div>
                </div>
                <div class="metric">
                    <strong>{t['top_sites_count']}</strong>
                    <div class="metric-value">{report.top_sites_count:,}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>{t['wsi_statistics']}</h2>
            <table class="stats-table">
                <thead>
                    <tr>
                        <th>Estadística</th>
                        <th>Valor</th>
                        <th>Descripción</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>{t['mean_wsi']}</strong></td>
                        <td>{report.wsi_statistics['mean']:.3f}</td>
                        <td>Valor promedio del índice de idoneidad eólica</td>
                    </tr>
                    <tr>
                        <td><strong>{t['standard_deviation']}</strong></td>
                        <td>{report.wsi_statistics['std']:.3f}</td>
                        <td>Variabilidad de los valores del WSI</td>
                    </tr>
                    <tr>
                        <td><strong>{t['min_wsi']}</strong></td>
                        <td>{report.wsi_statistics['min']:.3f}</td>
                        <td>Valor mínimo encontrado en el área</td>
                    </tr>
                    <tr>
                        <td><strong>{t['max_wsi']}</strong></td>
                        <td>{report.wsi_statistics['max']:.3f}</td>
                        <td>Valor máximo encontrado en el área</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>{t['processing_info']}</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>{t['processing_time']}</strong>
                    {wsi_result.processing_time:.2f} segundos
                </div>
                <div class="info-item">
                    <strong>{t['memory_usage']}</strong>
                    {wsi_result.memory_usage:.1f} MB
                </div>
                <div class="info-item">
                    <strong>{t['engine']}</strong>
                    {config.engine.value}
                </div>
                <div class="info-item">
                    <strong>{t['resolution']}</strong>
                    {config.resolution_m} metros
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>{t['output_files']}</h2>
            <ul class="output-list">
                <li><strong>{t['wsi_raster']}:</strong> {wsi_result.wsi_raster_path}</li>
                <li><strong>{t['candidate_sites']}:</strong> {wsi_result.candidate_sites_path}</li>
                <li><strong>{t['interactive_map']}:</strong> {wsi_result.interactive_map_path}</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    print("Script para mejorar los reportes HTML creado exitosamente!")
    print("Este script proporciona:")
    print(" Traducción completa al español")
    print(" Mejor formato de tablas")
    print(" Diseño responsivo")
    print(" Estilos modernos")
