#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 16:12:17 2023

@author: alistair
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data_str = 'https://data.england.nhs.uk/dataset/dbf14bed-85bc-4aef-856c-38eb9d6de730/resource/e281a471-f546-44b9-99f1-12e80b27a638/download/220iicancerscreeningcoveragecervicalcancer.data.csv'

# read url file into a dataframe
df = pd.read_csv(data_str)

# use dark style for plots
plt.style.use('dark_background')



class Analysis_Plot:
    
    def __init__(self, in_dimensions, title, x_label, y_label, show_legend):
        self.dimensions = in_dimensions
        self.fig = plt.figure(figsize=(self.dimensions[0], self.dimensions[1]), facecolor=(0.075, 0.075, 0.075))
        self.ax = self.fig.add_subplot()
        self.legend_visible = show_legend
        
        self.ax.set_title(title)
        
        self.ax.set_xlabel(x_label, fontsize=12)
        self.ax.set_ylabel(y_label, fontsize=12)
        self.ax.tick_params(axis='both', labelsize=12)
        
        self.ax.grid(linestyle='--')
        
        self.ax.set_facecolor((0.075, 0.075, 0.075))
        
        self.ax.legend().set_visible(show_legend)
        
        
    def update_legend(self):
        if self.legend_visible:
            self.ax.legend()
            
            
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
        
        
# get statistics for country as a whole (class inherits from Dataframe_preprocessing)
class Country_Analysis(Dataframe_preprocessing):
    
    def __init__(self, init_df):
        super().__init__(init_df)
        
        self.clean_df = self.clean_data_for_country_analysis(self.processed_df)
        
        # save data for testing
        #self.clean_df.to_csv('country_data.csv')
        self.plot_value_across_years()
        
        highest_year = self.get_year_with_highest_val()
        print(f'highest_year = {highest_year}')
        
        lowest_year = self.get_year_with_lowest_val()
        print(f'lowest_year = {lowest_year}')
        
    def clean_data_for_country_analysis(self, in_df):
        filtered_df = in_df[in_df['Area Type'] == 'Country']
        filtered_df = filtered_df[filtered_df['Value note'].isnull()]
        filtered_df = filtered_df[filtered_df['Category'].isnull()]
        
        filtered_df = filtered_df.drop(labels=['Area Name'], axis=1)
        filtered_df = filtered_df.drop(labels=['Area Code'], axis=1)
        filtered_df = filtered_df.drop(labels=['Area Type'], axis=1)
        filtered_df = filtered_df.drop(labels=['Value note'], axis=1)
        filtered_df = filtered_df.drop(labels=['Category'], axis=1)
        filtered_df = filtered_df.drop(labels=['Category Type'], axis=1)
        
                        
        filtered_df.rename(columns={'Time period':'year'}, inplace=True)
        
        # set index to year
        filtered_df.set_index('year', inplace=True)
        
        return filtered_df
    
    def get_year_with_highest_val(self):
        return self.clean_df['Value'].idxmax()
    
    def get_year_with_lowest_val(self):
        return self.clean_df['Value'].idxmin()
    
    def plot_value_across_years(self):
        plot_title = 'How \'Value\' for England has changed between 2010 and 2016\n'
        x_label = 'Year'
        y_label = 'Value'

        plot = Analysis_Plot([8, 4], plot_title, x_label, y_label, False)
        
        plot.ax.plot(self.clean_df['Value'], 'co-', label='England')
                
        # as 'show_legend' set to False, won't show legend
        plot.update_legend()
        
        plt.show()
        

country_test = Country_Analysis(df)
        
        
        