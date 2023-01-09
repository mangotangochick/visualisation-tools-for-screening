import pandas as pd
import matplotlib.pyplot as plt
cervical_url = "https://data.england.nhs.uk/dataset/dbf14bed-85bc-4aef-856c-38eb9d6de730/resource/e281a471-f546-44b9-99f1-12e80b27a638/download/220iicancerscreeningcoveragecervicalcancer.data.csv"
bowel_url = "https://data.england.nhs.uk/dataset/255dc4c3-5229-423b-a966-af065c31bed3/resource/23d0b393-3087-445e-ae95-2c244fb3deaa/download/220iiicancerscreeningcoveragebowelcancer.data.csv"
breast_url = "https://data.england.nhs.uk/dataset/b509e701-7e64-457c-9d12-9739e8de89bb/resource/19cfefeb-3d21-41e6-8539-23985b554273/download/220icancerscreeningcoveragebreastcancer.data.csv"
cerv_df = pd.read_csv(cervical_url)
bowel_df = pd.read_csv(bowel_url)
breast_df = pd.read_csv(breast_url)
'''print(cerv_df.T)
cerv_df.shape
cerv_df.info()'''

keep_col = ['Area Code', 'Area Name', 'Area Type', 'Time period', 'Value', 'Lower CI limit', 'Upper CI limit']
cerv_df = cerv_df[keep_col]
bowel_df = bowel_df[keep_col]
breast_df = breast_df[keep_col]

def combine_dfs(df_c, df_bo, df_br, screening_types=["cervical", "bowel", "breast"]):
    '''Takes three data frames of available cancer screening data and 
    the types of cancers we are interested to visualise. Returns a new
    dataframe with the chosen dataframes combined.
    Parameters:
    -----------
    df_c: DataFrame
        cervical cancer dataframe
    df_bo: DataFrame
        bowel cancer dataframe
    df_br: DataFrame
        breast cancer dataframe 
    screening_types: lst of str
        a list of cancer screening programmes of interest chosen from
        "bowel", "breast", "cervical"
    Returns:
    -------
    df_comb DataFrame
        concatenated chosen data frames with two layer indexing. First layer
        is the type of cancer, the second layer is the types of data.'''
    df_lst=[]
    keys = []
    for i in screening_types:
        if i == "cervical":
            df_lst.append(df_c)
            keys.append(i)
        elif i == "bowel":
            df_lst.append(df_bo)
            keys.append(i)
        elif i == "breast":
            df_lst.append(df_br)
            keys.append(i)
    df_comb = pd.concat(df_lst, axis="columns", keys=keys, names=["cancer"])
    return df_comb


to_comb=["cervical", "breast"]
df_full = combine_dfs(cerv_df, bowel_df, breast_df, screening_types=to_comb)

'''df_full.columns.get_level_values("cancer").tolist()
df_full.index.get_level_values("cancer")
df_full["Value"].loc[df_full["Area Name"]=="Exeter"].loc["cervical"]'''



def area_chart(df_canc, unit="Exeter", num_chart=1, 
               chart_title = "Area Chart", xlabel="Years", 
               ylabel="Proportion Screened, %", fontsize=12):
    '''
    Takes dataset combined of the types of cancer screening dataframes we
    are interested in. Crates area charts comparing different cancers screening
    attendance in the chosen location (unit). If number of charts is chosen as 
    two, the comparison regional chart is added, if number of charts is chosen 
    as three, regional and national charts are added. 
    Parameters:
    ----------
    df_canc: DataFrame
        the dataframe combined from chosen cancers data frames
    unit: str
        the name of the unit of interest
    num_chart: int
        number of charts:
        1 - just the unit chart
        2 - unit and regional charts
        3 - unit, regional and national charts
    chart_title: str
        the title of the chart, shown at the top middle of the chart
    xlabel: str
        the name of the X axis
    ylabel: str
        the name of the Y axis
    fontsize: int
        the size of the font to use for the text elements in the graph
    '''
    df_canc = df_canc.set_index(df_canc["cervical"]["Time period"])
    cancers = [*set(df_canc.columns.get_level_values("cancer").tolist())]
    subgroups = [df_canc.loc[df_canc[i]["Area Name"]=="Exeter"][i]["Value"] for i in cancers]
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot()
    ax.set_ylim(0,200)
    ax.legend(loc="best", labels=cancers)
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    stack = ax.stackplot(subgroups[0].index, subgroups, labels=cancers)
    return stack

test = area_chart(df_full)
plt.show()