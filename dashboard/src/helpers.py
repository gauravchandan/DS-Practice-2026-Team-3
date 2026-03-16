import pandas as pd 
import streamlit as st

sources = {"Census 2011":"../../data_sources/NDAP/2011_census_final.csv", "World Bank":"../data_sources/World_Bank/Ages.csv"}

plot_types = {"Census 2011":"../../data_sources/NDAP/2011_census_final.csv","World Bank": ["Time Series"]}

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
        if plot_type == "Time Series":
            metrics = st.multiselect("Select Metrics.", self.columns)
        st.line_chart(self.df,y=metrics)
    
    
