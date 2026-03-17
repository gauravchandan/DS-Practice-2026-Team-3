sources = {
           "Census 2011":"../data_sources/NDAP/2011_census_final.csv", 
           "World Bank":"../data_sources/World_Bank/Ages.csv"
          }

plot_types = {
              "Census 2011":["Histogram"],
              "World Bank": ["Time Series (Line Chart)", "Time Series (Scatter Plot)"]
             }

groupings = {
              "Census 2011":['State', 'District', 'Sub-District', 'Village Or Town Name',
       'Residence Type'],
              "World Bank": []
             }

aggregates = ["sum", "mean", "max", "min"]

