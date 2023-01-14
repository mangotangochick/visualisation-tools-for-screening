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
    
def test_get_geoshape_info_from_api_request_for_areacode():
    region_test = visualisation.Region_Analysis()
    shape, was_error = region_test.get_geoshape_info_from_api_request_for_areacode('E12000001')
    assert was_error == False

def test_get_all_region_area_codes():
    region_test = Region_Analysis()
    regions_return = region_test.get_all_region_area_codes()
    assert len(regions_return) == 9


test_col_pres('cervical')