#Importing Dash web development Libraries, pandas library and geographical libraries for points and latitudes.
import dash
import code_majeur
import pandas as pd
import dash_table as dt
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from shapely.geometry import Point
from dash.dependencies import Input,Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


#Defining the web app
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

#Defining the layout of the questions to be asked 
app.layout = html.Div([
    html.H1("Welcome to the state of New York"),
    html.Div("Put down the radius of the region(Please only insert a float number)"),
    dcc.Input(id='radius', type='text', debounce=True,  step=1),
    html.Div("Put the longitude coordinate (New York State varies approximately from -79.5 to -71.5)(Please put all numeric quantities here)"),
    dcc.Input(id='x_cord', type='text', debounce=True,  step=1),
    html.Div("Put the latitude coordinate (New York State varies approximately from 40 to 45)(Please put all the numeric characters here)"),
    dcc.Input(id='y_cord', type='text', debounce=True,  step=1),
    html.Button('Click here to see the results', id='button'),
    html.Div(id='my-div')
])

#Define a basic output string in case the numbers don't add up to the exact region of interest and all the three required inputs.(radius ,x coordinate and y coordinate)
@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='radius', component_property='value'),
     Input(component_id='x_cord', component_property='value'),
     Input(component_id='y_cord', component_property='value')
    ]
)
def update_output_div(rad,x_val,y_val):
    if (x_val is None):
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate
    if (y_val is None):
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate
    if (rad is None):
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate
    #Try converting the float number strings to float type.
    try:
        x = float(x_val)
        y = float(y_val)
        r = float(rad)
    except:
        return "You probably didn't put a number there.Please input a number in them or it won't work"
    #Converts the coordinates into geographical coordinate type mentioned in the Shapely class
    pint = Point(float(x_val),float(y_val))
    #Results of the main code taken here. Dictionary a is used for graph plotting. List b is used for common street names. List c is used for unusual names 
    a,b,c = code_majeur.resultat(pint,r)
    #list of dictionaries converted into dataframes for casting them on web as tables.
    df = pd.DataFrame(b)
    tf = pd.DataFrame(c)
    #print (len(ass)==1)
    if (len(a)==1):
        return 'There are no items here . Please search elsewhere or put the right coordinates of the région'
    else:
        return html.Div(
            [
                html.H2("Histogram for the top "+str(len(a))+" types of roads in New York"),
                dcc.Graph(
                    id='column',
                    figure = {
                        'data' : [
                            go.Bar(
                                x = list(a.keys()),
                                y = list(a.values()),
                            )
                        ],
                        'layout' :go.Layout(
                            legend={'x':0, 'y': 1},
                            hovermode = 'closest'
                        )
                    }
                ),
                html.H2("20 Most common street names in New York"),
                html.Div(
                    dt.DataTable(
                        id = 'table',
                        columns=[{"id": i, "name": i} for i in df.columns],
                        data=df.to_dict("rows"),
                    ),
                ),
                html.H2("20 Unusual street names in New York"),
                html.Div(
                    dt.DataTable(
                        id = 'table',
                        columns=[{"name": i, "id": i} for i in tf.columns],
                        data=tf.to_dict("rows"),
                    ),
                ),
            ],    
        )
        

#

if __name__ == '__main__':
	app.run_server(debug=True)
