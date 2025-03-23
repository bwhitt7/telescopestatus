from astroquery.mast import Observations
from astropy.time import Time
import astropy.units as u
import pandas as pd
import plotly.express as px
from datetime import datetime

default_min_year = Time('1990-01-01')

class TelescopeData:
    """
    Stores, generates, and visualizes MAST data for a given telescope (JWST, HST, or TESS).
    """
    
    def __init__(self, telescope: str, start_time: Time = default_min_year, end_time: Time = Time.now(), max_data: int = None, token: str = None, data_file_path: str = None, data_file_type: str = None):
        """
        If no TelescopeData data file is given, it will automatically call fetch_telescope_data() with given parameters.
        telescope, max_data, start_time, and end_time become useless when data is given manually, but telescope, start_time, and end_time should be filled out for usage in the graphs.
        
        Args:
            telescope (str): The telescope to fetch data for. Should be a telescope in the MAST database (jwst, hst, tess)
            start_time (astropy.time.Time, optional): The start time of query. Defaults to 1990-01-01.
            end_time (astropy.time.Time, optional): The end time of query. Defaults to the current time.
            max_data (int, optional): The maximum number of data entries you want to query for. Defaults to no limit.
            token (str, optional): MAST token. Defaults to None.
            data_file_path (str, optional): The location of a saved TelescopeData data file.
            data_file_type (str, optional): The file type of the TelescopeData data file. Should be a file type parsable by pandas (csv, json, pickles, etc)
        """
        self.telescope = None
        self.start_time = default_min_year
        self.end_time = Time.now()
        self.data = None
        self.set_data(telescope, start_time, end_time, max_data, token, data_file_path=data_file_path, data_file_type=data_file_type)
    

    def set_data(self, telescope: str = None, start_time: Time = None, end_time: Time = None, max_data: int = None, token: str = None, data_file_path: str = None, data_file_type: str = None):
        """Setting the data for the class. This is called during initialization, but it can be called again to reset the data and requery if needed.

        Args:
            telescope (str, optional): The telescope to fetch data for. Should be a telescope in the MAST database (jwst, hst, tess). Defaults to None.
            start_time (Time, optional): The start time of query. Defaults to None.
            end_time (Time, optional): The end time of query.. Defaults to None.
            max_data (int, optional): The maximum number of data entries you want to query for. Defaults to no limit.. Defaults to None.
            token (str, optional): MAST token. Defaults to None.
            data_file_path (str, optional): The location of a saved TelescopeData data file.
            data_file_type (str, optional): The file type of the TelescopeData data file. Should be a file type parsable by pandas (csv, json, pickles, etc)

        Raises:
            ValueError: Invalid telescope name given.
        """
        # if an invalid telescope name was given, raise an error
        # must be in the astroquery observations list
        if telescope:
            self.telescope = telescope.upper()
            if not self.telescope in [t.upper() for t in Observations.list_missions()]:
                raise ValueError(f"Invalid telescope/mission name given. Please use {", ".join(Observations.list_missions())}.")
        
        
        
        start_time = self.validate_and_convert_time_param(start_time) if start_time else self.start_time
        end_time = self.validate_and_convert_time_param(end_time) if end_time else self.end_time
        
        # if the start time is later than the end time, raise an error
        if start_time and end_time:
            if start_time > end_time:
                raise ValueError(f"start_time should be less than end_time.")
        
        self.start_time = start_time
        self.end_time = end_time
        
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
                self.fetch_telescope_data(max_data, token)
            except Exception as e:
                print(e)


    def validate_and_convert_time_param(self, time) -> Time:
        if isinstance(time,str) or isinstance(time,datetime):
            if time == "now":
                return Time.now()
            try:
                return Time(str)
            except Exception:
                raise ValueError(f"{time} -> Improper format for time.")
        elif isinstance(time,Time):
            return time
        else:
            raise ValueError(f"{time} -> Improper format for time.")


    def fetch_telescope_data(self, max_data: int = None, token: str = None) -> pd.DataFrame:
        """
        Fetches MAST data for all observations made by the telescope in the past year.
        Uses the data parameters stored in the class. To change those values, call set_data() instead.
        
        Args:
            max_data (int, optional): The maximum number of data entries you want to query for. Defaults to None, for no limit.
            token (str, optional): MAST token. Defaults to None.
        
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
            # May get memory errors with low memory
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
