# Wind Suitability Analysis Methodology

## Overview

This document describes the methodology for wind suitability analysis using multicriteria decision making (MCDM) for wind energy site assessment.

## Input Data Requirements

The analysis requires:
- **Wind Speed Data**: Raster data with wind speed at 100m height (m/s)
- **Digital Elevation Model (DEM)**: Terrain elevation data for slope calculation
- **Electrical Grid Infrastructure**: Vector data of transmission lines and substations
- **Area of Interest (AOI)**: Polygon defining the analysis extent

## Criteria and Formulas

### Wind Speed Criterion
**Weight**: 0.6 (60% of total suitability)
```
WSI_wind = (V_wind - V_min) / (V_max - V_min)
```

### Terrain Slope Criterion
**Weight**: 0.2 (20% of total suitability)
```
WSI_slope = (S_max - S_slope) / (S_max - S_min)
```

### Grid Distance Criterion
**Weight**: 0.2 (20% of total suitability)
```
WSI_grid = (D_max - D_grid) / (D_max - D_min)
```

## Wind Suitability Index (WSI)

The final WSI is calculated using the weighted sum method:

```
WSI = (0.6 × WSI_wind) + (0.2 × WSI_slope) + (0.2 × WSI_grid)
```

## WSI Classification

| WSI Range | Suitability Level |
|-----------|------------------|
| 0.8 - 1.0 | Excellent |
| 0.6 - 0.8 | High |
| 0.4 - 0.6 | Good |
| 0.2 - 0.4 | Fair |
| 0.0 - 0.2 | Poor |

## Viability Assessment

```
Viability = (Suitable Cells / Total Cells) × 100
```

Where:
- Suitable Cells = cells with WSI ≥ threshold
- Total Cells = total valid cells in analysis

## Outputs

- **WSI Raster**: GeoTIFF with suitability values
- **Interactive Maps**: HTML with Folium visualization
- **Reports**: HTML with analysis results and statistics



