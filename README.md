# IndiaMetrics: Demographic Data Dashboard


An end-to-end data pipeline and interactive analytics dashboard designed to explore, visualize, and unravel the demographic-economic transition across India's states and districts.

### **[View the Live Dashboard Here!](https://indiametrics.streamlit.app)**

---

## Project Overview
**IndiaMetrics** creates massive datasets combining data from the Indian Government's official Census, the World Bank, and DLHS into a sleek, highly interactive, and multivariate dashboard. Rather than siloed reports, this tool empowers researchers, policymakers, and the public to analyze regional disparities right in their browser.

---

## Key Features

* **National Demographic Overview**: High-level statistical summaries, dynamic Age Pyramids, historic Life Expectancy curves, and crude birth/death rate trends mapped from 1960 to 2025.
* **State-Level Trajectories**: Interactive state-wise comparisons of Total Fertility Rates (TFR), Literacy Improvements, Per-Capita Income growth, and multivariate radar charts benchmarking socio-economic well-being.
* **District Explorer**: Deep-dive choropleth maps rendering data at the granularity of over 600 Indian districts. Visualize geographical clustering for metrics like the Rural-Urban literacy gap and sex ratio imbalances.
* **Insights & Correlations**: Instantly compute and visualize Pearson correlations to prove out theories (e.g., the negative correlation between female literacy and fertility rates).
* **Composite Demographic Health Index**: A synthesized index score mapped geographically to approximate human development performance.

---

## How to Run Locally

If you'd like to explore the data pipeline and run the application on your own machine:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/DS-Practice-2026-Team-3.git
   cd DS-Practice-2026-Team-3
   ```

2. **Install Dependencies**
   Ensure you have Python 3.8+ installed. Install the required libraries:
   ```bash
   pip install streamlit pandas numpy plotly geopandas matplotlib
   ```

3. **Run the Dashboard**
   Boot up the Streamlit server locally:
   ```bash
   streamlit run dashboard_v3.py
   ```
   The application will automatically open in your web browser at `http://localhost:8501`.

---

## Data Sources

This project relies on merging robust public datasets using common geographic identifiers. Key datasets include:

| Domain | Source | Description |
|--------|--------|-------------|
| **Population** | Census 2001, 2011 | Absolute numbers, rural/urban splits, sex ratios |
| **Economic** | data.gov | State-wise GDP (constant pricing) and Per-Capita Income |
| **Healthcare** | DLHS, SRS, World Bank | TFR, MCPR, mortality rates, and life expectancy |
| **Literacy** | Census 2011, 2001 | Male/Female literacy rates and temporal gains |
| **Mobility** | VAHAN Registry | EV & CNG Market share tracking |

---

## Team Members

* **Gaurav Chandan**
* **Soumya Ranjan**
* **Shweta Shankar**
* **Dheeraj Kumar Gehlot**

*Mini Project for DS3294: Data Science Practice*
