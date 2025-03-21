from astroquery.mast import Observations
from astropy.time import Time
import astropy.units as u
import pandas as pd
import plotly.express as px
from getpass import getpass
    
class TelescopeData:
    """
    Stores, generates, and visualizes MAST data for a given telescope (JWST, HST, or TESS).
    """
    
    def __init__(self, telescope: str, token: str = None, max_data: int = None, start_time: Time = None, end_time: Time = None, data_file_path: str = None, data_file_type: str = None):
        """
        If no TelescopeData data file is given, it will automatically call fetch_telescope_data() with given parameters.
        telescope, max_data, start_time, and end_time become useless when data is given manually, but telescope, start_time, and end_time should be filled out for usage in the graphs.
        
        Args:
            telescope (str): The telescope to fetch data for. Should be a telescope in the MAST database (jwst, hst, tess)
            token (str, optional): 
            max_data (int, optional): The maximum number of data entries you want to query for. Defaults to no limit.
            start_time (astropy.time.Time, optional): The start time of query. Defaults to one year ago.
            end_time (astropy.time.Time, optional): The end time of query. Defaults to today.
            data_file_path (str, optional): The location of a saved TelescopeData data file.
            data_file_type (str, optional): The file type of the TelescopeData data file. Should be a file type parsable by pandas (csv, json, pickles, etc)
        """
        self.telescope = None
        self.start_time = None
        self.end_time = None
        self.data = None
        self.set_data(telescope, max_data, start_time, end_time, reset_dates=True, data_file_path=data_file_path, data_file_type=data_file_type)
    

    def set_data(self, telescope: str = None, token: str = None, max_data: int = None, start_time: Time = None, end_time: Time = None, reset_dates = False, clear_dates = False, data_file_path: str = None, data_file_type: str = None):
        """Setting the data for the class. This is called during initialization, but it can be called again to reset the data and requery if needed.

        Args:
            telescope (str, optional): The telescope to fetch data for. Should be a telescope in the MAST database (jwst, hst, tess). Defaults to None.
            token (str, optional): 
            max_data (int, optional): The maximum number of data entries you want to query for. Defaults to no limit.. Defaults to None.
            start_time (Time, optional): The start time of query. Defaults to None.
            end_time (Time, optional): The end time of query.. Defaults to None.
            reset_dates (bool, optional): Reset the start and end times to default values (one year ago - today). Defaults to False.
            clear_dates (bool, optional): If start and end dates are not needed (for example, if data was given manually instead of through a fetch), set this to True. Defaults to False.
            data_file_path (str, optional): The location of a saved TelescopeData data file.
            data_file_type (str, optional): The file type of the TelescopeData data file. Should be a file type parsable by pandas (csv, json, pickles, etc)

        Raises:
            ValueError: Invalid telescope name given.
        """
        if telescope:
            self.telescope = telescope.upper()
            if not self.telescope in [t.upper() for t in Observations.list_missions()]:
                raise ValueError(f"Invalid telescope/mission name given. Please use {", ".join(Observations.list_missions())}.")
        
        if start_time: # if start time given
            self.start_time = start_time
        elif reset_dates: # if we don't already have some start time and we're not resetting the times
            self.start_time = Time.now() - 1 *u.year
            
        if end_time: # if end time given
            self.end_time = start_time
        elif reset_dates: # if we don't already have some end time and we're not resetting the times
            self.end_time = Time.now()
        
        if clear_dates:
            self.start_time = None
            self.end_time = None
        
        self.data = pd.DataFrame()
        
        # TelescopeData file given
        if data_file_path:
            if not data_file_type:
                raise ValueError("data_file_type should be given in addition to data_file_path.")
            try:
                self.read_data(file_path=data_file_path, file_type=data_file_type)
            except Exception as e:
                print(e)
        # Otherwise, fetch data!
        else:
            try:
                self.fetch_telescope_data(max_data)
            except Exception as e:
                print(e)


    def fetch_telescope_data(self, token: str = None, max_data: int = None) -> pd.DataFrame:
        """
        Fetches MAST data for all observations made by the telescope in the past year.
        Uses the data parameters stored in the class. To change those values, call set_data() instead.
        
        Args:
            token (str, optional): 
            max_data (int, optional): The maximum number of data entries you want to query for. Defaults to no limit.
        
        Returns:
            pd.DataFrame: The fetched MAST data in pandas format. Also stored in class' data variable.
        """
        
        # if token was given, try logging in!
        if token:
            try:
                Observations.login(token)
            except Exception as e:
                print("[ Login error. ]")
                raise e
        
        # Connect to MAST through astroquery and load data.
        print(f"[ Loading {self.telescope} data from MAST... ]")
        try:
            obs = Observations.query_criteria(
                obs_collection=[self.telescope],
                t_min=[self.start_time.mjd, self.end_time.mjd],
                page = 1 if max_data else None,
                pagesize = max_data if max_data else None
            )
            
            # Convert to pandas
            self.data = obs.to_pandas()
            print("[ Done loading data! ]")
            return self.data
        
        except Exception as e:
            # Currently get a lot of Memory Errors
            print("[ Error getting data ]")
            raise e
    
    
    def export_data(self, file_name: str = "telescope_data.csv", file_type: str = "csv"):
        if file_type == "csv":
            self.data.to_csv(file_name)
        elif file_type == "pickle":
            self.data.to_pickle(file_name)
    
    def read_data(self, file_path, file_type):
        if file_type == "csv":
            data = pd.read_csv(file_path)
        elif file_type == "pickle":
            data = pd.read_pickle(file_path)
        self.data = data
    
    
    def _pie_chart(self, column:str, column_name:str, title:str):
        counts = self.data[column].value_counts()
        df_result = pd.DataFrame(counts).reset_index() 
        start_time = self.start_time.to_value("iso", subfmt="date")
        end_time = self.end_time.to_value("iso", subfmt="date")
        
        fig = px.pie(
            df_result,
            names=column,
            values="count",
            labels={column: column_name, "count": "# of Observations"},
            title=f"{title} (between {start_time} and {end_time})"
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
        start_time = self.start_time.to_value("iso", subfmt="date")
        end_time = self.end_time.to_value("iso", subfmt="date")
        
        fig = px.histogram(
            self.data,
            x="t_exptime",
            labels={"t_exptime": "Exposure Length"},
            log_y=log_scale,
            title=f"Exposure Length of Observations (between {start_time} and {end_time})"
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
