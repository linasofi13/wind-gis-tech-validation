"""
Domain entities for wind suitability analysis.

This module contains the core business entities that represent
the fundamental concepts in wind energy suitability assessment.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class EngineType(Enum):
    """Supported GIS engines for processing."""
    PYTHON = "python"
    PYQGIS = "pyqgis"
    ARCPY = "arcpy"


@dataclass
class AOI:
    """Area of Interest entity."""
    geometry: str  # GeoJSON string or file path
    crs: str
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate AOI after initialization."""
        if not self.geometry:
            raise ValueError("AOI geometry cannot be empty")
        if not self.crs:
            raise ValueError("AOI CRS cannot be empty")


@dataclass
class Criterion:
    """Wind suitability criterion entity."""
    name: str
    weight: float
    file_path: str
    is_benefit: bool = True  # True for benefit criteria, False for cost criteria
    normalization_method: str = "minmax"  # minmax, zscore, etc.
    
    def __post_init__(self):
        """Validate criterion after initialization."""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight for {self.name} must be between 0 and 1")
        if not self.file_path:
            raise ValueError(f"File path for {self.name} cannot be empty")


@dataclass
class WeightScheme:
    """Weight scheme for multicriteria analysis."""
    wind: float
    slope: float
    grid_distance: float
    other_criteria: Dict[str, float] = None
    
    def __post_init__(self):
        """Validate weight scheme after initialization."""
        total_weight = self.wind + self.slope + self.grid_distance
        if self.other_criteria:
            total_weight += sum(self.other_criteria.values())
        
        if not abs(total_weight - 1.0) < 0.01:  # Allow small floating point errors
            raise ValueError(f"Total weights must sum to 1.0, got {total_weight}")
    
    def get_all_weights(self) -> Dict[str, float]:
        """Get all weights as a dictionary."""
        weights = {
            "wind": self.wind,
            "slope": self.slope,
            "grid_distance": self.grid_distance
        }
        if self.other_criteria:
            weights.update(self.other_criteria)
        return weights


@dataclass
class ReportSpec:
    """Report specification entity."""
    output_format: str  # html, pdf, both
    include_metrics: bool = True
    include_map: bool = True
    include_charts: bool = True
    language: str = "en"  # en, es
    
    def __post_init__(self):
        """Validate report specification after initialization."""
        valid_formats = ["html", "pdf", "both"]
        if self.output_format not in valid_formats:
            raise ValueError(f"Output format must be one of {valid_formats}")


@dataclass
class ProcessingConfig:
    """Processing configuration entity."""
    aoi: AOI
    criteria: List[Criterion]
    weight_scheme: WeightScheme
    report_spec: ReportSpec
    engine: EngineType
    resolution_m: int = 100
    top_percent: float = 0.15
    output_dir: str = "outputs"
    
    def __post_init__(self):
        """Validate processing configuration after initialization."""
        if not 0 < self.top_percent <= 1:
            raise ValueError(f"Top percent must be between 0 and 1, got {self.top_percent}")
        if self.resolution_m <= 0:
            raise ValueError(f"Resolution must be positive, got {self.resolution_m}")


@dataclass
class WindSuitabilityResult:
    """Wind suitability analysis result entity."""
    wsi_raster_path: str
    candidate_sites_path: str
    interactive_map_path: str
    metrics: Dict[str, float]
    processing_time: float
    memory_usage: float
    
    def __post_init__(self):
        """Validate result after initialization."""
        if self.processing_time < 0:
            raise ValueError("Processing time cannot be negative")
        if self.memory_usage < 0:
            raise ValueError("Memory usage cannot be negative")


@dataclass
class ViabilityReport:
    """Wind viability report entity."""
    report_id: str
    aoi_name: str
    viability_percentage: float
    total_area: float
    suitable_area: float
    top_sites_count: int
    wsi_statistics: Dict[str, float]
    generation_date: str
    
    def __post_init__(self):
        """Validate viability report after initialization."""
        if not 0 <= self.viability_percentage <= 100:
            raise ValueError(f"Viability percentage must be between 0 and 100, got {self.viability_percentage}")
        if self.total_area <= 0:
            raise ValueError(f"Total area must be positive, got {self.total_area}")
        if self.suitable_area < 0:
            raise ValueError(f"Suitable area cannot be negative, got {self.suitable_area}")


