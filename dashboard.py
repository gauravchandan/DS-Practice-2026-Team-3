import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json
import numpy as np

# ── Page Config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Census 2011",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark Theme CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e2e8f0;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e2e;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #141420 0%, #1a1a2e 100%);
    border: 1px solid #2d2d4a;
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #f1f5f9;
    font-family: 'DM Mono', monospace;
    line-height: 1;
    margin-bottom: 4px;
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.metric-delta {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 8px;
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
}

.metric-delta.positive {
    color: #34d399;
    background: rgba(52, 211, 153, 0.1);
}

.metric-delta.neutral {
    color: #a78bfa;
    background: rgba(167, 139, 250, 0.1);
}

/* Section headers */
.section-header {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #2d2d4a, transparent);
}

/* Chart containers */
.chart-container {
    background: #141420;
    border: 1px solid #2d2d4a;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Title */
.dashboard-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.02em;
}

.dashboard-subtitle {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 4px;
}

/* Plotly charts background fix */
.js-plotly-plot, .plotly {
    border-radius: 12px;
}

/* Sidebar title */
.sidebar-brand {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.01em;
    padding: 8px 0 24px 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 24px;
}

.sidebar-brand span {
    color: #6366f1;
}

/* Hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Divider */
hr {
    border-color: #1e1e2e;
    margin: 24px 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #141420;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #2d2d4a;
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    background: #6366f1 !important;
    color: white !important;
}

/* Select boxes */
.stSelectbox > div > div {
    background: #141420;
    border-color: #2d2d4a;
    color: #e2e8f0;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Data Loading ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    df_pivot = pd.read_csv('df_pivot.csv')
    df_pivot['pc11_d_id'] = df_pivot['pc11_d_id'].astype(int).apply(lambda x: str(x).zfill(3))
    return df_pivot

@st.cache_data
def load_state_data():
    df_lit = pd.read_csv('State-wise_literacy_rates_and_increase-in_literacy_rates_as_per_Census_during_2001_and_2011.csv')
    df_ru = pd.read_csv('State_UT-wise_Rural_and_Urban_Population_as_Per_Census_during_2001_and_2011.csv')

    df_lit = df_lit[df_lit['S. No.'] != 'INDIA'].copy()
    df_lit.drop(columns=['S. No.'], inplace=True)
    df_lit.columns = ['State','Lit_Total_2001','Lit_Total_2011','Lit_Male_2001','Lit_Male_2011',
                      'Lit_Female_2001','Lit_Female_2011','Inc_Total','Inc_Male','Inc_Female']
    df_lit['State'] = df_lit['State'].str.strip()

    df_ru.drop(columns=['S. No.', 'Note of State/ UT'], inplace=True)
    df_ru = df_ru[~df_ru['State/ UT'].str.contains('Total', na=False)].copy()
    df_ru.columns = ['State','Rural_Pop_2001','Urban_Pop_2001','Total_Pop_2001','Rural_Pct_2001',
                     'Rural_Pop_2011','Urban_Pop_2011','Total_Pop_2011','Rural_Pct_2011']
    df_ru['Urban_Pct_2011'] = (100 - df_ru['Rural_Pct_2011']).round(2)
    df_ru['Urban_Pct_2001'] = (100 - df_ru['Rural_Pct_2001']).round(2)
    df_ru['State'] = df_ru['State'].str.strip()
    df_ru['State'] = df_ru['State'].replace({'A & N Island': 'Andaman & Nicobar Islands', 'Uttarakhand': 'Uttrakhand'})

    df_state = pd.merge(df_lit, df_ru, on='State', how='outer')
    df_state['Gender_Gap_2011'] = (df_state['Lit_Male_2011'] - df_state['Lit_Female_2011']).round(2)
    df_state['Pop_Growth_Pct'] = ((df_state['Total_Pop_2011'] - df_state['Total_Pop_2001']) / df_state['Total_Pop_2001'] * 100).round(2)
    return df_state


@st.cache_data
def load_geojson():
    with open('india_compressed.geojson') as f:
        return json.load(f)

@st.cache_data
def load_boundary():
    gdf = gpd.read_file('india_compressed.geojson')
    gdf['geometry'] = gdf['geometry'].buffer(0)
    return gdf.dissolve()

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
                             line=dict(color='#94a3b8', width=1.5),
                             hoverinfo='skip', showlegend=False)

def make_choropleth(df, geojson, col, title, range_color, colorscale, india_boundary):
    fig = px.choropleth_mapbox(
        df, geojson=geojson, featureidkey='properties.pc11_d_id',
        locations='pc11_d_id', color=col,
        color_continuous_scale=colorscale, range_color=range_color,
        title=title, hover_data=['State', 'District_Name', 'Total_Pop', col],
        mapbox_style='white-bg', center={"lat": 22, "lon": 83}, zoom=3.3, opacity=0.85
    )
    fig.add_trace(get_boundary_trace(india_boundary))
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0}, height=550,
        paper_bgcolor='#141420', plot_bgcolor='#141420',
        font=dict(color='#e2e8f0', family='DM Sans'),
        title_font=dict(size=14, color='#94a3b8')
    )
    return fig

# ── Load everything ────────────────────────────────────────────────
df_pivot = load_data()
df_state = load_state_data()
geojson = load_geojson()
india_boundary = load_boundary()

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🇮🇳 Census <span>2011</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["Overview", "District Maps", "Literacy Analysis", "Demographics", "2001 vs 2011"], label_visibility="collapsed")

    st.markdown('<div class="section-header" style="margin-top:24px">Filter</div>', unsafe_allow_html=True)
    selected_state = st.selectbox("State", ["All States"] + sorted(df_pivot['State'].unique().tolist()))

    st.markdown("---")
    st.markdown('<p style="color:#334155;font-size:0.7rem;text-align:center">India Census 2011 · District Level</p>', unsafe_allow_html=True)

# Apply state filter
df_filtered = df_pivot if selected_state == "All States" else df_pivot[df_pivot['State'] == selected_state]

# ── Chart theme helper ──────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor='#141420', plot_bgcolor='#141420',
    font=dict(color='#94a3b8', family='DM Sans', size=11),
    title_font=dict(size=13, color='#cbd5e1'),
    xaxis=dict(gridcolor='#1e1e2e', zerolinecolor='#1e1e2e'),
    yaxis=dict(gridcolor='#1e1e2e', zerolinecolor='#1e1e2e'),
    margin=dict(t=40, b=20, l=10, r=10)
)

# ══════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown('<div class="dashboard-title">India Demographics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Census 2011 · District-level analysis across 640 districts</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # KPI Cards
    total_pop = df_filtered['Total_Pop'].sum()
    avg_literacy = df_filtered['Literacy_Rate'].mean()
    avg_sex_ratio = df_filtered['Sex_Ratio'].mean()
    avg_urban = df_filtered['Urban_Pct'].mean()
    num_districts = len(df_filtered)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_pop/1e6:.1f}M</div>
            <div class="metric-label">Total Population</div>
            <div class="metric-delta neutral">Census 2011</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{avg_literacy:.1f}%</div>
            <div class="metric-label">Avg Literacy Rate</div>
            <div class="metric-delta positive">↑ from 64.8% in 2001</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{avg_sex_ratio:.0f}</div>
            <div class="metric-label">Avg Sex Ratio</div>
            <div class="metric-delta neutral">per 1000 males</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{avg_urban:.1f}%</div>
            <div class="metric-label">Avg Urban Pop</div>
            <div class="metric-delta positive">↑ from 27.8% in 2001</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{num_districts}</div>
            <div class="metric-label">Districts</div>
            <div class="metric-delta neutral">across 35 states/UTs</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Overview map + histogram
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-header">Literacy Rate by District</div>', unsafe_allow_html=True)
        fig = make_choropleth(df_filtered, geojson, 'Literacy_Rate', '', [30, 100], 'Viridis', india_boundary)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Literacy Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(df_filtered, x='Literacy_Rate', nbins=25,
                                color_discrete_sequence=['#6366f1'],
                                labels={'Literacy_Rate': 'Literacy Rate (%)'})
        fig_hist.update_layout(height=260, showlegend=False, **CHART_LAYOUT,
                                bargap=0.05)
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown('<div class="section-header" style="margin-top:8px">Sex Ratio Distribution</div>', unsafe_allow_html=True)
        fig_hist2 = px.histogram(df_filtered, x='Sex_Ratio', nbins=25,
                                  color_discrete_sequence=['#a78bfa'],
                                  labels={'Sex_Ratio': 'Females per 1000 Males'})
        fig_hist2.update_layout(height=220, showlegend=False, **CHART_LAYOUT, bargap=0.05)
        st.plotly_chart(fig_hist2, use_container_width=True)

    # Bottom row
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-header">Top 5 & Bottom 5 Districts — Literacy</div>', unsafe_allow_html=True)
        top5 = df_filtered.nlargest(5, 'Literacy_Rate')[['District_Name', 'State', 'Literacy_Rate']]
        bot5 = df_filtered.nsmallest(5, 'Literacy_Rate')[['District_Name', 'State', 'Literacy_Rate']]
        top5['Category'] = 'Top 5'
        bot5['Category'] = 'Bottom 5'
        combined = pd.concat([top5, bot5])
        fig_tb = px.bar(combined, x='Literacy_Rate', y='District_Name', color='Category',
                        orientation='h',
                        color_discrete_map={'Top 5': '#34d399', 'Bottom 5': '#f87171'},
                        hover_data=['State'])
        fig_tb.update_layout(height=320, yaxis={'categoryorder': 'total ascending'}, **CHART_LAYOUT)
        st.plotly_chart(fig_tb, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Rural vs Urban Literacy — Top 10 States</div>', unsafe_allow_html=True)
        state_lit = df_pivot.groupby('State').agg(
            Rural_Lit=('Literacy_Rate_Rural', 'mean'),
            Urban_Lit=('Literacy_Rate_Urban', 'mean')
        ).reset_index().sort_values('Rural_Lit').tail(10)
        fig_ru = px.bar(state_lit, x='State', y=['Rural_Lit', 'Urban_Lit'], barmode='group',
                        color_discrete_map={'Rural_Lit': '#38bdf8', 'Urban_Lit': '#f472b6'})
        fig_ru.update_layout(height=320, xaxis_tickangle=-30, legend_title='', **CHART_LAYOUT)
        st.plotly_chart(fig_ru, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: DISTRICT MAPS
# ══════════════════════════════════════════════════════════════════
elif page == "District Maps":
    st.markdown('<div class="dashboard-title">District-Level Maps</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Choropleth maps across key demographic indicators</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    indicator = st.selectbox("Select Indicator", [
        "Literacy Rate (%)",
        "Sex Ratio (F per 1000 M)",
        "Urban Population (%)",
        "Rural Population (%)",
        "Urban-Rural Literacy Gap",
        "Rural Literacy Rate (%)",
        "Urban Literacy Rate (%)"
    ])

    config = {
        "Literacy Rate (%)": ('Literacy_Rate', [30, 100], 'Viridis'),
        "Sex Ratio (F per 1000 M)": ('Sex_Ratio', [600, 1200], 'RdYlGn'),
        "Urban Population (%)": ('Urban_Pct', [0, 100], 'Blues'),
        "Rural Population (%)": ('Rural_Pct', [0, 100], 'Greens'),
        "Urban-Rural Literacy Gap": ('Literacy_Gap', [0, 40], 'Reds'),
        "Rural Literacy Rate (%)": ('Literacy_Rate_Rural', [20, 100], 'YlGn'),
        "Urban Literacy Rate (%)": ('Literacy_Rate_Urban', [40, 100], 'YlOrRd'),
    }

    col, range_c, cscale = config[indicator]
    fig = make_choropleth(df_pivot, geojson, col, indicator, range_c, cscale, india_boundary)
    fig.update_layout(height=650)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: LITERACY ANALYSIS
# ══════════════════════════════════════════════════════════════════
elif page == "Literacy Analysis":
    st.markdown('<div class="dashboard-title">Literacy Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">District and state-level literacy breakdown</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Top & Bottom Districts", "Rural vs Urban", "Scatter Analysis"])

    with tab1:
        n = st.slider("Number of districts", 5, 20, 10)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">By Literacy Rate</div>', unsafe_allow_html=True)
            top = df_filtered.nlargest(n, 'Literacy_Rate')[['District_Name', 'State', 'Literacy_Rate']]
            bot = df_filtered.nsmallest(n, 'Literacy_Rate')[['District_Name', 'State', 'Literacy_Rate']]
            top['Category'] = f'Top {n}'
            bot['Category'] = f'Bottom {n}'
            combined = pd.concat([top, bot])
            fig = px.bar(combined, x='Literacy_Rate', y='District_Name', color='Category',
                         orientation='h', hover_data=['State'],
                         color_discrete_map={f'Top {n}': '#34d399', f'Bottom {n}': '#f87171'})
            fig.update_layout(height=550, yaxis={'categoryorder': 'total ascending'}, **CHART_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">By Sex Ratio</div>', unsafe_allow_html=True)
            top_sr = df_filtered.nlargest(n, 'Sex_Ratio')[['District_Name', 'State', 'Sex_Ratio']]
            bot_sr = df_filtered.nsmallest(n, 'Sex_Ratio')[['District_Name', 'State', 'Sex_Ratio']]
            top_sr['Category'] = f'Top {n}'
            bot_sr['Category'] = f'Bottom {n}'
            combined_sr = pd.concat([top_sr, bot_sr])
            fig_sr = px.bar(combined_sr, x='Sex_Ratio', y='District_Name', color='Category',
                            orientation='h', hover_data=['State'],
                            color_discrete_map={f'Top {n}': '#818cf8', f'Bottom {n}': '#fb7185'})
            fig_sr.update_layout(height=550, yaxis={'categoryorder': 'total ascending'}, **CHART_LAYOUT)
            st.plotly_chart(fig_sr, use_container_width=True)

    with tab2:
        state_lit = df_pivot.groupby('State').agg(
            Rural_Lit=('Literacy_Rate_Rural', 'mean'),
            Urban_Lit=('Literacy_Rate_Urban', 'mean'),
            Lit_Gap=('Literacy_Gap', 'mean')
        ).reset_index().sort_values('Rural_Lit')

        fig_ru = px.bar(state_lit, x='State', y=['Rural_Lit', 'Urban_Lit'], barmode='group',
                        title='Rural vs Urban Literacy Rate by State — 2011',
                        color_discrete_map={'Rural_Lit': '#38bdf8', 'Urban_Lit': '#f472b6'},
                        labels={'value': 'Literacy Rate (%)', 'variable': 'Area'})
        fig_ru.update_layout(height=450, xaxis_tickangle=-45, **CHART_LAYOUT)
        st.plotly_chart(fig_ru, use_container_width=True)

        fig_gap = px.bar(state_lit.sort_values('Lit_Gap', ascending=False),
                         x='Lit_Gap', y='State', orientation='h',
                         color='Lit_Gap', color_continuous_scale='Reds',
                         title='Average Urban-Rural Literacy Gap by State',
                         labels={'Lit_Gap': 'Gap (pp)', 'State': ''})
        fig_gap.update_layout(height=600, **CHART_LAYOUT)
        st.plotly_chart(fig_gap, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fig_s1 = px.scatter(df_filtered, x='Urban_Pct', y='Literacy_Rate',
                                color='Total_Pop', color_continuous_scale='Viridis',
                                hover_data=['State', 'District_Name', 'Total_Pop'],
                                title='Literacy Rate vs Urbanisation',
                                labels={'Urban_Pct': 'Urban %', 'Literacy_Rate': 'Literacy Rate (%)',
                                        'Total_Pop': 'Population'},
                                opacity=0.7)
            fig_s1.update_traces(marker=dict(size=6))
            fig_s1.update_layout(height=400, **CHART_LAYOUT)
            st.plotly_chart(fig_s1, use_container_width=True)

        with col2:
            fig_s2 = px.scatter(df_filtered, x='Literacy_Rate', y='Sex_Ratio',
                                color='Urban_Pct', color_continuous_scale='RdYlGn',
                                hover_data=['State', 'District_Name'],
                                title='Sex Ratio vs Literacy Rate',
                                labels={'Literacy_Rate': 'Literacy Rate (%)',
                                        'Sex_Ratio': 'Sex Ratio', 'Urban_Pct': 'Urban %'},
                                opacity=0.7)
            fig_s2.update_traces(marker=dict(size=6))
            fig_s2.update_layout(height=400, **CHART_LAYOUT)
            st.plotly_chart(fig_s2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: DEMOGRAPHICS
# ══════════════════════════════════════════════════════════════════
elif page == "Demographics":
    st.markdown('<div class="dashboard-title">Demographic Breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Population, sex ratio and urbanisation patterns</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Gender Literacy Gap by State — 2011</div>', unsafe_allow_html=True)
        df_gap = df_state.dropna(subset=['Gender_Gap_2011']).sort_values('Gender_Gap_2011', ascending=False)
        fig_gg = px.bar(df_gap, x='Gender_Gap_2011', y='State', orientation='h',
                        color='Gender_Gap_2011', color_continuous_scale='Reds',
                        labels={'Gender_Gap_2011': 'Gap (pp)', 'State': ''})
        fig_gg.update_layout(height=600, **CHART_LAYOUT)
        st.plotly_chart(fig_gg, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Population Growth Rate — 2001 to 2011</div>', unsafe_allow_html=True)
        df_growth = df_state.dropna(subset=['Pop_Growth_Pct'])
        df_growth = df_growth[df_growth['State'] != 'Andhra Pradesh'].sort_values('Pop_Growth_Pct', ascending=False)
        fig_growth = px.bar(df_growth, x='Pop_Growth_Pct', y='State', orientation='h',
                            color='Pop_Growth_Pct', color_continuous_scale='RdYlGn',
                            labels={'Pop_Growth_Pct': 'Growth (%)', 'State': ''})
        fig_growth.update_layout(height=600, **CHART_LAYOUT)
        st.plotly_chart(fig_growth, use_container_width=True)

    st.markdown('<div class="section-header">Urbanisation Rate by State — 2001 vs 2011</div>', unsafe_allow_html=True)
    df_urb = df_state.dropna(subset=['Urban_Pct_2011']).sort_values('Urban_Pct_2011')
    fig_urb = px.bar(df_urb, x='State', y=['Urban_Pct_2001', 'Urban_Pct_2011'], barmode='group',
                     color_discrete_map={'Urban_Pct_2001': '#fbbf24', 'Urban_Pct_2011': '#a78bfa'},
                     labels={'value': 'Urban Population (%)', 'variable': 'Year'})
    fig_urb.update_layout(height=420, xaxis_tickangle=-45, **CHART_LAYOUT)
    st.plotly_chart(fig_urb, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# PAGE: 2001 vs 2011
# ══════════════════════════════════════════════════════════════════
elif page == "2001 vs 2011":
    st.markdown('<div class="dashboard-title">2001 vs 2011 Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Tracking change across a decade of census data</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Literacy Rate — 2001 vs 2011</div>', unsafe_allow_html=True)
        df_plot = df_state.dropna(subset=['Lit_Total_2011']).sort_values('Lit_Total_2011')
        fig_lt = px.bar(df_plot, x='State', y=['Lit_Total_2001', 'Lit_Total_2011'], barmode='group',
                        color_discrete_map={'Lit_Total_2001': '#6366f1', 'Lit_Total_2011': '#34d399'},
                        labels={'value': 'Literacy Rate (%)', 'variable': 'Year'})
        fig_lt.update_layout(height=420, xaxis_tickangle=-45, **CHART_LAYOUT)
        st.plotly_chart(fig_lt, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Most Improved States — Literacy Gain</div>', unsafe_allow_html=True)
        df_imp = df_state.dropna(subset=['Inc_Total']).sort_values('Inc_Total', ascending=False)
        fig_imp = px.bar(df_imp, x='Inc_Total', y='State', orientation='h',
                         color='Inc_Total', color_continuous_scale='Viridis',
                         labels={'Inc_Total': 'Increase (pp)', 'State': ''})
        fig_imp.update_layout(height=420, **CHART_LAYOUT)
        st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown('<div class="section-header">Male vs Female Literacy — 2001 & 2011</div>', unsafe_allow_html=True)
    df_mf = df_state.dropna(subset=['Lit_Male_2011']).sort_values('Lit_Total_2011')
    fig_mf = px.bar(df_mf, x='State',
                    y=['Lit_Male_2001', 'Lit_Female_2001', 'Lit_Male_2011', 'Lit_Female_2011'],
                    barmode='group',
                    color_discrete_map={
                        'Lit_Male_2001': '#6366f1', 'Lit_Female_2001': '#f472b6',
                        'Lit_Male_2011': '#818cf8', 'Lit_Female_2011': '#fb7185'
                    },
                    labels={'value': 'Literacy Rate (%)', 'variable': 'Group'})
    fig_mf.update_layout(height=420, xaxis_tickangle=-45, **CHART_LAYOUT)
    st.plotly_chart(fig_mf, use_container_width=True)
