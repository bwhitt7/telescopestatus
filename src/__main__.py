# From plotly docs
from dash import Dash, html, dcc
from graphs import pie_instruments
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Container([
        html.H1("Home Page"),
        dbc.Card([
            html.H2(["JWST Instrument Usage"]),
            dcc.Graph(figure=pie_instruments("jwst"))
        ], class_name="p-3")
    ])
])

if __name__ == '__main__':
    app.run(debug=True)