# File for Code to create Local Authorities Uptake Values Heatmap

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

loc_auth = gpd.read_file(\
'shape_files/statistical-gis-boundaries-london/London_Borough_Excluding_MHW.shp')

df = pd.read_pickle('data/cerv_data_clean.pkl')

def plot_london_map(df, time_period = int, val_labels = bool):
    '''
    Plots and saves a London map displaying the screening uptake by boroughs

    By default will create a map of the UK with the mean screening values for each boroough by year, unless a year is specified (int)
    
    Parameters:
    df (pandas DataFrame): DataFrame with local authority codes and screening uptake values. 
    time_period (int): Year of interest
    val_labels(bool): Set to True to add Annotation to map of % uptakes
    
    Returns:
    None
    '''

    loc_auth = gpd.read_file(\
    'shape_files/statistical-gis-boundaries-london/London_Borough_Excluding_MHW.shp')

    # Define Time-periods
    if time_period == 2010:
        df = df.loc[df['Time period'] == 2010]
    elif time_period == 2011:
        df = df.loc[df['Time period'] == 2011]
    elif time_period == 2012:
        df = df.loc[df['Time period'] == 2012]
    elif time_period == 2013:
        df = df.loc[df['Time period'] == 2013]
    elif time_period == 2014:
        df = df.loc[df['Time period'] == 2014]
    elif time_period == 2015:
        df = df.loc[df['Time period'] == 2015]
    elif time_period == 2016:
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
    if type(time_period) == int:
        plt.title(f'UK Screening Uptake by London Borough in {time_period}', fontsize=50)
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
                    if val_labels == True:
                        plt.annotate(str(round(row['Value'],1)), xy=(row['geometry'].centroid.x, row['geometry'].centroid.y - 500),
                                horizontalalignment='right', fontsize=15)

    plt.figure(dpi=300)

    if type(time_period) == int:
        plt.savefig(f'London_Screening_Heatmap_{time_period}')
    else:
        plt.savefig('London_Screening_Heatmap_Means')

    plt.show()
    return None

plot_london_map(df)

