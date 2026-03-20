## Testing

Make sure you have streamlit installed (`pip install streamlit` should do the job). In the unlikely event that you have missing dependencies, you can use `pip install requirements.txt` as a last resort to install all the packages I have in my local venv dedicated to this project.

Use `streamlit dash.py` from inside the `/dashboard` directory to open the dashboard in a browser window and play around. Warning: Some things might be broken.

*Note:* Only those columns of the data you select in the sidebar of the dashboard will be loaded in. So if you wanna group by, say 'State' or display a time-series plot you will have to explicitly select the 'State' or 'Year' columns to be imported. This can be a little unintuitive, so a fix here is most welcome.

## Convention for new datasets

The way I've set up the code, I will need your datasets to follow the convention that the first column lists the year (I'm assuming we don't have any datasets with finer timescales). Even if the data corresponds to a single year just add a column whose every entry is that year.

Add any datasets you want in the `/datasets` folder as a `.csv` file.

## Code structure

`/src` contains `.py` files imported in `dash.py`. 

`helpers.py` contains the code to import datasets based on selected columns and time ranges. The imported dataset is stored as an object of the class `dataset` and contains methods to display various kinds of plots associated to it. 

`metadata.py` just contains some very important dictionaries (They're in a separate file just for readability). `sources`, as the name suggests contains the names of the datasets (which is what will be displayed in the dashboard) and their paths ***relative to `dash.py`***. These paths will be used in `helpers.py` to import the `.csv` files.

`plot_types` lists all the plots that will be made available for a given dataset. The names are what will be seen in the dashboard and need not correspond to library functions or anything. The `plot` method of the `dataset` class in `helpers.py` is configured to take these plot types as an input and do the necessary work. This is the way to add your own plots to the dashboard. Add your plotting code to a new `if` block in the definition of `helpers.dataset.plot()` with whatever name you want to give to that plot and add the same name to the list corresponding to the relevant dataset in the `plot_types` dictionary.

`groupings` lists features that the data can be grouped by before plotting and `aggregates` is just a list of ways to derive a single value for a column from all the rows that might be grouped. I'm not sure if we really need the `groupings` dictionaries as we can just offer the user the choice to group based on any non-numeric columns in the data, but as of now that hasn't been done.

The code itself doesn't contain any documentation, but I'm hoping it's readable enough (thanks to streamlit being surprisingly easy to get started with) that it can still be worked on. Apologies if I'm horribly wrong about this.
