import pandas as pd
import plotly.express as px
from data_fetching import telescope_data

def pie_instruments(telescope):
    df = telescope_data[telescope]
    counts = df['instrument_name'].value_counts()
    df_result = pd.DataFrame(counts).reset_index() 
    fig = px.pie(df_result, names="instrument_name", values="count")
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    return fig
