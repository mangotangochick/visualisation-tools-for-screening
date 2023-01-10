# File for Code to create Local Authorities Uptake Values Heatmap

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


df = pd.read_pickle('data/cerv_data_clean.pkl')
df['Time period']

def plot_uk_map(df, time_period = int):
    '''
    Plots and saves a UK map displaying the screening uptake by local authority, excluding London

    By default will create a map of the UK with the mean screening values for each local authority by year, unless a year is specified (int)
    
    Parameters:
    df (pandas DataFrame): DataFrame with local authority codes and screening uptake values. 
    time_period (int): Year of interest
    
    Returns:
    None
    '''

    loc_auth = gpd.read_file(\
    'shape_files/Local_Authority_Districts_(December_2022)_Boundaries_UK_BFC/LAD_DEC_2022_UK_BFC.shp')
    print(loc_auth.LAD22CD)

    # Define Time-periods
    if time_period == 2010:
        df = df.loc[df['Time period'] == 2010]
    elif time_period == 2011:
        df = df.loc[df['Time period'] == 201]
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
        df = df

    df['Value'] = df.groupby('Time period')['Value'].transform(lambda x: x.fillna(x.mean()))

    # Merge shapefile with dataset
    uk_map = loc_auth.merge(df, left_on='LAD22CD', right_on='Area Code')
    print(uk_map['Area Name'])

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
    fig = uk_map.plot(column='Value', cmap=cmap, legend=True, figsize=(100, 50))

    plt.title('UK Screening Uptake by Local Authority', fontsize=50)

    # Add local authority labels
    for idx, row in uk_map.iterrows():
        plt.annotate(row['Area Name'], xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
                horizontalalignment='center', fontsize=10)

    plt.figure(dpi=300)
    plt.savefig('UK_Local_Authorities_Screening_Heatmap')
    plt.show()
    return None

plot_uk_map(df, time_period = 2015)

