import pytest
import pandas as pd
import telescopestatus as ts
from astropy.time import Time
import astropy.units as u


test_start_time = Time('2024-01-01')
test_end_time = Time('2025-01-01')

default_telescope = "JWST"
second_telescope = "HST"

@pytest.fixture(scope="session")
def data():
    return ts.TelescopeData(default_telescope, start_time=test_start_time, end_time=test_end_time)

@pytest.fixture
def data_no_query(monkeypatch):
    monkeypatch.setattr(ts.TelescopeData, "fetch_telescope_data", lambda: pd.DataFrame())
    return ts.TelescopeData(default_telescope, start_time=test_start_time, end_time=test_end_time)


# telescope name properly initialized
def test_data_init_telescope(data_no_query):
    assert data_no_query.telescope == default_telescope
    
def test_data_init_time(data_no_query):
    assert data_no_query.start_time == test_start_time
    
def test_data_init_time2(data_no_query):
    assert data_no_query.end_time == test_end_time

# when not giving a start time, see that it uses the default value
def test_data_init_time3(monkeypatch):
    monkeypatch.setattr(ts.TelescopeData, "fetch_telescope_data", lambda: pd.DataFrame())
    data = ts.TelescopeData("JWST")
    assert data.start_time == Time('1990-01-01')
    
# when not giving a end time, see that it uses the default value
# since time.now will change, check to see if they're at least the correct date.
# makes it so it probably wouldn't be a good idea to run this test suite around midnight!
def test_data_init_time4(monkeypatch):
    monkeypatch.setattr(ts.TelescopeData, "fetch_telescope_data", lambda: pd.DataFrame())
    data = ts.TelescopeData("JWST")
    assert data.end_time.to_value("iso", subfmt="date") == Time.now().to_value("iso", subfmt="date")

# properly gives us an error when an invalid telescope name is used
def test_data_init_error_telescope(monkeypatch):
    monkeypatch.setattr(ts.TelescopeData, "fetch_telescope_data", lambda: pd.DataFrame())
    
    with pytest.raises(ValueError):
        ts.TelescopeData("nonsense name")

# properly gives us an error when an earlier end time is given compared to the start time.
def test_data_init_error_time(monkeypatch):
    monkeypatch.setattr(ts.TelescopeData, "fetch_telescope_data", lambda: pd.DataFrame())
    
    with pytest.raises(ValueError):
        ts.TelescopeData(default_telescope, start_time=Time("2020-01-01"), end_time=Time("2019-01-01"))


# when changing the data, the telescope name should change properly
def test_data_setdata_telescope(data_no_query):
    data_no_query.set_data(telescope=second_telescope)
    assert data_no_query.telescope == second_telescope