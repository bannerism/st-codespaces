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

def unique_non_null(s):
    return s.dropna().unique()

def get_unique_values(df, field):
    d = dict()
    list_of_vals = []
    for i,r in df.iterrows():
        pi = r[field]
        try:
            vals = pi.split(', ')
        except:
            vals = [pi]
        list_of_vals.append(vals)
    
    all_vals = list({x for l in list_of_vals for x in l})
    d[field] = all_vals
    
    return d[field]

def regexify(searchfor):
    OR = "|"
    query = [i for i in searchfor]
    return OR.join(query)


st.title(":male-technologist: Investor RFM")

uploaded_file = st.file_uploader(":file_folder: Upload a file",type = (['csv']))
if uploaded_file is not None:
    filename = uploaded_file.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")
else:
    df = pd.read_csv("/workspaces/st-codespaces/techstars_interview_data_rfm.csv", encoding = "ISO-8859-1")

# Create a preferred industry multiselect widget
with st.form("Filter Dataframe"):
    selected_names = st.multiselect(
        "Find investors whose preferred industry is:",
        get_unique_values(df,'Preferred Industry'),
        # default=[" "],
    )
    submit_button = st.form_submit_button('Search')


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

if submit_button:
    # Filter the dataframe
    s1 = df['Preferred Industry']
    df = df[s1.str.contains(regexify(selected_names), na = False)].copy()
    df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()
else:
    df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()


## side bar filters
st.sidebar.header('Choose your filter: ')

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
    st.subheader("# of Investors")
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

## Data Download
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Segment ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv,
                            file_name = 'Segment_ViewData.csv',
                              mime = "text/csv",
                                help = "Click to Download CSV")
        
with cl2:
    with st.expander("Investor ViewData"):
        data = filtered_df.groupby(by = ['Segment','Primary Investor Type'], as_index = False)['Investors'].count()
        st.write(data.style.background_gradient(cmap='Oranges'))
        csv = data.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv,
                            file_name = 'Investor_ViewData.csv',
                              mime = "text/csv",
                                help = "Click to Download CSV")


st.subheader("RFM Analysis")
with st.expander("Learn More about RFM"):
    st.markdown("""
                Recency = `Last Investment Date` \n
                Frequency = `Total Investments` \n
                Monetary = `Last Investment Size` \n

                RFM stands for Recency, Frequency, and Monetary Value. It is a customer segmentation technique that uses these three metrics to measure and analyze investor behavior.

                - 111 is the lowest score while 555 is the highest score.
                - Scores are determined by splitting the values of each metric into five equal groups.

                """)
fig = px.treemap(filtered_df, path=[px.Constant("All"),'Segment', 'Investors'], values='Last Investment Size',
                  color='Primary Investor Type', hover_data=['Recency Score','Frequency Score','Monetary Score','Last Investment Type','Preferred Industry','Preferred Verticals'],
                  color_continuous_scale='RdBu',
                #   color_continuous_midpoint=np.average(filtered_df['Recency Score'], weights=filtered_df['Monetary'])
                )
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig,use_container_width=True)

rfm = filtered_df.filter(['RFM Score','Investors','Primary Investor Type','Last Investment Delta','Total Investments','Last Investment Size','Preferred Industry'])
with st.expander("Recency, Frequency and Monetary Data"):

        st.write(" ")
        st.write(rfm)
        csv = rfm.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv,
                            file_name = 'RFM_Campaign.csv',
                              mime = "text/csv",
                                help = "Click to Download CSV")