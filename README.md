# Demographic Data Dashboard for India

Short description:

This project builds an end-to-end data pipeline to ingest, clean, analyze, and visualize demographic data for India. The dashboard enables comparison across states using indicators from population, economic, healthcare, and food datasets.

---

# 2. Team Members

- Gaurav Chandan     
- Soumya Ranjan
- Shweta Shankar
- Dheeraj Kumar Gehlot
---

# 3. Project Objective

The goal of this project is to analyze demographic patterns across India using datasets from multiple sectors including:

- Population
- Economy
- Healthcare
- Literacy and Urbanisation

We aim to build an interactive dashboard that helps users explore regional disparities and relationships between these indicators.

---

# 4. Data Sources

| Dataset | Source | Description |
|--------|--------|-------------|
| Population | Census 2001,2011 | Population by state/district |
| Economic | data.gov | Income, GDP |
| Healthcare | data.gov | mortality,fertility |
| Literacy and Urbanisation | data.gov | literacy rate, population data |

---

# 5. Data Preprocessing Plan

## 5.1 Data Cleaning
- Standardize column names
- Remove duplicate records
- Handle missing values

## 5.2 Data Standardization
- Standardize state/district names
- Convert columns to correct data types

## 5.3 Normalization
Convert absolute values into comparable indicators such as:

- GDP per capita
- literacy rate statewise
- Income in rural v/s urban

## 5.4 Dataset Integration
Merge datasets using common geographic identifiers (state or district).

---

# 6. Planned Analysis

## Population Analysis
- Population distribution
- Population density

## Economic Analysis
- Income vs population
- Poverty rates by region

## Healthcare Analysis
- Fertility distrivt-wise
- Mortality indicators

--

# 7. Visualization Plan

Planned visualizations include:

- Choropleth of demographic indicators
- Bar charts comparing states
- Scatter plots showing correlations
- Time-series plots 

---

# 8. Code Structure Plan


Short description:

This project builds an end-to-end data pipeline to ingest, clean, analyze, and visualize demographic data for India. The dashboard enables comparison across states using indicators from population, economic, healthcare, and food datasets.

---

# 2. Team Members

**Team Name:** _______

**Members:**
- Name 1
- Name 2
- Name 3
- Name 4

---

# 3. Project Objective

The goal of this project is to analyze demographic patterns across India using datasets from multiple sectors including:

- Population
- Economy
- Healthcare
- Food

We aim to build an interactive dashboard that helps users explore regional disparities and relationships between these indicators.

---

# 4. Data Sources

| Dataset | Source | Description |
|--------|--------|-------------|
| Population | (link) | Population by state/district |
| Economic | (link) | Income, GDP, employment |
| Healthcare | (link) | Hospitals, doctors, mortality |
| Food | (link) | Production, nutrition indicators |

Example sources:
- Population Data: Census of India  
- Economic Data: Government Open Data Portal  
- Healthcare Data: National Health Mission  
- Food Data: Ministry of Agriculture / FAOSTAT  

---

# 5. Data Preprocessing Plan

## 5.1 Data Cleaning
- Standardize column names
- Remove duplicate records
- Handle missing values

## 5.2 Data Standardization
- Standardize state/district names
- Convert columns to correct data types

## 5.3 Normalization
Convert absolute values into comparable indicators such as:

- GDP per capita
- Hospitals per 100k population
- Food production per capita

## 5.4 Dataset Integration
Merge datasets using common geographic identifiers (state or district).

---

# 6. Planned Analysis

## Population Analysis
- Population distribution
- Population density

## Economic Analysis
- Income vs population
- Poverty rates by region

## Healthcare Analysis
- Healthcare infrastructure per population
- Mortality indicators

## Food Analysis
- Food production vs population
- Malnutrition patterns

## Cross-sector Analysis
- Population vs healthcare access
- Poverty vs malnutrition
- Population density vs economic activity

---

# 7. Visualization Plan

Planned visualizations include:

- Choropleth maps of demographic indicators
- Bar charts comparing states
- Scatter plots showing correlations
- Time-series plots (if multi-year data available)

---
## 8. Code Structrure

- Create a single class whose objects will be initialised with the following variables describing the data it loads:
--> Granularity (State-wise, District-wise, etc.)
--> Indicators
--> Timescale (if applicable)
--> Data source

(Note: Clearly not all combinations of these variables can be accepted as inputs. The gui will be hard-coded to accept only compatible inputs.)

- Equip the class with methods to plot combinations of the loaded data in styles of the user's choosing

- Wrap the whole thing in an easy-to-use GUI.

