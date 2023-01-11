'''
Testing the built-in datasets.
'''
import pytest
from vis_tools import datasets as ds
from vis_tools import visualisation


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

def test_region_analysis_year_setting():
    region_test = visualisation.Region_Analysis(2016, False)
    assert region_test.year == 2016
    
def test_get_geoshape_info_from_api_request_for_areacode():
    region_test = visualisation.Region_Analysis(2016, False)
    shape, was_error = region_test.get_geoshape_info_from_api_request_for_areacode('E12000001')
    assert was_error == False


test_col_pres('cervical')