#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import matplotlib.pyplot as plt
import requests

import geopandas as gpd
from shapely.geometry import Point, Polygon
import ast
from fiona.crs import from_epsg
import shapefile as shp # pyshp

import plotly.express as px
import pyproj
import os



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
        self.create_map_of_all_regions_for_year()
        
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
        self.create_combined_map_shapefile(region_codes)
        # Present user with interactable map
        self.display_map()
        
                
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
        geodataframe = self.create_combined_map_geodf(area_codes)
        
        # Set the output path for the shapefile
        outfp = f'{self.directory_name}/combined_shapefile.shp'
        # Create the shapefile
        geodataframe.to_file(outfp)
        
    def create_combined_map_geodf(self, area_codes):
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
            geodf = self.create_region_geodf(code)
            # Concatenate the region dataframe with the combined dataframe 
            merged_df = gpd.GeoDataFrame(pd.concat([merged_df, geodf], ignore_index=True))
        
        # Return the combined dataframe
        return merged_df

        
        
    def create_region_shapefile(self, area_code):
        # Check that the shapefiles directory exists before attempting to save files, in order to prevent an error
        self.error_prevention_directory_check()
        
        # Create the dataframe for the region
        geodataframe = self.create_region_geodf(area_code)
        
        # Set the output path for the region shapefile
        outfp = f'{self.directory_name}/{area_code}_shapefile.shp'
        # Create the shapefile
        geodataframe.to_file(outfp)
        
    def create_region_geodf(self, area_code):
        # Get the polygon coordinates data from the API request
        geoshape = self.get_geoshape_info_from_api_request_for_areacode(area_code)
        # Convert the API data to usable coordinates
        polygon_coordinates = self.convert_geoshape_to_polygon_coordinates(geoshape)
        # Create a geopandas dataframe using the cooridnates for the region
        geodataframe = self.create_geodataframe_with_area_data(polygon_coordinates)
        # Return the created dataframe
        return geodataframe
        
        
    def get_geoshape_info_from_api_request_for_areacode(self, area_code):
        # Create the API GET request for the specified region
        api_str = f'https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-united-kingdom-region&q=rgn_code={area_code}'
        # Collect the JSON response from the API
        json_response = requests.get(api_str).json()

        # Retrieve the polygon coordinates data string from the JSON response
        shape_info = str(json_response['records'][0]['fields']['geo_shape']['coordinates'])
        # Return the coordinate information
        return shape_info
    
    # ERROR CHECKING! & unit test   
    
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
