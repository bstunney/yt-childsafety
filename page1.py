
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
#youtube_api_key = "AIzaSyBHEAurZG_mPwMO8Qde6Av19v_SPZP6qYc"
youtube_api_key = "AIzaSyCbn2IWXVEn0vuFZdNzK5U8V1Cjv_JEp-s"

from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots
import time

import badwords

def main():
    # Use a breakpoint in the code line below to debug your script.
    transcript = badwords.get_transcript("xD9RpU7ZRuk")
    lst1 = badwords.get_badwords("en.txt")
    lst2 = badwords.get_badwords("badwords.txt")
    biglst = [["", "", ""]]
    df = pd.DataFrame(biglst, columns=['Name', "Description", "ID"])

    biglst, multiplewordlst = badwords.clean_badwords(lst1, lst2)

    #badlst = transcript_analyze(transcript, biglst, multiplewordlst)
    #get_stats(badlst, transcript)

    # make app
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    # stylesheet with the .dbc class
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
    app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL,dbc.themes.BOOTSTRAP,dbc_css])


    channel_input = dcc.Input(
        id="input-value",
        type="text",
        value = "",
        size ="lg",
        style={"font-size": "1.6rem","margin-top": ".5px"},
        className="mb-3"
    )
    button = dbc.Button(
        id="search-button",
        children="Search",
        n_clicks=0,
        size="lg",
        style={"font-size": "1.2rem", "margin-left": "12px", "margin-top": "-8px"},
        color="primary",
        className="me-1",
    )

    search_results = dash_table.DataTable(
            id='table',
            #columns=[{"name": i, "id": i} if i != "ID" else {"name": i, "id": i, "hidden": True} for i in df.columns],
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_selectable="single",
            style_cell_conditional=[
                {'if': {'column_id': i},
                 'textAlign': 'left'
             } for i in ['Name', "Description"]
            ],
            style_data_conditional=[
                {'if': {'column_id': 'ID', },
                     'display': 'None', }],
            style_header_conditional=[
                {'if': {'column_id': 'ID', },
                     'display': 'None', }],
            style_as_list_view=True,
        )

    header = html.H1("YouTube Channel Child Safety Rating",
                     style = {"margin-top": "50px"})

    caption = html.H6("Search Youtube Channel By Username",
                      style={"margin-top": "10px"})

    next_button = dbc.Button(
                id="next-button",
                children="Get Profanity Rating",
                n_clicks=0,
                size="lg",
                className="mb-3",
                color="primary",
                style={"font-size": "1.2rem", "margin-top": "20px", 'background-color': 'gray'},
            )


    collapse1 = html.Div(
        [
            dbc.Collapse(
                dbc.Card(dbc.CardBody([header, caption, channel_input, button, html.Div(className='gap'),
                 search_results])),
                id="collapse1",
                is_open=True,
            ),
        ]
    )

    channel_name = html.H1("Channel Name Here",
                           id = 'channel-name',
                           style={"margin-top": "50px"})

    avg_num_explicit_phrases = html.H6("avg per video here",
                                       id='avg-num',
                                       style={"margin-top": "10px"})

    avg_percent_explicit_phrases = html.H6("avg percent per video here",
                                           id='avg-prop',
                                           style={"margin-top": "10px"})

    collapse2 = html.Div(
        [
            next_button,
            dbc.Collapse(
                dbc.Card(dbc.CardBody([channel_name, avg_num_explicit_phrases, avg_percent_explicit_phrases])),
                id="collapse2",
                is_open=False,
            ),
        ]
    )

    html.Div(
        [
            dcc.Input([next_button]),
            dcc.Loading(
                id="loading-2",
                children=[html.Div([html.Div(id="collapse2")])],
                type="circle",
            )
        ]
    )


    app.layout = dbc.Container(
        [

        # top line of Dash
        dbc.Row([
            dbc.Col(
                # YouTube Channel Profanity Rating
                [collapse1, collapse2],
                #[collapse, header, caption, channel_input, button, html.Div(className='gap'),
                 #search_results],
                lg=6
            )
        ],
            justify = "center",
            style = dict(textAlign="center"),
            className="d-flex justify-content-center",
        ),],
        className="p-4",
        fluid = True)

    @app.callback(
        Output("search-button", "style"),
        Input("input-value", "value"),
    )
    def change_button_color(channel_input):
        if channel_input != "":
            return {"font-size": "1.2rem", "margin-left": "12px", "margin-top": "-8px", "background-color":"red"}
        else:
            return {"font-size": "1.2rem", "margin-left": "12px", "margin-top": "-8px", 'background-color': 'gray'}

    @app.callback(
        Output("table", "data"),
        Output("search-button", "n_clicks"),
        Input("search-button", "n_clicks"),
        Input("input-value", "value"),
    )
    def init_countdown_store(n_clicks, search_results):

        biglst = [["", "", ""]]
        df = pd.DataFrame(biglst, columns=['Name', "Description", "ID"])
        if n_clicks > 0:
            ndf = badwords.get_channelid_options(search_results)
            #df['ID'] = df['ID'].str.slice(0, 3)
            return ndf.to_dict('records'), 0
        else:
            return df.to_dict('records'), 0

    @app.callback(
        Output("next-button", "style"),
        Input("table", "derived_virtual_selected_rows"),
        [Input('next-button', 'n_clicks')]
    )
    def change_button_color(derived_virtual_selected_rows, n):
        if derived_virtual_selected_rows != [] and derived_virtual_selected_rows != None and n:
            return {"font-size": "1.2rem", "margin-top": "20px", "margin-left": "15px", 'background-color': 'blue'}
        if derived_virtual_selected_rows != [] and derived_virtual_selected_rows != None:
            return {"font-size": "1.2rem", "margin-top": "20px","margin-left": "15px", 'background-color': 'red'}
        else:
            return {"font-size": "1.2rem", "margin-top": "20px", 'background-color': 'gray'}

    """
    @app.callback(Output("collapse2", "is_open"), Output("collapse1", "is_open"),Input("next-button", "n_clicks"),
                  [State('collapse1', 'is_open')],
                [State('collapse2', 'is_open')])
    def input_triggers_spinner(n, is_open1, is_open2):
        print(n)
        if n:
            time.sleep(1)
            return not is_open1, not is_open2
        else:
            return is_open1, is_open2
    """
    @app.callback(Output('collapse1', 'is_open'),
                  Output('collapse2', 'is_open'),
                  Output('channel-name','children'),
                  Output('avg-num', 'children'),
                  Output('avg-prop', 'children'),
                  Output('next-button', 'children'),
                  [Output('table', 'derived_virtual_selected_rows')],
                  [Output('next-button', 'n_clicks')],
                  [Input('next-button', 'n_clicks')],
                  Input("table","derived_virtual_selected_rows"),
                  Input('table', 'data'),
                  [State('collapse1', 'is_open')],
                [State('collapse2', 'is_open')])

    def toggle_collapse1(n, derived_virtual_selected_rows, data, is_open1, is_open2):

        if n:
            if derived_virtual_selected_rows != [] and derived_virtual_selected_rows != None:
                num_phrases, prop_phrases = badwords.get_channel_stats(data[derived_virtual_selected_rows[0]]['ID'])
                num = "Average Number of Explicit Words/Phrases Used per Video: " +str(num_phrases)
                prop = "Average Percentage of Explicit Words/Phrases per Video: " + str(round(prop_phrases * 100, 2)) +"%"
                return not is_open1, not is_open2, data[derived_virtual_selected_rows[0]]['Name'], num, prop, \
                       "Search Channels",  None, 0
        elif is_open2 == True:
            return not is_open1, not is_open2, "Channel Name Here", 0,0, "Search Channels",  derived_virtual_selected_rows, n
        else:
            return is_open1, is_open2, "Channel Name Here", 0, 0, "Search Channels", derived_virtual_selected_rows, n


    # run server
    app.run_server(debug=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

