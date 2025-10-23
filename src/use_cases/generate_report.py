"""
Use case for generating wind viability reports.

This module orchestrates the report generation workflow
to create HTML/PDF reports with analysis results.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

from ..domain.entities import (
    ProcessingConfig, WindSuitabilityResult, ViabilityReport
)
from ..domain.policies import ScoringPolicy
from ..infrastructure.metrics import MetricsCollector
from ..infrastructure.rasterio_adapter import RasterioAdapter


class GenerateReportUseCase:
    """Use case for generating wind viability reports."""
    
    def __init__(self, 
                 rasterio_adapter: RasterioAdapter,
                 metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize the generate report use case.
        
        Args:
            rasterio_adapter: Rasterio adapter for data access
            metrics_collector: Optional metrics collector for performance monitoring
        """
        self.rasterio_adapter = rasterio_adapter
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, 
                config: ProcessingConfig, 
                wsi_result: WindSuitabilityResult) -> ViabilityReport:
        """
        Execute the report generation workflow.
        
        Args:
            config: Processing configuration
            wsi_result: WSI computation result
            
        Returns:
            Viability report with analysis results
        """
        start_time = time.time()
        self.logger.info("Starting viability report generation")
        
        try:
            # Step 1: Load WSI data
            self.logger.info("Loading WSI data...")
            wsi_data = self.rasterio_adapter.load_raster(wsi_result.wsi_raster_path)
            
            # Step 2: Calculate viability metrics
            self.logger.info("Calculating viability metrics...")
            viability_metrics = self._calculate_viability_metrics(wsi_data, config)
            
            # Step 3: Generate report
            self.logger.info("Generating report...")
            report = self._create_viability_report(
                config, wsi_result, viability_metrics
            )
            
            # Step 4: Save report files
            self.logger.info("Saving report files...")
            self._save_report_files(report, config, wsi_result)
            
            # Step 5: Update history
            self.logger.info("Updating report history...")
            self._update_report_history(report)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Report generation completed in {processing_time:.2f} seconds")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise
    
    def _calculate_viability_metrics(self, 
                                   wsi_data: np.ndarray, 
                                   config: ProcessingConfig) -> Dict[str, float]:
        """
        Calculate viability metrics from WSI data.
        
        Args:
            wsi_data: WSI array
            config: Processing configuration
            
        Returns:
            Dictionary of viability metrics
        """
        valid_values = wsi_data[~np.isnan(wsi_data)]
        
        if len(valid_values) == 0:
            return {
                "viability_percentage": 0.0,
                "total_area": 0.0,
                "suitable_area": 0.0,
                "top_sites_count": 0,
                "wsi_mean": 0.0,
                "wsi_std": 0.0,
                "wsi_min": 0.0,
                "wsi_max": 0.0
            }
        
        # Calculate basic statistics
        wsi_mean = float(np.mean(valid_values))
        wsi_std = float(np.std(valid_values))
        wsi_min = float(np.min(valid_values))
        wsi_max = float(np.max(valid_values))
        
        # Calculate viability percentage
        viability_percentage = ScoringPolicy.calculate_viability_percentage(valid_values)
        
        # Calculate areas (assuming square cells)
        cell_area = config.resolution_m ** 2  # m²
        total_cells = len(valid_values)
        total_area = total_cells * cell_area / 1_000_000  # Convert to km²
        
        # Calculate suitable area (top percentage)
        top_sites_mask = valid_values >= np.percentile(valid_values, (1 - config.top_percent) * 100)
        suitable_cells = np.sum(top_sites_mask)
        suitable_area = suitable_cells * cell_area / 1_000_000  # Convert to km²
        
        return {
            "viability_percentage": viability_percentage,
            "total_area": total_area,
            "suitable_area": suitable_area,
            "top_sites_count": int(suitable_cells),
            "wsi_mean": wsi_mean,
            "wsi_std": wsi_std,
            "wsi_min": wsi_min,
            "wsi_max": wsi_max
        }
    
    def _create_viability_report(self, 
                               config: ProcessingConfig, 
                               wsi_result: WindSuitabilityResult, 
                               viability_metrics: Dict[str, float]) -> ViabilityReport:
        """
        Create viability report entity.
        
        Args:
            config: Processing configuration
            wsi_result: WSI computation result
            viability_metrics: Calculated viability metrics
            
        Returns:
            Viability report entity
        """
        report_id = f"vento_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ViabilityReport(
            report_id=report_id,
            aoi_name=config.aoi.name or "Unnamed AOI",
            viability_percentage=viability_metrics["viability_percentage"],
            total_area=viability_metrics["total_area"],
            suitable_area=viability_metrics["suitable_area"],
            top_sites_count=viability_metrics["top_sites_count"],
            wsi_statistics={
                "mean": viability_metrics["wsi_mean"],
                "std": viability_metrics["wsi_std"],
                "min": viability_metrics["wsi_min"],
                "max": viability_metrics["wsi_max"]
            },
            generation_date=datetime.now().isoformat()
        )
    
    def _save_report_files(self, 
                          report: ViabilityReport, 
                          config: ProcessingConfig, 
                          wsi_result: WindSuitabilityResult) -> None:
        """
        Save report files (HTML and/or PDF).
        
        Args:
            report: Viability report entity
            config: Processing configuration
            wsi_result: WSI computation result
        """
        output_dir = f"{config.output_dir}/reports"
        
        if config.report_spec.output_format in ["html", "both"]:
            html_path = f"{output_dir}/viability_report_{report.report_id}.html"
            self._generate_html_report(report, config, wsi_result, html_path)
        
        if config.report_spec.output_format in ["pdf", "both"]:
            pdf_path = f"{output_dir}/viability_report_{report.report_id}.pdf"
            self._generate_pdf_report(report, config, wsi_result, pdf_path)
    
    def _generate_html_report(self, 
                            report: ViabilityReport, 
                            config: ProcessingConfig, 
                            wsi_result: WindSuitabilityResult, 
                            output_path: str) -> None:
        """
        Generate HTML report.
        
        Args:
            report: Viability report entity
            config: Processing configuration
            wsi_result: WSI computation result
            output_path: Output path for HTML report
        """
        # This would be implemented with a proper HTML template engine
        # For now, we'll create a basic HTML structure
        html_content = self._create_html_content(report, config, wsi_result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report saved to: {output_path}")
    
    def _generate_pdf_report(self, 
                           report: ViabilityReport, 
                           config: ProcessingConfig, 
                           wsi_result: WindSuitabilityResult, 
                           output_path: str) -> None:
        """
        Generate PDF report.
        
        Args:
            report: Viability report entity
            config: Processing configuration
            wsi_result: WSI computation result
            output_path: Output path for PDF report
        """
        # This would be implemented with a PDF generation library
        # For now, we'll create a placeholder
        self.logger.info(f"PDF report generation not yet implemented: {output_path}")
    
    def _create_html_content(self, 
                           report: ViabilityReport, 
                           config: ProcessingConfig, 
                           wsi_result: WindSuitabilityResult) -> str:
        """
        Create HTML content for the report.
        
        Args:
            report: Viability report entity
            config: Processing configuration
            wsi_result: WSI computation result
            
        Returns:
            HTML content string
        """
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
    
    def _update_report_history(self, report: ViabilityReport) -> None:
        """
        Update the report history CSV file.
        
        Args:
            report: Viability report entity
        """
        import csv
        import os
        
        history_file = "outputs/reports/history.csv"
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(history_file)
        
        with open(history_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                # Write header
                writer.writerow([
                    'report_id', 'aoi_name', 'viability_percentage', 'total_area',
                    'suitable_area', 'top_sites_count', 'wsi_mean', 'wsi_std',
                    'wsi_min', 'wsi_max', 'generation_date'
                ])
            
            # Write report data
            writer.writerow([
                report.report_id,
                report.aoi_name,
                report.viability_percentage,
                report.total_area,
                report.suitable_area,
                report.top_sites_count,
                report.wsi_statistics['mean'],
                report.wsi_statistics['std'],
                report.wsi_statistics['min'],
                report.wsi_statistics['max'],
                report.generation_date
            ])
        
        self.logger.info(f"Report history updated: {history_file}")


