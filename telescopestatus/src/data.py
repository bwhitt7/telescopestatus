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
            telescope (str): The telescope to fetch data for. Should be a telescope in the MAST database (jwst, hst, tess)
        """
        self.telescope = telescope.lower()
        if self.telescope != "jwst" and self.telescope != "hst" and self.telescope != "tess":
            raise ValueError("Invalid telescope name given. Please use jwst, hst, or tess.")
        self.data = pd.DataFrame()
        
        self.min_time = Time.now() - 1 *u.year
        self.max_time = Time.now()
        
        self.fetch_telescope_data()


    def fetch_telescope_data(self) -> pd.DataFrame:
        """
        Fetches MAST data for all observations made by the telescope in the past year.
        
        Returns:
            pd.DataFrame: The fetched MAST data in pandas format. Also stored in class' data variable.
        """

        # Otherwise, connect to MAST through astroquery and load data.
        print(f"[ Loading {self.telescope.upper()} data from MAST... ]")
        
        try:
            obs = Observations.query_criteria(obs_collection=[self.telescope.upper()], t_min=[self.min_time.mjd, self.max_time.mjd])
            # Convert to pandas
            self.data = obs.to_pandas()
            print("[ Done ]")
            return self.data
        
        except Exception as e:
            # Currently get a lot of Memory Errors
            print("[Error getting data")
            print(e)
            return pd.DataFrame()
    
    
    def _pie_chart(self, column:str, column_name:str, title:str):
        counts = self.data[column].value_counts()
        df_result = pd.DataFrame(counts).reset_index() 
        min_time = self.min_time.to_value("iso", subfmt="date")
        max_time = self.max_time.to_value("iso", subfmt="date")
        
        fig = px.pie(
            df_result,
            names=column,
            values="count",
            labels={column: column_name, "count": "# of Observations"},
            title=f"{title} (between {min_time} and {max_time})"
        )
        fig.update_traces(textposition='inside')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        fig.update_layout(margin=dict(t=50, b=20, l=0, r=0))
        return fig
    
    
    def instruments_pie(self):
        """
        Prints a Plotly pie chart that displays the instrument usage in stored observations.

        Returns:
            Figure: Plotly figure.
        """
        return self._pie_chart("instrument_name", "Instrument", f"Instrument Usage in {self.telescope.upper()} Observations")


    def data_type_pie(self):
        """
        Prints a Plotly pie chart that displays the type of observations.

        Returns:
            Figure: Plotly figure.
        """
        return self._pie_chart("dataproduct_type", "Data Product Type", f"Data Product Type of {self.telescope.upper()} Observations")


    def exposure_length_hist(self, log_scale=False):
        """Prints a Plotly histogram that displays the exposure length of stored observations.

        Args:
            log_scale (bool, optional): Display graph in log scale. Defaults to False.

        Returns:
            Figure: Plotly figure.
        """
        min_time = self.min_time.to_value("iso", subfmt="date")
        max_time = self.max_time.to_value("iso", subfmt="date")
        
        fig = px.histogram(
            self.data,
            x="t_exptime",
            labels={"t_exptime": "Exposure Length"},
            log_y=log_scale,
            title=f"Exposure Length of Observations (between {min_time} and {max_time})"
        )
        fig.update_layout(yaxis_title_text = '# of Observations')
        return fig

    def compare_scatter(self, x:str, y:str):
        """Generate your own scatter by feeding in column names of MAST data. Must be numeric columns.
        Visit https://mast.stsci.edu/api/v0/_c_a_o_mfields.html to see available columns and their datatypes.

        Args:
            x (str): MAST column name.
            y (str): MAST column name.

        Returns:
            Figure: Plotly figure.
        """
        try:
            fig = px.scatter(self.data, x=x, y=y)
            return fig
        except Exception as e:
            print("Error, likely gave invalid column name(s), or columns that weren't numeric.")
            print(e)