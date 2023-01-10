# File for Code to create Local Authorities Uptake Values Heatmap

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


df = pd.read_pickle('data/cerv_data_clean.pkl')


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