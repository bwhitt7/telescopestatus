from dash import html

class Page():
    def __init__(self, telescope: str):
        self.telescope = telescope
    
    def layout(self):
        return html.Div()

class HomePage(Page):
    def layout(self):
        return html.Div([
            html.H1([f"Home Page for {self.telescope}"])
        ])