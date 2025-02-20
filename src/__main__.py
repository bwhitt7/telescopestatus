# From plotly docs
from dash import Dash, html, dcc, callback, Output, Input
import dash
import plotly.express as px
import pandas as pd
from page_parts.page import HomePage

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__, use_pages=True, pages_folder="")

dash.register_page("home", path="/", layout= html.Div([
    html.H1(["Home Page"])
]))


for telescope in ["jwst", "hst"]:
    home_page = HomePage(telescope)
    dash.register_page(f"{telescope} - home", path=f"/{telescope}", layout=home_page.layout())

app.layout = html.Div([
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)