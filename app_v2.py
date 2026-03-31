import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json
import os

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Demographic Dashboard V2",
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

.stApp {
    background-color: #0a0a0a !important;
}

/* Sidebar styling for Dark Theme */
[data-testid="stSidebar"] {
    background-color: #121217 !important;
    border-right: 1px solid #262626;
}

/* Glowing Metric Cards */
.metric-card {
    background: #141416;
    border-radius: 20px;
    padding: 24px;
    border: 1px solid #262626;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    height: 100%;
    margin-bottom: 24px;
    transition: transform 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #404040;
}
.metric-title {
    font-size: 14px;
    color: #a3a3a3;
    font-weight: 500;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 32px;
    font-weight: 600;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 12px;
}
.metric-badge {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 12px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
}
.badge-green { background: rgba(52, 211, 153, 0.1); color: #34d399; }
.badge-purple { background: rgba(167, 139, 250, 0.1); color: #a78bfa; }
.badge-yellow { background: rgba(251, 191, 36, 0.1); color: #fbbf24; }
.metric-subtitle {
    font-size: 12px;
    color: #737373;
    margin-top: 8px;
}

/* Brand Logo */
.brand {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
    padding: 20px 0;
    text-align: center;
}
.brand span {
    color: #a78bfa;
}

/* Section Titles (Without wrapping empty divs) */
.section-title {
    font-size: 18px;
    font-weight: 500;
    color: #e5e5e5;
    margin-top: 32px;
    margin-bottom: 16px;
    border-bottom: 1px solid #262626;
    padding-bottom: 8px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: transparent;
    gap: 20px;
}
.stTabs [data-baseweb="tab"] {
    color: #a3a3a3;
}
.stTabs [aria-selected="true"] {
    color: #a78bfa !important;
}

/* Gender Infographic Card */
.gender-card {
    background: #1f2937;
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    border: 1px solid #374151;
    height: 100%;
}
</style>
""", unsafe_allow_html=True)

# ── Chart Theme Constants ──────────────────────────────────────────
PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
GRID_COLOR = "#262626"
TEXT_COLOR = "#a3a3a3"

CHART_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family="Outfit", color=TEXT_COLOR, size=12),
    margin=dict(t=40, b=20, l=20, r=20),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
)

# ── Data Loading ───────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@st.cache_data
def load_boundary():
    gdf = gpd.read_file(os.path.join(DATA_DIR, "india_compressed.geojson"))
    gdf['geometry'] = gdf['geometry'].buffer(0)
    return gdf.dissolve()

@st.cache_data
def load_data():
    # 1. Pivot Data (Districts)
    df_pivot = pd.read_csv(os.path.join(DATA_DIR, "df_pivot.csv"))
    df_pivot['pc11_d_id'] = df_pivot['pc11_d_id'].astype(int).apply(lambda x: str(x).zfill(3))
    if 'Sex_Ratio' not in df_pivot.columns:
        df_pivot['Sex_Ratio'] = 943
    
    # 2. Geojson
    with open(os.path.join(DATA_DIR, "india_compressed.geojson")) as f:
        geojson = json.load(f)
        
    # 3. Literacy & Urbanisation
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
    
    # 4. GDP
    df_gdp = pd.read_excel(os.path.join(DATA_DIR, "State_GDP_Map_1773382936775.xlsx"))
    df_gdp = df_gdp.dropna(subset=['State', 'Year'])
    df_gdp.rename(columns={'Price (in Rs.Lakh Crore)': 'GDP_Lakh_Cr'}, inplace=True)
    df_gdp_cons = df_gdp[df_gdp['Price Category'] == 'constant'].copy()
    
    # 5. Per Capita
    df_pc = pd.read_excel(os.path.join(DATA_DIR, "Per_Capita_Income_1773575689370.xlsx"))
    df_pc = df_pc.dropna(subset=['State', 'Year'])
    df_pc.rename(columns={'Price (in ₹)': 'Per_Capita'}, inplace=True)
    
    # 6. Ages
    df_ages = pd.read_csv(os.path.join(DATA_DIR, "Ages.csv"))
    df_ages = df_ages.replace('..', np.nan)
    for col in df_ages.columns:
        if col != 'Year':
            df_ages[col] = pd.to_numeric(df_ages[col], errors='coerce')
    
    # 7. Healthcare/Fertility
    df_dlhs = pd.read_csv(os.path.join(DATA_DIR, "dlhs_fertility.csv"))
    df_tfr_ts = pd.read_csv(os.path.join(DATA_DIR, "tfr_timeseries.csv"))
    df_mcpr = pd.read_csv(os.path.join(DATA_DIR, "tfr_mcpr_2011.csv"))
    df_gmfr = pd.read_csv(os.path.join(DATA_DIR, "gmfr_tmfr.csv"))
    df_sr_dist = pd.read_csv(os.path.join(DATA_DIR, "district_sex_ratio.csv"))

    return df_pivot, geojson, df_state, df_gdp_cons, df_pc, df_ages, df_dlhs, df_tfr_ts, df_mcpr, df_gmfr, df_sr_dist

df_pivot, geojson, df_state, df_gdp, df_pc, df_ages, df_dlhs, df_tfr_ts, df_mcpr, df_gmfr, df_sr_dist = load_data()
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
    return go.Scattermapbox(lon=lons, lat=lats, mode='lines',
                            line=dict(color='#cbd5e1', width=1.0),
                            hoverinfo='skip', showlegend=False)

def build_choropleth(df_target, location_col, color_col, title, hover_data=None):
    fig = px.choropleth_mapbox(
        df_target, geojson=geojson, featureidkey='properties.pc11_d_id',
        locations=location_col, color=color_col,
        color_continuous_scale="Viridis", 
        hover_name='District_Name' if 'District_Name' in df_target.columns else 'State',
        hover_data=hover_data,
        mapbox_style="carto-darkmatter", center={"lat": 22, "lon": 83}, zoom=3.3
    )
    fig.add_trace(get_boundary_trace(india_boundary))
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0}, height=500, 
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        title=title, title_font=dict(color="#e5e5e5")
    )
    return fig


# ── Sidebar Navigation ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">india<span>metrics</span><br><span style="font-size:12px;color:#34d399">v2.0 Experimental</span></div>', unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#262626; margin:0 0 20px 0;">', unsafe_allow_html=True)
    
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Demographics", "Economy", "Healthcare", "Literacy & Urban"]
    )
    
    st.markdown('<hr style="border-color:#262626; margin:20px 0;">', unsafe_allow_html=True)
    st.markdown("**Global Filters**")
    selected_state = st.selectbox("Select State", ["All States"] + sorted(df_pivot['State'].dropna().unique().tolist()))
    st.caption("Filters district-level datasets and highlights state-specific data where applicable.")
    st.markdown("<br><br>", unsafe_allow_html=True)

# ── Dynamic Filtering Logic ────────────────────────────────────────
df_pivot_f = df_pivot if selected_state == "All States" else df_pivot[df_pivot['State'] == selected_state]
df_sr_dist_f = df_sr_dist if selected_state == "All States" else df_sr_dist

# ══════════════════════════════════════════════════════════════════
# 1. OVERVIEW
# ══════════════════════════════════════════════════════════════════
if page == "Overview":
    st.title("National Overview")
    if selected_state != "All States":
        st.subheader(f"Filtered for: {selected_state}")
    
    # ── METRIC CARDS ──
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
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Population (2011)</div>
            <div class="metric-value">{tot_pop/1e9:.2f} B</div>
            <div class="metric-subtitle">Across {len(df_pivot_f)} districts</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Literacy Rate (2011)</div>
            <div class="metric-value">{avg_lit:.1f}%</div>
            <div class="metric-subtitle">District Average</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total GDP ({latest_gdp_yr})</div>
            <div class="metric-value">₹{tot_gdp:.1f} L Cr</div>
            <div class="metric-subtitle">Constant prices</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg TFR (2011)</div>
            <div class="metric-value">{avg_tfr:.1f}</div>
            <div class="metric-subtitle">Children per woman</div>
        </div>
        """, unsafe_allow_html=True)

    # ── EXPERIMENTAL INFOGRAPHICS ──
    df_ages_clean = df_ages.dropna(subset=['Population, female (% of total population)']).copy()
    if not df_ages_clean.empty:
        latest = df_ages_clean.iloc[-1]
        latest_yr = int(latest.get('Year', 2025))
        fem_pct = round(latest['Population, female (% of total population)'])
        mal_pct = round(latest['Population, male (% of total population)'])
        dependents = latest.get('Population ages 0-14 (% of total population)', 28.0)
        working = latest.get('Population ages 15-64 (% of total population)', 66.0)
        seniors = latest.get('Population ages 65 and above (% of total population)', 6.0)
    else:
        latest_yr = 2025
        fem_pct, mal_pct = 48, 52
        dependents, working, seniors = 28.0, 66.0, 6.0
        
    st.markdown(f'<div class="section-title">Demographics Summary (Infographics - {latest_yr})</div>', unsafe_allow_html=True)

    ic1, ic2, ic3 = st.columns([1.5, 2, 1.5])
    
    with ic1:
        st.markdown(f"""
        <div class="gender-card">
            <h4 style="margin:0 0 20px 0; color:#e5e5e5; align-self:flex-start">Gender Ratio</h4>
            <div style="display:flex; gap:30px;">
                <!-- Female -->
                <div style="text-align:center;">
                    <svg viewBox="0 0 100 200" width="80" height="160">
                      <defs>
                        <linearGradient id="fillFemale" x1="0" x2="0" y1="1" y2="0">
                          <stop offset="{fem_pct}%" stop-color="#34d399"/>
                          <stop offset="{fem_pct}%" stop-color="#4b5563"/>
                        </linearGradient>
                      </defs>
                      <path fill="url(#fillFemale)" d="M50 15 A15 15 0 1 0 50 45 A15 15 0 1 0 50 15 Z M50 50 L85 140 L65 140 L65 190 L35 190 L35 140 L15 140 Z"/>
                    </svg>
                    <div style="color:#e5e5e5; margin-top:10px; font-weight:600;">{fem_pct}% Female</div>
                </div>
                <!-- Male -->
                <div style="text-align:center;">
                    <svg viewBox="0 0 100 200" width="80" height="160">
                      <defs>
                        <linearGradient id="fillMale" x1="0" x2="0" y1="1" y2="0">
                          <stop offset="{mal_pct}%" stop-color="#60a5fa"/>
                          <stop offset="{mal_pct}%" stop-color="#4b5563"/>
                        </linearGradient>
                      </defs>
                      <path fill="url(#fillMale)" d="M50 15 A15 15 0 1 0 50 45 A15 15 0 1 0 50 15 Z M30 55 L70 55 C75 55 80 60 80 65 L80 120 L65 120 L65 190 L35 190 L35 120 L20 120 L20 65 C20 60 25 55 30 55 Z"/>
                    </svg>
                    <div style="color:#e5e5e5; margin-top:10px; font-weight:600;">{mal_pct}% Male</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ic2:
        st.markdown('<h4 style="margin:0 0 10px 0; color:#e5e5e5; border-bottom:1px solid #262626; padding-bottom:8px;">Age Brackets</h4>', unsafe_allow_html=True)
        bands = ['00-04','05-09','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79']
        age_totals = []
        if not df_ages_clean.empty:
            for b in bands:
                m = latest.get(f"Population ages {b}, male", 0)
                f = latest.get(f"Population ages {b}, female", 0)
                age_totals.append((m+f)/1e6)
        df_age_bar = pd.DataFrame({"Age": bands, "Pop (M)": age_totals})
        fig_bar = px.bar(df_age_bar, y="Age", x="Pop (M)", orientation='h', color_discrete_sequence=['#60a5fa'])
        
        fig_bar.update_layout(**CHART_LAYOUT)
        fig_bar.update_layout(height=230, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        fig_bar.update_yaxes(type='category', categoryorder='total ascending', showgrid=False)
        fig_bar.update_xaxes(showgrid=False)
        
        st.plotly_chart(fig_bar, use_container_width=True)

    with ic3:
        st.markdown('<h4 style="margin:0 0 10px 0; color:#e5e5e5; border-bottom:1px solid #262626; padding-bottom:8px;">Population Structure</h4>', unsafe_allow_html=True)
        donut_df = pd.DataFrame({
            "Group": ["Children (0-14)", "Working (15-64)", "Seniors (65+)"],
            "Pct": [dependents, working, seniors]
        })
        fig_donut = px.pie(donut_df, names="Group", values="Pct", hole=0.6, color_discrete_sequence=['#f43f5e', '#60a5fa', '#fbbf24'])
        fig_donut.update_layout(height=230, margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#a3a3a3'))
        fig_donut.update_traces(textinfo='percent')
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── MAPS ──
    col_map, col_dist = st.columns([2, 1])
    with col_map:
        st.markdown('<div class="section-title">Population Density Map (2011)</div>', unsafe_allow_html=True)
        fig_map = build_choropleth(df_pivot_f, 'pc11_d_id', 'Total_Pop', '', hover_data=['State', 'Total_Pop'])
        st.plotly_chart(fig_map, use_container_width=True)

    with col_dist:
        st.markdown('<div class="section-title">Top Districts by Population (2011)</div>', unsafe_allow_html=True)
        top_dist = df_pivot_f.nlargest(10, 'Total_Pop')
        fig_b_map = px.bar(top_dist, x='Total_Pop', y='District_Name', orientation='h', color_discrete_sequence=['#a78bfa'], hover_data=['State'])
        fig_b_map.update_layout(**CHART_LAYOUT, height=500)
        fig_b_map.update_yaxes(categoryorder='total ascending', title="")
        fig_b_map.update_xaxes(title="", showgrid=False, showticklabels=False)
        st.plotly_chart(fig_b_map, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 2. DEMOGRAPHICS (Age & Sex Ratio)
# ══════════════════════════════════════════════════════════════════
elif page == "Demographics":
    st.title("Demographics Analysis")
    t1, t2 = st.tabs(["Age & Population Models", "Sex Ratio Analysis"])
    
    with t1:
        latest_year_data = df_ages.fillna(0).iloc[-1]
        proj_yr = int(latest_year_data.get('Year', 2025))
        st.markdown(f'<div class="section-title">Age Pyramid ({proj_yr} Projection)</div>', unsafe_allow_html=True)
        
        bands = ['00-04','05-09','10-14','15-19','20-24','25-29','30-34','35-39','40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79']
        male_pop, female_pop = [], []
        
        for b in bands:
            m_col = f"Population ages {b}, male"
            f_col = f"Population ages {b}, female"
            if m_col in df_ages.columns and f_col in df_ages.columns:
                male_pop.append(latest_year_data.get(m_col, 0) * -1) # Make negative for pyramid
                female_pop.append(latest_year_data.get(f_col, 0))
            else:
                male_pop.append(0); female_pop.append(0)
        
        fig_pyr = go.Figure()
        fig_pyr.add_trace(go.Bar(y=bands, x=male_pop, name='Male', orientation='h', marker_color='#60a5fa'))
        fig_pyr.add_trace(go.Bar(y=bands, x=female_pop, name='Female', orientation='h', marker_color='#f43f5e'))
        fig_pyr.update_layout(**CHART_LAYOUT, barmode='relative', height=600, xaxis_title="Population", yaxis_title="Age Group")
        st.plotly_chart(fig_pyr, use_container_width=True)

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">Sex Ratio (F/1000M) Bar Chart (2011)</div>', unsafe_allow_html=True)
            sr_state = df_pivot_f.groupby('District_Name')['Sex_Ratio'].mean().dropna().nlargest(15).reset_index()
            fig_sr_bar = px.bar(sr_state, x='Sex_Ratio', y='District_Name', orientation='h', color='Sex_Ratio', color_continuous_scale="Viridis")
            fig_sr_bar.update_layout(**CHART_LAYOUT, height=400)
            fig_sr_bar.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_sr_bar, use_container_width=True)
            
        with c2:
            st.markdown('<div class="section-title">2001 vs 2011 Sex Ratio Trends</div>', unsafe_allow_html=True)
            df_sr_top = df_sr_dist_f.head(20)
            fig_sr_line = go.Figure()
            fig_sr_line.add_trace(go.Scatter(x=df_sr_top['District'], y=df_sr_top['SR_2001_Total'], mode='lines+markers', name='2001 SR'))
            fig_sr_line.add_trace(go.Scatter(x=df_sr_top['District'], y=df_sr_top['SR_2011_Total'], mode='lines+markers', name='2011 SR'))
            fig_sr_line.update_layout(**CHART_LAYOUT, height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_sr_line, use_container_width=True)
            
        st.markdown('<div class="section-title">Sex Ratio Correlation Heatmap (Rural vs Urban: 2001 & 2011)</div>', unsafe_allow_html=True)
        corr_cols = ['SR_2001_Rural', 'SR_2001_Urban', 'SR_2011_Rural', 'SR_2011_Urban']
        corr_matrix = df_sr_dist[corr_cols].corr()
        fig_heat = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='Viridis', aspect="auto")
        fig_heat.update_layout(**CHART_LAYOUT, height=400)
        st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 3. ECONOMY
# ══════════════════════════════════════════════════════════════════
elif page == "Economy":
    st.title("Economic Output & Income")
    t1, t2 = st.tabs(["GDP Analytics", "Per Capita Income"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            max_gdp_yr = df_gdp['Year'].max()
            st.markdown(f'<div class="section-title">State GDP ({max_gdp_yr})</div>', unsafe_allow_html=True)
            gdp_latest = df_gdp[df_gdp['Year'] == max_gdp_yr].sort_values('GDP_Lakh_Cr', ascending=False).head(15)
            fig_gdp_bar = px.bar(gdp_latest, x='State', y='GDP_Lakh_Cr', color='GDP_Lakh_Cr', color_continuous_scale="Viridis", hover_data=['State'])
            fig_gdp_bar.update_layout(**CHART_LAYOUT, height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_gdp_bar, use_container_width=True)
        with c2:
            st.markdown('<div class="section-title">Historical GDP Trajectory (Constant Prices)</div>', unsafe_allow_html=True)
            top_states = gdp_latest.head(6)['State'].tolist()
            if selected_state != "All States" and selected_state in df_gdp['State'].values and selected_state not in top_states:
                top_states.append(selected_state)
            df_gdp_traj = df_gdp[df_gdp['State'].isin(top_states)].sort_values('Year')
            fig_gdp_line = px.line(df_gdp_traj, x='Year', y='GDP_Lakh_Cr', color='State', markers=True)
            fig_gdp_line.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_gdp_line, use_container_width=True)
            
    with t2:
        c3, c4 = st.columns(2)
        pc_curr = df_pc[df_pc['Price Category'] == 'current']
        with c3:
            max_pc_yr = pc_curr['Year'].max()
            st.markdown(f'<div class="section-title">Per Capita Income ({max_pc_yr})</div>', unsafe_allow_html=True)
            pc_latest = pc_curr[pc_curr['Year'] == max_pc_yr].sort_values('Per_Capita', ascending=False).head(15)
            fig_pc_bar = px.bar(pc_latest, y='State', x='Per_Capita', orientation='h', color='Per_Capita', color_continuous_scale="Viridis", hover_data=['State'])
            fig_pc_bar.update_layout(**CHART_LAYOUT, height=400)
            fig_pc_bar.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_pc_bar, use_container_width=True)
        with c4:
            st.markdown('<div class="section-title">Per Capita Growth Trend</div>', unsafe_allow_html=True)
            sel_states = pc_latest.head(6)['State'].tolist()
            pc_traj = pc_curr[pc_curr['State'].isin(sel_states)].sort_values('Year')
            fig_pc_line = px.line(pc_traj, x='Year', y='Per_Capita', color='State', markers=True)
            fig_pc_line.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_pc_line, use_container_width=True)
        
        st.markdown('<div class="section-title">Per Capita Income Heatmap Over Years</div>', unsafe_allow_html=True)
        pivot_pc = pc_curr.pivot_table(index='State', columns='Year', values='Per_Capita').dropna()
        fig_pc_heat = px.imshow(pivot_pc, color_continuous_scale='Viridis', aspect="auto")
        fig_pc_heat.update_layout(**CHART_LAYOUT, height=600)
        st.plotly_chart(fig_pc_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 4. HEALTHCARE & FERTILITY
# ══════════════════════════════════════════════════════════════════
elif page == "Healthcare":
    st.title("Healthcare & Global Fertility Indicators")
    t1, t2, t3, t4 = st.tabs(["TFR India 2011", "TFR + MCPR", "Fertility Indicators (06-13)", "Fertility % (DLHS)"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">TFR by State (2011)</div>', unsafe_allow_html=True)
            df_mcpr_sort = df_mcpr.sort_values('TFR_2011', ascending=False)
            fig_tfr_bar = px.bar(df_mcpr_sort, x='State', y='TFR_2011', color='TFR_2011', color_continuous_scale='Viridis', hover_data=['State'])
            fig_tfr_bar.update_layout(**CHART_LAYOUT, height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_tfr_bar, use_container_width=True)
        with c2:
            st.markdown('<div class="section-title">TFR Distribution (2011)</div>', unsafe_allow_html=True)
            fig_tfr_hist = px.histogram(df_mcpr, x='TFR_2011', nbins=15, color_discrete_sequence=['#a78bfa'])
            fig_tfr_hist.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_tfr_hist, use_container_width=True)
            
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-title">Replacement Level Breakdown (2011)</div>', unsafe_allow_html=True)
            above = len(df_mcpr[df_mcpr['TFR_2011'] >= 2.1])
            below = len(df_mcpr[df_mcpr['TFR_2011'] < 2.1])
            pie_df = pd.DataFrame({"Status": ["Above Replacement (>2.1)", "Below Replacement (<2.1)"], "Count": [above, below]})
            fig_pie = px.pie(pie_df, names='Status', values='Count', color_discrete_sequence=['#f43f5e', '#34d399'])
            fig_pie.update_layout(paper_bgcolor=PAPER_BG, font=dict(family="Outfit", color=TEXT_COLOR))
            st.plotly_chart(fig_pie, use_container_width=True)

    with t2:
        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<div class="section-title">TFR vs MCPR Correlation (2011)</div>', unsafe_allow_html=True)
            fig_scat = px.scatter(df_mcpr, x='MCPR_Pct', y='TFR_2011', size='TFR_2011', color='TFR_2011', hover_name='State', color_continuous_scale='Viridis')
            fig_scat.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_scat, use_container_width=True)
        with c6:
            st.markdown('<div class="section-title">Indicator Spread (Box Plot - 2011)</div>', unsafe_allow_html=True)
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(y=df_mcpr['TFR_2011']*10, name='TFR (scaled x10)', marker_color='#a78bfa'))
            fig_box.add_trace(go.Box(y=df_mcpr['MCPR_Pct'], name='MCPR %', marker_color='#fbbf24'))
            fig_box.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_box, use_container_width=True)

    with t3:
        c7, c8 = st.columns(2)
        with c7:
            st.markdown('<div class="section-title">Fertility History (2006-2013)</div>', unsafe_allow_html=True)
            gmfr_all = df_gmfr[df_gmfr['State'] == 'All India']
            fig_line = px.line(gmfr_all, x='Year', y='TMFR_Total', markers=True, color_discrete_sequence=['#60a5fa'])
            fig_line.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        with c8:
            st.markdown('<div class="section-title">Rural vs Urban (2006-2013)</div>', unsafe_allow_html=True)
            fig_ru = go.Figure()
            fig_ru.add_trace(go.Scatter(x=gmfr_all['Year'], y=gmfr_all['TMFR_Rural'], name='Rural', mode='lines+markers', line=dict(color='#f43f5e')))
            fig_ru.add_trace(go.Scatter(x=gmfr_all['Year'], y=gmfr_all['TMFR_Urban'], name='Urban', mode='lines+markers', line=dict(color='#34d399')))
            fig_ru.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(fig_ru, use_container_width=True)

    with t4:
        st.markdown('<div class="section-title">Modern Contraception Usage by State (DLHS-4)</div>', unsafe_allow_html=True)
        dlhs_avg = df_dlhs.groupby('State')['Modern_Contraception_Pct'].mean().reset_index().sort_values('Modern_Contraception_Pct', ascending=False)
        fig_dlhs = px.bar(dlhs_avg, x='State', y='Modern_Contraception_Pct', color='Modern_Contraception_Pct', color_continuous_scale='Viridis')
        fig_dlhs.update_layout(**CHART_LAYOUT, height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_dlhs, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# 5. LITERACY & URBANIZATION
# ══════════════════════════════════════════════════════════════════
elif page == "Literacy & Urban":
    st.title("Literacy & Urbanization")
    
    if selected_state != "All States":
        st.subheader(f"Filters Active: Mapping districts in {selected_state}")

    t1, t2, t3, t4 = st.tabs(["Choropleths", "Bar Charts", "2001 vs 2011 Progress", "Distributions"])
    
    with t1:
        st.markdown('<div class="section-title">Geographical Density Mappings (2011)</div>', unsafe_allow_html=True)
        map_select = st.selectbox("Select District Metric", ["Literacy Rate", "Sex Ratio", "Urban %", "Rural Literacy", "Urban Literacy", "Literacy Gap (Urban - Rural)"])
        col_map = {"Literacy Rate": "Literacy_Rate", "Sex Ratio": "Sex_Ratio", "Urban %": "Urban_Pct", 
                   "Rural Literacy": "Literacy_Rate_Rural", "Urban Literacy": "Literacy_Rate_Urban", "Literacy Gap (Urban - Rural)": "Literacy_Gap"}
        if col_map[map_select] in df_pivot.columns:
            fig_cmap = build_choropleth(df_pivot_f, 'pc11_d_id', col_map[map_select], f"Choropleth: {map_select}", hover_data=['State', 'District_Name'])
            st.plotly_chart(fig_cmap, use_container_width=True)
        else:
            st.warning(f"{col_map[map_select]} column missing in df_pivot")

    with t2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-title">Top 10 Districts by Literacy (2011)</div>', unsafe_allow_html=True)
            top_lit = df_pivot_f.nlargest(10, 'Literacy_Rate')
            f1 = px.bar(top_lit, x='Literacy_Rate', y='District_Name', orientation='h', color='Literacy_Rate', color_continuous_scale='Viridis', hover_data=['State'])
            f1.update_layout(**CHART_LAYOUT, height=400); f1.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(f1, use_container_width=True)
        with c2:
            st.markdown('<div class="section-title">Bottom 10 Districts by Literacy (2011)</div>', unsafe_allow_html=True)
            bot_lit = df_pivot_f.nsmallest(10, 'Literacy_Rate')
            f2 = px.bar(bot_lit, x='Literacy_Rate', y='District_Name', orientation='h', color='Literacy_Rate', color_continuous_scale='Viridis', hover_data=['State'])
            f2.update_layout(**CHART_LAYOUT, height=400); f2.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(f2, use_container_width=True)
            
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="section-title">Rural vs Urban Lit across Top States (2011)</div>', unsafe_allow_html=True)
            ru_avg = df_pivot.groupby('State')[['Literacy_Rate_Rural', 'Literacy_Rate_Urban']].mean().reset_index().sort_values('Literacy_Rate_Urban').tail(10)
            f_ru = go.Figure()
            f_ru.add_trace(go.Bar(x=ru_avg['State'], y=ru_avg['Literacy_Rate_Rural'], name='Rural', marker_color='#a78bfa'))
            f_ru.add_trace(go.Bar(x=ru_avg['State'], y=ru_avg['Literacy_Rate_Urban'], name='Urban', marker_color='#34d399'))
            f_ru.update_layout(**CHART_LAYOUT, barmode='group', height=400, xaxis_tickangle=-45)
            st.plotly_chart(f_ru, use_container_width=True)
        with c4:
            st.markdown('<div class="section-title">State Average Literacy (2011)</div>', unsafe_allow_html=True)
            avg_lit_st = df_pivot.groupby('State')['Literacy_Rate'].mean().reset_index().sort_values('Literacy_Rate').tail(15)
            f_al = px.bar(avg_lit_st, x='Literacy_Rate', y='State', orientation='h', color='Literacy_Rate', color_continuous_scale='Viridis')
            f_al.update_layout(**CHART_LAYOUT, height=400)
            st.plotly_chart(f_al, use_container_width=True)

    with t3:
        st.markdown('<div class="section-title">Literacy Base Change 2001 to 2011</div>', unsafe_allow_html=True)
        df_state_clean = df_state.dropna(subset=['Lit_Tot_01', 'Lit_Tot_11']).sort_values('Lit_Tot_11')
        f_diff = go.Figure()
        f_diff.add_trace(go.Bar(x=df_state_clean['State'], y=df_state_clean['Lit_Tot_01'], name='2001', marker_color='#64748b'))
        f_diff.add_trace(go.Bar(x=df_state_clean['State'], y=df_state_clean['Lit_Tot_11'], name='2011', marker_color='#34d399'))
        f_diff.update_layout(**CHART_LAYOUT, barmode='group', height=450, xaxis_tickangle=-45)
        st.plotly_chart(f_diff, use_container_width=True)
        
        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<div class="section-title">Most Improved States (2001-2011)</div>', unsafe_allow_html=True)
            imp_df = df_state.sort_values('Inc_Tot', ascending=False).dropna(subset=['Inc_Tot']).head(15)
            f_imp = px.bar(imp_df, x='Inc_Tot', y='State', orientation='h', color='Inc_Tot', color_continuous_scale='Viridis')
            f_imp.update_layout(**CHART_LAYOUT, height=400); f_imp.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(f_imp, use_container_width=True)
        with c6:
            st.markdown('<div class="section-title">Male vs Female Literacy Gap (2011)</div>', unsafe_allow_html=True)
            gap_df = df_state.sort_values('Gender_Gap_11', ascending=False).dropna(subset=['Gender_Gap_11']).head(15)
            f_gap = px.bar(gap_df, x='Gender_Gap_11', y='State', orientation='h', color='Gender_Gap_11', color_continuous_scale='Viridis')
            f_gap.update_layout(**CHART_LAYOUT, height=400); f_gap.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(f_gap, use_container_width=True)

    with t4:
        c7, c8 = st.columns(2)
        with c7:
            st.markdown('<div class="section-title">Literacy Volume Distribution (2011)</div>', unsafe_allow_html=True)
            f_hist = px.histogram(df_pivot_f, x='Literacy_Rate', nbins=30, color_discrete_sequence=['#60a5fa'])
            f_hist.update_layout(**CHART_LAYOUT, height=450)
            st.plotly_chart(f_hist, use_container_width=True)
        with c8:
            st.markdown('<div class="section-title">Correlation: Literacy vs Urban % (2011)</div>', unsafe_allow_html=True)
            f_sc_lu = px.scatter(df_pivot_f, x='Urban_Pct', y='Literacy_Rate', color='Total_Pop', hover_data=['State', 'District_Name'], color_continuous_scale='Viridis')
            f_sc_lu.update_layout(**CHART_LAYOUT, height=450)
            st.plotly_chart(f_sc_lu, use_container_width=True)
            
        st.markdown('<div class="section-title">Correlation: Sex Ratio vs Literacy (2011)</div>', unsafe_allow_html=True)
        f_sc_sl = px.scatter(df_pivot_f, x='Literacy_Rate', y='Sex_Ratio', color='Urban_Pct', hover_data=['State', 'District_Name'], color_continuous_scale='Viridis')
        f_sc_sl.update_layout(**CHART_LAYOUT, height=450)
        st.plotly_chart(f_sc_sl, use_container_width=True)
