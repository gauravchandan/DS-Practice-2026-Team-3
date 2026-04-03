import pandas as pd
import json
import plotly.express as px

df = pd.read_csv('data/df_pivot.csv')
df['pc11_d_id'] = df['pc11_d_id'].astype(int).apply(lambda x: str(x).zfill(3))
df_f = df[df['State'].str.title() == 'Chandigarh']

with open('data/india_compressed.geojson') as f:
    geojson = json.load(f)

def calc_bounds(geojson, target_ids):
    lons, lats = [], []
    for f in geojson['features']:
        if str(f['properties'].get('pc11_d_id')) in target_ids:
            coords = f['geometry']['coordinates']
            geom_type = f['geometry']['type']
            if geom_type == 'Polygon':
                for ring in coords:
                    for pt in ring:
                        lons.append(pt[0]); lats.append(pt[1])
            elif geom_type == 'MultiPolygon':
                for poly in coords:
                    for ring in poly:
                        for pt in ring:
                            lons.append(pt[0]); lats.append(pt[1])
    if not lons: return None
    return {"west": min(lons), "east": max(lons), "south": min(lats), "north": max(lats)}

bounds = calc_bounds(geojson, df_f['pc11_d_id'].tolist())

fig = px.choropleth_mapbox(
    df_f, geojson=geojson, featureidkey='properties.pc11_d_id',
    locations='pc11_d_id', color='Total_Pop',
    mapbox_style="carto-darkmatter"
)
if bounds:
    fig.update_layout(mapbox_bounds=bounds)
else:
    fig.update_layout(mapbox=dict(center={"lat": 22, "lon": 83}, zoom=3.3))

fig.write_image("test_choro2.png", engine="kaleido")
