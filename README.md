# Space Telescope Data

WIP Python package to get JWST MAST data and analyze operational data.

## To install
1. `pip install -i https://test.pypi.org/pypi/ --extra-index-url https://pypi.org/simple telescopestatus`

## To build locally
1. Clone repository.
2. Install [poetry](https://python-poetry.org/).
3. Run `poetry install` in root folder. This will install all needed packages, as well as telescopestatus locally.
    - To install with Jupyter Lab, run `poetry install --with test`

## How to use
```python
import telescopestatus as ts

# this will take a while.
# WARNING, may fail with low memory :(
jwst_data = ts.TelescopeData("jwst") 

# generates a plotly pie chart that displays how frequently instruments are used.
jwst_data.pie_instruments() 

```