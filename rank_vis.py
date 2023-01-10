# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

cerv_data = pd.read_csv('data/cervical_cancer_data.csv')

def basic_data_cleaning(df, age=bool, sex=bool):

    """
    Function for basic data cleaning of an NHS screening uptake dataset.
    
    This function returns two cleaned datasets, one with no deprivation deciles and one with deprivation deciles

    Parameters
    ----------
    df: pandas DataFrame
        DataFrame containing the data to be explored.
    age: bool
        If True, then executes code that removes age information
    sex: bool
        If True, then executes code that removes sex information
    
    Returns
    -------
    df: pandas DataFrame
        cleaned dataframe    
    """

    # Fill NaNs
    df['Category Type'].fillna('NA', inplace=True)
    keep_col = ['Area Code', 'Area Name', 'Area Type', 'Time period', 'Value']
    if age==True:
        keep_col.append('Age')

    if sex==True:
        keep_col.append('Sex')

    # Remove Unnecessary Columns
    df = df[keep_col]
    return df


class Rank_Based_Graph:
    def __init__(self, df):
        self.df = df
    

    def list_areas(self, area_type="Region"):
        '''
        Prints available areas based on the area type chosen. 
        Parameters:
        ----------
        area_type: str
            either a "Reagion" or "LA"
        '''
        # Slicing the dataframe:
        self.df = self.df[self.df["Area Type"]==area_type]
        # Creating a list of area names
        ar_lst = [*set(self.df["Area Name"])]
        print(ar_lst)


    def clean_rank(self, list_reg=['East of England region', 'London region', 'South East region'], area_type="Region"):
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
                     'South East region'], sns_palette="Spectral"):
        '''
        Utilises other functions in class Rank_Based_Graph to clean dataframe,
        select colour palette and plot an animated bar chart, of chosen areas 
        rank change over time. 
        Parameters:
        ----------
        area_type: str
            either "Region" or "LA", default "Region"
        list_reg: lst
            list of region names to be compared over time
            list_areas() function can be used to see options
        sns_palette: str
            name of seaborn palette to be used
            https://seaborn.pydata.org/tutorial/color_palettes.html
        '''
        df_cleaned = self.clean_rank(list_reg=list_reg, area_type=area_type)
        dict_color = self.color_pal(df_cleaned, sns_palette=sns_palette)
        fig = px.bar(df_cleaned, x='Area Name', y='Value',
             color='Area Name', text='rank',
             color_discrete_map= dict_color,
             animation_frame='Time period',
             animation_group='Area Name',
             range_y=[50, 90],
             labels={ 'Value': 'Proportion Screened, %'},
            )
        fig.update_layout(width=1000, height=600, showlegend=False,
                        xaxis = dict(tickmode = 'linear', dtick = 1))
        fig.update_traces(textfont_size=16, textangle=0)
        fig.show()

df = basic_data_cleaning(cerv_data, False, False)
new_graph=Rank_Based_Graph(df)
new_graph.list_areas(area_type="LA")
print(new_graph.animated_bars(area_type="LA", list_reg=['Exeter', 'Broxtowe', 'Chorley', 'Harlow', 'South Oxfordshire']))
