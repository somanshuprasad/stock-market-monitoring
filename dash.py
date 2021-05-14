import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3 as sl

import sys
sys.path.append(r"C:\Users\soman\OneDrive\Desktop\Python Projects\Dad's projects\technicals-scraper")
import lib.front_end_functions


create_df = lib.front_end_functions.CreateDf()
pivot_df = create_df.pivot()

app = dash.Dash(__name__,external_stylesheets = [dbc.themes.BOOTSTRAP])
dash_datatable = dash_table.DataTable(style_data={'whiteSpace': 'normal','height': 'auto','border': '1px solid gray'},
                                style_cell={'overflow': 'hidden','textAlign': 'left'},
                                style_header={'fontWeight': 'bold','border': '1px solid black'},
                                style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(235, 235, 235)'}],
                                id="Pivot",
                                columns=[{"name": col, "id": col} for col in pivot_df.columns],
                                data=pivot_df.to_dict("records"))


div_pivot_table = html.Div([dash_datatable],style={'width': '50%', 'display': 'inline-block'})
h1_heading = html.H1("Investing.com Technicals Tracker",style={"text-align": "center"})
test_text = html.H1("Test Text")


app.layout = html.Div([h1_heading,
                       dcc.Tabs(id="tabs", children=[
                           dcc.Tab(label="Pivot",children=[div_pivot_table]),
                           dcc.Tab(label="Moving Average",children=[test_text]),
                           dcc.Tab(label="Charts", children=[test_text])
                                ]),
                       dcc.Interval(
                           id='interval-component',
                           interval=1*1000,  # in milliseconds
                           n_intervals=0)
                       ])


# Update the Price data from database in real time
# @app.callback(Output("Pivot","data"),Input("interval-component","n_intervals"))
@app.callback(Output("Pivot","data"),Input("interval-component","n_intervals"))
def update_price_df(n):
    updated_df = create_df.pivot()
    data=updated_df.to_dict("records")

    return data

# import dash
# import dash_bootstrap_components as dbc
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_table

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# div_body_tabs = dcc.Tabs

# body = html.Div([
#     html.H1("Bootstrap Grid System Example")
#     , dbc.Row(dbc.Col(html.Div(dbc.Alert("This is one column", color="primary"))))
#     , dbc.Row([
#             dbc.Col(html.Div(dbc.Alert("One of three columns", color="primary")))
#             , dbc.Col(html.Div(dbc.Alert("One of three columns", color="primary")))
#             , dbc.Col(html.Div(dbc.Alert("One of three columns", color="primary")))
#             ])
#         ])

# table1 = dash_table.DataTable(style_data={'whiteSpace': 'normal','height': 'auto'},
#                                   style_cell={'width': f"10%",'textOverflow': 'ellipsis','overflow': 'hidden'},
#                                   id="Prices",
#                                   columns=[{"name": col, "id": col} for col in df.columns],
#                                   data=df.to_dict("records"))

# tabs = dcc.Tabs(id="tabs",children=[table1,table1])

# app.layout = html.Div([body,tabs])

if __name__ == "__main__":
    app.run_server(debug = True)


