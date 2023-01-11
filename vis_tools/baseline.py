'''
Tools for simple descriptive visualisations of screening data.

These tools might be useful to gain a better understanding of the statistical
properties of the dataset at hand. 

Carry last value forward across forecast horizon (random walk)

SNaive:
    Carry forward value from last seasonal period

Average: np.sqrt(((h - 1) / self._period).astype(np.int)+1)
    Carry forward average of observations

Drift:
    Carry forward last time period, but allow for upwards/downwards drift.

EnsembleNaive:
    An unweighted average of all of the Naive forecasting methods.
'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os 

# from vis_tools import datasets as ds

def basic_data_cleaning(df, age=True, sex=True, deprivation=False):
    """
    Function for basic data cleaning of an NHS screening uptake dataset.
    It is possible to choose if to include age, sex and deprivation status. 

    Parameters
    ----------
    df: pandas DataFrame
        DataFrame containing the data to be explored.
    age: bool
        If True, then includes age information
    sex: bool
        If True, then includes sex information
    deprivation: bool
        If True, then includes "Category type" and "Category columns", which
        describe deprivation groups. 
    Returns
    -------
    df: pandas DataFrame
        cleaned dataframe    
    """
    # Fill NaNs
    df['Category Type'].fillna('NA', inplace=True)
    
    # Dropping "Cl_L3_..." values representing types of areas.
    df = df[df['Area Code'].str.contains('E')]
    # Columns we want to keep. 
    keep_col = ['Area Code', 'Area Name', 'Area Type', 'Time period', 'Value']

    if deprivation==True:
        df = df[df['Category Type'].str.contains('deprivation deciles in England')]
    else:
        if age == True:
            keep_col.append('Age')
        if sex == True:
            keep_col.append('Sex')

    # Remove Unnecessary Columns
    df = df[keep_col]
    return df

class Analysis_Plot:
    
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.ax.tick_params(axis='both', labelsize=12)
        self.ax.grid(linestyle='--')

    def title(self, title, fontsize):
        self.ax.set_title(title).set_fontsize(fontsize)

    def x_label(self, x_label):
        self.ax.set_xlabel(x_label, fontsize=12)
    
    def y_label(self, y_label):
        self.ax.set_ylabel(y_label, fontsize=12)

    def fontsize(self, fontsize):
        self.ax.xaxis.label.set_size(fontsize)
        self.ax.yaxis.label.set_size(fontsize)
    
    def legend(self, include_leg):
        if include_leg:
            self.ax.legend()
    
    def figure_size(self, figsize):
        self.fig.set_size_inches(figsize)
    
    def adjust_fig(self, title="Plot", x_label="X", y_label="Y", fontsize=12, include_leg=True, figsize=(8,5)):
        self.title(title, fontsize)
        self.x_label(x_label)
        self.y_label(y_label)
        self.fontsize(fontsize)
        self.legend(include_leg)
        self.figure_size(figsize)

# Histogram of any float values:
def hist(df, col, title="Plot", x_label="X", y_label="Y", fontsize=12, include_leg=False, figsize=(8,5)):
    plot_o = Analysis_Plot()
    plot_o.adjust_fig(title=title, x_label=x_label, y_label=y_label, fontsize=fontsize, include_leg=include_leg, figsize=figsize)
    _=plot_o.ax.hist(df[col])
    plt.show()

def clean_data_for_area_analysis(df, area_name):
    df = df[df['Area Name'] == area_name]
    keep = ['Time period', 'Value']
    df = df[keep]
    df.rename(columns={'Time period':'year'}, inplace=True)
    # set index to year
    df.set_index('year', inplace=True)
    return df

# can plot area, or region data over time. 
def area_analysis(in_df, area_name, fontsize=12, include_leg=True, figsize=(8,5)):
    in_df = clean_data_for_area_analysis(in_df, area_name)
    title = f"{area_name} Screening Coverage Over the Years"
    x_label = 'Year'
    y_label = 'Value'
    plot = Analysis_Plot()
    plot.adjust_fig(title=title, x_label=x_label, y_label=y_label, fontsize=fontsize, include_leg=include_leg, figsize=figsize)
    plot.ax.plot(in_df['Value'], 'co-', label=area_name)
    plt.show()

def linear_comp(df, area_list, title="Plot", fontsize=12, include_leg=True, figsize=(8,5)):
    '''
    Function takes a list of area names and provides a comparison linear graph
    of how screening rates changed in the chosen areas.
    Parameters:
    ----------
    df: pandas DataFrame
        data set
    area_list: lst of str
        a list of area names
    title: str
        title of the graph
    fontsize: int
        size of the axes font
    include_leg: bool
        if true includes the legend in the graph
    figsize: touple
        size of the graph in inches
    '''
    plot_o = Analysis_Plot()
    y_label = "Proportion Screened, %"
    x_label="Years"
    for i in area_list:
        print(i)
        df1 = df.loc[df['Area Name']==i]
        plt.plot(df1['Time period'], df1['Value'], label=i)
    plot_o.adjust_fig(title=title, x_label=x_label, y_label=y_label, fontsize=fontsize, include_leg=include_leg, figsize=figsize)
    plt.show()

