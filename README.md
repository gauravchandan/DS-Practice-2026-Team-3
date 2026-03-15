# Demographic Data Dashboard for India

Short description:

This project builds an end-to-end data pipeline to ingest, clean, analyze, and visualize demographic data for India. The dashboard enables comparison across states using indicators from population, economic, healthcare, and food datasets.

---

## Team Members

- Gaurav Chandan     
- Soumya Ranjan
- Shweta Shankar
- Dheeraj Kumar Gehlot
---

## Project Objective

The goal of this project is to analyze demographic patterns across India using datasets from multiple sectors including:

- Population
- Economy
- Healthcare
- Literacy and Urbanisation

We aim to build an interactive dashboard that helps users explore regional disparities and relationships between these indicators.

---

## Data Sources

| Dataset | Source | Description |
|--------|--------|-------------|
| Population | Census 2001,2011 | Population by state/district |
| Economic | data.gov | Income, GDP |
| Healthcare | data.gov | mortality,fertility |
| Literacy and Urbanisation | data.gov | literacy rate, population data |

---

## Data Preprocessing Plan

### Data Cleaning
- Standardize column names
- Remove duplicate records
- Handle missing values

### Data Standardization
- Standardize state/district names
- Convert columns to correct data types

### Normalization
Convert absolute values into comparable indicators such as:

- GDP per capita
- literacy rate statewise
- Income in rural v/s urban

### Dataset Integration
Merge datasets using common geographic identifiers (state or district).

---

## Planned Analysis

### Population Analysis
- Population distribution
- Population density

### Economic Analysis
- Income vs population
- Poverty rates by region

### Healthcare Analysis
- Fertility distrivt-wise
- Mortality indicators

--

## Visualization Plan

Planned visualizations include:

- Choropleth of demographic indicators
- Bar charts comparing states
- Scatter plots showing correlations
- Time-series plots 

---
## Code Structrure

1. Create a single class whose objects will be initialised with the following variables describing the data it loads:
- Granularity (State-wise, District-wise, etc.)
- Indicators
- Timescale (if applicable)
-  Data source

(Note: Clearly not all combinations of these variables can be accepted as inputs. The gui will be hard-coded to accept only compatible inputs.)

2. Equip the class with methods to plot combinations of the loaded data in styles of the user's choosing

3. Wrap the whole thing in an easy-to-use GUI.


