"""
Unit tests for multicriteria decision making (MCDM) functionality.

This module contains tests for the core MCDM algorithms and policies
used in wind suitability analysis.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.domain.entities import Criterion, WeightScheme, AOI, EngineType
from src.domain.policies import (
    NormalizationPolicy, ScoringPolicy, ThresholdPolicy, ValidationPolicy
)


class TestNormalizationPolicy:
    """Test cases for normalization policies."""
    
    def test_minmax_normalize_benefit_criterion(self):
        """Test min-max normalization for benefit criteria."""
        values = np.array([1, 2, 3, 4, 5])
        normalized = NormalizationPolicy.minmax_normalize(values, is_benefit=True)
        
        expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        np.testing.assert_array_almost_equal(normalized, expected)
    
    def test_minmax_normalize_cost_criterion(self):
        """Test min-max normalization for cost criteria."""
        values = np.array([1, 2, 3, 4, 5])
        normalized = NormalizationPolicy.minmax_normalize(values, is_benefit=False)
        
        expected = np.array([1.0, 0.75, 0.5, 0.25, 0.0])
        np.testing.assert_array_almost_equal(normalized, expected)
    
    def test_minmax_normalize_constant_values(self):
        """Test min-max normalization with constant values."""
        values = np.array([5, 5, 5, 5])
        normalized = NormalizationPolicy.minmax_normalize(values, is_benefit=True)
        
        expected = np.array([0.5, 0.5, 0.5, 0.5])
        np.testing.assert_array_almost_equal(normalized, expected)
    
    def test_minmax_normalize_empty_array(self):
        """Test min-max normalization with empty array."""
        values = np.array([])
        normalized = NormalizationPolicy.minmax_normalize(values, is_benefit=True)
        
        assert len(normalized) == 0
    
    def test_zscore_normalize_benefit_criterion(self):
        """Test z-score normalization for benefit criteria."""
        values = np.array([1, 2, 3, 4, 5])
        normalized = NormalizationPolicy.zscore_normalize(values, is_benefit=True)
        
        # Should be normalized to [0, 1] range
        assert np.all(normalized >= 0)
        assert np.all(normalized <= 1)
    
    def test_normalize_criterion(self):
        """Test criterion normalization."""
        values = np.array([1, 2, 3, 4, 5])
        criterion = Criterion(
            name="test",
            weight=0.5,
            file_path="test.tif",
            is_benefit=True,
            normalization_method="minmax"
        )
        
        normalized = NormalizationPolicy.normalize_criterion(values, criterion)
        expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        np.testing.assert_array_almost_equal(normalized, expected)


class TestScoringPolicy:
    """Test cases for scoring policies."""
    
    def test_weighted_sum(self):
        """Test weighted sum calculation."""
        normalized_layers = {
            "wind": np.array([0.8, 0.6, 0.4]),
            "slope": np.array([0.9, 0.7, 0.5]),
            "grid": np.array([0.6, 0.8, 0.9])
        }
        weights = {
            "wind": 0.6,
            "slope": 0.2,
            "grid": 0.2
        }
        
        wsi = ScoringPolicy.weighted_sum(normalized_layers, weights)
        
        expected = np.array([0.8*0.6 + 0.9*0.2 + 0.6*0.2,
                           0.6*0.6 + 0.7*0.2 + 0.8*0.2,
                           0.4*0.6 + 0.5*0.2 + 0.9*0.2])
        
        np.testing.assert_array_almost_equal(wsi, expected)
    
    def test_weighted_sum_missing_weights(self):
        """Test weighted sum with missing weights."""
        normalized_layers = {
            "wind": np.array([0.8, 0.6]),
            "slope": np.array([0.9, 0.7])
        }
        weights = {
            "wind": 0.6
            # Missing slope weight
        }
        
        with pytest.raises(ValueError):
            ScoringPolicy.weighted_sum(normalized_layers, weights)
    
    def test_calculate_viability_percentage(self):
        """Test viability percentage calculation."""
        wsi_values = np.array([0.3, 0.5, 0.7, 0.9, 0.4])
        viability = ScoringPolicy.calculate_viability_percentage(wsi_values, threshold=0.5)
        
        # 3 out of 5 values >= 0.5
        expected = 60.0
        assert viability == expected
    
    def test_calculate_viability_percentage_empty(self):
        """Test viability percentage with empty array."""
        wsi_values = np.array([])
        viability = ScoringPolicy.calculate_viability_percentage(wsi_values)
        
        assert viability == 0.0


class TestThresholdPolicy:
    """Test cases for threshold policies."""
    
    def test_calculate_top_percent_threshold(self):
        """Test top percent threshold calculation."""
        values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        threshold = ThresholdPolicy.calculate_top_percent_threshold(values, top_percent=0.2)
        
        # Top 20% should be 0.8 and above
        assert threshold == 0.8
    
    def test_calculate_top_percent_threshold_invalid_percent(self):
        """Test top percent threshold with invalid percentage."""
        values = np.array([0.1, 0.2, 0.3])
        
        with pytest.raises(ValueError):
            ThresholdPolicy.calculate_top_percent_threshold(values, top_percent=1.5)
    
    def test_get_top_sites_mask(self):
        """Test top sites mask generation."""
        wsi_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        mask = ThresholdPolicy.get_top_sites_mask(wsi_values, top_percent=0.2)
        
        # Top 20% should be 0.8 and above
        expected = np.array([False, False, False, False, False, False, False, True, True, True])
        np.testing.assert_array_equal(mask, expected)


class TestValidationPolicy:
    """Test cases for validation policies."""
    
    def test_validate_wind_data_valid(self):
        """Test wind data validation with valid data."""
        wind_values = np.array([3.5, 4.2, 5.1, 6.8, 7.2])
        is_valid, error_msg = ValidationPolicy.validate_wind_data(wind_values)
        
        assert is_valid
        assert error_msg == ""
    
    def test_validate_wind_data_negative(self):
        """Test wind data validation with negative values."""
        wind_values = np.array([3.5, -1.2, 5.1, 6.8, 7.2])
        is_valid, error_msg = ValidationPolicy.validate_wind_data(wind_values)
        
        assert not is_valid
        assert "negative" in error_msg.lower()
    
    def test_validate_wind_data_too_high(self):
        """Test wind data validation with unreasonably high values."""
        wind_values = np.array([3.5, 4.2, 55.1, 6.8, 7.2])
        is_valid, error_msg = ValidationPolicy.validate_wind_data(wind_values)
        
        assert not is_valid
        assert "high" in error_msg.lower()
    
    def test_validate_wind_data_low_coverage(self):
        """Test wind data validation with low coverage."""
        wind_values = np.array([3.5, np.nan, np.nan, np.nan, np.nan])
        is_valid, error_msg = ValidationPolicy.validate_wind_data(wind_values)
        
        assert not is_valid
        assert "coverage" in error_msg.lower()
    
    def test_validate_slope_data_valid(self):
        """Test slope data validation with valid data."""
        slope_values = np.array([5.2, 12.8, 25.1, 35.6, 45.2])
        is_valid, error_msg = ValidationPolicy.validate_slope_data(slope_values)
        
        assert is_valid
        assert error_msg == ""
    
    def test_validate_slope_data_negative(self):
        """Test slope data validation with negative values."""
        slope_values = np.array([5.2, -2.1, 25.1, 35.6, 45.2])
        is_valid, error_msg = ValidationPolicy.validate_slope_data(slope_values)
        
        assert not is_valid
        assert "negative" in error_msg.lower()
    
    def test_validate_slope_data_too_high(self):
        """Test slope data validation with values > 90 degrees."""
        slope_values = np.array([5.2, 12.8, 95.1, 35.6, 45.2])
        is_valid, error_msg = ValidationPolicy.validate_slope_data(slope_values)
        
        assert not is_valid
        assert "90" in error_msg
    
    def test_validate_wsi_result_valid(self):
        """Test WSI result validation with valid data."""
        wsi_values = np.array([0.2, 0.4, 0.6, 0.8, 0.9])
        is_valid, error_msg = ValidationPolicy.validate_wsi_result(wsi_values)
        
        assert is_valid
        assert error_msg == ""
    
    def test_validate_wsi_result_out_of_range(self):
        """Test WSI result validation with out-of-range values."""
        wsi_values = np.array([0.2, 0.4, 1.5, 0.8, 0.9])
        is_valid, error_msg = ValidationPolicy.validate_wsi_result(wsi_values)
        
        assert not is_valid
        assert "range" in error_msg.lower()


class TestEntities:
    """Test cases for domain entities."""
    
    def test_aoi_validation(self):
        """Test AOI entity validation."""
        # Valid AOI
        aoi = AOI(geometry="test.geojson", crs="EPSG:4326")
        assert aoi.geometry == "test.geojson"
        assert aoi.crs == "EPSG:4326"
        
        # Invalid AOI - empty geometry
        with pytest.raises(ValueError):
            AOI(geometry="", crs="EPSG:4326")
        
        # Invalid AOI - empty CRS
        with pytest.raises(ValueError):
            AOI(geometry="test.geojson", crs="")
    
    def test_criterion_validation(self):
        """Test Criterion entity validation."""
        # Valid criterion
        criterion = Criterion(
            name="wind",
            weight=0.6,
            file_path="wind.tif"
        )
        assert criterion.name == "wind"
        assert criterion.weight == 0.6
        
        # Invalid criterion - weight out of range
        with pytest.raises(ValueError):
            Criterion(
                name="wind",
                weight=1.5,
                file_path="wind.tif"
            )
    
    def test_weight_scheme_validation(self):
        """Test WeightScheme entity validation."""
        # Valid weight scheme
        weights = WeightScheme(wind=0.6, slope=0.2, grid_distance=0.2)
        assert weights.wind == 0.6
        assert weights.slope == 0.2
        assert weights.grid_distance == 0.2
        
        # Invalid weight scheme - weights don't sum to 1.0
        with pytest.raises(ValueError):
            WeightScheme(wind=0.6, slope=0.2, grid_distance=0.1)
    
    def test_engine_type_enum(self):
        """Test EngineType enum."""
        assert EngineType.PYTHON.value == "python"
        assert EngineType.PYQGIS.value == "pyqgis"
        assert EngineType.ARCPY.value == "arcpy"



