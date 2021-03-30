import streamlit as st
from streamlit_metrics import metric, metric_row
import pandas as pd
from google.cloud import bigquery
from google.cloud import bigquery_storage
import google.auth
import os

st.title('Vancouver Listing Prices')
st.write('A descriptive analysis based on data retrieved on November 12, 2020 from REW')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/Users/S Lo/Workspace/VancouverHousingPrices/Housing Project-db68639e1bff.json"

'''
## Step 1: Import Data
'''

# Documentation for importing data from bigquery: https://cloud.google.com/bigquery/docs/bigquery-storage-python-pandas
# Explicitly create a credentials object. This allows you to use the same
# credentials for both the BigQuery and BigQuery Storage clients, avoiding
# unnecessary API calls to fetch duplicate authentication tokens.
credentials, your_project_id = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# Make clients.
bqclient = bigquery.Client(credentials=credentials, project=your_project_id,)
bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)

# Construct a BigQuery client object.
bqclient = bigquery.Client()

query_string = """
    SELECT *
    FROM `housing-project-300900.ds_main.f_real_estate_listings_view`
"""
query_job = bqclient.query(query_string)  # Make an API request.

df_list_price = (
    bqclient.query(query_string)
    .result()
    .to_dataframe(bqstorage_client=bqstorageclient)
)

# Change data types
df_list_price['scrape_dt'] = pd.to_datetime(df_list_price['scrape_dt'])
df_list_price['bed'] = pd.to_numeric(df_list_price['bed'])
df_list_price['bath'] = pd.to_numeric(df_list_price['bath'])
df_list_price['price'] = pd.to_numeric(df_list_price['price'])
df_list_price['strata_fee'] = pd.to_numeric(df_list_price['strata_fee'])

# Inspect the raw data
st.subheader('Listing prices data')
st.write(df_list_price)

'''
## Step 2: Create KPI cards
'''
# Calculate KPIs
listings_count = len(pd.unique(df_list_price['listing_id']))
# TODO: calculate average days in market
avg_market_days = 'placeholder'


# Create visuals
st.subheader('Vancouver Housing Inventory')
metric_row(
    {
        "Number of listings": listings_count,
        "Average days on market": avg_market_days
    }
)

'''
## Step 3: Create graphs
'''
# Create dataframe with count of unique listings by date
df_inventory = df_list_price[['scrape_dt', 'listing_id']].groupby(['scrape_dt']).agg(['nunique']).reset_index()
df_inventory.columns = ['scrape_dt', 'listings_count']

st.subheader('Number of listings over time')
st.line_chart(df_inventory.set_index('scrape_dt'))

'''
## Step 4: Create tables
'''
# Create dataframe with count of listings by property type and number of bedrooms
df_prop_bed = df_list_price[['listing_id', 'property_type', 'bed']].groupby(['property_type', 'bed']).agg(['nunique']).reset_index()
df_prop_bed.columns = ['property_type', 'bed', 'listings_count']
df_prop_bed['bed'] = df_prop_bed['bed'].astype(str) + ' Bedroom(s)'

# Create separate dataframes for each property type
df_apt_bed = df_prop_bed[df_prop_bed['property_type'] == 'Apt/Condo']
df_duplex_bed = df_prop_bed[df_prop_bed['property_type'] == 'Duplex']
df_house_bed = df_prop_bed[df_prop_bed['property_type'] == 'House']
df_rec_bed = df_prop_bed[df_prop_bed['property_type'] == 'Recreational']
df_town_bed = df_prop_bed[df_prop_bed['property_type'] == 'Townhouse']

# TODO: create separate tabs for the 5 tables, potentially using Bokeh (https://discuss.streamlit.io/t/bokeh-can-provide-layouts-tabs-advanced-tables-and-js-callbacks-in-streamlit/1108)
st.write(df_apt_bed)
st.write(df_duplex_bed)
st.write(df_house_bed)
st.write(df_rec_bed)
st.write(df_town_bed)