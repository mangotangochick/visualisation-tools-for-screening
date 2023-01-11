'''
Tools for advanced visualisations of screening data.

This module helps generate a variety of different visualisations for screening
uptake, and can be customised to display data in formats such as heatmaps,
interactive bar charts making it easy to compare different regions over time.

London_Map:
    Plots and saves a London map displaying the screening uptake by boroughs.

animated_bars(): part of Rank_Graph class
    Creates an animated, interactive bar chart of the ranking of a chosen list
    of areas over time.
'''
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
import os
#from vis_tools import datasets as ds

import requests
from shapely.geometry import Point, Polygon
import ast
from fiona.crs import from_epsg
import shapefile as shp # pyshp
import pyproj

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


class Dataframe_preprocessing:
    
    def __init__(self):
        # Create pandas dataframe from online dataset
        self.init_df = self.initialise_df()
        # Basic cleaning of dataset to remove redundant columns
        self.processed_df = self.preprocess_data()
        
    def initialise_df(self):
        # URL for screening dataset
        data_str = 'https://data.england.nhs.uk/dataset/dbf14bed-85bc-4aef-856c-38eb9d6de730/resource/e281a471-f546-44b9-99f1-12e80b27a638/download/220iicancerscreeningcoveragecervicalcancer.data.csv'

        # Read the URL file into a dataframe and return it
        return pd.read_csv(data_str)
        
    def preprocess_data(self):
        # Get the original dataset
        temp_df = self.init_df
        # Remove the redundant columns from dataframe
        temp_df = temp_df.drop(labels=['Sex'], axis=1)
        temp_df = temp_df.drop(labels=['Age'], axis=1)
        temp_df = temp_df.drop(labels=['Lower CI limit'], axis=1)
        temp_df = temp_df.drop(labels=['Upper CI limit'], axis=1)
        # Return the updated dataframe
        return temp_df

    
class Region_Analysis(Dataframe_preprocessing):
    
    def __init__(self, in_year):
        super().__init__()
        # Set the 'Time period' focus for dataset filtering
        self.year = in_year
        # Set the name to be used for storing shapefiles to be used for creating map visuals
        self.directory_name = 'Shapefiles'
        
        # Main function to create and display Plotly express (interactable) choropleth map of regions
        was_error = self.create_map_of_all_regions_for_year()
        
        # If an error was encountered creating the map
        if was_error:
            # Indicate this to the user
            print('Creating map of regions failed. Please see previous logs for more information.')
        
    def error_prevention_directory_check(self):
        # Check if the directory exists
        exists = os.path.exists(self.directory_name)
        # If the directory doesn't already exist
        if not exists:
            # Indicate to the user that directory does not exist
            print('Directory for saving shapefiles does not exist')
            # Create the directory to prevent errors in saving created files
            os.makedirs(self.directory_name)
            # Indicate the changes to the directory to user
            print('Created directory')
        
    
    def create_map_of_all_regions_for_year(self):
        # Create a filtered dataframe of only the regions (only for specified time period)
        self.regions_df = self.get_all_regions()
        # Create a list of 'Area Code's for all regions for accessing regions & querying dataset
        region_codes = self.get_all_region_area_codes()
        
        # Create a shapefile that includes all regions (country map)
        was_error = self.create_combined_map_shapefile(region_codes)
        
        # If no error was encountered creating the map shapefile
        if not was_error:
            # Present user with interactable map
            self.display_map()
            
            # Return a negative boolean to indicate no error was encountered
            return False
        # If an error was encountered creating the map shapefile
        else:
            # Return a positive boolean to indicate an error was encountered
            return True
        
                
    def get_all_region_area_codes(self):
        # Initialise empty list to hold the 'Area Code's
        region_codes = []
        
        # For each row in the filtered dataframe
        for index, row in self.regions_df.iterrows():
            # Get 'Area Code' value from the row, and add to the list
            region_codes.append(row['Area Code'])
            
        # Once all of the codes have been collected, return the list
        return region_codes
    
    def display_map(self):
        # Check that the shapefiles directory exists before attempting to retrieve files, in order to prevent an error
        self.error_prevention_directory_check()
        
        # Get the filepath for the shapefile
        fp = f'{self.directory_name}/combined_shapefile.shx'
        # Read the file into a Geopandas dataframe
        map_df = gpd.read_file(fp)
        # Correct the projection settings
        map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        
        # Create the Plotly express map using the created dataframe to populate it
        fig = px.choropleth(map_df, geojson=map_df.geometry, 
                    locations=map_df.index, color='value',
                    height=500,
                   color_continuous_scale='mint')
        fig.update_geos(fitbounds="locations", visible=True)
        # Set the title of the plot
        fig.update_layout(
            title_text=f'Choropleth map to show percentage uptake of screening for each region in {self.year}'
        )
        # Position the title in the centre of the view
        fig.update(layout = dict(title=dict(x=0.5)))
        # Layout settings for the colorbar to represent 'Value' (legend)
        fig.update_layout(
            margin={"r":0,"t":30,"l":10,"b":10},
            coloraxis_colorbar={
                'title':'Percent Uptake'})
                
        # Present the map to the user
        fig.show()
        
    
    def display_area_polygon(self, area_code):
        # Check that the shapefiles directory exists before attempting to retrieve files, in order to prevent an error
        self.error_prevention_directory_check()
        
        # Update the currenty focused on region
        self.current_area_code = area_code
        # Open the shapefile
        sf = shp.Reader(f'{self.directory_name}/{area_code}_shapefile.shp')

        # Using matplotlib, plot the individual region shapefile
        plt.figure()
        for shape in sf.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            plt.plot(x,y)
        # Present plot to the user
        plt.show()
        
        
    def create_combined_map_shapefile(self, area_codes):
        # Check that the shapefiles directory exists before attempting to save files, in order to prevent an error
        self.error_prevention_directory_check()
        
        # Create the dataframe that holds all of the region map data (combining all individual dataframes)
        geodataframe, was_error = self.create_combined_map_geodf(area_codes)
        
        # If no error was encountered creating the map dataframe
        if not was_error:
            # Set the output path for the shapefile
            outfp = f'{self.directory_name}/combined_shapefile.shp'
            # Create the shapefile
            geodataframe.to_file(outfp)
            
            # Return negative boolean to indicate no error was encountered
            return False
        # If an error was encountered creating the map dataframe
        else:
            # Return a positive boolean to indicate an error was encountered
            return True
            
        
    def create_combined_map_geodf(self, area_codes):
        encountered_error = False
        
        # Create a geopandas dataframe with the same structure as the individual region dataframes
        merged_df = gpd.GeoDataFrame()
        merged_df['geometry'] = None
        merged_df['value'] = None
        merged_df['area_code'] = None
        # Correct the projection settings
        merged_df.crs = from_epsg(4326)
        
        # Iterate through each region using collected region codes
        for code in area_codes:
            # Update the current region of focus
            self.current_area_code = code
            # Create a dataframe for the current region
            geodf, was_error = self.create_region_geodf(code)
            
            # If no error was encountered creating dataframe
            if not was_error:
                # Concatenate the region dataframe with the combined dataframe 
                merged_df = gpd.GeoDataFrame(pd.concat([merged_df, geodf], ignore_index=True))
            # If an error was encountered creating dataframe
            else:
                # Set error boolean to True to return error state to calling method
                encountered_error = True
        
        # Return the combined dataframe
        return merged_df, encountered_error

        
        
    def create_region_shapefile(self, area_code):
        # Check that the shapefiles directory exists before attempting to save files, in order to prevent an error
        self.error_prevention_directory_check()
        
        # Create the dataframe for the region
        geodataframe, was_error = self.create_region_geodf(area_code)
        
        # If no error was encountered creating the dataframe
        if not was_error:
            # Set the output path for the region shapefile
            outfp = f'{self.directory_name}/{area_code}_shapefile.shp'
            # Create the shapefile
            geodataframe.to_file(outfp)
            return False
        # If an error was encountered creating the dataframe
        else:
            print('Error creating region shapefile')
            return True
            
        
    def create_region_geodf(self, area_code):
        # Get the polygon coordinates data from the API request
        geoshape, was_error = self.get_geoshape_info_from_api_request_for_areacode(area_code)
        
        # If no error encountered requesting API data
        if not was_error:
            # Convert the API data to usable coordinates
            polygon_coordinates = self.convert_geoshape_to_polygon_coordinates(geoshape)
            # Create a geopandas dataframe using the cooridnates for the region
            geodataframe = self.create_geodataframe_with_area_data(polygon_coordinates)
            # Return the created dataframe, and a negative boolean to indicate no errors were encountered
            return geodataframe, False
        
        # If an error is encountered when requesting data
        else:
            # Indicate error to the user
            print('Error creating region geopandas dataframe: API request failed')
            # Return empty dataframe, and a positive boolean to indicate an error was encountered
            return gpd.GeoDataFrame(), True
        
        
    def get_geoshape_info_from_api_request_for_areacode(self, area_code):
        # Create the API GET request for the specified region
        api_str = f'https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-united-kingdom-region&q=rgn_code={area_code}'
                
        # Process API GET request and store response from server
        response = requests.get(api_str)
        
        # If API request fails
        if response.status_code != 200:
            # Return empty string as request faied, along with positive boolean to indicate there was an error to abort further processing attempts
            return str(), True
            
        
        # Collect the JSON response from the API
        json_response = response.json()
        
        # Check number of matches for API query - if zero matches, return an error as it failed to find the area
        if json_response['nhits'] == 0:
            # Return empty string as request faied, along with positive boolean to indicate there was an error to abort further processing attempts
            return str(), True
        

        # Retrieve the polygon coordinates data string from the JSON response
        shape_info = str(json_response['records'][0]['fields']['geo_shape']['coordinates'])
        # Return the coordinate information and negative boolean to indicate no errors encountered
        return shape_info, False
    
    
    def recursive_check_for_polygon_coords(self, parent_lst):
        # Initialise an empty list to hold polygon coordinates
        temp_polygon_coords = []
        
        # If the current list has more than one element
        if len(parent_lst) > 1:
            # Iterate through each element in the list
            for child in parent_lst:
                # Recursive call of the method to search the current elements sublist for cooridnates
                child_poly_coords = self.recursive_check_for_polygon_coords(child)
                # For each returned polygon outline from the recursive call
                for coords in child_poly_coords:
                    # Add the coordinates to the list of coordinates to be returned by the acting 'parent' list
                    temp_polygon_coords.append(coords)
        # If the current list has only one element - identified polygon coordinates
        else:
            # Retrieve the coordinates and add them to the cooridnates list to be returned
            temp_polygon_coords.append(parent_lst[0])
                
        # Return the collected cooridnates
        return temp_polygon_coords
    
        
        
    def convert_geoshape_to_polygon_coordinates(self, shape_data):
        # Convert the string representation of the coordinates list to a list data type
        coordinates_lst = ast.literal_eval(shape_data)
               
        # Recursively traverse the cooridnates list to create polygon cooridnates compatible with Shapely
        poly_coords = self.recursive_check_for_polygon_coords(coordinates_lst)
                
        # Return the polygon coordinates
        return poly_coords
    
    
    def create_geodataframe_with_area_data(self, poly_coords):
        # Create a geopandas dataframe for the region using provided polygon coordinates
        newdata = gpd.GeoDataFrame()
        
        newdata['geometry'] = None
        
        # Initialise an empty list to hold the encompassed polygons
        polygons_lst = []
        
        # Iterate through each set of coordinates
        for i in range(len(poly_coords)):
            # Create a Shapely Polygon using the current set of coordinates
            poly = Polygon(poly_coords[i])
            # Add the created polygon to the list of polygons for this region
            polygons_lst.append(poly)
            
            # Insert the polygon in the 'geometry' column of the dataframe
            newdata.loc[i, 'geometry'] = poly
            
            # Retrieve 'Value' cell data for the row in the dataframe that macthes the current 'Area Code'
            val = self.regions_df.loc[self.regions_df['Area Code'] == self.current_area_code, 'Value'].values[0]
            newdata.loc[i, 'value'] = val
            
            # Add the current 'Area Code' to the dataframe entry
            newdata.loc[i, 'area_code'] = self.current_area_code
        
        # Correct the projection settings
        newdata.crs = from_epsg(4326)
        
        # Return the dataframe
        return newdata
            
    
    def get_all_regions(self):
        # Filter the dataframe to only include entries of the specified 'Time period'
        filtered_df = self.init_df[self.init_df['Time period'] == self.year]
        # Filter the updated dataframe to only include regions, and return the dataframe
        return filtered_df[filtered_df['Area Type'] == 'Region']
    

# Example of how to use the region analysis class    
#region_test = Region_Analysis(2016)


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
        'data/shape_files/London_Borough_Excluding_MHW.shp')

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
        ldn_map = loc_auth.merge(self.df, left_on='GSS_CODE', right_on='Area Code')

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
            plt.savefig(f'London_Screening_Heatmap_{self.time_period}.png')
        else:
            plt.savefig('London_Screening_Heatmap_Means.png')

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
            either a "Reagion", "UA, or "LA", default = "Region"
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
        fig.show()