"""
Domain policies for wind suitability analysis.

This module contains the business rules and policies for
normalization, scoring, and threshold calculations.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from .entities import Criterion


class NormalizationPolicy:
    """Policy for normalizing criterion values."""
    
    @staticmethod
    def minmax_normalize(values: np.ndarray, is_benefit: bool = True) -> np.ndarray:
        """
        Apply min-max normalization to values.
        
        Args:
            values: Array of values to normalize
            is_benefit: True for benefit criteria (higher is better),
                       False for cost criteria (lower is better)
        
        Returns:
            Normalized values between 0 and 1
        """
        if len(values) == 0:
            return values
        
        min_val = np.nanmin(values)
        max_val = np.nanmax(values)
        
        if min_val == max_val:
            return np.ones_like(values) * 0.5
        
        if is_benefit:
            # For benefit criteria: (value - min) / (max - min)
            normalized = (values - min_val) / (max_val - min_val)
        else:
            # For cost criteria: (max - value) / (max - min)
            normalized = (max_val - values) / (max_val - min_val)
        
        return np.clip(normalized, 0, 1)
    
    @staticmethod
    def zscore_normalize(values: np.ndarray, is_benefit: bool = True) -> np.ndarray:
        """
        Apply z-score normalization to values.
        
        Args:
            values: Array of values to normalize
            is_benefit: True for benefit criteria (higher is better),
                       False for cost criteria (lower is better)
        
        Returns:
            Normalized values (not necessarily between 0 and 1)
        """
        if len(values) == 0:
            return values
        
        mean_val = np.nanmean(values)
        std_val = np.nanstd(values)
        
        if std_val == 0:
            return np.ones_like(values) * 0.5
        
        z_scores = (values - mean_val) / std_val
        
        if is_benefit:
            # For benefit criteria: higher z-scores are better
            normalized = (z_scores - np.nanmin(z_scores)) / (np.nanmax(z_scores) - np.nanmin(z_scores))
        else:
            # For cost criteria: lower z-scores are better
            normalized = (np.nanmax(z_scores) - z_scores) / (np.nanmax(z_scores) - np.nanmin(z_scores))
        
        return np.clip(normalized, 0, 1)
    
    @staticmethod
    def normalize_criterion(values: np.ndarray, criterion: Criterion) -> np.ndarray:
        """
        Normalize values according to criterion specifications.
        
        Args:
            values: Array of values to normalize
            criterion: Criterion entity with normalization settings
        
        Returns:
            Normalized values
        """
        if criterion.normalization_method == "minmax":
            return NormalizationPolicy.minmax_normalize(values, criterion.is_benefit)
        elif criterion.normalization_method == "zscore":
            return NormalizationPolicy.zscore_normalize(values, criterion.is_benefit)
        else:
            raise ValueError(f"Unknown normalization method: {criterion.normalization_method}")


class ScoringPolicy:
    """Policy for calculating wind suitability scores."""
    
    @staticmethod
    def weighted_sum(normalized_layers: Dict[str, np.ndarray], 
                    weights: Dict[str, float]) -> np.ndarray:
        """
        Calculate weighted sum of normalized layers.
        
        Args:
            normalized_layers: Dictionary of normalized criterion arrays
            weights: Dictionary of criterion weights
        
        Returns:
            Wind Suitability Index (WSI) array
        """
        if not normalized_layers:
            raise ValueError("No normalized layers provided")
        
        if not weights:
            raise ValueError("No weights provided")
        
        # Ensure all layers have the same shape
        shapes = [layer.shape for layer in normalized_layers.values()]
        if len(set(shapes)) > 1:
            raise ValueError("All layers must have the same shape")
        
        # Calculate weighted sum
        wsi = np.zeros_like(list(normalized_layers.values())[0])
        
        for criterion_name, normalized_values in normalized_layers.items():
            if criterion_name in weights:
                weight = weights[criterion_name]
                wsi += weight * normalized_values
        
        return np.clip(wsi, 0, 1)
    
    @staticmethod
    def calculate_viability_percentage(wsi_values: np.ndarray, 
                                     threshold: float = 0.5) -> float:
        """
        Calculate viability percentage based on WSI threshold.
        
        Args:
            wsi_values: Array of WSI values
            threshold: WSI threshold for viability (default: 0.5)
        
        Returns:
            Percentage of viable cells
        """
        if len(wsi_values) == 0:
            return 0.0
        
        valid_values = wsi_values[~np.isnan(wsi_values)]
        if len(valid_values) == 0:
            return 0.0
        
        viable_count = np.sum(valid_values >= threshold)
        total_count = len(valid_values)
        
        return (viable_count / total_count) * 100


class ThresholdPolicy:
    """Policy for determining thresholds and cutoffs."""
    
    @staticmethod
    def calculate_top_percent_threshold(values: np.ndarray, 
                                      top_percent: float) -> float:
        """
        Calculate threshold for top percentage of values.
        
        Args:
            values: Array of values
            top_percent: Percentage of top values to select (0-1)
        
        Returns:
            Threshold value
        """
        if len(values) == 0:
            return 0.0
        
        if not 0 < top_percent <= 1:
            raise ValueError(f"Top percent must be between 0 and 1, got {top_percent}")
        
        valid_values = values[~np.isnan(values)]
        if len(valid_values) == 0:
            return 0.0
        
        # Calculate percentile threshold
        percentile = (1 - top_percent) * 100
        threshold = np.percentile(valid_values, percentile)
        
        return threshold
    
    @staticmethod
    def get_top_sites_mask(wsi_values: np.ndarray, 
                          top_percent: float) -> np.ndarray:
        """
        Get boolean mask for top percentage of sites.
        
        Args:
            wsi_values: Array of WSI values
            top_percent: Percentage of top values to select (0-1)
        
        Returns:
            Boolean mask for top sites
        """
        if len(wsi_values) == 0:
            return np.zeros_like(wsi_values, dtype=bool)
        
        threshold = ThresholdPolicy.calculate_top_percent_threshold(
            wsi_values, top_percent
        )
        
        return (wsi_values >= threshold) & ~np.isnan(wsi_values)


class ValidationPolicy:
    """Policy for validating data and results."""
    
    @staticmethod
    def validate_wind_data(wind_values: np.ndarray) -> Tuple[bool, str]:
        """
        Validate wind data quality.
        
        Args:
            wind_values: Array of wind speed values
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(wind_values) == 0:
            return False, "Wind data is empty"
        
        valid_values = wind_values[~np.isnan(wind_values)]
        if len(valid_values) == 0:
            return False, "No valid wind data found"
        
        # Check for reasonable wind speed range (0-50 m/s)
        if np.any(valid_values < 0):
            return False, "Wind speeds cannot be negative"
        
        if np.any(valid_values > 50):
            return False, "Wind speeds seem unreasonably high (>50 m/s)"
        
        # Check for sufficient data coverage
        coverage = len(valid_values) / len(wind_values)
        if coverage < 0.5:
            return False, f"Wind data coverage too low: {coverage:.1%}"
        
        return True, ""
    
    @staticmethod
    def validate_slope_data(slope_values: np.ndarray) -> Tuple[bool, str]:
        """
        Validate slope data quality.
        
        Args:
            slope_values: Array of slope values in degrees
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(slope_values) == 0:
            return False, "Slope data is empty"
        
        valid_values = slope_values[~np.isnan(slope_values)]
        if len(valid_values) == 0:
            return False, "No valid slope data found"
        
        # Check for reasonable slope range (0-90 degrees)
        if np.any(valid_values < 0):
            return False, "Slopes cannot be negative"
        
        if np.any(valid_values > 90):
            return False, "Slopes cannot exceed 90 degrees"
        
        return True, ""
    
    @staticmethod
    def validate_wsi_result(wsi_values: np.ndarray) -> Tuple[bool, str]:
        """
        Validate WSI calculation result.
        
        Args:
            wsi_values: Array of WSI values
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(wsi_values) == 0:
            return False, "WSI result is empty"
        
        valid_values = wsi_values[~np.isnan(wsi_values)]
        if len(valid_values) == 0:
            return False, "No valid WSI values found"
        
        # Check WSI range (should be 0-1)
        if np.any(valid_values < 0) or np.any(valid_values > 1):
            return False, f"WSI values out of range [0,1]: min={np.min(valid_values):.3f}, max={np.max(valid_values):.3f}"
        
        return True, ""


