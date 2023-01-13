import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from datasets import *

df = load_cerv(deprivation=True)
df.head()

class DeprivationPlots():
    """
    DeprivationPlots class

    This class is used to generate plots of the most and least deprived areas.

    Attributes:
        df (DataFrame): DataFrame containing the required data.

    Methods:
        most_least_plot(year): Generates a plot of the most and least deprived
            areas based on the year provided. Defaults to plotting graphs for all years.
    """
    def __init__(self, df):
        """Initialize the class with a dataframe

        Args:
            df (DataFrame): DataFrame containing data
        """
        self.df = df

    def most_least_plot(self, year=df['Time period']):
        """
        Plot two graphs with the most and least values within a given year 

        Parameters: 
        year (str): year to filter by 

        Returns:
        None 
        """
        df = self.df
        df_grouped = df.loc[df['Time period'] == year].groupby('Time period')
        
        for name, group in df_grouped:
            df_most = group[group['Category'].str.contains('Most|most|more')]
            df_least = group[group['Category'].str.contains('Least|least|less')]
            fig, ax = plt.subplots(1, 2)
            df_most.plot(kind='bar', x='Category', y='Value', ax=ax[0])
            df_least.plot(kind='bar', x='Category', y='Value', ax=ax[1])
            plt.suptitle(name)
            
            fig.set_size_inches(30, 10)
            ax[0].tick_params(axis='x', labelrotation=45)
            ax[1].tick_params(axis='x', labelrotation=45)
            ax[0].set_facecolor('#ffd3e5')
            ax[1].set_facecolor('#d3f2ff')
            
            for p in ax[0].patches:
                ax[0].annotate(
                    str(p.get_height().round(1)) + '%',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10),
                    textcoords='offset points')
                
            for p in ax[1].patches:
                ax[1].annotate(
                    str(p.get_height().round(1)) + '%',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10),
                    textcoords='offset points')

            plt.show()

