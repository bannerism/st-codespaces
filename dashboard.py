import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os 
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title='techstars_', 
    page_icon=':male-technologist:',
    layout = 'wide'
)

st.title(":male-technologist: Investor RFM")

fl = st.file_uploader(":file_folder: Upload a file",type = (['csv']))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("/workspaces/st-codespaces/techstars_interview_data_rfm.csv", encoding = "ISO-8859-1")

## date picker
col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Last Updated Date'])
startDate = pd.to_datetime(df['Last Updated Date']).min()
endDate = pd.to_datetime(df['Last Updated Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input('Start Date',startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date",endDate))

df['value'] = 1
df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

## side bar filters
st.sidebar.header('Choose your filter: ')

def unique_non_null(s):
    return s.dropna().unique()

region = st.sidebar.multiselect("HQ Global Region", unique_non_null(df['HQ Global Region']))
if not region:
    df2 = df.copy()
else:
    df2 = df[df['HQ Global Region'].isin(region)]

country = st.sidebar.multiselect("HQ Country/ Territory",unique_non_null(df2['HQ Country/Territory']))
if not country:
    df3 = df2.copy()
else:
    df3 = df2[df2['HQ Country/Territory'].isin(country)]

state = st.sidebar.multiselect("HQ State/Province", unique_non_null(df2['HQ State/Province']) )
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['HQ State/Province'].isin(state)]

## filter the date based on region, country and state

if not region and not country and not state:
    filtered_df = df
elif not country and not state:
    filtered_df = df[df['HQ Global Region'].isin(region)]
elif not region and not state:
    filtered_df = df[df['HQ State/Province'].isin(state)]
elif region and state:
    filtered_df = df3[df3['HQ Global Region'].isin(region) & df3['HQ State/Province'].isin(state)]
elif country and state:
    filtered_df = df3[df3['HQ Country/Territory'].isin(country) & df3['HQ State/Province'].isin(state)]
elif region and country:
    filtered_df = df3[df3['HQ Global Region'].isin(region) & df3['HQ Country/Territory'].isin(country)]
elif state:
    filtered_df = df3[df3['HQ State/Province'].isin(state)]
else:
    filtered_df = df3[df3['HQ Global Region'].isin(region)\
                    & df3['HQ Country/Territory'].isin(country)\
                    & df3['HQ State/Province'].isin(state)]

## category df
category_df = filtered_df.groupby(by = ['Segment'], as_index = False)['Investors'].count()
category_df = category_df.sort_values('Investors')

with col1:
    st.subheader("Count of Investors")
    fig = px.bar(category_df, 
                 x = 'Segment',
                 y = 'Investors',
                 text = category_df['Investors'],
    template = 'seaborn')
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Primary Investor")
    filtered_df = filtered_df.sort_values('value')
    fig = px.pie(filtered_df, values = "value", names = "Segment", hole = 0.5)
    fig.update_traces(text = filtered_df["Primary Investor Type"],
                      textposition = "outside",
                      showlegend = False)

    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Segment ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv,
                            file_name = 'Segment_ViewData.csv',
                              mime = "text/csv",
                                help = "Download CSV")
        
# with cl2:
#     with st.expander("Primary Investors"):
        
                           