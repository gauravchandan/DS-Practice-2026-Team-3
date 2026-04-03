import plotly.express as px
import pandas as pd

df = pd.DataFrame({'id':['1'],'v':[1]})
fig = px.choropleth_mapbox(df, locations='id')

# Try setting to None
fig.update_layout(mapbox=dict(center=None, zoom=None, bounds={"west": 70, "east": 80, "south": 10, "north": 20}))
print(fig.layout.mapbox)
