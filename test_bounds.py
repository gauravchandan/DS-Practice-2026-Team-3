import plotly.express as px
import pandas as pd

df = pd.DataFrame({"id": ["a"], "val": [1]})
fig = px.choropleth_mapbox(df, locations="id", mapbox_style="carto-darkmatter")
try:
    fig.update_layout(mapbox_bounds={"west": 70, "east": 80, "south": 10, "north": 20})
    print("mapbox_bounds is valid")
except Exception as e:
    print(e)
    
print(fig.to_dict()['layout'].keys())
