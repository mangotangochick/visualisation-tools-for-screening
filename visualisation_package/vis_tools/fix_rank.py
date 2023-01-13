'''
Tools for advanced visualisations of screening data.

This module helps generate a variety of different visualisations for screening
uptake, and can be customised to display data in formats such as choropleth maps,
interactive bar charts making it easy to compare different regions over time.

Region_Analysis:
    Creates an interactive choropleth map of country separated into regions to visualise screening uptake.

LondonMap:
    Plots and saves a London map displaying the screening uptake by boroughs.

animated_bars(): part of Rank_Graph class
    Creates an animated, interactive bar chart of the ranking of a chosen list
    of areas over time.
'''
import os
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as pyo
### New bit
import plotly.io as pio
pio.renderers.default = "vscode"
### End new bit
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import data
package_dir = os.path.dirname(data.__file__)
import requests
from shapely.geometry import Point, Polygon
import ast
from fiona.crs import from_epsg
import shapefile as shp # pyshp
import pyproj

class Rank_Based:
    def __init__(self, df):
        self.df = df
    
    def list_areas(self, area_type="Region"):
        '''
        Prints available areas based on the area type chosen. 
        Parameters:
        ----------
        area_type: str
            either a "Region", "UA, or "LA", default = "Region"
        '''
        # Slicing the dataframe:
        self.df = self.df[self.df["Area Type"]==area_type]
        # Creating a list of area names
        ar_lst = [*set(self.df["Area Name"])]
        print(ar_lst)


    def clean_rank(self, list_reg=['East of England region', 'London region',
                   'South East region'], area_type="Region"):
        '''
        Returns a df_year dataframe containing the rank of each region in the
        list_reg relative to each other for each year.

        Parameters:
        list_reg: list
            list of regions (default: ['East of England region',
            'London region', 'South East region'])
        area_type: str
            the type of area to compare (default: "Region")

        Returns:
        df_year: a dataframe containing the rank of each region in the list_reg
        relative to each other for each year 
        '''
        # Selects areas we want to compare
        self.df = self.df[self.df["Area Type"]==area_type]
        # Selects which regions to compare
        list_select=list_reg
        df_select = self.df[self.df['Area Name'].isin(list_select)]
        # Changing the data type into string:
        df_select = df_select.astype({'Area Name': str})
        df_select.reset_index(inplace=True)
        df_year = df_select
        if "index" in df_year.columns:
            df_year = df_year.drop(columns=["index"])
    
        # Splitting data into dfs by the year and ranking based on Value.
        keep = []
        years = list(set(df_year['Time period']))
        years
        for i in years:
            df = df_year.loc[df_year['Time period']==i]
            order = df['Value'].rank(ascending=0)
            df['rank'] = [int(i) for i in order]
            keep.append(df)
        # Combining all the dfs and sorting based on name and year.
        df_year = pd.concat(keep)
        df_year.sort_values(['Area Name', 'Time period'], ascending=True,
                            inplace=True, ignore_index=True)
        return df_year
    

    def color_pal(self, df_clean, sns_palette='Spectral'):
        '''
        Takes a clean dataframe and adds colours based on areas included.
        Parameters: 
        ----------
        df_clean: pandas DataFrame
            dafaframe prepared with clean_rank function
        sns_palette: str
            name of the palette to be used, found on:
            https://seaborn.pydata.org/tutorial/color_palettes.html
        '''
        # color palette
        area_name = list(set(df_clean['Area Name']))
        pal = list(sns.color_palette(palette=sns_palette,
                                    n_colors=len(area_name)).as_hex())
        dict_color = dict(zip(area_name, pal))
        return dict_color
    

   
    def animated_bars(self, area_type="Region", list_reg=[
                        'East of England region', 'London region', 
                        'South East region'], sns_palette="Spectral",
                        width=1000, height=600, showlegend=False,
                        rank_text_size=16):
        '''
        Utilises other functions in class Rank_Based_Graph to clean dataframe,
        select colour palette and plot an animated bar chart, of chosen areas' 
        rank change over time. 
        Parameters:
        ----------
        area_type: str
            can be "Region", "UA", or "LA", default "Region"
        list_reg: lst
            list of region names to be compared over time
            list_areas() function can be used to see options
        sns_palette: str
            name of seaborn palette to be used
            https://seaborn.pydata.org/tutorial/color_palettes.html
        width: int
            width of the graph in pixels, default 1000
        height: int
            height of the graph in pixels, default 1000
        showlegend: bool
            if True, adds a legend of the areas, default False
        rank_text_size: int

        '''
        df_cleaned = self.clean_rank(list_reg=list_reg, area_type=area_type)
        dict_color = self.color_pal(df_cleaned, sns_palette=sns_palette)
        fig = px.bar(df_cleaned, x='Area Name', y='Value',
                    color='Area Name', text='rank',
                    color_discrete_map= dict_color,
                    animation_frame='Time period',
                    animation_group='Area Name', range_y=[50, 90],
                    labels={ 'Value': 'Proportion Screened, %'})
        fig.update_layout(width=width, height=height, showlegend=showlegend,
                        xaxis = dict(tickmode = 'linear', dtick = 1))
        fig.update_traces(textfont_size=rank_text_size, textangle=0)
        #pyo.plot(fig, filename='plots/animated_rank_from_list.html', auto_open=False)
        pyo.iplot(fig)
            

    def plot_full_animated_graph(self, area_type = 'Region', sns_palette="Spectral",
                        width=1000, height=600, showlegend=False,
                        rank_text_size=16):
        region_df = self.df[self.df['Area Type'] == area_type]
        fig = px.bar(region_df, x='Area Name', y='Value', animation_frame='Time period', animation_group='Area Name',
                     range_y=[region_df['Value'].min() - 10, region_df['Value'].max()],
                     labels={ 'Value': 'Proportion Screened, %'},
                     hover_name='Area Name',
                     color='Area Name', 
                     title='Region Ranking Change')
        fig.update_layout(width=width, height=height, showlegend=showlegend,
                xaxis = dict(tickmode = 'linear', dtick = 1))
        fig.update_traces(textfont_size=rank_text_size, textangle=0)
        pyo.plot(fig, filename='plots/animated_rank_full.html', auto_open=False)
        pyo.iplot(fig)

    def animated_scatter(self, area_type="Region", list_reg=[
                            'East of England region', 'London region', 
                            'South East region'], sns_palette="Spectral",
                            width=1000, height=600, showlegend=False,
                            rank_text_size=16):
        df_cleaned = self.clean_rank(list_reg=list_reg, area_type=area_type)
        area_color = self.color_pal(df_cleaned, sns_palette=sns_palette)
        years = list(set(self.df['Time period']))
        years.sort()

        df_cleaned['Position'] = [years.index(i) for i in df_cleaned['Time period']]
        df_cleaned['Val_str'] = [str(round(i,2)) for i in df_cleaned['Value']]
        df_cleaned['Val_text'] = [str(round(i,2))+' ppm' for i in df_cleaned['Value']]
        fig = px.scatter(df_cleaned, x='Position', y='rank',
                        size= 'Value',
                        color='Area Name', text='Val_text',
                        color_discrete_map= area_color,
                        animation_frame='Time period',
                        animation_group='Area Name',
                        range_x=[-2,len(years)],
                        range_y=[0.5,6.5]
                        )
        fig.update_xaxes(title='', visible=False)
        fig.update_yaxes(autorange='reversed', title='Rank',
                        visible=True, showticklabels=True)
        fig.update_layout(xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True), width=800, height=600)
        fig.update_traces(textposition='middle left')
        pyo.iplot(fig)


