'''
Tools for advanced visualisations of screening data.

Explanation:

UK_Map:
    

London_Map:
    

RankGraph: animated bar chart
'''
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
#from vis_tools import datasets as ds

# Importing the 
loc_auth = gpd.read_file('shape_files/statistical-gis-boundaries-london/London_Borough_Excluding_MHW.shp')


### To be deleted
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


class UK_Map:
    '''
    Plots and saves a UK map displaying the screening uptake by local authority, excluding London.
    '''

    def __init__(self, df, time_period = int, val_labels = bool):
        self.df = df
        self.time_period = time_period
        self.val_labels = val_labels

    def plot_uk_map(self):
        '''
        Plots and saves a UK map displaying the screening uptake by local authority, excluding London

        By default will create a map of the UK with the mean screening values for each local authority by year, unless a year is specified (int)
        
        Parameters:
        df (pandas DataFrame): DataFrame with local authority codes and screening uptake values. 
        time_period (int): Year of interest
        val_labels(bool): Set to True to add Annotation to map of % uptakes; Default = False

        Returns:
        None
        '''
        loc_auth = gpd.read_file(\
        'shape_files/Local_Authority_Districts_(December_2022)_Boundaries_UK_BFC/LAD_DEC_2022_UK_BFC.shp')

        # Define Time-periods
        if self.time_period == 2010:
            self.df = self.df.loc[self.df['Time period'] == 2010]
        elif self.time_period == 2011:
            self.df = self.df.loc[self.df['Time period'] == 2011]
        elif self.time_period == 2012:
            self.df = self.df.loc[self.df['Time period'] == 2012]
        elif self.time_period == 2013:
            self.df = self.df.loc[self.df['Time period'] == 2013]
        elif self.time_period == 2014:
            self.df = self.df.loc[self.df['Time period'] == 2014]
        elif self.time_period == 2015:
            self.df = self.df.loc[self.df['Time period'] == 2015]
        elif self.time_period == 2016:
            self.df = self.df.loc[self.df['Time period'] == 2016]
        else:
            mean_values = self.df.groupby('Area Name')['Value'].mean().to_dict()
            self.df['Value'] = self.df['Area Name'].map(mean_values)

        # Merge shapefile with dataset
        uk_map = loc_auth.merge(self.df, left_on='LAD22CD', right_on='Area Code')

        # Exclude London LA's
        uk_map = uk_map[~uk_map['Area Name'].isin(['Barking and Dagenham', 'Barnet', 'Bexley', \
            'Brent', 'Bromley', 'Camden', 'Croydon', 'Ealing', 'Enfield', 'Greenwich', 'Hackney', 'Hammersmith and Fulham', \
                'Haringey', 'Harrow', 'Havering', 'Hillingdon', 'Hounslow', 'Islington', 'Kensington and Chelsea',\
                    'Kingston upon Thames', 'Lambeth', 'Lewisham', 'Merton', 'Newham', 'Redbridge', 'Richmond upon Thames', 'Southwark',\
                        'Sutton', 'Tower Hamlets', 'Waltham Forest', 'Wandsworth', 'Westminster'])]

        # Set figure size
        plt.figure(figsize=(20, 10))

        # Create colourmap
        cmap = LinearSegmentedColormap.from_list('mycmap', ['#FFFFFF', '#0F2B7F', '#0078B4'])

        # Plot map
        fig = uk_map.plot(column='Value', cmap=cmap, legend=True, figsize=(125, 70))

        plt.title('UK Screening Uptake by Local Authority', fontsize=50)

        # Add local authority labels
        for idx, row in uk_map.iterrows():
            plt.annotate(row['Area Name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                    horizontalalignment='center', fontsize=15)
            if self.val_labels == True:
                plt.annotate(str(round(row['Value'],1)), xy=(row['geometry'].centroid.x, row['geometry'].centroid.y - 6000),
                        horizontalalignment='right', fontsize=15)

        plt.figure(dpi=300)

        if type(self.time_period) == int:
            plt.savefig(f'UK_Screening_Heatmap_{self.time_period}')
        else:
            plt.savefig('UK_Screening_Heatmap_Means')

        plt.show()
        return None


class LondonMap():
    """
    Plots and saves a London map displaying the screening uptake by boroughs. 
    
    Parameters:
    df (pandas DataFrame): DataFrame with local authority codes and screening uptake values. 
    time_period (int): Year of interest
    val_labels(bool): Set to True to add Annotation to map of % uptakes
    
    Returns:
    None
    """
    
    def __init__(self, df, time_period = int, val_labels = bool):
        self.df = df
        self.time_period = time_period
        self.val_labels = val_labels
        
    def plot_london_map(self):
        loc_auth = gpd.read_file(\
        'shape_files/statistical-gis-boundaries-london/London_Borough_Excluding_MHW.shp')

        # Define Time-periods
        if self.time_period == 2010:
            df = df.loc[df['Time period'] == 2010]
        elif self.time_period == 2011:
            df = df.loc[df['Time period'] == 2011]
        elif self.time_period == 2012:
            df = df.loc[df['Time period'] == 2012]
        elif self.time_period == 2013:
            df = df.loc[df['Time period'] == 2013]
        elif self.time_period == 2014:
            df = df.loc[df['Time period'] == 2014]
        elif self.time_period == 2015:
            df = df.loc[df['Time period'] == 2015]
        elif self.time_period == 2016:
            df = df.loc[df['Time period'] == 2016]
        else:
            mean_values = df.groupby('Area Name')['Value'].mean().to_dict()
            df['Value'] = df['Area Name'].map(mean_values)

        # Merge shapefile with dataset
        ldn_map = loc_auth.merge(df, left_on='GSS_CODE', right_on='Area Code')

        # Set figure size
        plt.figure(figsize=(20, 10))

        # Create colourmap
        cmap = LinearSegmentedColormap.from_list('mycmap', ['#FFFFFF', '#0F2B7F', '#0078B4'])

        # Plot map
        fig = ldn_map.plot(column='Value', cmap=cmap, legend=True, figsize=(50, 30))

        # Add local authority labels
        if type(self.time_period) == int:
            plt.title(f'UK Screening Uptake by London Borough in {self.time_period}', fontsize=50)
            for idx, row in ldn_map.iterrows():
                plt.annotate(row['Area Name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                        horizontalalignment='center', fontsize=15)
                plt.annotate(str(round(row['Value'],1)), xy=(row['geometry'].centroid.x, row['geometry'].centroid.y - 500),
                        horizontalalignment='right', fontsize=15)
        else:
            plt.title(f'UK Screening Uptake by London Borough Means', fontsize=50)
            for idx, row in ldn_map.iterrows():
                        plt.annotate(row['Area Name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                                horizontalalignment='center', fontsize=15)
                        if self.val_labels == True:
                            plt.annotate(str(round(row['Value'],1)), xy=(row['geometry'].centroid.x, row['geometry'].centroid.y - 500),
                                    horizontalalignment='right', fontsize=15)

        plt.figure(dpi=300)

        if type(self.time_period) == int:
            plt.savefig(f'London_Screening_Heatmap_{self.time_period}')
        else:
            plt.savefig('London_Screening_Heatmap_Means')

        plt.show()
        return None


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
                     'South East region'], sns_palette="Spectral",
                     width=1000, height=600, showlegend=False,
                     rank_text_size=16):
        '''
        Utilises other functions in class Rank_Based_Graph to clean dataframe,
        select colour palette and plot an animated bar chart, of chosen areas 
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
        fig.show()