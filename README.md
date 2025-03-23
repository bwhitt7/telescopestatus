# Space Telescope Data

Python package that fetches MAST data for a given telescope (JWST, HST, or TESS) and generates graphs.

## To install
1. `pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple telescopestatus`

## To build locally
1. Clone repository.
2. Install [poetry](https://python-poetry.org/).
3. Run `poetry install` in root folder. This will install all needed packages, as well as telescopestatus locally.
    - To install with Jupyter Lab and pytest, run `poetry install --with test`

## How to use
```python
import telescopestatus as ts

# this will take a while, and may fail with low memory. I highly recommend using start_time and end_time to limit the range.
# can use strings of dates, a datetime object, or use an astropy.time.Time object
jwst_data = ts.TelescopeData("jwst", start_time="2025-01-01", end_time="now")

# generates a plotly pie chart that displays how frequently instruments are used.
jwst_data.pie_instruments() 

```