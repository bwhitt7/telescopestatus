from astroquery.mast import Observations
from astropy.time import Time
import astropy.units as u
import pandas as pd
import plotly.express as px
    
class TelescopeData:
    """
    Stores, generates, and visualizes MAST data for a given telescope (JWST, HST, or TESS).
    """
    
    def __init__(self, telescope: str):
        """
        Args:
            telescope (str): The telescope to fetch data for. Should be a telescope in the MAST database (JWST, HST, TESS)
        """
        self.telescope = telescope.lower()
        if self.telescope != "jwst" and self.telescope != "hst" and self.telescope != "tess":
            raise ValueError("Invalid telescope name given. Please use jwst, hst, or tess.")
        self.data = pd.DataFrame()
        self.fetch_telescope_data()


    def fetch_telescope_data(self) -> pd.DataFrame:
        """
        Fetches MAST data for all observations made by the telescope in the past year.
        
        Returns:
            pd.DataFrame: The fetched MAST data in pandas format. Also stored in class' data variable.
        """
        # min_time = Time("2024-01-01T00:00:00", format="isot")
        min_time = Time.now() - 1 *u.year
        max_time = Time.now()

        # Otherwise, connect to MAST through astroquery and load data.
        print(f"[ Loading {self.telescope.upper()} data from MAST... ]")
        
        try:
            obs = Observations.query_criteria(obs_collection=[self.telescope.upper()], t_min=[min_time.mjd, max_time.mjd])
            # Convert to pandas
            self.data = obs.to_pandas()
            print("[ Done ]")
            return self.data
        
        except Exception as e:
            # Currently get a lot of Memory Errors
            print("[Error getting data")
            print(e)
            return pd.DataFrame()
    
    
    def pie_instruments(self):
        """
        Prints a Plotly pie chart that displays the instrument usage in the past year's observations.

        Returns:
            Figure: Plotly figure
        """
        counts = self.data['instrument_name'].value_counts()
        df_result = pd.DataFrame(counts).reset_index() 
        fig = px.pie(df_result, names="instrument_name", values="count", title=f"Instrument Usage in {self.telescope.upper()} Observations (past year)")
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        return fig