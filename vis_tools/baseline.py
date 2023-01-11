'''
Tools for simple descriptive visualisations of screening data.

These tools might be useful to gain a better understanding of the statistical
properties of the dataset at hand. 

Analysis_Plot:
    Provides customisability to the graphs.

histogram():
    Plots a histogram of the chosen float column.

area_analysis():
    Allows the user to choose an area and graph its proportion of patients
    screened over time.

linear_comp:
    Allows the user to choose areas to compare in an over the time analysis.
'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Analysis_Plot:
    '''
    Creates an empty matplotlib.pyplot figure as an object.
    Atributes:
    ----------
    fig
    ax
    Methods:
    --------
    title(title, fontsize)
    x_label(x_label)
    y_label(y_label)
    fontsize(fontsize)
    legend(include_leg)
    figure_size(figsize)
    '''
    def __init__(self):
        '''
        Constructs an empty matplotlib.pyplot figure.
        Parameters:
        ----------
        fig: object
            figure
        ax: object
            ax
        '''
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        self.ax.tick_params(axis='both', labelsize=12)
        self.ax.grid(linestyle='--')

    def title(self, title, fontsize=12):
        '''
        Adds title and changes its fontsize.
        Parameters:
        ----------
        title: str
            title of the graph
        fontsize: int
            size of font for title
        '''
        self.ax.set_title(title).set_fontsize(fontsize)

    def x_label(self, x_label):
        '''
        Adds a chosen label to the x axis.
        Parameters:
        ----------
        x_label: str
            chosen label for x axis
        '''
        self.ax.set_xlabel(x_label, fontsize=12)
    
    def y_label(self, y_label):
        '''
        Adds a chosen label to the y axis.
        Parameters:
        ----------
        y_label: str
            chosen label for x axis
        '''
        self.ax.set_ylabel(y_label, fontsize=12)

    def fontsize(self, fontsize):
        '''
        Changes the fontsize of the axis labels after the figure is already
        created.
        Parameters:
        ----------
        fontsize:
            size of the font for the axis labels
        '''
        self.ax.xaxis.label.set_size(fontsize)
        self.ax.yaxis.label.set_size(fontsize)
    
    def legend(self, include_leg):
        '''
        Adds a legend to the graph.
        Parameters:
        ----------
        include_leg: bool
            If True, includes the legend
        '''
        if include_leg:
            self.ax.legend()
    
    def figure_size(self, figsize):
        '''
        Allows the user to choose figure size.
        Parameters:
        ----------
        figsize: touple
            size of the figure in inches (width, height)
        '''
        self.fig.set_size_inches(figsize)
    
    def adjust_fig(self, title="Plot", x_label="X", y_label="Y", fontsize=12,
                  include_leg=True, figsize=(8,5)):
        '''
        Combines other figure customisation functions to ajust figure
        parameters at once.
        Parameters:
        ----------
        title: str
            the title of the plot, default="Plot"
        x_label: str
            name of X axis on the plot, default="X"
        y_label: str
            name of the Y axis on the plot, default="Y"
        fontsize: int
            size of the font, default=12
        include_leg: bool
            if True includes legend, default=True
        figsize: touple
            size of the figure in inches (width, height), default=(8,5)
        '''
        self.title(title, fontsize)
        self.x_label(x_label)
        self.y_label(y_label)
        self.fontsize(fontsize)
        self.legend(include_leg)
        self.figure_size(figsize)

# Histogram of any float values:
def hist(df, col, title="Plot", x_label="X", y_label="Y", fontsize=12,
        include_leg=False, figsize=(8,5)):
    '''
    Plots an customised histogram.
    Parameters:
    ----------
    df: pandas DataFrame
        dataframe containing the column user wishes to plot
    col: str
        name of the column to be plotted
    title: str
        the title of the plot, default="Plot"
    x_label: str
        name of X axis on the plot, default="X"
    y_label: str
        name of the Y axis on the plot, default="Y"
    fontsize: int
        size of the font, default=12
    include_leg: bool
        if True includes legend, default=True
    figsize: touple
        size of the figure in inches (width, height), default=(8,5)
    '''
    plot_o = Analysis_Plot()
    plot_o.adjust_fig(title=title, x_label=x_label, y_label=y_label,
                     fontsize=fontsize, include_leg=include_leg,
                     figsize=figsize)
    _=plot_o.ax.hist(df, col)
    plt.show()

def clean_data_for_area_analysis(df, area_name):
    '''
    Cleans dataframe only leaving data about the chosen area.
    Parameters:
    ----------
    area_name: str
        chosen area name
    Returns:
    --------
    df: pandas DataFrame
        cleaned dataframe
    '''
    df = df[df['Area Name'] == area_name]
    keep = ['Time period', 'Value']
    df = df[keep]
    df.rename(columns={'Time period':'year'}, inplace=True)
    # set index to year
    df.set_index('year', inplace=True)
    return df

# can plot area, or region data over time. 
def area_analysis(in_df, area_name, fontsize=12, include_leg=True,
                 figsize=(8,5)):
    '''
    Plots the change of the proportion of screened patients over time.
    In the chosen dataframe column
    Parameters:
    ----------
    df: pandas DataFrame
        dataframe
    area_name: str
        name of the area to be plotted over time
    fontsize: int
        size of the font, default=12
    include_leg: bool
        if True includes legend, default=True
    figsize: touple
        size of the figure in inches (width, height), default=(8,5)
    '''
    in_df = clean_data_for_area_analysis(in_df, area_name)
    title = f"{area_name} Screening Coverage Over the Years"
    x_label = 'Year'
    y_label = 'Value'
    plot = Analysis_Plot()
    plot.adjust_fig(title=title, x_label=x_label, y_label=y_label,
                    fontsize=fontsize, include_leg=include_leg,
                    figsize=figsize)
    plot.ax.plot(in_df['Value'], 'co-', label=area_name)
    plt.show()

def linear_comp(df, area_list, title="Plot", fontsize=12, include_leg=True, 
                figsize=(8,5)):
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
    # Checks if more than one area was included to be plotted.
    if(len(area_list) == 1):
        area_analysis(df, area_list, title="Plot", fontsize=12, 
                      include_leg=True, figsize=(8,5))
    else:
        # Loops through the areas in the list, plotting them on the same axis.
        for i in area_list:
            print(i)
            df1 = df.loc[df['Area Name']==i]
            plt.plot(df1['Time period'], df1['Value'], label=i)
        plot_o.adjust_fig(title=title, x_label=x_label, y_label=y_label,
                          fontsize=fontsize, include_leg=include_leg,
                          figsize=figsize)
        plt.show()



# Some testing, does not work atm, because of imports.
hist(df, 'Value', figsize=(8,5))
area_analysis(df, 'Exeter')
linear_comp(df, ['Exeter', 'Mid Sussex', 'Horsham'])

