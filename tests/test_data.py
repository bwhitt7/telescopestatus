import pytest
import pandas as pd
import telescopestatus as ts

@pytest.fixture(scope="session")
def data():
    return ts.TelescopeData("jwst")

# telescope name properly initialized
def test_data_telescope(data):
    assert data.telescope == "JWST"

def test_data_dataframe(data):
    assert not data.data.empty