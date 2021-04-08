# This app is for educational purpose only. Insights gained are not financial advice. Use at your own risk!
import streamlit as st
from streamlit_metrics import metric, metric_row
from PIL import Image
import pandas as pd
import datetime as dt
#import base64 as b
#import matplotlib.pyplot as plt
#from bs4 import BeautifulSoup
#import requests
#import json
#------------------------------------#
# 1) APP TITLE, DESCRIPTION & LAYOUT
## Page expands to full width
## Layout... Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
#------------------------------------#
st.set_page_config(layout="wide")

# Title
#------------------------------------#

image = Image.open('real-estate.png')

st.image(image, width = 100)

st.title('Real Estate Listing Prices')
st.markdown("""
This app helps visualize real estate listings data. Use the Sample dataset, or upload your own!

""")


# About
#------------------------------------#

expander_bar = st.beta_expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Sample data source:** [CoinMarketCap](http://rew.ca).
* **Credit:** Layout adapted from various example applications *[Build 12 Data Science Apps with Python and Streamlit - Full Course](https://www.youtube.com/watch?v=JwSS70SZdyM&ab_channel=freeCodeCamp.org)*  by [Chanin Nantasenamat](https://github.com/dataprofessor).
""")


# Layout
#------------------------------------#

col1 = st.sidebar
col2, col3 = st.beta_columns((2,1)) # col1 is 2x greater than col2


#-----------------------------------#
# 2) SIDEBAR, DATA MUTATIONS
## User upload data feature
## Relevant & simple filtering options
#-----------------------------------#

## Sidebar title
st.sidebar.header('User Input Features')

## Expandable sidebar 2: Upload data set (Limit 200MB per file, CSV)
expander_bar2 = st.sidebar.beta_expander("Upload Your Own Data!")
expander_bar2.markdown("""
* Each row must be a unique listing
* Required columns: `bath, bed, city, days_on_site, price, property_age, property_type, scrape_date, sqft`
"""
                       )
uploaded_file = expander_bar2.file_uploader("Upload your file below", type=["csv"])

## Expandable sidebar 1: Example CSV input file download
expander_bar1 = st.sidebar.beta_expander("See Example Data")
expander_bar1.markdown("""
* Right click [Example CSV input file](https://raw.githubusercontent.com/dmf95/realtor_streamlit_app/master/dummy_df.csv)  
* Hit `Save link as..`
* Change file from `.txt` to `.csv`
""")

## Conditional dataset creation
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # reset buffer (see documentation here: https://discuss.streamlit.io/t/issue-in-rerunning-file-uploader/6333)
    uploaded_file.seek(0)
else:
    df = pd.read_csv('dummy_df.csv')

## Change data types
df['scrape_date'] = pd.to_datetime(df['scrape_date'])
df['bed'] = pd.to_numeric(df['bed'])
df['bath'] = pd.to_numeric(df['bath'])
df['price'] = pd.to_numeric(df['price'])
df['strata_fee'] = pd.to_numeric(df['strata_fee'])



## Scenario 1 (user uploads data): read in csv if it exists
if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)

## Scenario 2: (user has not uploaded data yet): read in default values from input selection in the app
else:
    def user_input_features():

        ### date stuff
        today = dt.datetime.now()
        year = today.year
        d = df.scrape_date
        d1 = pd.DatetimeIndex(d).month.astype(str) + "/" + pd.DatetimeIndex(d).year.astype(str)
        d2= sorted(d1.unique())
        scrape_dt = st.sidebar.selectbox('Date Retrieved', d2)
        ###
        sorted_city = sorted(df.city.unique())
        city = st.sidebar.selectbox('City', sorted_city)

        #TODO figure out to to add neighbourhood such that it filters based on city selection above
        #TODO see if there is a way to search through description and to find all listings that match

        sorted_beds = sorted(df.bed.unique())
        beds = st.sidebar.multiselect('Bedrooms', sorted_beds, sorted_beds)
        sorted_baths = sorted(df.bath.unique())
        baths = st.sidebar.multiselect('Bathrooms', sorted_baths, sorted_baths)
        sorted_property_type = sorted(df.property_type.unique())
        property_type = st.sidebar.multiselect('Property Type', sorted_property_type, sorted_property_type)
        price = st.sidebar.slider('Listing Price', min_value=200000, max_value=5000000, value=(200000,5000000),step=100000)
        sqft = st.sidebar.slider('Square Feet', min_value=300, max_value=10000, value=(300,10000),step=50)
        property_age = st.sidebar.slider('Property Age', min_value=1900, max_value=year, value=(1900,year),step=1)
        days = max(df.days_on_site)
        days_on_site = st.sidebar.slider('Days on Site', min_value=0, max_value=days, value=(0,days),step=1)

    input_df = user_input_features()

# TODO: MAIN PANEL SHIT @shannons part :)

#-----------------------------------#
# 3) MAINPANEL, VISUALS
#-----------------------------------#

## Inspect the raw data
st.subheader('Listing prices data')
st.write(df)

'''
## Step 1: Create KPI cards
'''
# Calculate KPIs
listings_count = len(pd.unique(df['listing_id']))
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
df_inventory = df[['scrape_date', 'listing_id']].groupby(['scrape_date']).agg(['nunique']).reset_index()
df_inventory.columns = ['scrape_date', 'listings_count']

st.subheader('Number of listings over time')
st.line_chart(df_inventory.set_index('scrape_date'))

'''
## Step 4: Create tables
'''
# Create dataframe with count of listings by property type and number of bedrooms
df_prop_bed = df[['listing_id', 'property_type', 'bed']].groupby(['property_type', 'bed']).agg(['nunique']).reset_index()
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