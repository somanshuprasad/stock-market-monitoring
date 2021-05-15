import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sqlite3 as sl

import lib.front_end_functions

#====================================================== Initializing =======================================================
create_df = lib.front_end_functions.CreateDf()
create_plot = lib.front_end_functions.CreatePlot()

pivot_df = create_df.pivot()
ma_df = create_df.mov_avg()

fig1 = create_plot.pivot()
fig2 = create_plot.pivot()
fig3 = create_plot.pivot()
fig4 = create_plot.pivot()

_,ticker_list = create_df.all_prices_tday()

app = dash.Dash(__name__)

#=================================================== Defining the pivot and ma datatables ===================================================
pivot_dash_datatable = dash_table.DataTable(style_data={'whiteSpace': 'normal','height': 'auto','border': '1px solid gray'},
                                style_cell={'overflow': 'hidden','textAlign': 'left'},
                                style_header={'fontWeight': 'bold','border': '1px solid black'},
                                style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(235, 235, 235)'}],
                                id="Pivot",
                                columns=[{"name": col, "id": col} for col in pivot_df.columns],
                                data=pivot_df.to_dict("records"),
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi")

ma_dash_datatable = dash_table.DataTable(style_data={'whiteSpace': 'normal','height': 'auto','border': '1px solid gray'},
                                style_cell={'overflow': 'hidden','textAlign': 'left'},
                                style_header={'fontWeight': 'bold','border': '1px solid black'},
                                style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(235, 235, 235)'}],
                                id="MovAvg",
                                columns=[{"name": col, "id": col} for col in ma_df.columns],
                                data=ma_df.to_dict("records"),
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi")

#=================================================== Defining the HTML Elements ===================================================
# Creating the HTML elements
div_pivot_table = html.Div([pivot_dash_datatable],style={'width': '50%', 'display': 'inline-block'})
div_ma_table = html.Div([ma_dash_datatable],style={'width': '40%', 'display': 'inline-block'})
h1_heading = html.H1("Investing.com Technicals Tracker",style={"text-align": "center"})

# Chart Tab
div_pivot_chart1 = html.Div([dcc.Graph(figure=fig1, id="pivot_chart1")])
div_pivot_chart2 = html.Div([dcc.Graph(figure=fig2, id="pivot_chart2")])
div_pivot_chart3 = html.Div([dcc.Graph(figure=fig3, id="pivot_chart3")])

div_pivot_dropdown1 = html.Div([dcc.Dropdown(id='graphs_dropdown1',value=ticker_list[0],
                                            options=[{'label': ticker,'value':ticker} for ticker in ticker_list])])
div_pivot_dropdown2 = html.Div([dcc.Dropdown(id='graphs_dropdown2',value=ticker_list[0],
                                            options=[{'label': ticker,'value':ticker} for ticker in ticker_list])])
div_pivot_dropdown3 = html.Div([dcc.Dropdown(id='graphs_dropdown3',value=ticker_list[0],
                                            options=[{'label': ticker,'value':ticker} for ticker in ticker_list])])

div_tab = html.Div([div_pivot_dropdown1,div_pivot_chart1,
                    div_pivot_dropdown2,div_pivot_chart2,
                    div_pivot_dropdown3,div_pivot_chart3
                    ],
                    style={'width': '70%', 'display': 'inline-block'})

test_text = html.H1("Test Text")

# Defining the layout
app.layout = html.Div([h1_heading,
                       dcc.Tabs(id="tabs", children=[
                           dcc.Tab(label="Pivot",children=[div_pivot_table]),
                           dcc.Tab(label="Moving Average",children=[div_ma_table]),
                           dcc.Tab(label="Charts", children=[div_tab])
                                ]),
                       dcc.Interval(
                           id='interval-component',
                           interval=5*1000,  # in milliseconds
                           n_intervals=0)
                       ])

#=================================================== Defining the tabular callbacks ===================================================
@app.callback(Output("Pivot","data"),Input("interval-component","n_intervals"))
def update_price_df(n):
    create_df = lib.front_end_functions.CreateDf()
    updated_df = create_df.pivot()
    data=updated_df.to_dict("records")
    return data

# Update the MovAvg data from database in real time
@app.callback(Output("MovAvg","data"),Input("interval-component","n_intervals"))
def update_ma_df(n):
    create_df = lib.front_end_functions.CreateDf()
    updated_df = create_df.mov_avg()
    data=updated_df.to_dict("records")
    return data

#=================================================== Defining the Chart callbacks ===================================================
@app.callback(Output("pivot_chart1","figure"),
              Input("graphs_dropdown1","value"),
              Input("interval-component","n_intervals"))
def update_pivot_chart1_df(ticker,n):
    create_plot = lib.front_end_functions.CreatePlot()
    updated_fig = create_plot.pivot(ticker)    
    return updated_fig


@app.callback(Output("pivot_chart2","figure"),
              Input("graphs_dropdown2","value"),
              Input("interval-component","n_intervals"))
def update_pivot_chart1_df(ticker,n):
    create_plot = lib.front_end_functions.CreatePlot()
    updated_fig = create_plot.pivot(ticker)
    return updated_fig

@app.callback(Output("pivot_chart3","figure"),
              Input("graphs_dropdown3","value"),
              Input("interval-component","n_intervals"))
def update_pivot_chart1_df(ticker,n):
    create_plot = lib.front_end_functions.CreatePlot()
    updated_fig = create_plot.pivot(ticker)
    return updated_fig



if __name__ == "__main__":
    app.run_server(debug = False)