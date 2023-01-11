#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 04:44:56 2023

@author: alistair
"""

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

data_str = 'https://data.england.nhs.uk/dataset/dbf14bed-85bc-4aef-856c-38eb9d6de730/resource/e281a471-f546-44b9-99f1-12e80b27a638/download/220iicancerscreeningcoveragecervicalcancer.data.csv'

# read url file into a dataframe
df = pd.read_csv(data_str)



class Dataframe_preprocessing:
    
    def __init__(self, init_df):
        self.processed_df = self.preprocess_data(init_df)
        
    def preprocess_data(self, in_df):
        temp_df = in_df
        temp_df = temp_df.drop(labels=['Sex'], axis=1)
        temp_df = temp_df.drop(labels=['Age'], axis=1)
        temp_df = temp_df.drop(labels=['Lower CI limit'], axis=1)
        temp_df = temp_df.drop(labels=['Upper CI limit'], axis=1)
        return temp_df

    
class Region_Analysis(Dataframe_preprocessing):
    
    def __init__(self, init_df, in_year):
        super().__init__(init_df)
        self.year = in_year
        self.directory_name = 'Shapefiles'
        
        self.create_map_of_all_regions_for_year(init_df)
        
    def error_prevention_directory_check(self):
        # check if directory exists
        exists = os.path.exists(self.directory_name)
        #printing if the path exists or not
        if not exists:
            print('Directory for saving shapefiles does not exist')
            os.makedirs(self.directory_name)
            print('Created directory')
        
    
    def create_map_of_all_regions_for_year(self, in_df):
        self.regions_df = self.get_all_regions(in_df)
        region_codes = self.get_all_region_area_codes()
        
        self.create_combined_map_shapefile(region_codes)
        self.display_map()
        
                
    def get_all_region_area_codes(self):
        region_codes = []
        
        for index, row in self.regions_df.iterrows():
            region_codes.append(row['Area Code'])
            
        return region_codes
    
    def display_map(self):
        self.error_prevention_directory_check()
        
        fp = f'{self.directory_name}/combined_shapefile.shx'
        map_df = gpd.read_file(fp)
        map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        
        fig = px.choropleth(map_df, geojson=map_df.geometry, 
                    locations=map_df.index, color='value',
                    height=500,
                   color_continuous_scale='mint')
        fig.update_geos(fitbounds="locations", visible=True)
        fig.update_layout(
            title_text=f'Choropleth map to show percentage uptake of screening for each region in {self.year}'
        )
        fig.update(layout = dict(title=dict(x=0.5)))
        fig.update_layout(
            margin={"r":0,"t":30,"l":10,"b":10},
            coloraxis_colorbar={
                'title':'Percent Uptake'})
                
        fig.show()
        
    
    def display_area_polygon(self, area_code):
        self.error_prevention_directory_check()
        
        self.current_area_code = area_code
        sf = shp.Reader(f'{self.directory_name}/{area_code}_shapefile.shp')

        plt.figure()
        for shape in sf.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            plt.plot(x,y)
        plt.show()
        
        
    def create_combined_map_shapefile(self, area_codes):
        self.error_prevention_directory_check()
        
        geodataframe = self.create_combined_map_geodf(area_codes)
        
        # output path for shapefile
        outfp = f'{self.directory_name}/combined_shapefile.shp'
        # write data to file
        geodataframe.to_file(outfp)
        
    def create_combined_map_geodf(self, area_codes):
        merged_df = gpd.GeoDataFrame()
        merged_df['geometry'] = None
        merged_df['value'] = None
        merged_df['area_code'] = None
        merged_df.crs = from_epsg(4326)
        
        for code in area_codes:
            self.current_area_code = code
            geodf = self.create_region_geodf(code)
            merged_df = gpd.GeoDataFrame(pd.concat([merged_df, geodf], ignore_index=True))
        
        return merged_df

        
        
    def create_region_shapefile(self, area_code):
        self.error_prevention_directory_check()
        
        geodataframe = self.create_region_geodf(area_code)
        
        # output path for shapefile
        outfp = f'{self.directory_name}/{area_code}_shapefile.shp'
        # write data to file
        geodataframe.to_file(outfp)
        
    def create_region_geodf(self, area_code):
        geoshape = self.get_geoshape_info_from_api_request_for_areacode(area_code)
        polygon_coordinates = self.convert_geoshape_to_polygon_coordinates(geoshape)
        geodataframe = self.create_geodataframe_with_area_data(polygon_coordinates)
        return geodataframe
        
        
    def get_geoshape_info_from_api_request_for_areacode(self, area_code):
        api_str = f'https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-united-kingdom-region&q=rgn_code={area_code}'
        json_response = requests.get(api_str).json()

        shape_info = str(json_response['records'][0]['fields']['geo_shape']['coordinates'])
        return shape_info
    
    # ERROR CHECKING! & unit test   
    
    def recursive_check_for_polygon_coords(self, parent_lst):
        temp_polygon_coords = []
        
        if len(parent_lst) > 1:
            for child in parent_lst:
                child_poly_coords = self.recursive_check_for_polygon_coords(child)
                for coords in child_poly_coords:
                    temp_polygon_coords.append(coords)
        else:
            # if only one element in list - polygon coordinates
            temp_polygon_coords.append(parent_lst[0])
                
        return temp_polygon_coords
    
        
        
    def convert_geoshape_to_polygon_coordinates(self, shape_data):
        # convert string representation to list data type
        coordinates_lst = ast.literal_eval(shape_data)
               
        poly_coords = self.recursive_check_for_polygon_coords(coordinates_lst)
                
        return poly_coords
    
    
    def create_geodataframe_with_area_data(self, poly_coords):
        newdata = gpd.GeoDataFrame()
        
        newdata['geometry'] = None
        
        
        polygons_lst = []
        
        for i in range(len(poly_coords)):
            poly = Polygon(poly_coords[i])
            polygons_lst.append(poly)
            
            # insert polygon in 'geometry' column
            newdata.loc[i, 'geometry'] = poly
            
            val = self.regions_df.loc[self.regions_df['Area Code'] == self.current_area_code, 'Value'].values[0]
            newdata.loc[i, 'value'] = val
            
            newdata.loc[i, 'area_code'] = self.current_area_code
        
        # set  dataframe's coordinate system to epsg code 4326
        newdata.crs = from_epsg(4326)
        
        return newdata
            
    
    def get_all_regions(self, in_df):
        filtered_df = in_df[in_df['Time period'] == self.year]
        return filtered_df[filtered_df['Area Type'] == 'Region']
    
    
    
region_test = Region_Analysis(df, 2016)


    
    