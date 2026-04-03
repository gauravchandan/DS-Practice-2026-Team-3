import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json
import os
import re

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Demographic Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ── Themes & CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: #0a0a0a !important; 
    color: #e2e8f0;
}
.stApp { background-color: #0a0a0a !important; }
[data-testid="stSidebar"] {
    background-color: #121217 !important;
    border-right: 1px solid #262626;
}
.metric-card {
    background: #141416;
    border-radius: 20px; padding: 24px; border: 1px solid #262626;
    display: flex; flex-direction: column; justify-content: center;
    position: relative; overflow: hidden; height: 100%; margin-bottom: 24px;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); border-color: #404040; }
.metric-title { font-size: 14px; color: #a3a3a3; font-weight: 500; margin-bottom: 8px; }
.metric-value { font-size: 32px; font-weight: 600; color: #ffffff; font-family: 'JetBrains Mono', monospace; }
.metric-subtitle { font-size: 12px; color: #737373; margin-top: 8px; }
.brand { font-size: 24px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px; padding: 20px 0; text-align: center; }
.brand span { color: #a78bfa; }
.section-title { font-size: 18px; font-weight: 500; color: #e5e5e5; margin-top: 32px; margin-bottom: 16px; border-bottom: 1px solid #262626; padding-bottom: 8px; }
.stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 20px; }
.stTabs [data-baseweb="tab"] { color: #a3a3a3; }
.stTabs [aria-selected="true"] { color: #a78bfa !important; }
</style>
""", unsafe_allow_html=True)

PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
GRID_COLOR = "#262626"
TEXT_COLOR = "#a3a3a3"

LABELS = {
    'Literacy_Rate': 'Literacy Rate (%)',
    'TFR_2011': 'Total Fertility Rate',
    'Total_Pop': 'Total Population',
    'Per_Capita': 'Per Capita Income (₹)',
    'Urban_Pct': 'Urbanisation Rate (%)',
    'Sex_Ratio': 'Sex Ratio (F per 1000 M)',
    'Gender_Gap_11': 'Male-Female Lit Gap (% pt)',
    'registrations': 'Absolute Vehicle Registrations',
    'Green_Pct': 'EV & CNG Market Share (%)',
    'Composite_Index': 'Composite Health Index (0-100)',
    'Infant_Mortality_Rate': 'Infant Mortality Rate',
    'Decadal_Change': 'Decadal Change in Sex Ratio',
    'Inc_Tot': 'Absolute Literacy Gain (%)',
    'Gap': 'Rural-Urban Literacy Gap (%)',
    'GDP_Lakh_Cr': 'GDP (Lakh Crore ₹)'
}

CHART_LAYOUT = dict(
    paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
    font=dict(family="Outfit", color=TEXT_COLOR, size=12),
    margin=dict(t=40, b=20, l=20, r=20),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_boundary():
    gdf = gpd.read_file(os.path.join(DATA_DIR, "india_compressed.geojson"))
    gdf['geometry'] = gdf['geometry'].buffer(0)
    return gdf.dissolve()

@st.cache_data
def load_data():
    df_pivot = pd.read_csv(os.path.join(DATA_DIR, "df_pivot.csv"))
    df_pivot['pc11_d_id'] = df_pivot['pc11_d_id'].astype(int).apply(lambda x: str(x).zfill(3))
    if 'Sex_Ratio' not in df_pivot.columns: df_pivot['Sex_Ratio'] = 943
    
    with open(os.path.join(DATA_DIR, "india_compressed.geojson")) as f:
        geojson = json.load(f)
        
    df_lit = pd.read_csv(os.path.join(DATA_DIR, "State-wise_literacy_rates_and_increase-in_literacy_rates_as_per_Census_during_2001_and_2011.csv"))
    df_lit = df_lit[df_lit['S. No.'] != 'INDIA'].copy()
    df_lit.columns = ['S.No', 'State','Lit_Tot_01','Lit_Tot_11','Lit_M_01','Lit_M_11','Lit_F_01','Lit_F_11','Inc_Tot','Inc_M','Inc_F']
    df_lit['State'] = df_lit['State'].str.strip()
    
    df_ru = pd.read_csv(os.path.join(DATA_DIR, "State_UT-wise_Rural_and_Urban_Population_as_Per_Census_during_2001_and_2011.csv"))
    df_ru.columns = ['S.No', 'State', 'R_Pop_01', 'U_Pop_01', 'Tot_Pop_01', 'R_Pct_01', 'R_Pop_11', 'U_Pop_11', 'Tot_Pop_11', 'R_Pct_11', 'Note']
    df_ru['State'] = df_ru['State'].str.strip()
    df_ru['U_Pct_11'] = 100 - df_ru['R_Pct_11']
    
    df_state = pd.merge(df_lit, df_ru, on='State', how='outer')
    df_state['Gender_Gap_11'] = df_state['Lit_M_11'] - df_state['Lit_F_11']
    
    df_gdp = pd.read_excel(os.path.join(DATA_DIR, "State_GDP_Map_1773382936775.xlsx"))
    df_gdp = df_gdp.dropna(subset=['State', 'Year'])
    df_gdp.rename(columns={'Price (in Rs.Lakh Crore)': 'GDP_Lakh_Cr'}, inplace=True)
    df_gdp_cons = df_gdp[df_gdp['Price Category'] == 'constant'].copy()
    
    df_pc = pd.read_excel(os.path.join(DATA_DIR, "Per_Capita_Income_1773575689370.xlsx"))
    df_pc = df_pc.dropna(subset=['State', 'Year'])
    df_pc.rename(columns={'Price (in ₹)': 'Per_Capita'}, inplace=True)
    
    df_ages = pd.read_csv(os.path.join(DATA_DIR, "Ages.csv")).replace('..', np.nan)
    for col in df_ages.columns:
        if col != 'Year':
            df_ages[col] = pd.to_numeric(df_ages[col], errors='coerce')
            
    df_dlhs = pd.read_csv(os.path.join(DATA_DIR, "Fertility (%) - DLHS IV.csv")).replace('NA', np.nan)
    for col in df_dlhs.columns[2:]:
        df_dlhs[col] = pd.to_numeric(df_dlhs[col], errors='coerce')
        
    df_tfr_ts = pd.read_csv(os.path.join(DATA_DIR, "tfr_timeseries.csv"))
    df_mcpr = pd.read_csv(os.path.join(DATA_DIR, "tfr_mcpr_2011.csv"))
    df_gmfr = pd.read_csv(os.path.join(DATA_DIR, "gmfr_tmfr.csv"))
    df_sr_dist = pd.read_csv(os.path.join(DATA_DIR, "district_sex_ratio.csv"))

    parsed_data = []
    years = [str(y) for y in range(1971, 2011)]
    try:
        with open(os.path.join(DATA_DIR, "Total_Fertility_Rate_India_2011.csv"), 'r') as f:
            lines = f.readlines()
        for line in lines[1:]:
            if not line.strip(): continue
            parts = line.split()
            if len(parts) >= 40:
                rest = line.strip().split(maxsplit=1)[1]
                tail_vals = rest.split()[-39:]
                head_str = rest.rsplit(None, 39)[0].strip()
                m2 = re.search(r"^(.*?)(\d+\.?\d*)$", head_str)
                state = m2.group(1).strip() if m2 else head_str
                val_71 = m2.group(2).strip() if m2 else '0'
                parsed_data.append([state, float(val_71)] + [float(v) for v in tail_vals])
        df_tfr_2011 = pd.DataFrame(parsed_data, columns=['State'] + years).replace(0, np.nan)
    except Exception:
        df_tfr_2011 = pd.DataFrame()

    try:
        df_vahan = pd.read_csv(os.path.join(DATA_DIR, "vahan_cleaned.csv"))
        df_vahan['date'] = pd.to_datetime(df_vahan['date'], errors='coerce')
        df_vahan['year'] = pd.to_numeric(df_vahan['year'], errors='coerce')
        df_vahan_state = df_vahan.groupby(['state_name', 'fuel_type', 'year'])['registrations'].sum().reset_index()
    except Exception:
        df_vahan = pd.DataFrame()
        df_vahan_state = pd.DataFrame()

    try:
        df_wb = pd.read_csv(os.path.join(DATA_DIR, "WorldBank_Final.csv")).replace('..', np.nan)
        df_wb_melt = df_wb.melt(id_vars=['Series Name'], var_name='YearRaw', value_name='Value')
        df_wb_melt['Year'] = df_wb_melt['YearRaw'].str.extract(r'(\d{4})').astype(float)
        df_wb_melt['Value'] = pd.to_numeric(df_wb_melt['Value'], errors='coerce')
        df_wb_melt['Value'] = df_wb_melt.groupby('Series Name')['Value'].transform(lambda x: x.interpolate(limit_direction='both'))
        df_wb_wide = df_wb_melt.dropna(subset=['Year']).pivot(index='Year', columns='Series Name', values='Value').reset_index()
    except Exception:
        df_wb_wide = pd.DataFrame()

    return df_pivot, geojson, df_state, df_gdp_cons, df_pc, df_ages, df_dlhs, df_tfr_ts, df_mcpr, df_gmfr, df_sr_dist, df_tfr_2011, df_vahan, df_vahan_state, df_wb_wide

df_pivot, geojson, df_state, df_gdp, df_pc, df_ages, df_dlhs, df_tfr_ts, df_mcpr, df_gmfr, df_sr_dist, df_tfr_2011, df_vahan, df_vahan_state, df_wb_wide = load_data()
df_mcpr = df_mcpr[~df_mcpr['State'].str.upper().isin(['INDIA', 'ALL INDIA'])]
df_pivot = df_pivot[~df_pivot['State'].str.upper().isin(['INDIA', 'ALL INDIA'])]

def clean_state(s):
    if not isinstance(s, str): return s
    s = s.strip().title().replace('&', 'And')
    s = s.replace('Nct Of Delhi', 'Delhi').replace('The Nct Of Delhi', 'Delhi')
    s = s.replace('Islands', '').strip() # e.g. Andaman and Nicobar
    return s

for _df in [df_pivot, df_state, df_gdp, df_pc, df_mcpr, df_gmfr, df_tfr_2011]:
    if not _df.empty and 'State' in _df.columns:
        _df['State'] = _df['State'].apply(clean_state)

# Duplicate Andhra Pradesh to Telangana for legacy state-level datasets missing Telangana
if not df_state.empty and 'Telangana' not in df_state['State'].values and 'Andhra Pradesh' in df_state['State'].values:
    df_state = pd.concat([df_state, df_state[df_state['State'] == 'Andhra Pradesh'].assign(State='Telangana')], ignore_index=True)
if not df_gdp.empty and 'Telangana' not in df_gdp['State'].values and 'Andhra Pradesh' in df_gdp['State'].values:
    df_gdp = pd.concat([df_gdp, df_gdp[df_gdp['State'] == 'Andhra Pradesh'].assign(State='Telangana')], ignore_index=True)
if not df_pc.empty and 'Telangana' not in df_pc['State'].values and 'Andhra Pradesh' in df_pc['State'].values:
    df_pc = pd.concat([df_pc, df_pc[df_pc['State'] == 'Andhra Pradesh'].assign(State='Telangana')], ignore_index=True)
if not df_mcpr.empty and 'Telangana' not in df_mcpr['State'].values and 'Andhra Pradesh' in df_mcpr['State'].values:
    df_mcpr = pd.concat([df_mcpr, df_mcpr[df_mcpr['State'] == 'Andhra Pradesh'].assign(State='Telangana')], ignore_index=True)
if not df_gmfr.empty and 'Telangana' not in df_gmfr['State'].values and 'Andhra Pradesh' in df_gmfr['State'].values:
    df_gmfr = pd.concat([df_gmfr, df_gmfr[df_gmfr['State'] == 'Andhra Pradesh'].assign(State='Telangana')], ignore_index=True)
if not df_tfr_2011.empty and 'Telangana' not in df_tfr_2011['State'].values and 'Andhra Pradesh' in df_tfr_2011['State'].values:
    df_tfr_2011 = pd.concat([df_tfr_2011, df_tfr_2011[df_tfr_2011['State'] == 'Andhra Pradesh'].assign(State='Telangana')], ignore_index=True)

india_boundary = load_boundary()

def get_boundary_trace(india_boundary):
    boundary_geom = india_boundary.geometry.iloc[0]
    lons, lats = [], []
    if boundary_geom.geom_type == 'MultiPolygon':
        for poly in boundary_geom.geoms:
            coords = list(poly.exterior.coords)
            lons += [c[0] for c in coords] + [None]
            lats += [c[1] for c in coords] + [None]
    else:
        coords = list(boundary_geom.exterior.coords)
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
    return go.Scattermapbox(lon=lons, lat=lats, mode='lines', line=dict(color='#cbd5e1', width=1.0), hoverinfo='skip', showlegend=False)

def build_choropleth(df_target, location_col, color_col, title, hover_data=None, theme_scale=None):
    fig = px.choropleth_mapbox(
        df_target, geojson=geojson, featureidkey='properties.pc11_d_id',
        locations=location_col, color=color_col,
        color_continuous_scale=theme_scale, 
        hover_name='District_Name' if 'District_Name' in df_target.columns else 'State',
        hover_data=hover_data,
        mapbox_style="carto-darkmatter"
    )
    if 'geometry' in india_boundary.columns:
        fig.add_trace(get_boundary_trace(india_boundary))
        
    lons, lats = [], []
    target_ids = set(df_target[location_col].astype(str).tolist())
    for f in geojson.get('features', []):
        if str(f.get('properties', {}).get('pc11_d_id')) in target_ids:
            geom = f.get('geometry')
            if not geom: continue
            geom_type = geom.get('type')
            coords = geom.get('coordinates', [])
            if geom_type == 'Polygon':
                for ring in coords:
                    for pt in ring:
                        lons.append(pt[0]); lats.append(pt[1])
            elif geom_type == 'MultiPolygon':
                for poly in coords:
                    for ring in poly:
                        for pt in ring:
                            lons.append(pt[0]); lats.append(pt[1])
                            
    base_layout = dict(
        margin={"r":0,"t":40,"l":0,"b":0}, height=500, 
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        title=title, title_font=dict(color="#e5e5e5")
    )
    
    if lons and lats:
        lon_pad = (max(lons) - min(lons)) * 0.05
        lat_pad = (max(lats) - min(lats)) * 0.05
        bounds = {
            "west": min(lons) - lon_pad,
            "east": max(lons) + lon_pad,
            "south": min(lats) - lat_pad,
            "north": max(lats) + (lat_pad * 1.5)  # Extra padding on top to prevent cropping
        }
        # Set zoom to None so bounds take precedence
        fig.update_layout(**base_layout, mapbox=dict(bounds=bounds, zoom=None, center=None))
    else:
        fig.update_layout(**base_layout, mapbox=dict(center={"lat": 22, "lon": 83}, zoom=3.3))
        
    return fig

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="brand" style="position:relative;">
            <span style="position:relative; z-index:2; display:inline-block;">
                india<span>metrics</span>
                <span style="position:absolute; top:-15px; right:-20px; font-size:24px; transform: rotate(15deg);">🎀</span>
            </span><br>
            <span style="font-size:12px;color:#34d399; position:relative; z-index:2;">v3.0 Analytics Report</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#262626; margin:0 0 20px 0;">', unsafe_allow_html=True)
    
    page = st.radio("Navigation", ["Overview", "State Comparisons", "District Explorer", "Insights & Correlations"], label_visibility="collapsed")
    st.markdown('<hr style="border-color:#262626; margin:20px 0;">', unsafe_allow_html=True)
    selected_state = st.selectbox("Select State (Filters Data)", ["All States"] + sorted(df_pivot['State'].dropna().unique().tolist()))
    
    min_yr, max_yr = 1960, 2025
    if not df_wb_wide.empty and 'Year' in df_wb_wide.columns:
        min_yr = int(df_wb_wide['Year'].min())
        max_yr = int(df_wb_wide['Year'].max())
        
    selected_year = st.slider("Select Year", min_value=min_yr, max_value=max_yr, value=max_yr, step=1)
    
    use_per_capita = st.toggle("Use Per-Capita / Rates", help="Where applicable, converts absolute counts (like GDP or total vehicles) into per-capita or rate values.")
    cb_mode = st.toggle("Color-Blind Safe Mode", help="Use Okabe-Ito friendly categorical palettes.")
    
    if cb_mode:
        THEME = {
            'CONT_SCALE': 'Cividis',
            'FEMALE': '#d55e00', 'MALE': '#0072b2',
            'CHILD': '#e69f00', 'WORK': '#56b4e9', 'SENIOR': '#f0e442',
            'SEQ_1': '#cc79a7', 'SEQ_2': '#009e73', 'BASE_NEUTRAL': '#64748b'
        }
    else:
        THEME = {
            'CONT_SCALE': 'Viridis',
            'FEMALE': '#f43f5e', 'MALE': '#60a5fa',
            'CHILD': '#f43f5e', 'WORK': '#60a5fa', 'SENIOR': '#fbbf24',
            'SEQ_1': '#a78bfa', 'SEQ_2': '#34d399', 'BASE_NEUTRAL': '#64748b'
        }
        
    st.markdown('<hr style="border-color:#262626; margin:20px 0;">', unsafe_allow_html=True)
    with st.expander("Metric Glossary"):
        st.markdown("""
        **TFR** — Total Fertility Rate: average number of children a woman would have over her lifetime at current age-specific fertility rates. \n
        **MCPR** — Modern Contraceptive Prevalence Rate: % of women aged 15–49 in union using modern contraception. \n
        **TMFR** — Total Marital Fertility Rate: like TFR but restricted to married women. \n
        **GMFR** — General Marital Fertility Rate: births per 1,000 married women aged 15–49. \n
        **SRS** — Sample Registration System: India's continuous demographic survey. \n
        **DLHS** — District Level Household Survey: large-scale survey of health/fertility. \n
        **NSDP** — Net State Domestic Product: state-level equivalent of GDP, net of depreciation. \n
        **Sex Ratio** — Females per 1,000 males (Indian convention). \n
        **Replacement Level** — TFR of 2.1; below this, a population shrinks in the long run.
        """)

df_pivot_f = df_pivot if selected_state == "All States" else df_pivot[df_pivot['State'] == selected_state]

# ── Overview ─────────────────────────────────────────────────────────────

# ========== TAB 1: OVERVIEW ==========
if page == "Overview":
    st.markdown('<h2 style="margin-top:0;">National Demographic Overview</h2>', unsafe_allow_html=True)
    st.markdown("> **India is undergoing a demographic transition fertility is falling, life expectancy is rising, and the working-age share of the population is at a historic peak.** This tab shows the national arc of that change from 1960 to the present.")
    
    # METRIC CARDS
    c1, c2, c3, c4 = st.columns(4)
    tot_pop = df_pivot_f['Total_Pop'].sum()
    avg_lit = df_pivot_f['Literacy_Rate'].mean()
    avg_tfr = df_mcpr['TFR_2011'].mean()
    latest_gdp_yr = df_gdp['Year'].max()
    
    if selected_state != "All States" and selected_state in df_gdp['State'].values:
        tot_gdp = df_gdp[(df_gdp['Year'] == latest_gdp_yr) & (df_gdp['State'] == selected_state)]['GDP_Lakh_Cr'].sum()
    else:
        tot_gdp = df_gdp[df_gdp['Year'] == latest_gdp_yr]['GDP_Lakh_Cr'].sum()

    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Population (2011)</div><div class="metric-value">{tot_pop/1e9:.2f} B</div><div class="metric-subtitle">Source: Census 2011, district aggregation</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Literacy Rate (2011)</div><div class="metric-value">{avg_lit:.1f}%</div><div class="metric-subtitle">% of population aged 7+ who can read and write</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Avg TFR (2011)</div><div class="metric-value">{avg_tfr:.1f}</div><div class="metric-subtitle">Total Fertility Rate — Replacement level = 2.1</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">GDP ({latest_gdp_yr})</div><div class="metric-value">₹{tot_gdp:.1f} L Cr</div><div class="metric-subtitle">Constant prices, removes inflation effect</div></div>', unsafe_allow_html=True)

    # INFOGRAPHICS ROW
    st.markdown("---")
    ic1, ic2, ic3 = st.columns([1.4, 0.8, 1.2])
    
    df_ages_clean = df_wb_wide.dropna(subset=['Year', 'Population, female (% of total population)']).copy()
    if not df_ages_clean.empty:
        pyr_yr = selected_year
        target_row = df_ages_clean[df_ages_clean['Year'] == pyr_yr].iloc[0] if pyr_yr in df_ages_clean['Year'].values else df_ages_clean.iloc[0]
        dependents = target_row.get('Population ages 0-14 (% of total population)', 28.0)
        working = target_row.get('Population ages 15-64 (% of total population)', 66.0)
        seniors = target_row.get('Population ages 65 and above (% of total population)', 6.0)
    else:
        pyr_yr, target_row = 2018, {}
        dependents, working, seniors = 28.0, 66.0, 6.0

    with ic1:
        st.markdown(f"#### Age Pyramid ({pyr_yr})")
        bands = ['00-04','05-09','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79']
        male_pop, female_pop = [], []
        if not df_ages_clean.empty:
            for b in bands:
                m_col = f"Population ages {b}, male"
                f_col = f"Population ages {b}, female"
                male_pop.append(target_row.get(m_col, 0) * -1)
                female_pop.append(target_row.get(f_col, 0))
        
        fig_pyr = go.Figure()
        fig_pyr.add_trace(go.Bar(y=bands, x=male_pop, name='Male', orientation='h', marker_color=THEME['MALE']))
        fig_pyr.add_trace(go.Bar(y=bands, x=female_pop, name='Female', orientation='h', marker_color=THEME['FEMALE']))
        
        # Color-coded zones via shapes/annotations
        fig_pyr.add_hrect(y0=-0.5, y1=2.5, fillcolor=THEME['CHILD'], opacity=0.1, line_width=0, annotation_text="Children", annotation_position="top left")
        fig_pyr.add_hrect(y0=2.5, y1=12.5, fillcolor=THEME['WORK'], opacity=0.1, line_width=0, annotation_text="Working Age", annotation_position="top left")
        fig_pyr.add_hrect(y0=12.5, y1=15.5, fillcolor=THEME['SENIOR'], opacity=0.1, line_width=0, annotation_text="Seniors", annotation_position="top left")
        
        fig_pyr.update_layout(**CHART_LAYOUT, height=400, barmode='relative', showlegend=False)
        fig_pyr.update_yaxes(type='category', showgrid=False)
        fig_pyr.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
        st.plotly_chart(fig_pyr, use_container_width=True)
        st.caption("Each bar shows the population in that 5-year age band. A wide base = young population. Narrowing base over time = fertility decline.")

    with ic2:
        st.markdown(f"#### Gender Ratio ({pyr_yr})")
        if not df_ages_clean.empty:
            f_pct = target_row.get('Population, female (% of total population)', 48.0)
            m_pct = 100.0 - f_pct
            svg_f = f'''<svg viewBox="0 0 100 200" style="height:120px; width:60px; display:block; margin:0 auto;">
              <defs>
                <linearGradient id="gradF" x1="0" x2="0" y1="200" y2="0" gradientUnits="userSpaceOnUse">
                  <stop offset="{f_pct}%" stop-color="{THEME['FEMALE']}"/>
                  <stop offset="{f_pct}%" stop-color="#475569"/>
                </linearGradient>
              </defs>
              <circle cx="50" cy="30" r="20" fill="url(#gradF)"/>
              <path d="M50 55 L15 140 L85 140 Z" fill="url(#gradF)"/>
              <rect x="35" y="140" width="30" height="60" fill="url(#gradF)"/>
            </svg>'''

            svg_m = f'''<svg viewBox="0 0 100 200" style="height:120px; width:60px; display:block; margin:0 auto;">
              <defs>
                <linearGradient id="gradM" x1="0" x2="0" y1="200" y2="0" gradientUnits="userSpaceOnUse">
                  <stop offset="{m_pct}%" stop-color="{THEME['MALE']}"/>
                  <stop offset="{m_pct}%" stop-color="#475569"/>
                </linearGradient>
              </defs>
              <circle cx="50" cy="30" r="20" fill="url(#gradM)"/>
              <rect x="20" y="55" width="60" height="70" rx="15" fill="url(#gradM)"/>
              <rect x="35" y="125" width="30" height="75" fill="url(#gradM)"/>
            </svg>'''

            st.markdown(f'''
            <div style="background:rgba(30,41,59,0.5); border-radius:10px; padding:15px; margin-top:0px; margin-bottom:20px; height: 380px; display: flex; flex-direction: column; justify-content: center;">
                <div style="display:flex; justify-content:center; gap:20px;">
                    <div style="text-align:center;">
                        {svg_f}
                        <div style="margin-top:25px; font-weight:600; font-size:16px; color:#f8fafc;">{f_pct:.1f}% Female</div>
                    </div>
                    <div style="text-align:center;">
                        {svg_m}
                        <div style="margin-top:25px; font-weight:600; font-size:16px; color:#f8fafc;">{m_pct:.1f}% Male</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        st.caption("Ratio of biological males to females in the population. (Total share)")

    with ic3:
        st.markdown(f"#### Population Structure ({pyr_yr})")
        donut_df = pd.DataFrame({"Group": ["Children (0-14)", "Working (15-64)", "Seniors (65+)"], "Pct": [dependents, working, seniors]})
        fig_donut = px.pie(donut_df, names="Group", values="Pct", hole=0.6, color_discrete_sequence=[THEME['CHILD'], THEME['WORK'], THEME['SENIOR']], labels=LABELS)
        fig_donut.update_layout(height=400, margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#a3a3a3'))
        fig_donut.update_traces(textinfo='percent')
        st.plotly_chart(fig_donut, use_container_width=True)
        st.caption("The 'demographic dividend' occurs when the working-age group (15–64) is at its largest relative share — India is currently in this window.")

    # WORLD BANK TIME SERIES
    if not df_wb_wide.empty:
        st.markdown("---")
        st.markdown("#### Vital Transitions (1960 - 2025)")
        cwb1, cwb2 = st.columns(2)
        with cwb1:
            le_cols = ["Life expectancy at birth, female (years)", "Life expectancy at birth, male (years)"]
            if all(c in df_wb_wide.columns for c in le_cols):
                fig_le = go.Figure()
                fig_le.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[le_cols[0]], name='Female Life Exp.', mode='lines', line=dict(color=THEME['FEMALE'])))
                fig_le.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[le_cols[1]], name='Male Life Exp.', mode='lines', line=dict(color=THEME['MALE'])))
                fig_le.update_layout(**CHART_LAYOUT, title="Life Expectancy", height=350, hovermode="x unified")
                st.plotly_chart(fig_le, use_container_width=True)
                st.caption("Female life expectancy consistently exceeds male. The gap narrowing or widening reflects healthcare access and maternal mortality trends.")
                
            mort_cols = ["Mortality rate, infant (per 1,000 live births)", "Mortality rate, neonatal (per 1,000 live births)"]
            if all(c in df_wb_wide.columns for c in mort_cols):
                fig_mo = go.Figure()
                fig_mo.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[mort_cols[0]], name='Infant Mortality', fill='tonexty', mode='lines', line=dict(color=THEME['SEQ_1'])))
                fig_mo.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[mort_cols[1]], name='Neonatal Mortality', fill='tozeroy', mode='lines', line=dict(color=THEME['BASE_NEUTRAL'])))
                fig_mo.update_layout(**CHART_LAYOUT, title="Infant & Neonatal Mortality", height=350, hovermode="x unified")
                st.plotly_chart(fig_mo, use_container_width=True)
                st.caption("Infant mortality = deaths before age 1 per 1,000 live births. Neonatal = deaths in first 28 days. India has halved infant mortality since 1990.")

        with cwb2:
            crude_cols = ["Birth rate, crude (per 1,000 people)", "Death rate, crude (per 1,000 people)"]
            if all(c in df_wb_wide.columns for c in crude_cols):
                fig_crude = go.Figure()
                fig_crude.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[crude_cols[0]], name='Crude Birth Rate', mode='lines', line=dict(color=THEME['SEQ_2'])))
                fig_crude.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[crude_cols[1]], name='Crude Death Rate', mode='lines', line=dict(color=THEME['FEMALE'])))
                fig_crude.update_layout(**CHART_LAYOUT, title="Crude Birth vs Death Rate", height=350, hovermode="x unified")
                st.plotly_chart(fig_crude, use_container_width=True)
                st.caption("When the birth rate line crosses toward the death rate line, natural population growth slows. This 'vital transition' is visible in India post-1980.")
                
            ad_cols = ["Age dependency ratio, old", "Age dependency ratio, young"]
            if all(c in df_wb_wide.columns for c in ad_cols):
                fig_ad = go.Figure()
                fig_ad.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[ad_cols[0]], stackgroup='one', name='Old-Age Dependency', fillcolor=THEME['SENIOR'], line=dict(color=THEME['SENIOR'])))
                fig_ad.add_trace(go.Scatter(x=df_wb_wide['Year'], y=df_wb_wide[ad_cols[1]], stackgroup='one', name='Youth Dependency', fillcolor=THEME['CHILD'], line=dict(color=THEME['CHILD'])))
                fig_ad.update_layout(**CHART_LAYOUT, title="Age Dependency Ratio", height=350, hovermode="x unified")
                st.plotly_chart(fig_ad, use_container_width=True)
                st.caption("Dependency ratio = (dependents / working-age population) × 100. High youth dependency = burden of education. High old-age dependency = burden of healthcare. India's ratio is falling — a rare opportunity.")

    with st.expander("Data Quality & Sources"):
        st.markdown("""
        - **Census Base:** 2011 for district data. Note that district boundaries reflect the 2011 Census — some states have since been reorganised.
        - **World Bank Series:** 1960–2025, with some values interpolated for missing years using robust filling.
        - **Age Pyramid Data:** Uses World Bank estimates covering 1960-2025, allowing visual tracking of demographic changes.
        """)

# ========== TAB 2: STATE COMPARISONS ==========
elif page == "State Comparisons":
    st.markdown('<h2 style="margin-top:0;">State-Level Trajectories</h2>', unsafe_allow_html=True)
    st.markdown("> **India's 28 states and 8 union territories tell dramatically different demographic stories.** Kerala and Bihar are often cited as opposite ends of the spectrum, separated by 30 years of development trajectory. This tab lets you compare states across education, fertility, income, and gender equity.")
    
    st2_1, st2_2, st2_3, st2_4 = st.tabs(["Fertility", "Literacy", "Economy", "Multi-metric (Radar)"])
    
    with st2_1:
        st.markdown("#### Fertility Dynamics")
        c1, c2 = st.columns(2)
        with c1:
            df_mcpr_sort = df_mcpr.sort_values('TFR_2011', ascending=False)
            fig_tfr_bar = px.bar(df_mcpr_sort, x='State', y='TFR_2011', color='TFR_2011', color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
            fig_tfr_bar.add_hline(y=2.1, line_dash="dash", line_color="white", annotation_text="Replacement Level (2.1)")
            fig_tfr_bar.update_layout(**CHART_LAYOUT, height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_tfr_bar, use_container_width=True)
            st.caption("TFR = Total Fertility Rate. Values above 2.1 (dashed line) indicate population growth; below = long-run shrinkage. Bihar vs Tamil Nadu illustrates India's internal divergence.")
            
            fig_gap = go.Figure()
            gmfr_all = df_gmfr[df_gmfr['State'] == 'All India']
            fig_gap.add_trace(go.Scatter(x=gmfr_all['Year'], y=gmfr_all['TMFR_Rural'], name='Rural', mode='lines+markers', line=dict(color=THEME['FEMALE'])))
            fig_gap.add_trace(go.Scatter(x=gmfr_all['Year'], y=gmfr_all['TMFR_Urban'], name='Urban', mode='lines+markers', line=dict(color=THEME['SEQ_2'])))
            fig_gap.update_layout(**CHART_LAYOUT, height=400, title="Rural vs Urban TMFR Gap", xaxis_title="Year", yaxis_title="TMFR")
            st.plotly_chart(fig_gap, use_container_width=True)
            st.caption("TMFR = Total Marital Fertility Rate. The rural-urban gap reflects differences in education, contraceptive access, and women's workforce participation. The gap narrowing over time signals urbanisation.")

        with c2:
            if 'State' in df_mcpr.columns and 'State' in df_pivot.columns:
                pop_map = df_pivot.groupby('State')['Total_Pop'].sum().reset_index()
                scat_df = pd.merge(df_mcpr, pop_map, on='State', how='left')
                scat_df['Total_Pop'] = scat_df['Total_Pop'].fillna(1e6) 
            else:
                scat_df = df_mcpr.copy()
                scat_df['Total_Pop'] = 10
            
            fig_scat = px.scatter(scat_df, x='MCPR_Pct', y='TFR_2011', size='Total_Pop', color='TFR_2011', hover_name='State', size_max=40, color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
            fig_scat.update_layout(**CHART_LAYOUT, height=400, title="TFR vs MCPR<br><sup>Bubble Size: Total Population</sup>")
            st.plotly_chart(fig_scat, use_container_width=True)
            st.caption("MCPR = Modern Contraceptive Prevalence Rate. The negative correlation with TFR is the clearest evidence that family planning access drives fertility decline.")
            
            if not df_tfr_2011.empty:
                melted_tfr = df_tfr_2011.melt(id_vars='State', var_name='Year', value_name='TFR')
                def_states = df_tfr_2011.sort_values('2010', ascending=False).head(10)['State'].tolist()
                selected_tfr = st.multiselect("Compare Historical Fertility Trends by State:", options=df_tfr_2011['State'].unique(), default=def_states)
                
                fig_tfr_hist = px.line(melted_tfr[melted_tfr['State'].isin(selected_tfr)], x='Year', y='TFR', color='State', labels=LABELS)
                fig_tfr_hist.add_hline(y=2.1, line_dash="dash", line_color="white")
                fig_tfr_hist.update_layout(**CHART_LAYOUT, height=400, title="State-level TFR (SRS 1971–2010)")
                st.plotly_chart(fig_tfr_hist, use_container_width=True)
                st.caption("The convergence of lines toward 2.1 shows the pan-India fertility transition, though at very different speeds.")

    with st2_2:
        st.markdown("#### Educational Attainment")
        c3, c4 = st.columns(2)
        with c3:
            df_state_clean = df_state.dropna(subset=['Lit_Tot_01', 'Lit_Tot_11', 'State']).sort_values('Lit_Tot_11')
            fig_slope = go.Figure()
            slope_states = st.multiselect("Filter States for Slope Chart", df_state_clean['State'].tolist(), default=df_state_clean['State'].tolist()[-5:] + df_state_clean['State'].tolist()[:5])
            for idx, row in df_state_clean[df_state_clean['State'].isin(slope_states)].iterrows():
                gap_change = (row['Lit_M_11'] - row['Lit_F_11']) - (row['Lit_M_01'] - row['Lit_F_01'])
                color = THEME['SEQ_2'] if gap_change < 0 else THEME['FEMALE'] # green if narrowed, red if widened
                fig_slope.add_trace(go.Scatter(x=[2001, 2011], y=[row['Lit_Tot_01'], row['Lit_Tot_11']], mode='lines+markers+text', text=["", row['State']], textposition="middle right", name=row['State'], line=dict(color=color, width=2), hoverinfo='name+y'))
            fig_slope.update_layout(**CHART_LAYOUT, height=450, showlegend=False, title="Literacy Slope (2001 to 2011)")
            fig_slope.update_layout(margin=dict(t=40, b=20, l=20, r=80))
            fig_slope.update_xaxes(tickvals=[2001, 2011], range=[2000.5, 2013.5])
            st.plotly_chart(fig_slope, use_container_width=True)
            st.caption("Each line is one state. Steep upward slope = large improvement 2001→2011. Green line = Gender gap narrowed; Red line = Gender gap widened. Source: Census.")
            
        with c4:
            def_gap = df_state.sort_values('Gender_Gap_11', ascending=False).dropna(subset=['Gender_Gap_11']).head(15)['State'].tolist()
            sel_gap = st.multiselect("Compare Literacy Gap by State", df_state['State'].dropna().unique(), default=def_gap)
            gap_df = df_state[df_state['State'].isin(sel_gap)].sort_values('Gender_Gap_11', ascending=False)
            f_gap = px.bar(gap_df, x='Gender_Gap_11', y='State', orientation='h', color='Gender_Gap_11', color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
            f_gap.update_layout(**CHART_LAYOUT, height=260, title="Male vs Female Literacy Gap (2011)")
            f_gap.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(f_gap, use_container_width=True)
            st.caption("Gender literacy gap = Male literacy % − Female literacy %. Rajasthan and Bihar show gaps above 20 percentage points.")

            def_imp = df_state.sort_values('Inc_Tot', ascending=False).dropna(subset=['Inc_Tot']).head(15)['State'].tolist()
            sel_imp = st.multiselect("Compare Literacy Improvements by State", df_state['State'].dropna().unique(), default=def_imp)
            imp_df = df_state[df_state['State'].isin(sel_imp)].sort_values('Inc_Tot', ascending=False)
            f_imp = px.bar(imp_df, x='Inc_Tot', y='State', orientation='h', color='Inc_Tot', color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
            f_imp.update_layout(**CHART_LAYOUT, height=260, title="Most Improved States (Absolute Lit. Gain)")
            f_imp.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(f_imp, use_container_width=True)
            st.caption("Improvement reflects both baseline (it's easier to gain from 40% than from 75%) and policy investment.")

    with st2_3:
        st.markdown("#### Economic Output")
        c5, c6 = st.columns(2)
        with c5:
            max_gdp_yr = df_gdp['Year'].max()
            def_gdp = df_gdp[df_gdp['Year'] == max_gdp_yr].sort_values('GDP_Lakh_Cr', ascending=False).head(10)['State'].tolist()
            sel_gdp = st.multiselect("Compare GDP by State", df_gdp['State'].dropna().unique(), default=def_gdp)
            gdp_latest = df_gdp[(df_gdp['Year'] == max_gdp_yr) & (df_gdp['State'].isin(sel_gdp))].sort_values('GDP_Lakh_Cr', ascending=False)
            fig_gdp_bar = px.bar(gdp_latest, x='State', y='GDP_Lakh_Cr', color='GDP_Lakh_Cr', color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
            fig_gdp_bar.update_layout(**CHART_LAYOUT, height=450, title="State GDP Trajectory")
            st.plotly_chart(fig_gdp_bar, use_container_width=True)
            st.caption("State GDP at constant prices. Constant prices remove inflation, making year-on-year comparisons fair. Maharashtra and Tamil Nadu consistently lead.")

            pc_curr = df_pc[df_pc['Price Category'] == 'current']
            pivot_pc = pc_curr.pivot_table(index='State', columns='Year', values='Per_Capita').dropna()
            fig_pc_heat = px.imshow(pivot_pc, color_continuous_scale=THEME['CONT_SCALE'], aspect="auto", labels=LABELS)
            fig_pc_heat.update_layout(**CHART_LAYOUT, height=400, title="Per-capita Income Heatmap")
            st.plotly_chart(fig_pc_heat, use_container_width=True)
            st.caption("Per capita NSDP in ₹. Cells going dark to light = income growth. Goa's high value is partly explained by its small population base.")

        with c6:
            pc_max_yr = pc_curr['Year'].max()
            pc_latest = pc_curr[pc_curr['Year'] == pc_max_yr][['State', 'Per_Capita']]
            inc_tfr = pd.merge(df_mcpr[['State', 'TFR_2011']], pc_latest, on='State', how='inner')
            if not inc_tfr.empty:
                pop_map2 = df_pivot.groupby('State')['Total_Pop'].sum().reset_index()
                inc_tfr = pd.merge(inc_tfr, pop_map2, on='State', how='left').fillna(1e6)
                fig_inc_tfr = px.scatter(inc_tfr, x='Per_Capita', y='TFR_2011', size='Total_Pop', color='TFR_2011', hover_name='State', size_max=40, color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
                fig_inc_tfr.update_layout(**CHART_LAYOUT, height=840, title="Per-capita Income vs TFR (The Demographic-Economic Transition)<br><sup>Bubble Size: Total Population</sup>")
                st.plotly_chart(fig_inc_tfr, use_container_width=True)
                st.caption("The demographic-economic transition: as income rises, fertility falls. This relationship is clearly present across Indian states. Outliers are analytically interesting cases.")
    
    with st2_4:
        st.markdown("#### Multivariate Radar Comparison")
        comp_states = st.multiselect("Select up to 4 States for comparison:", sorted(df_state['State'].dropna().unique()), default=["Kerala", "Bihar", "Tamil Nadu", "Uttar Pradesh"], max_selections=4)
        if len(comp_states) > 0:
            radar_cols = ['State', 'Literacy_Rate', 'Sex_Ratio', 'Urban_Pct']
            st_data = df_pivot.groupby('State')[radar_cols[1:]].mean().reset_index()
            tfr_data = df_mcpr[['State', 'TFR_2011']]
            pc_data = df_pc[df_pc['Year'] == df_pc['Year'].max()][['State', 'Per_Capita']]
            
            radar_df = pd.merge(st_data, tfr_data, on='State', how='inner')
            radar_df = pd.merge(radar_df, pc_data, on='State', how='inner')
            
            def minmax(series): return (series - series.min()) / (series.max() - series.min()) * 100
            
            radar_df['Literacy_Norm'] = minmax(radar_df['Literacy_Rate'])
            radar_df['SexRatio_Norm'] = minmax(radar_df['Sex_Ratio'])
            radar_df['Urban_Norm'] = minmax(radar_df['Urban_Pct'])
            radar_df['Income_Norm'] = minmax(radar_df['Per_Capita'])
            radar_df['TFR_Norm'] = 100 - minmax(radar_df['TFR_2011']) # Inverted: lower is better
            
            fig_radar = go.Figure()
            colors = [THEME['SEQ_1'], THEME['SEQ_2'], THEME['FEMALE'], THEME['MALE']]
            categories = ['Literacy', 'Sex Ratio (F/M)', 'Urban %', 'Per-Capita Income', 'TFR (Inverted)']
            
            for i, st_name in enumerate(comp_states):
                row = radar_df[radar_df['State'] == st_name]
                if not row.empty:
                    row = row.iloc[0]
                    vals = [row['Literacy_Norm'], row['SexRatio_Norm'], row['Urban_Norm'], row['Income_Norm'], row['TFR_Norm']]
                    fig_radar.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=categories + [categories[0]], fill='toself', name=st_name, line_color=colors[i % len(colors)]))
            
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, paper_bgcolor=PAPER_BG, font=dict(family="Outfit", color=TEXT_COLOR), height=550)
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption("Radar chart normalises all axes to 0–100. Each axis is scaled so that 'outward' means 'better demographic outcome'. Normalisation method: min-max scaling across all states. This is a relative comparison.")

# ========== TAB 3: DISTRICT EXPLORER ==========
elif page == "District Explorer":
    st.markdown('<h2 style="margin-top:0;">District Explorer</h2>', unsafe_allow_html=True)
    st.markdown("> **India's 640 districts show more variation than most countries.** A district in Kerala and one in Rajasthan can differ more in literacy or sex ratio than France differs from Bangladesh. This tab lets you explore sub-state granularity.")
    
    st.markdown("#### District Interactive Map")
    c7, c8 = st.columns([1, 2])
    with c7:
        map_select = st.selectbox("Select District Metric", ["Population Size", "Literacy Rate", "Sex Ratio", "Urban %", "Rural Literacy", "Urban Literacy", "Literacy Gap (Urban - Rural)"])
        col_map = {"Population Size": "Total_Pop", "Literacy Rate": "Literacy_Rate", "Sex Ratio": "Sex_Ratio", "Urban %": "Urban_Pct", "Rural Literacy": "Literacy_Rate_Rural", "Urban Literacy": "Literacy_Rate_Urban", "Literacy Gap (Urban - Rural)": "Literacy_Gap"}
        
        caption_map = {
            "Population Size": "Total absolute population of the district.",
            "Literacy Rate": "District-level literacy rate (Census 2011). % of population aged 7+. Dark = lower literacy.",
            "Sex Ratio": "Females per 1,000 males (Census 2011). National average: 940. Values below 900 indicate severe gender imbalance.",
            "Literacy Gap (Urban - Rural)": "Urban literacy % − Rural literacy %. High values indicate urban residents have significantly better access to education.",
            "Urban %": "Percentage of district population living in urban areas.",
            "Rural Literacy": "Literacy rate among rural population.",
            "Urban Literacy": "Literacy rate among urban population."
        }
        st.info(caption_map.get(map_select, ""))
        
        st.markdown("#### Top & Bottom Districts")
        if col_map[map_select] in df_pivot_f.columns:
             num_dist = st.slider("Number of Districts to Show", 5, 20, 10)
             top_dist = df_pivot_f.nlargest(num_dist, col_map[map_select])
             bot_dist = df_pivot_f.nsmallest(num_dist, col_map[map_select])
             
             fig_p1 = px.bar(top_dist, x=col_map[map_select], y='District_Name', orientation='h', color=col_map[map_select], color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
             fig_p1.update_layout(**CHART_LAYOUT, height=num_dist*25 + 100, title=f"Top {num_dist}: {map_select}"); fig_p1.update_yaxes(categoryorder='total ascending')
             st.plotly_chart(fig_p1, use_container_width=True)
             
             fig_p2 = px.bar(bot_dist, x=col_map[map_select], y='District_Name', orientation='h', color=col_map[map_select], color_continuous_scale=THEME['CONT_SCALE'], labels=LABELS)
             fig_p2.update_layout(**CHART_LAYOUT, height=num_dist*25 + 100, title=f"Bottom {num_dist}: {map_select}"); fig_p2.update_yaxes(categoryorder='total ascending')
             st.plotly_chart(fig_p2, use_container_width=True)
             st.caption("District rankings help identify outliers. Top performers reflect historical investment. Bottom performers often cluster geographically.")

    with c8:
        if col_map[map_select] in df_pivot_f.columns:
            fig_cmap = build_choropleth(df_pivot_f, 'pc11_d_id', col_map[map_select], f"Choropleth: {map_select}", hover_data=['State', 'District_Name'], theme_scale=THEME['CONT_SCALE'])
            fig_cmap.update_layout(height=780)
            st.plotly_chart(fig_cmap, use_container_width=True)

    st.markdown("---")
    st.markdown("#### District Metric Deep-Dives")
    c9, c10 = st.columns(2)
    with c9:
        if not df_sr_dist.empty:
            df_sr_dist['Decadal_Change'] = df_sr_dist['SR_2011_Total'] - df_sr_dist['SR_2001_Total']
            num_dumb = st.slider("Select Num Districts (Top/Bottom Expansion)", 5, 30, 20)
            top_dumb = df_sr_dist.nlargest(num_dumb, 'Decadal_Change')
            bot_dumb = df_sr_dist.nsmallest(num_dumb, 'Decadal_Change')
            dumb_df = pd.concat([top_dumb, bot_dumb]).sort_values('Decadal_Change')
            
            fig_dumb = go.Figure()
            for i, row in dumb_df.iterrows():
                color = THEME['SEQ_2'] if row['Decadal_Change'] > 0 else THEME['FEMALE']
                fig_dumb.add_trace(go.Scatter(x=[row['SR_2001_Total'], row['SR_2011_Total']], y=[row['District'], row['District']], mode='lines+markers', line=dict(color=color, width=3), hoverinfo='text', text=f"2001: {row['SR_2001_Total']} -> 2011: {row['SR_2011_Total']}"))
            fig_dumb.update_layout(**CHART_LAYOUT, height=num_dumb*20 + 200, showlegend=False, title=f"Sex Ratio Dumbbell Chart (2001 to 2011)")
            st.plotly_chart(fig_dumb, use_container_width=True)
            st.caption("Each dumbbell connects a district's 2001 and 2011 sex ratio. Green = improvement. Red = worsening. Districts declining despite national improvement are flagged.")

    with c10:
        ru_avg = df_pivot_f.groupby('District_Name')[['Literacy_Rate_Rural', 'Literacy_Rate_Urban']].mean().reset_index()
        ru_avg['Gap'] = ru_avg['Literacy_Rate_Urban'] - ru_avg['Literacy_Rate_Rural']
        ru_avg = ru_avg.sort_values('Gap').tail(20) # show ones with largest gap
        f_ru = go.Figure()
        f_ru.add_trace(go.Bar(x=ru_avg['Literacy_Rate_Rural'], y=ru_avg['District_Name'], name='Rural', orientation='h', marker_color=THEME['SEQ_1']))
        f_ru.add_trace(go.Bar(x=ru_avg['Literacy_Rate_Urban'], y=ru_avg['District_Name'], name='Urban', orientation='h', marker_color=THEME['SEQ_2']))
        f_ru.update_layout(**CHART_LAYOUT, barmode='group', height=600, title="Rural-Urban Literacy Divide (Top Gaps)")
        st.plotly_chart(f_ru, use_container_width=True)
        st.caption("Rural literacy is consistently lower than urban. The gap size varies significantly across districts.")


# ========== TAB 4: INSIGHTS & CORRELATIONS ==========
elif page == "Insights & Correlations":
    st.markdown('<h2 style="margin-top:0;">Insights & Correlations</h2>', unsafe_allow_html=True)
    st.markdown("> **Demographic indicators don't exist in isolation.** Fertility is shaped by education. Education is shaped by income. This tab makes those relationships explicit — identifying which states break the expected patterns.")
    
    st.markdown("#### The Master Correlation: Education, Fertility & Income")
    c11, c12 = st.columns([1.5, 1])
    
    # Process core data
    tfr_data = df_mcpr[['State', 'TFR_2011']]
    lit_data = df_pivot.groupby('State')['Literacy_Rate'].mean().reset_index()
    pc_data = df_pc[df_pc['Year'] == df_pc['Year'].max()][['State', 'Per_Capita']]
    pop_data = df_pivot.groupby('State')['Total_Pop'].sum().reset_index()
    sr_data = df_pivot.groupby('State')['Sex_Ratio'].mean().reset_index()
    urb_data = df_pivot.groupby('State')['Urban_Pct'].mean().reset_index()
    lit_gap_data = df_state[['State', 'Gender_Gap_11']]
    
    merged_insights = tfr_data.merge(lit_data, on='State', how='outer').merge(pc_data, on='State', how='outer').merge(pop_data, on='State', how='outer')
    merged_heat = merged_insights.merge(sr_data, on='State', how='outer').merge(urb_data, on='State', how='outer').merge(lit_gap_data, on='State', how='outer')

    with c11:
        if not merged_insights.empty:
            scat_data = merged_insights.dropna(subset=['Literacy_Rate', 'TFR_2011', 'Total_Pop', 'Per_Capita'])
            fig_bub = px.scatter(scat_data, x='Literacy_Rate', y='TFR_2011', size='Total_Pop', color='Per_Capita', hover_name='State', size_max=45, color_continuous_scale=THEME['CONT_SCALE'])
            # Quadrant annotations
            fig_bub.add_annotation(x=85, y=1.7, text="High Lit, Low TFR<br>(Kerala, TN)", showarrow=False, font=dict(color="#a3a3a3", size=10), bgcolor="#1e293b", opacity=0.8)
            fig_bub.add_annotation(x=65, y=3.2, text="Low Lit, High TFR<br>(Bihar, UP)", showarrow=False, font=dict(color="#a3a3a3", size=10), bgcolor="#1e293b", opacity=0.8)
            fig_bub.update_layout(**CHART_LAYOUT, height=500, title="<sup>Bubble Size: Total Population</sup>")
            st.plotly_chart(fig_bub, use_container_width=True)
            st.caption("This chart is the central argument of demographic transition theory: education reduces fertility. Bubble size = population. Color = income. Note high-income states cluster in the low-TFR quadrant.")

    with c12:
        if not merged_heat.empty:
            corr_cols = ['Literacy_Rate', 'Sex_Ratio', 'TFR_2011', 'Per_Capita', 'Urban_Pct', 'Gender_Gap_11']
            corr_matrix = merged_heat[corr_cols].corr()
            fig_corr = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale=THEME['CONT_SCALE'], aspect="auto", labels=LABELS)
            fig_corr.update_layout(**CHART_LAYOUT, height=500)
            st.plotly_chart(fig_corr, use_container_width=True)
            st.caption("Pearson correlation. Values close to +1 or -1 indicate strong relationships. Literacy and TFR show a strong negative correlation.")

    st.markdown("---")
    st.markdown("#### Composite Demographic Health Index & Green Mobility")
    c13, c14 = st.columns(2)
    
    with c13:
        if not merged_heat.empty:
            def norm(s): return (s - s.min()) / (s.max() - s.min())
            merged_heat['Lit_score'] = norm(merged_heat['Literacy_Rate'])
            merged_heat['SR_score'] = norm(merged_heat['Sex_Ratio'])
            merged_heat['TFR_score'] = 1 - norm(merged_heat['TFR_2011'])
            merged_heat['Urb_score'] = norm(merged_heat['Urban_Pct'])
            merged_heat['Composite_Index'] = (merged_heat['Lit_score'] + merged_heat['SR_score'] + merged_heat['TFR_score'] + merged_heat['Urb_score']) / 4 * 100
            
            # Since we only have state level merged_heat, and our map takes district level...
            # We must map state scores to district shapes
            dist_idx = pd.merge(df_pivot[['pc11_d_id', 'District_Name', 'State']], merged_heat[['State', 'Composite_Index']], on='State', how='left')
            fig_idx_map = build_choropleth(dist_idx, 'pc11_d_id', 'Composite_Index', "Composite Index (State mapping)", hover_data=['State'], theme_scale=THEME['CONT_SCALE'])
            fig_idx_map.update_layout(height=600)
            st.plotly_chart(fig_idx_map, use_container_width=True)
            
            with st.expander("How is this index calculated?"):
                st.markdown("Score = (0.25 × Literacy Norm) + (0.25 × Sex Ratio Norm) + (0.25 × Inverted TFR Norm) + (0.25 × Urban Norm)\n\n*Limitations: Weights are equal baseline, this is a synthetic measure and not an official state index.*")
            st.caption("Synthetic measure combining 4 indicators. It enables a single-map relative comparison.")

    with c14:
        # VAHAN Linkage
        if not df_vahan_state.empty and not merged_heat.empty:
            is_green = df_vahan_state['fuel_type'].str.upper().str.contains('CNG|ELECTRIC', na=False)
            cg_ev = df_vahan_state[is_green].groupby(['state_name', 'year'])['registrations'].sum().reset_index()
            tot = df_vahan_state.groupby(['state_name', 'year'])['registrations'].sum().reset_index()
            tot.rename(columns={'registrations': 'tot_reg'}, inplace=True)
            v_merge = pd.merge(cg_ev, tot, on=['state_name', 'year'])
            v_merge['Green_Pct'] = (v_merge['registrations'] / v_merge['tot_reg']) * 100
            
            # Merge with urbanisation from merged_heat
            v_merge['State'] = v_merge['state_name'].apply(clean_state)
            final_v = pd.merge(v_merge, merged_heat[['State', 'Urban_Pct', 'Total_Pop']], on='State', how='inner')
            
            if not final_v.empty:
                # Absolute vs Rate logic applied here
                y_col = 'registrations' if not use_per_capita else 'Green_Pct'
                y_lbl = 'Absolute Green EVs/CNGs' if not use_per_capita else 'Green Mobility %'
                
                final_v_clean = final_v.dropna(subset=['Urban_Pct', y_col, 'Total_Pop'])
                
                fig_vh = px.scatter(final_v_clean, x='Urban_Pct', y=y_col, animation_frame='year', animation_group='State', size='Total_Pop', color=y_col, hover_name='State', size_max=40, color_continuous_scale=THEME['CONT_SCALE'])
                fig_vh.update_layout(**CHART_LAYOUT, height=530, title=f"Green Mobility vs Urbanisation ({y_lbl})<br><sup>Bubble Size: Total Population</sup>")
                st.plotly_chart(fig_vh, use_container_width=True)
                    
                st.caption("Vehicle fuel type as a development proxy. CNG and Electric adoption is concentrated in high-urbanisation states, mirroring fertility transitions. (VAHAN starts 2019)")
            else:
                st.info("Insufficient spatial mapping for VAHAN data.")



