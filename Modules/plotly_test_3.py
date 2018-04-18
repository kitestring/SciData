from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout

# https://stackoverflow.com/questions/40243446/how-to-save-plotly-offline-graph-in-format-png?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])],auto_open=True, image = 'png', image_filename='plot_image',
             output_type='file', 
             filename='temp-plot.html', validate=False)