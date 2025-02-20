from astroquery.mast import Observations
from astropy.time import Time
import pandas as pd
from pathlib import Path

min_time = Time("2019-01-01T00:00:00", format="isot")
max_time = Time.now()

telescopes = {
    "jwst": {
        "url": "data/jwst_obs.pkl",
        "query": "JWST"
    }
}

telescope_data = {
    "jwst": pd.DataFrame()
}

# Loop through telescopes, load data and save.
for telescope, data in telescopes.items():
    if Path(data["url"]).is_file(): # If data file already exists, just load it.
        #TODO: Update data somehow, do it through app?
        print("[Data file found, loading into dataframe...]")
        try:
            telescope_data[telescope] = pd.read_pickle(data["url"])
            print("[Done]")
        except:
            print("[Error reading file]")
    else:
        # Otherwise, connect to MAST through astroquery and load data.
        print(f"[Loading {telescope} data from MAST...]")
        try:
            obs = Observations.query_criteria(obs_collection=[data["query"]], t_min=[min_time.mjd, max_time.mjd])
            print("[Finished, saving file...]")
            # Convert to pandas and save to pickle file.
            # Using pickle since data types are saved, so data typing only needs to be done once.
            telescope_data[telescope] = obs.to_pandas()
            telescope_data[telescope].to_pickle(data["url"])
            print("[Done]")
        except Exception as e:
            # Currently get a lot of Memory Errors, probably because my laptop RAM isn't the best
            print("[Error getting data or saving file]")
            print(e)