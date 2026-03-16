import streamlit as st
import pandas as pd
import src.helpers as dload 

st.title("Demographic Data Dashboard for India")


source = st.sidebar.selectbox("Pick a data source.", ["World Bank", "Census 2011"])
columns, times =  dload.columns_times(source)

columns = st.sidebar.multiselect('Select Indicators', columns)

# Add a slider to the sidebar:
times = st.sidebar.slider('Select time range', times[0], times[-1], (times[0], times[-1]))
times = range(times[0],times[1]+1)

data = dload.dataset(source,columns,times)

st.write(data.df)

st.write("Plot Something")

plot_type = st.selectbox("Select Type of Plot", data.list_plots())

data.plot(plot_type)
