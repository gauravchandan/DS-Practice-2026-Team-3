"""**BUILDING MY OWN GEOJSON FILE FOR INDIA 2011**"""

from google.colab import files
uploaded = files.upload()  # select all 5 files together

!pip install geopandas

import geopandas as gpd
import json

# Read shapefile
gdf = gpd.read_file('district.shp')

# Check what's inside
print("Shape:", gdf.shape)
print("\nColumns:", gdf.columns.tolist())
print("\nSample:")
print(gdf.head())

# Convert to GeoJSON
gdf.to_file('india_census_2011_official.geojson', driver='GeoJSON')

# Load back for Plotly
with open('india_census_2011_official.geojson') as f:
    official_geojson = json.load(f)

print("Total features:", len(official_geojson['features']))
print("\nProperties:", official_geojson['features'][0]['properties'])

# In that notebook, download the geojson file
from google.colab import files
files.download('india_census_2011_official.geojson')

#!pip install topojson

#upload india_census_2011_official.geojson and assign it to the variable large_geojson

with open('/content/india_census_2011_official.geojson') as f:  # use actual filename
    large_geojson = json.load(f)

import topojson
import json
import os

# Simplify first then convert
topo = topojson.Topology(large_geojson, prequantize=False)
topo_simplified = topo.toposimplify(0.001)
compressed = topo_simplified.to_geojson()

with open('india_compressed.geojson', 'w') as f:
    f.write(compressed)

size = os.path.getsize('india_compressed.geojson') / (1024*1024)
print(f"Compressed size: {size:.1f} MB")

from google.colab import files
files.download('india_compressed.geojson')