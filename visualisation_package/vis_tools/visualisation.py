"""
Tools for advanced visualisations of screening data.

This module helps generate a variety of different visualisations for screening
uptake, and can be customised to display data in formats such as choropleth
maps, interactive bar charts making it easy to compare different regions over
time.

Region_Analysis:
    Creates an animated interactive choropleth map of country separated into
    regions to visualise screening uptake.

LondonMap:
    Plots and saves a London map displaying the screening uptake by boroughs.

Rank_Based_Graphs: 
    Creates an animated, interactive charts of the ranking of a chosen list
    of areas over time. Can create:
    Bar chart with: animated_bars()
    Scatter plot with: animated_scatter()



"""
import os
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
import plotly.offline as pyo
import plotly.io as pio

pio.renderers.default = "vscode"
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import data

package_dir = os.path.dirname(data.__file__)
import requests
import numpy as np
from shapely.geometry import Point, Polygon
import ast
from fiona.crs import from_epsg
import shapefile as shp  # pyshp
import pyproj
import math
from datasets import *


class DataframePreprocessing:

    """
    Class that includes methods for downloading and basic cleaning of an NHS
    screening uptake dataset, to be inherited from by analysis classes. Allows
    for increased expandability of the code.


    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    def __init__(self):
        # Create pandas dataframe from online dataset
        self.init_df = self.initialise_df()
        # Basic cleaning of dataset to remove redundant columns
        self.processed_df = self.preprocess_data()

    def initialise_df(self):
        """
        Function to download the dataset and read it into a pandas dataframe.


        Parameters
        ----------
        None

        Returns
        -------
        pd.read_csv(data_str): pandas dataframe
            The pandas dataframe created with the screening data
        """

        # URL for screening dataset
        data_str = "https://data.england.nhs.uk/dataset/dbf14bed-85bc-4aef-856c-38eb9d6de730/resource/e281a471-f546-44b9-99f1-12e80b27a638/download/220iicancerscreeningcoveragecervicalcancer.data.csv"

        # Read the URL file into a dataframe and return it
        return pd.read_csv(data_str)

    def preprocess_data(self):
        """
        Function to clean the pandas dataframe - removing redundant columns.


        Parameters
        ----------
        None

        Returns
        -------
        temp_df: pandas dataframe
            The updated dataframe
        """

        # Get the original dataset
        temp_df = self.init_df
        # Remove the redundant columns from dataframe
        temp_df = temp_df.drop(labels=["Sex"], axis=1)
        temp_df = temp_df.drop(labels=["Age"], axis=1)
        temp_df = temp_df.drop(labels=["Lower CI limit"], axis=1)
        temp_df = temp_df.drop(labels=["Upper CI limit"], axis=1)
        # Return the updated dataframe
        return temp_df


class Region_Analysis(DataframePreprocessing):
    """
    Class to create a choropleth map of the country to show the percentage
    uptake of screening for each region, animating to show the change across
    the dataset time period (2010-2016).

    This class handles making an API GET request to recieve shapefile polygon
    cooridnate data, transforming the data, and plotting it to visualise the
    region category data.

    This class inherits from the 'Dataframe_preprocessing' class, and therefore
    shares all its methods.

    To initialise this class, a user must provide a plotly express 'colorscale';
    the default is 'mint'. If the user does not provide one, or provides an
    unacceptable colorscale, the default will be used.

    For more information on available colorscales, run the command:
    'print(px.colors.named_colorscales())'.


    Parameters
    ----------
    colorscale: String
        A string identifying the plotly express colorscale to be used for
        styling the graph.

    Returns
    -------
    None
    """

    def __init__(self, colorscale):
        super().__init__()

        # Check whether or not the input colorscale is acceptable, and set it.
        self.colorscale = self.process_colorscale(colorscale)

        # Set the name to be used for storing shapefiles to be used for maps.
        self.directory_name = "Shapefiles"

        # Main function to create and display interactable choropleth map.
        was_error = self.create_map_of_all_regions()

        # If an error was encountered creating the map
        if was_error:
            # Indicate this to the user
            print(
                "Creating map of regions failed. Please see previous logs for \
                    more information."
            )

    def error_prevention_directory_check(self):
        """
        Function to check if the desired output directory exists, in order to
        mitigate errors from arising whilst attempting to access the directory.
        If the directory does not exist, it will be created in this function to
        prevent an errors.


        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Check if the directory exists
        exists = os.path.exists(self.directory_name)
        # If the directory doesn't already exist
        if not exists:
            # Indicate to the user that directory does not exist
            print("Directory for saving shapefiles does not exist")
            # Create the directory to prevent errors in saving created files
            os.makedirs(self.directory_name)
            # Indicate the changes to the directory to user
            print("Created directory")

    def process_colorscale(self, in_colorscale):
        """
        Function to check if the specified colorscale for the graph is a
        recognised name. Allows the colorscale to be used if recognised,
        or returns an alternative (default) setting if it is not recognised.

        If the user does not provide one, or provides an unacceptable
        colorscale, the default will be used.

        For more information on available colorscales, run the command:
        'print(px.colors.named_colorscales())', or read the Plotly
        documentation at: https://plotly.com/python/builtin-colorscales/.


        Parameters
        ----------
        in_colorscale: String
            A string identifying the plotly express colorscale to be used for styling
            the graph.

        Returns
        -------
        'mint': String
            The default colorscale setting

        in_colorscale.lower(): String
            The input colorscale, in lowercase form.
        """

        # If no colorscale was provided
        if (in_colorscale == None) or (in_colorscale == ""):
            # Indicate to user that no colorscale was provided
            print(
                "Error setting colorscale: no colorscale provided. Setting\
                    default instead."
            )
            # Return default setting: 'mint'
            return "mint"
        # If a colorscale has been provided
        else:
            # Check if input is of correct data type to avoid errors
            is_string = isinstance(in_colorscale, str)
            # If the input is of the correct data type
            if is_string:
                # If the specified colorscale is not recognised
                if in_colorscale.lower() not in px.colors.named_colorscales():
                    # Indicate to the user that it is not acceptable
                    print(
                        "Error setting colorscale: colorscale not recognised.\
                            Setting default instead."
                    )
                    # Return default setting: 'mint'
                    return "mint"
                # If the specified colorscale is recognised
                else:
                    # Return the colorscale as an acceptable option
                    return in_colorscale.lower()
            # If the input is not the correct data type
            else:
                # Indicate incorrect data type to the user
                print(
                    "Error setting colorscale: provided colorscale is of \
                        incorrect data type. Setting default instead."
                )
                # Return default setting: 'mint'
                return "mint"

    def create_map_of_all_regions(self):
        """
        Function to handle the creation of the choropleth map. For increased
        readbility, re-usability, and expandability, the main steps of this
        process are broken into separate functions, which are called and
        evaluated here.


        Parameters
        ----------
        None

        Returns
        -------
        True/False: Boolean
            This value indicates whether or not (respectively) an error was
            encountered in attempting to create the map.
        """

        # Create two filtered dataframes of only the regions; 
        # one for a specified year, 
        # and the other with data for all years
        self.all_years_regions_df, self.regions_df = self.get_all_regions()
        # Create a list of 'Area Code's for all regions 
        # for accessing regions & querying dataset
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
        """
        Function to get the 'Area Code' for all of the regions in the dataset.


        Parameters
        ----------
        None

        Returns
        -------
        region_codes: list
            A list of 'Area Code's, each representing a region in the dataset.
        """

        # Initialise empty list to hold the 'Area Code's
        region_codes = []

        # For each row in the filtered dataframe
        for index, row in self.regions_df.iterrows():
            # Get 'Area Code' value from the row, and add to the list
            region_codes.append(row["Area Code"])

        # Once all of the codes have been collected, return the list
        return region_codes

    def display_map(self):
        """
        Function to create a Plotly express choropleth map figure utilising the
        geopandas dataframe and display it to the user


        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Check that the shapefiles directory exists before attempting to
        # retrieve files, in order to prevent an error
        self.error_prevention_directory_check()

        # Get the filepath for the shapefile
        fp = f"{self.directory_name}/combined_shapefile.shx"
        # Read the file into a Geopandas dataframe
        map_df = gpd.read_file(fp)
        # Correct the projection settings
        map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

        # Create a populated Plotly express map using the created dataframe.
        fig = px.choropleth(
            map_df,
            geojson=map_df.geometry,
            locations=map_df.index,
            color="value",
            color_continuous_scale=self.colorscale,
            projection="orthographic",
            hover_name="value",
            hover_data=["value"],
            custom_data=np.stack(("value", "area_name"), axis=-1),
            animation_frame="year",
        )

        # Styling settings for the globe projection
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            resolution=50,
            showcountries=True,
            countrycolor="#969696",
            showland=True,
            landcolor="#cccccc",
        )

        # Calculate suitable color for slider:
        # Convert the graph to a dictionary
        graph_dict = fig.to_dict()
        # Retrieve the specified colorscale from the dictionary
        graph_color_scale = graph_dict["layout"]["coloraxis"]["colorscale"]
        # Select the middle (average) element in the list of colors
        avg_color = graph_color_scale[math.floor(len(graph_color_scale) / 2)][1]

        # Styling and layout settings for the plot
        fig.update_layout(
            title={
                "text": "Choropleth map to show % uptake of screening<br> for \
                    England regions from 2010 to 2016",
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
            },
            sliders=[
                {
                    "currentvalue": {"prefix": "Year: "},
                    "len": 0.6,
                    "xanchor": "left",
                    "bgcolor": avg_color,
                }
            ],
            margin={"r": 0, "t": 100, "l": 5, "b": 0},
            width=800,
            coloraxis_colorbar={
                "title": "% Uptake",
                "bordercolor": "#ccc",
                "borderwidth": 2,
                "orientation": "v",
                "x": 0,
                "xpad": 10,
                "xanchor": "left",
            },
        )

        # Set colorbar font sizes
        fig.update_coloraxes(colorbar_title_font=dict(size=15))
        fig.update_coloraxes(colorbar_tickfont=dict(size=14))

        # Set hovertemplate for map (displayed text when hovering on region)
        fig.update_traces(
            hovertemplate="".join(
                ["%{customdata[1]}", "<br><b>", "%{customdata[0]:0.2f}", "%", 
                "</b>"]
            )
        )

        # Present the map to the user
        fig.show()


    def display_area_polygon(self, area_code):
        """
        Function to create a matplotlib rendering of the region polygon, and
        display it to the user.

        Parameters
        ----------
        area_code: string
            The 'Area Code' for the region whose data has been collected.

        Returns
        -------
        None
        """

        # Check that the shapefiles directory exists before attempting to
        # retrieve files, in order to prevent an error
        self.error_prevention_directory_check()

        # Update the currenty focused on region
        self.current_area_code = area_code
        # Open the shapefile
        sf = shp.Reader(f"{self.directory_name}/{area_code}_shapefile.shp")

        # Using matplotlib, plot the individual region shapefile
        plt.figure()
        for shape in sf.shapeRecords():
            x = [i[0] for i in shape.shape.points[:]]
            y = [i[1] for i in shape.shape.points[:]]
            plt.plot(x, y)
        # Present plot to the user
        plt.show()

    def create_combined_map_shapefile(self, area_codes):
        """
        Function to create a shapefile for the country map that combines
        individual region shapefile data; creating a combined dataframe to be
        used in the creation of the shapefile.


        Parameters
        ----------
        area_codes: list
            A list of 'Area Code's, each representing a region in the dataset.

        Returns
        -------
        None
        """

        # Check that the shapefiles directory exists before attempting to save
        # files, in order to prevent an error
        self.error_prevention_directory_check()

        # Create the dataframe that holds all of the region map data
        # (combining all individual dataframes)
        geodataframe, was_error = self.create_combined_map_geodf(area_codes)

        # If no error was encountered creating the map dataframe
        if not was_error:
            # Set the output path for the shapefile
            outfp = f"{self.directory_name}/combined_shapefile.shp"
            # Create the shapefile
            geodataframe.to_file(outfp)

            # Return negative boolean to indicate no error was encountered
            return False
        # If an error was encountered creating the map dataframe
        else:
            # Return a positive boolean to indicate an error was encountered
            return True

    def create_combined_map_geodf(self, area_codes):
        """
        Function to create a geopandas dataframe for the country map shapefile
        that combines individual region geopandas dataframes


        Parameters
        ----------
        area_codes: list
            A list of 'Area Code's, each representing a region in the dataset.

        Returns
        -------
        merged_df: geopandas dataframe
            The combined dataframe of individual region dataframes; holding
            coordinate data for shapely polygons.
        encountered_error: Boolean
            A positive or negative boolean value indicating that an error
            was/wasn't (respectively) encountered.
        """

        encountered_error = False

        # Create a geopandas df with the same structure as the region dfs.
        merged_df = gpd.GeoDataFrame()
        merged_df["geometry"] = None
        merged_df["value"] = None
        merged_df["area_code"] = None
        merged_df["area_name"] = None
        merged_df["year"] = None
        # Correct the projection settings
        merged_df.crs = from_epsg(4326)

        # Change the datatype of the 'year' column to integer to reduce storage.
        merged_df = merged_df.astype({"year": np.int32})

        # Iterate through each region using collected region codes.
        for code in area_codes:
            # Update the current region of focus.
            self.current_area_code = code
            # Create a dataframe for the current region.
            geodf, was_error = self.create_region_geodf(code)
            # Change the datatype of the 'year' column to match combined df.
            geodf = geodf.astype({"year": np.int32})

            # Rather than calculating geometries at each year, copy existing
            # df data and change year specific data to reduce computation time.
            temp_geodf = geodf.copy(deep=True)
            # Starting from 2016, for each remaining year
            for i in range(6):
                # Create a copy of the temporary dataframe
                altered_geodf = temp_geodf.copy(deep=True)
                # For each row in the dataframe
                for index, row in altered_geodf.iterrows():
                    # Alter the 'year' value to the current year
                    altered_geodf.loc[index, "year"] = 2016 - (i + 1)

                # Get 'Value' at current year from the all years dataframe
                val = self.all_years_regions_df.loc[
                    (self.all_years_regions_df["Area Code"] == code)
                    & (self.all_years_regions_df["Time period"] == 2016 - (i + \
                        1)),
                    "Value",
                ].values[0]
                # Alter the new dataframe 'value' to the correct value for year.
                altered_geodf.loc[index, "value"] = val

                # Combine the dataframes.
                geodf = gpd.GeoDataFrame(
                    pd.concat([geodf, altered_geodf], ignore_index=True)
                )

            # If no error was encountered creating dataframe.
            if not was_error:
                # Concatenate the region dataframe with the combined dataframe.
                merged_df = gpd.GeoDataFrame(
                    pd.concat([merged_df, geodf], ignore_index=True)
                )
            # If an error was encountered creating dataframe.
            else:
                # Set error boolean to True to return error to calling method.
                encountered_error = True

        # Return the combined dataframe.
        return merged_df, encountered_error

    def create_region_shapefile(self, area_code):
        """
        Function to create a shapefile for an individual region in the dataset.


        Parameters
        ----------
        area_code: string
            The 'Area Code' for the region whose data has been collected.

        Returns
        -------
        True/False: Boolean
            A positive or negative boolean value indicating that an error
            was/wasn't (respectively) encountered.
        """

        # Check that the shapefiles directory exists before attempting to save
        # files, in order to prevent an error.
        self.error_prevention_directory_check()

        # Create the dataframe for the region
        geodataframe, was_error = self.create_region_geodf(area_code)

        # If no error was encountered creating the dataframe
        if not was_error:
            # Set the output path for the region shapefile
            outfp = f"{self.directory_name}/{area_code}_shapefile.shp"
            # Create the shapefile
            geodataframe.to_file(outfp)
            return False
        # If an error was encountered creating the dataframe
        else:
            print("Error creating region shapefile")
            return True

    def create_region_geodf(self, area_code):
        """
        Function to create geopandas dataframe for an individual region.


        Parameters
        ----------
        area_code: string
            The 'Area Code' for the region whose data has been collected.

        Returns
        -------
        True/False: Boolean
            A positive or negative boolean value indicating that an error
            was/wasn't (respectively) encountered.
        """

        # Get the polygon coordinates data from the API request
        geoshape, was_error = \
            self.get_geoshape_info_from_api_request_for_areacode(
            area_code
        )

        # If no error encountered requesting API data
        if not was_error:
            # Convert the API data to usable coordinates
            polygon_coordinates = \
                self.convert_geoshape_to_polygon_coordinates(geoshape)
            # Create a geopandas dataframe using the cooridnates for the region
            geodataframe = \
                self.create_geodataframe_with_area_data(polygon_coordinates)
            # Return the created dataframe, and a False to indicate no errors. 
            return geodataframe, False

        # If an error is encountered when requesting data.
        else:
            # Indicate error to the user.
            print("Error creating region geopandas dataframe: API req failed")
            # Return empty dataframe, and a positive boolean to indicate an
            # error was encountered.
            return gpd.GeoDataFrame(), True

    def get_geoshape_info_from_api_request_for_areacode(self, area_code):
        """
        Function to make the API GET request, handle API response, process JSON,
        and parse out and return the polygon coordinates.

        The API provides access to a geographical repository maintained by
        Opendatasoft about regions.
        Available: https://public.opendatasoft.com/explore/dataset/georef-united-kingdom-region/information/
        The dataset contains coordinate data that can be used to render polygons
        of the region.

        Parameters
        ----------
        area_code: string
            The 'Area Code' for the region whose data has been collected.

        Returns
        -------
        shape_info: string
            A string representation of a list of coordinates describing indexes
            in polygons
        True/False: Boolean
            A positive or negative boolean value indicating that an error
            was/wasn't (respectively) encountered.
        """

        # Create the API GET request for the specified region.
        api_str = f"https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-united-kingdom-region&q=rgn_code={area_code}"

        # Process API GET request and store response from server.
        response = requests.get(api_str)

        # If API request fails
        if response.status_code != 200:
            # Return empty string as request faied, along with positive boolean
            # to indicate there was error to abort further processing attempts.
            return str(), True

        # Collect the JSON response from the API.
        json_response = response.json()

        # Check number of matches for API query - if zero matches, return an
        # error as it failed to find the area.
        if json_response["nhits"] == 0:
            # Return empty string as request faied, along with positive boolean
            # to indicate there was error to abort further processing attempts.
            return str(), True

        # Retrieve the polygon coordinates data string from the JSON response.
        shape_info = str(
            json_response["records"][0]["fields"]["geo_shape"]["coordinates"]
        )
        # Return the coordinate information and negative boolean to indicate no
        # errors encountered.
        return shape_info, False

    def recursive_check_for_polygon_coords(self, parent_lst):
        """
        Function to recursively traverse a list that contains sublists, in order
        to identify the polygon coordinates.

        Parameters
        ----------
        parent_lst: list
            The current 'top-level' list, to be searched for sublists and
            coordinates.

        Returns
        -------
        temp_polygon_coords: list
            A list of collected coordinates.
        """

        # Initialise an empty list to hold polygon coordinates
        temp_polygon_coords = []

        # If the current list has more than one element
        if len(parent_lst) > 1:
            # Iterate through each element in the list
            for child in parent_lst:
                # Recursive call of the method to search the current elements
                # sublist for cooridnates.
                child_poly_coords = \
                    self.recursive_check_for_polygon_coords(child)
                # For each returned polygon outline from the recursive call
                for coords in child_poly_coords:
                    # Add the coordinates to the list of coordinates to be
                    # returned by the acting 'parent' list.
                    temp_polygon_coords.append(coords)
        # If the current list has only one element - identified polygon
        # coordinates.
        else:
            # Retrieve the coordinates and add them to the cooridnates list to
            # be returned.
            temp_polygon_coords.append(parent_lst[0])

        # Return the collected cooridnates.
        return temp_polygon_coords

    def convert_geoshape_to_polygon_coordinates(self, shape_data):
        """
        Function to convert the string representation of a coordinates list into
        a list compatible with shapely.

        Parameters
        ----------
        shape_data: string
            The string representation of a list of coordinates.

        Returns
        -------
        poly_coords: list
            A list of coordinates that can be used with shapely to initialise
            polygons.
        """

        # Convert the string representation of the coordinates list to a list
        # data type.
        coordinates_lst = ast.literal_eval(shape_data)

        # Recursively traverse the cooridnates list to create polygon
        # cooridnates compatible with Shapely.
        poly_coords = self.recursive_check_for_polygon_coords(coordinates_lst)

        # Return the polygon coordinates.
        return poly_coords

    def create_geodataframe_with_area_data(self, poly_coords):
        """
        Function to create and populate a geopandas dataframe for the region
        using the coordinates list.

        Parameters
        ----------
        poly_coords: list
            A list of coordinates that can be used with shapely to initialise
            polygons.

        Returns
        -------
        newdata: geopandas dataframe
            A dataframe containing polygon data, screening uptake data, and area
            codes.
        """

        # Create a geopandas dataframe for the region using provided polygon
        # coordinates.
        newdata = gpd.GeoDataFrame()

        newdata["geometry"] = None

        # Initialise an empty list to hold the encompassed polygons.
        polygons_lst = []

        # Iterate through each set of coordinates.
        for i in range(len(poly_coords)):
            # Create a Shapely Polygon using the current set of coordinates.
            poly = Polygon(poly_coords[i])
            # Add the created polygon to the list of polygons for this region.
            polygons_lst.append(poly)

            # Insert the polygon in the 'geometry' column of the dataframe.
            newdata.loc[i, "geometry"] = poly

            # Retrieve 'Value' cell data for the row in the dataframe that
            # macthes the current 'Area Code'.
            val = self.regions_df.loc[
                self.regions_df["Area Code"] == self.current_area_code, "Value"
            ].values[0]
            newdata.loc[i, "value"] = val

            # Add the current 'Area Code' to the dataframe entry
            newdata.loc[i, "area_code"] = self.current_area_code

            # Add the current 'Area Name' to the dataframe entry
            rgn_name = self.regions_df.loc[
                self.regions_df["Area Code"] == \
                    self.current_area_code, "Area Name"
            ].values[0]
            newdata.loc[i, "area_name"] = rgn_name.replace(" region", "")

            # Add the initial year to the dataframe
            newdata.loc[i, "year"] = 2016

        # Correct the projection settings
        newdata.crs = from_epsg(4326)

        # Return the dataframe
        return newdata

    def get_all_regions(self):
        """
        Function to create a pandas dataframe containing only the nine regions
        in the dataset for a given year.

        Parameters
        ----------
        None

        Returns
        -------
        filtered_regions_df: Pandas dataframe
            A dataframe containing only region data, for all years

        year_regions_df: Pandas dataframe
            A dataframe containing only region data, for a specified year
        """

        # Filter the dataframe to only include regions
        filtered_regions_df = self.init_df[self.init_df["Area Type"] == \
            "Region"]
        # Copy the dataframe to another, for a year specific dataframe
        year_regions_df = filtered_regions_df.copy(deep=True)
        # Filter the updated dataframe to only include entries for one year
        year_regions_df = year_regions_df[year_regions_df["Time period"] == \
            2016]
        # Return the two filtered dataframes
        return filtered_regions_df, year_regions_df


class LondonMap:
    """
    Plots and saves a London map displaying the screening uptake by boroughs.

    Parameters:
    df (pandas DataFrame): DataFrame with local authority codes and screening
    uptake values.
    time_period (int): Year of interest
    val_labels(bool): Set to True to add Annotation to map of % uptakes

    Returns:
    None
    """

    def __init__(self, df, time_period=int, val_labels=bool):
        self.df = df
        self.time_period = time_period
        self.val_labels = val_labels

    def plot_london_map(self, colour_palette="blue"):
        filepath = os.path.join(
            package_dir, "shape_files", "London_Borough_Excluding_MHW.shp"
        )
        loc_auth = gpd.read_file(filepath)

        # Define Time-periods
        if self.time_period == 2010:
            self.df = self.df.loc[self.df["Time period"] == 2010]
        elif self.time_period == 2011:
            self.df = self.df.loc[self.df["Time period"] == 2011]
        elif self.time_period == 2012:
            self.df = self.df.loc[self.df["Time period"] == 2012]
        elif self.time_period == 2013:
            self.df = self.df.loc[self.df["Time period"] == 2013]
        elif self.time_period == 2014:
            self.df = self.df.loc[self.df["Time period"] == 2014]
        elif self.time_period == 2015:
            self.df = self.df.loc[self.df["Time period"] == 2015]
        elif self.time_period == 2016:
            self.df = self.df.loc[self.df["Time period"] == 2016]
        else:
            mean_values = self.df.groupby("Area Name")["Value"].mean().to_dict()
            self.df["Value"] = self.df["Area Name"].map(mean_values)

        # Merge shapefile with dataset
        ldn_map = loc_auth.merge(self.df, left_on="GSS_CODE",
        right_on="Area Code")

        # Set figure size
        plt.figure(figsize=(20, 10))

        if colour_palette == "blue":
            cmap = LinearSegmentedColormap.from_list(
                "mycmap", ["#FFFFFF", "#0F2B7F", "#0078B4"]
            )
        elif colour_palette == "green":
            cmap = LinearSegmentedColormap.from_list(
                "mycmap", ["#FFFFFF", "#FEFCCA", "#A2BD3F"]
            )
        elif colour_palette == "fire":
            cmap = LinearSegmentedColormap.from_list(
                "mycmap", ["#FFFFFF", "#FF0000", "#FFFF00"]
            )

        # Plot map
        ldn_map.plot(column="Value", cmap=cmap, legend=True, figsize=(50, 30))

        # Add local authority labels
        if type(self.time_period) == int:
            plt.title(
                f"UK Screening Uptake by London Borough in {self.time_period}",
                fontsize=50,
            )
            for idx, row in ldn_map.iterrows():
                plt.annotate(
                    row["Area Name"],
                    xy=(row["geometry"].centroid.x, row["geometry"].centroid.y),
                    horizontalalignment="center",
                    fontsize=20,
                )
                plt.annotate(
                    str(round(row["Value"], 1)), xy=(row["geometry"].centroid.x, 
                    row["geometry"].centroid.y - 700),
                    horizontalalignment="right", fontsize=20,
                )
        else:
            plt.title(f"UK Screening Uptake by London Borough Means",
            fontsize=50)
            for idx, row in ldn_map.iterrows():
                plt.annotate(
                    row["Area Name"], xy=(row["geometry"].centroid.x,
                    row["geometry"].centroid.y),
                    horizontalalignment="center", fontsize=20,
                )
                if self.val_labels == True:
                    plt.annotate(
                        str(round(row["Value"], 1)),
                        xy=(
                            row["geometry"].centroid.x,
                            row["geometry"].centroid.y - 700,
                        ),
                        horizontalalignment="right",
                        fontsize=20,
                    )
        plt.show()
        plt.close()

        return None


class Rank_Based_Graph:
    '''
    Plots animated graphs, which demonstrate the ranking of the chosen areas or
    regions by the proportion of people screened. 
    Two types of animated graphs available: bar, scatter. 
    
    Attributes:
    -----------
    df: pandas DataFrame
        input data frame to be plotted.
    Methods:
    -------
    list_areas() - lists all areas in the chosen area type: LA, UA, Region.
    clean_rank() - wrangles dataset for plotting.
    color_pal() - allows choice of sns colour palette.
    animated_bars() - plots comparison plot of the ranking of chosen regions.
    animated_scatter() - plots comparison plot of the ranking of chosen regions.

    '''
    def __init__(self, df):
        self.df = df

    def list_areas(self, area_type="Region"):
        """
        Prints available areas based on the area type chosen.
        Parameters:
        ----------
        area_type: str
            either a "Region", "UA, or "LA", default = "Region"
        Return:
        ar_lst: lst of str
            list of areas in the chosen area type.
        """
        # Slicing the dataframe:
        self.df = self.df[self.df["Area Type"] == area_type]
        # Creating a list of area names
        ar_lst = [*set(self.df["Area Name"])]
        print(ar_lst)

    def clean_rank(
        self,
        list_reg=["East of England region", "London region",
        "South East region"],
        area_type="Region",
    ):
        """
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
        """
        # Selects areas we want to compare
        self.df = self.df[self.df["Area Type"] == area_type]
        # Selects which regions to compare
        df_select = self.df[self.df["Area Name"].isin(list_reg)]
        # Changing the data type into string:
        df_select = df_select.astype({"Area Name": str})
        df_select.reset_index(inplace=True)
        # Drops the index column, if one is present.
        if "index" in df_select.columns:
            df_year = df_select.drop(columns=["index"])

        # Splitting data into dfs by the year and ranking based on Value.
        keep = []
        years = list(set(df_year["Time period"]))
        years
        for i in years:
            df = df_year.loc[df_year["Time period"] == i]
            order = df["Value"].rank(ascending=0)
            df["rank"] = [int(i) for i in order]
            keep.append(df)
        # Combining all the dfs and sorting based on name and year.
        df_year = pd.concat(keep)
        df_year.sort_values(
            ["Area Name", "Time period"],
            ascending=True,
            inplace=True,
            ignore_index=True,
        )
        return df_year

    def color_pal(self, df_clean, sns_palette="Spectral"):
        """
        Takes a clean dataframe and adds colours based on areas included.
        Parameters:
        ----------
        df_clean: pandas DataFrame
            dafaframe prepared with clean_rank function
        sns_palette: str
            name of the palette to be used, found on:
            https://seaborn.pydata.org/tutorial/color_palettes.html
        """
        # color palette
        area_name = list(set(df_clean["Area Name"]))
        pal = list(
            sns.color_palette(palette=sns_palette, 
            n_colors=len(area_name)).as_hex()
        )
        dict_color = dict(zip(area_name, pal))
        return dict_color

    def animated_bars(
        self,
        area_type="LA",
        list_reg=[],
        sns_palette="Spectral",
        width=800,
        height=600,
        showlegend=False,
        rank_text_size=16,
        open=False,
    ):
        """
        Utilises other functions in class Rank_Based_Graph to clean dataframe,
        select colour palette and plot an animated bar chart, of chosen areas'
        rank change over time.
        Parameters:
        ----------
        area_type: str
            can be "Region", "UA", or "LA", default "Region"
        list_reg: lst
            list of region names to be compared over time, deault: all
            list_areas() function can be used to see options
        sns_palette: str
            name of seaborn palette to be used
            https://seaborn.pydata.org/tutorial/color_palettes.html
        width: int
            width of the graph in pixels, default 800
        height: int
            height of the graph in pixels, default 600
        showlegend: bool
            if True, adds a legend of the areas, default False
        rank_text_size: int

        """
        df_cleaned = self.clean_rank(list_reg=list_reg, area_type=area_type)
        dict_color = self.color_pal(df_cleaned, sns_palette=sns_palette)
        fig = px.bar(
            df_cleaned,
            x="Area Name",
            y="Value",
            color="Area Name",
            text="rank",
            color_discrete_map=dict_color,
            animation_frame="Time period",
            animation_group="Area Name",
            range_y=[50, 90],
            labels={"Value": "Proportion Screened, %"},
        )
        fig.update_layout(
            width=width,
            height=height,
            showlegend=showlegend,
            xaxis=dict(tickmode="linear", dtick=1),
        )
        fig.update_traces(textfont_size=rank_text_size, textangle=0)
        pyo.plot(fig, filename="plots/animated_rank_from_list.html",
        auto_open=open)
        pyo.iplot(fig)

    def animated_scatter(
        self,
        area_type="LA",
        list_reg=[
            "Tendring",
            "Rossendale",
            "Bromsgrove",
            "Wyre",
            "Dartford",
            "East Staffordshire",
        ],
        sns_palette="Spectral",
        width=1000,
        height=600,
        showlegend=False,
        rank_text_size=16,
    ):
        """
        Utilises other functions in class Rank_Based_Graph to clean dataframe,
        select colour palette and plot an animated scatter plot, of chosen
        areas' rank change over time.
        Parameters:
        ----------
        area_type: str
            can be "Region", "UA", or "LA", default "Region"
        list_reg: lst
            list of region names to be compared over time, deault: all
            list_areas() function can be used to see options
        sns_palette: str
            name of seaborn palette to be used
            https://seaborn.pydata.org/tutorial/color_palettes.html
        width: int
            width of the graph in pixels, default 800
        height: int
            height of the graph in pixels, default 600
        showlegend: bool
            if True, adds a legend of the areas, default False
        rank_text_size: int

        """
        df_cleaned = self.clean_rank(list_reg=list_reg, area_type=area_type)
        area_color = self.color_pal(df_cleaned, sns_palette=sns_palette)
        years = list(set(self.df["Time period"]))
        years.sort()

        df_cleaned["Position"] = [years.index(i) \
            for i in df_cleaned["Time period"]]
        df_cleaned["Val_str"] = [str(round(i, 2)) \
            for i in df_cleaned["Value"]]
        df_cleaned["Val_text"] = [str(round(i, 2)) + " %" \
            for i in df_cleaned["Value"]]
        fig = px.scatter(
            df_cleaned,
            x="Position",
            y="rank",
            size="Value",
            color="Area Name",
            text="Val_text",
            color_discrete_map=area_color,
            animation_frame="Time period",
            animation_group="Area Name",
            range_x=[-2, len(years)],
            range_y=[0.5, 6.5],
        )
        fig.update_xaxes(title="", visible=False)
        fig.update_yaxes(
            autorange="reversed", title="Rank", visible=True, 
            showticklabels=True
        )
        fig.update_layout(
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True), width=width,
            height=height,
        )
        fig.update_traces(textposition="middle left")
        fig.show()


def visualise_rank(
    area_type="LA",
    list_reg=[
        "Tendring",
        "Rossendale",
        "Bromsgrove",
        "Wyre",
        "Dartford",
        "East Staffordshire",
    ],
    sns_palette="Spectral",
    width=800,
    height=600,
    showlegend=False,
    rank_text_size=16,
):
    import datasets as ds

    df = ds.load_cerv()
    Rank_Based_Graph(df).animated_scatter(
        area_type=area_type,
        list_reg=list_reg,
        sns_palette=sns_palette,
        width=width,
        height=height,
        showlegend=showlegend,
        rank_text_size=rank_text_size,
    )
    Rank_Based_Graph(df).animated_bars(
        area_type=area_type,
        list_reg=list_reg,
        sns_palette=sns_palette,
        width=width,
        height=height,
        showlegend=showlegend,
        rank_text_size=rank_text_size,
    )
    plt.show()


class Analysis_Plot:
    def __init__(self, in_dimensions, title, x_label, y_label, show_legend):
        self.dimensions = in_dimensions
        self.fig = plt.figure(
            figsize=(self.dimensions[0], self.dimensions[1]),
            facecolor=("#D3D3D3")
        )
        self.ax = self.fig.add_subplot()
        self.legend_visible = show_legend

        self.ax.set_title(title)

        self.ax.set_xlabel(x_label, fontsize=12)
        self.ax.set_ylabel(y_label, fontsize=12)
        self.ax.tick_params(axis="both", labelsize=12)

        self.ax.grid(linestyle="--")

        self.ax.set_facecolor((0.075, 0.075, 0.075))

        self.ax.legend().set_visible(show_legend)

    def update_legend(self):
        if self.legend_visible:
            self.ax.legend()


class Country_Analysis(DataframePreprocessing):
    """
    Class to analyse overall country trends in the datasets and create line
    plots to visualise the trends. Provides visualisation tools and analysis
    methods.

    This class inherits from the 'Dataframe_preprocessing' class, and therefore
    shares all its methods.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    def __init__(self):
        super().__init__()

        # Clean the dataframe, removing redundant columns, for processing
        self.clean_df = self.clean_data_for_country_analysis(self.processed_df)

        # Create and display a line plot to visualise the data
        self.plot_value_across_years()

        # Get the year with the highest uptake
        highest_year = self.get_year_with_highest_val()
        print(f"highest_year = {highest_year}")

        # Get the year with the lowest uptake
        lowest_year = self.get_year_with_lowest_val()
        print(f"lowest_year = {lowest_year}")

    def clean_data_for_country_analysis(self, in_df):
        """
        Function to clean the dataframe, filtering the dataframe and removing
        redundant columns, for further processing.

        Parameters
        ----------
        in_df: Pandas dataframe
            The dataframe to be cleaned. The expected dataframe contains a
            variety of columns that are not required for these analysis
            functions or plots (such as 'Area Name').

        Returns
        -------
        filtered_df: Pandas dataframe
            The cleaned dataframe. This is a filtered version of the initial
            dataset, with only the necessary columns.
        """

        # Filter the dataframe the only contain entries that have the
        # 'Area Type' of 'Country'.
        filtered_df = in_df[in_df["Area Type"] == "Country"]
        # Filter the dataframe to only contain entries that have a null
        # 'Value note'.
        filtered_df = filtered_df[filtered_df["Value note"].isnull()]
        # Filter the dataframe to only contain entries that have a null
        # 'Category'.
        filtered_df = filtered_df[filtered_df["Category"].isnull()]

        # Remove redundant columns from the dataframe
        filtered_df = filtered_df.drop(labels=["Area Name"], axis=1)
        filtered_df = filtered_df.drop(labels=["Area Code"], axis=1)
        filtered_df = filtered_df.drop(labels=["Area Type"], axis=1)
        filtered_df = filtered_df.drop(labels=["Value note"], axis=1)
        filtered_df = filtered_df.drop(labels=["Category"], axis=1)
        filtered_df = filtered_df.drop(labels=["Category Type"], axis=1)

        # Rename the 'Time period' column for improved readability and
        # accessibility.
        filtered_df.rename(columns={"Time period": "year"}, inplace=True)

        # Change the datatype of the 'year' column to integer to reduce storage
        # requirements.
        filtered_df = filtered_df.astype({"year": np.int32})

        # Set the dataframe index to the 'year' column as this is now a uniqu
        # identifier.
        filtered_df.set_index("year", inplace=True)

        # Return the cleaned dataframe
        return filtered_df

    def get_year_with_highest_val(self):
        """
        Function to identify from the data, and return, the year in which the
        uptake in screening was at its highest.

        Parameters
        ----------
        None

        Returns
        -------
        self.clean_df['Value'].idxmax(): int
            The index of the row in the dataframe that has the highest entry in
            the 'Value' column; where the index of the dataframe is the 'year'
            column, therefore, the returned index is the year.
        """
        # Return the index of the row in the dataframe that has the highest
        # entry in the 'Value' column
        return self.clean_df["Value"].idxmax()

    def get_year_with_lowest_val(self):
        """
        Function to identify from the data, and return, the year in which the
        uptake in screening was at its lowest.

        Parameters
        ----------
        None

        Returns
        -------
        self.clean_df['Value'].idxmin(): int
            The index of the row in the dataframe that has the lowest entry in
            the 'Value' column; where the index of the dataframe is the 'year'
            column, therefore, the returned index is the year.
        """
        # Return the index of the row in the dataframe that has the lowest entry
        # in the 'Value' column
        return self.clean_df["Value"].idxmin()

    def plot_value_across_years(self):
        """
        Function to plot the change in 'Value' for each year in the dataframe.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Set the title for the plot
        plot_title = "How 'Value' for England has changed between 2010 and \
            2016 for Cervical Cancer Screening Uptake (%)\n"
        # Set the label for the x-axis of the plot
        x_label = "Year"
        # Set the label for the y-axis of the plot
        y_label = "Value"

        # Create an instance of 'Analysis_Plot' to create a figure for plotting
        plot = Analysis_Plot([8, 4], plot_title, x_label, y_label, False)

        # Add the data to the created figure
        plot.ax.plot(self.clean_df["Value"], "co-", label="England")

        # Update the legend settings: as 'show_legend' is set to False, it won't
        # show legend
        plot.update_legend()

        # Display the plot
        plt.show()

    def lineplot_cancer_England(
        self, cervical_df=load_cerv(), breast_df=load_breast(), 
        bowel_df=load_bowel()
    ):
        """
        This function takes in three dataframes from the default datasets
        provided:
        one for cervical cancer,
        one for breast cancer and one for bowel cancer,
        and produces a lineplot which shows the mean value of the cervical,
        breast and bowel cancer datasets over 2010-2016 for only the England
        area.

        Parameters:
        cervical_df (pd.DataFrame): A dataframe containing cervical cancer data
        breast_df (pd.DataFrame): A dataframe containing breast cancer data
        bowel_df (pd.DataFrame): A dataframe containing bowel cancer data

        Returns:
        None
        """

        # Get the mean value for the cervical, breast and bowel cancer datasets
        # where Area Name = England
        cervical_mean = (
            cervical_df[cervical_df["Area Name"] == "England"]
            .groupby("Time period")
            .mean()["Value"]
        )
        breast_mean = (
            breast_df[breast_df["Area Name"] == "England"]
            .groupby("Time period")
            .mean()["Value"]
        )
        bowel_mean = (
            bowel_df[bowel_df["Area Name"] == "England"]
            .groupby("Time period")
            .mean()["Value"]
        )

        plot = Analysis_Plot(
            [8, 4],
            "Screening programme uptake means in England across 2010-2016",
            "Year",
            "Percentage Uptake (%)",
            False,
        )

        # Plot the means for the three datasets over 2010-2016
        plt.plot(cervical_mean, label="Cervical Cancer")
        plt.plot(breast_mean, label="Breast Cancer")
        plt.plot(bowel_mean, label="Bowel Cancer")
        plt.legend()

        plt.plot(
            cervical_mean.index,
            cervical_mean.values,
            "x",
            markersize=5,
            color="white",
            label="Cervical Cancer",
        )
        plt.plot(
            breast_mean.index,
            breast_mean.values,
            "x",
            markersize=5,
            color="white",
            label="Breast Cancer",
        )
        plt.plot(
            bowel_mean.index,
            bowel_mean.values,
            "x",
            markersize=5,
            color="white",
            label="Bowel Cancer",
        )
        plt.gcf().set_size_inches(13, 8)
        plt.gcf().set_dpi(150)

        plt.show()
