from astroquery.mast import Observations
from astropy.time import Time
import pandas as pd
import plotly.express as px
    
class TelescopeData:
    
    def __init__(self, telescope: str):
        self.telescope = telescope
        self.data = pd.DataFrame()
        self.fetch_telescope_data()

    def fetch_telescope_data(self):
        min_time = Time("2024-01-01T00:00:00", format="isot")
        max_time = Time.now()

        # Otherwise, connect to MAST through astroquery and load data.
        print(f"[Loading {self.telescope} data from MAST...]")
        try:
            obs = Observations.query_criteria(obs_collection=[self.telescope.upper()], t_min=[min_time.mjd, max_time.mjd])
            # Convert to pandas
            self.data = obs.to_pandas()
            print("[Done]")
        except Exception as e:
            # Currently get a lot of Memory Errors, probably because my laptop RAM isn't the best
            print("[Error getting data")
            print(e)
    
    def pie_instruments(self):
        counts = self.data['instrument_name'].value_counts()
        df_result = pd.DataFrame(counts).reset_index() 
        fig = px.pie(df_result, names="instrument_name", values="count")
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        return fig