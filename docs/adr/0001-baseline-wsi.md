# ADR-0001: Baseline Wind Suitability Index (WSI) Implementation

## Status
**Accepted** - 2024-01-15

## Context

The Vento Wind GIS Technology Validation project requires a baseline implementation of wind suitability analysis using multicriteria decision making (MCDM). This decision establishes the fundamental approach for calculating the Wind Suitability Index (WSI) and sets the foundation for technology comparison and validation.

## Decision

We will implement a baseline WSI calculation using the **weighted sum method** with the following characteristics:

### Core Methodology
- **MCDM Method**: Weighted Sum (WSM)
- **Normalization**: Min-Max normalization
- **Criteria**: Wind speed, terrain slope, grid distance
- **Weights**: Wind (60%), Slope (20%), Grid Distance (20%)
- **Output**: Continuous suitability index (0-1)

### Technical Implementation
- **Architecture**: Clean Architecture with domain-driven design
- **Primary Engine**: Python with rasterio
- **Alternative Engines**: QGIS (PyQGIS), ArcGIS (ArcPy)
- **Data Format**: GeoTIFF for rasters, GeoPackage for vectors
- **Visualization**: Folium for interactive maps

### Quality Assurance
- **Validation**: Input data range and coverage checks
- **Verification**: WSI value range (0-1) validation
- **Testing**: Unit tests for all core functions
- **Documentation**: Comprehensive methodology documentation

## Rationale

### Why Weighted Sum Method?
1. **Simplicity**: Easy to understand and implement
2. **Transparency**: Clear relationship between inputs and outputs
3. **Flexibility**: Easy to adjust weights for different scenarios
4. **Literature Support**: Widely used in wind energy assessments
5. **Baseline**: Provides foundation for comparing other methods

### Why Min-Max Normalization?
1. **Range Consistency**: All criteria normalized to [0,1] range
2. **Interpretability**: Easy to understand normalized values
3. **Stability**: Robust to outliers
4. **Efficiency**: Fast computation
5. **Standard Practice**: Commonly used in MCDM applications

### Why These Criteria?
1. **Wind Speed**: Primary factor for wind energy potential
2. **Terrain Slope**: Affects turbine installation feasibility
3. **Grid Distance**: Proximity to electrical infrastructure
4. **Balance**: Covers technical, economic, and practical factors
5. **Data Availability**: Commonly available datasets

### Why These Weights?
1. **Wind Dominance**: Wind speed is the most important factor
2. **Balanced Approach**: Equal weight for slope and grid factors
3. **Literature Review**: Based on wind energy assessment studies
4. **Sensitivity**: Allows for weight sensitivity analysis
5. **Configurability**: Easy to adjust for different scenarios

## Consequences

### Positive
- **Clear Baseline**: Establishes reference implementation
- **Comparability**: Enables technology comparison
- **Reproducibility**: Well-documented methodology
- **Flexibility**: Configurable parameters
- **Extensibility**: Foundation for advanced methods

### Negative
- **Simplification**: May not capture all complexities
- **Assumptions**: Linear relationships assumed
- **Static**: No temporal dynamics considered
- **Limited**: Only three criteria included
- **Subjectivity**: Weight selection is subjective

### Risks
- **Oversimplification**: May miss important factors
- **Bias**: Weight selection may introduce bias
- **Validation**: Requires extensive validation
- **Maintenance**: Need to update as knowledge evolves
- **Acceptance**: Stakeholder acceptance required

## Alternatives Considered

### 1. Analytic Hierarchy Process (AHP)
**Pros**: Structured decision-making, pairwise comparisons
**Cons**: Complex implementation, subjective judgments
**Decision**: Rejected for baseline, consider for future

### 2. Technique for Order Preference by Similarity to Ideal Solution (TOPSIS)
**Pros**: Considers ideal and anti-ideal solutions
**Cons**: More complex than weighted sum
**Decision**: Rejected for baseline, consider for future

### 3. Elimination and Choice Expressing Reality (ELECTRE)
**Pros**: Handles non-compensatory criteria
**Cons**: Complex implementation, difficult to interpret
**Decision**: Rejected for baseline, consider for future

### 4. Fuzzy Logic
**Pros**: Handles uncertainty and imprecision
**Cons**: Complex implementation, difficult to validate
**Decision**: Rejected for baseline, consider for future

## Implementation Plan

### Phase 1: Core Implementation (Weeks 1-2)
- [x] Domain entities and policies
- [x] Use cases for WSI computation
- [x] Infrastructure adapters
- [x] CLI interface
- [x] Basic testing

### Phase 2: Validation and Testing (Weeks 3-4)
- [ ] Comprehensive test suite
- [ ] Data validation procedures
- [ ] Performance benchmarking
- [ ] Documentation completion
- [ ] User acceptance testing

### Phase 3: Technology Comparison (Weeks 5-6)
- [ ] QGIS implementation
- [ ] ArcGIS implementation
- [ ] Performance comparison
- [ ] Accuracy assessment
- [ ] Usability evaluation

### Phase 4: Documentation and Deployment (Weeks 7-8)
- [ ] Methodology documentation
- [ ] Technology comparison matrix
- [ ] Deployment procedures
- [ ] Training materials
- [ ] Final validation

## Success Criteria

### Technical
- [ ] WSI values range from 0 to 1
- [ ] Processing time < 5 minutes for 1GB data
- [ ] Memory usage < 4GB peak
- [ ] All tests pass
- [ ] Documentation complete

### Functional
- [ ] Configurable weights and thresholds
- [ ] Multiple output formats
- [ ] Interactive visualization
- [ ] Performance metrics
- [ ] Error handling

### Quality
- [ ] Code coverage > 80%
- [ ] Documentation coverage > 90%
- [ ] User acceptance > 80%
- [ ] Performance within targets
- [ ] No critical bugs

## Monitoring and Review

### Metrics
- **Processing Time**: Track computation duration
- **Memory Usage**: Monitor RAM consumption
- **Accuracy**: Validate against known results
- **Usability**: User feedback and testing
- **Maintenance**: Bug reports and updates

### Review Schedule
- **Weekly**: Progress review
- **Monthly**: Performance assessment
- **Quarterly**: Methodology review
- **Annually**: Technology comparison update

## References

1. Saaty, T.L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
2. Malczewski, J. (1999). GIS and Multicriteria Decision Analysis. John Wiley & Sons.
3. International Energy Agency (2020). Wind Energy Technology Roadmap.
4. National Renewable Energy Laboratory (2018). Wind Resource Assessment Handbook.
5. European Wind Energy Association (2019). Wind Energy - The Facts.

---

**Decision Makers**: Vento Technical Team
**Stakeholders**: Wind Energy Researchers, GIS Professionals, Policy Makers
**Review Date**: 2024-04-15
**Next Review**: 2024-07-15




