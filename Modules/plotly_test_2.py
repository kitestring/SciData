import plotly
import plotly.offline as offline
import plotly.graph_objs as go

# plotly.tools.set_credentials_file(username='kitestring', api_key='H3PAvTID2ZvxBGZU0gfe')

offline.init_notebook_mode()

offline.iplot({'data': [{'y': [4, 2, 3, 4]}], 
               'layout': {'title': '123test456', 
                          'font': dict(size=16)}},
             image='png', filename='C:\SciData\Modules\test.html')