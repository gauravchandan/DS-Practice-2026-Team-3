import pandas as pd
import json

df = pd.read_csv('data/df_pivot.csv')
df['pc11_d_id'] = df['pc11_d_id'].astype(int).apply(lambda x: str(x).zfill(3))

with open('data/india_compressed.geojson') as f:
    geojson = json.load(f)

lons, lats = [], []
target_ids = set(df['pc11_d_id'].tolist())
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

if lons and lats:
    print({"west": min(lons), "east": max(lons), "south": min(lats), "north": max(lats)})
else:
    print("NO LONS/LATS")
