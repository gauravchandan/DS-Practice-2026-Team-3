import pandas as pd 
import streamlit as st
import altair as at
from src.metadata import *

# sources = {
#            "Census 2011":"../data_sources/NDAP/2011_census_final.csv", 
#            "World Bank":"../data_sources/World_Bank/Ages.csv"
#           }
#
# plot_types = {
#               "Census 2011":["Histogram"],
#               "World Bank": ["Time Series (Line Chart)", "Time Series (Scatter Plot)"]
#              }
#
# groupings = {
#               "Census 2011":['State', 'District', 'Sub-District', 'Village Or Town Name',
#        'Residence Type'],
#               "World Bank": []
#              }
#
# aggregates = ["sum", "mean", "max", "min"]


def columns_times(source):
    df = pd.read_csv(sources[source], index_col=0)
    return df.columns, df.index.tolist()


def load_data(source, columns, times):
    df =  pd.read_csv(sources[source], index_col=0)
    df['Year'] = df.index
    df = df[df['Year'].isin(times)]
    return df[columns]

class dataset():
    def __init__(self, source, columns, times):
        self.df = load_data(source, columns, times)
        self.source = source
        self.columns = columns
        self.times = times

    def list_plots(self):
        return plot_types[self.source]

    def plot(self,plot_type):
        if plot_type == "Time Series (Line Chart)":
            metrics = st.multiselect("Select Metrics.", self.columns)
            st.line_chart(self.df, y=metrics)

        if plot_type == "Time Series (Scatter Plot)":
            metrics = st.multiselect("Select Metrics.", self.columns)
            st.scatter_chart(self.df[metrics])

        if plot_type == "Histogram":
            grouping = st.selectbox("Groupby", groupings[self.source])
            aggregator = st.selectbox("Select aggregator", aggregates)
            metrics = st.multiselect("Select Metrics", self.df.select_dtypes(include='number').columns)
            grouped_df = df.groupby(grouping)[metrics]
            st.bar_chart(grouped_df)
    
    
