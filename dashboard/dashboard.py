from unittest import result
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import flask

from utils import *

BS = "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/pulse/bootstrap.min.css"
px.set_mapbox_access_token("pk.eyJ1IjoicWRlbGkiLCJhIjoiY2w0cHc0MzY4MGowNzNmbnY1and0Ym1yeiJ9.xEZ0n9648brEhFsIQU69Wg")

server = flask.Flask(__name__)

app = Dash(__name__,external_stylesheets=[BS],server=server)

result = init_df()
filtered = filter_df(result,6000,result.Discipline.unique())
fig = get_map(filtered)
table_fig = get_table(filtered)

graph = dcc.Graph(
            id='map',
            figure=fig,
            style={
                "width":"100%",
                "border-radius":"15px",
                "padding":"20px",
                "margin-bottom":"20px",
                "background-color":"#4C3575"
                }
        ) 

table_plot = dcc.Graph(
    id="table",
    figure= table_fig,
    style={
                "width":"100%",
                "border-radius":"15px",
                "background-color":"#4C3575"
                }
)

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("Mon Classement"),
                dcc.Input(id="rank", type="number", value=6000,style={"margin":"10px","width":"90%","border-radius":"10px","display":"block"}),
            ]
        ),
        html.Div(
            [
                dbc.Label("Spécialité",style={"margin-bottom":"10px"}),
                dcc.Checklist(
                    id="spe",
                    options=[
                        col for col in result["Discipline"].dropna().unique()
                    ],
                    style={"padding-left":"10px","display":"inline"},
                    labelStyle={"display": "flex"},
                ),
            ]
        )  
    ],
    style={
        "width":"30%",
        "border-radius":"15px",
        "padding":"20px",
        "background-color":"#4C3575",
        "color":"white"
        }
)

app.layout = html.Div(
    children=[
        html.Div(
            [
                html.H1("Bienvenue sur Vite Ma Spé !",
                style={"color":"white","text-align":"center"}),
                html.H5(
                    """Choisir sa spé c'est pas facile, j'espère que cet outil vous aidera ! Renseignez votre classement et
                     selectionnez les spés qui vous intéresse. Si il reste des places elles seront indiquées sur la carte et dans
                     le tableau. Vous pouvez zoomer et deplacer la carte ainsi que de passer votre souris pour plus d'informations sur la ville.
                     Ces données sont normalement aussi a jour que celles sur le cng santé, qui est la source de données.
                     C'est le dernier moment difficile de votre externat après ça à vous l'internat !""",
                style={"color":"white","text-align":"center"}
                ),
                html.P(
                    """Disclaimer : ceci est un outil fait avec les moyens du bord je ne suis en cas responsable si les données sont erronnées / absentes. 
                    Les tests que j'ai fait au moment du developpement étaient concluant néanmoins gardez bien le site du cng à coté pour être sûr que les informations sont vraies""",
                style={"color":"white","text-align":"center"}
                )
            ],
            style={
                "background-color":"#4C3575",
                "border-radius" : "10px",
                "padding":"20px",
                "margin-bottom":"20px"
            }
        ),
        html.Div(
            [
                controls,
                html.Div([
                    graph,
                    table_plot
            ],style={"width":"68%"})
            ],
            style={
                "display":"flex",
                "flex-direction":"row",
                "align-items":"flex-start",
                "justify-content":"space-between",
                }
        )
    ],
    style={
        "background-color":"#371B58",
        "padding":"20px"
        }
)



@app.callback(
    [
        Output(component_id="map",component_property="figure"),
        Output(component_id="table",component_property="figure")
    ],
    [
        Input(component_id="rank",component_property="value"),
        Input(component_id="spe",component_property="value")]
)
def onCursorChange(rank , spe):
    if spe == None or spe == []:
        spe = result.Discipline.unique()
    fdf = filter_df(result,rank,spe) 
    rfig = get_map(fdf)
    rtable = get_table(fdf)
    return rfig , rtable

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
