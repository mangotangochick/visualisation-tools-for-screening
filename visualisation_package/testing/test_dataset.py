'''
Testing the built-in datasets.
'''
import pytest
from vis_tools import datasets as ds


def test_col_pres(cancer_type):
    '''
    Tests if recquired columns are in the dataset.
    '''
    columns = ['Area Code', 'Area Name', 'Area Type', 'Time period',
    'Value', 'Age', 'Sex', 'Category Name', 'Category']
    if cancer_type.lower() == 'breast':
        data = ds.load_breast()
    elif cancer_type.lower() == 'bowel':
        data = ds.load_bowel()
    elif cancer_type.lower() == 'cervical':
        data = ds.load_cerv()
    df_columns = list(data.columns)
    assert columns in df_columns == True


test_col_pres('cervical')