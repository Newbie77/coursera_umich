# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 11:16:55 2018

@author: Gimli
"""


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind

data_dir = r'C:\Users\Gimli\Documents\coursera\data'

states_dict = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

# list of university towns from wikipedia
def get_list_of_university_towns():
    
    ### download txt file 
    df_univ = pd.read_csv(data_dir + r'\university_towns.txt', usecols = [0],
                          encoding='cp1252', header = 0, names = ['regions'])
    
    # check for NaNs
    print(df_univ[df_univ.regions.isnull()])
    
    ### seperate states into seperate columns
    # check if entry in states dictionary values and if yes then put in state column
    df_univ['state'] = np.nan
    for entry in range(len(df_univ)):
        for key, value in states_dict.items():
            if df_univ.iloc[entry, 0] == value:
                df_univ.iloc[entry, 1] = df_univ.iloc[entry, 0]
                
    # now fill state values downwards
    df_univ.state.ffill(inplace = True)
                
    # drop entries where regions == states 
    df_univ = df_univ[df_univ.regions != df_univ.state]
    
    # convert from full state name to abbreviation
    for key, value in states_dict.items():
        df_univ.state.replace(value, key, inplace = True)
    
    ### remove everything after ( in regions and [
    df_univ.regions =  df_univ.regions.apply(lambda x: x.split('(')[0])
    df_univ.regions =  df_univ.regions.apply(lambda x: x.split('[')[0])
        
    return df_univ
    
# get time series of GDP
def get_gdp():
    
    # download CSV
    df_gdp = pd.read_csv(data_dir + r'\gdplev.csv', header = 4, index_col = 1)
    
    # keep total GDP only 
    df_gdp = df_gdp[df_gdp.index.str.contains('Gross domestic product') == True]
    
    # drop first column 
    df_gdp.drop(['Line'], axis = 1, inplace = True)
    
    # rename columns so Q1, Q2, Q3, Q4 
    def rename_cols(c):
        if '.1' in c:
            return c[0:4] + 'Q2'
        elif '.2' in c: 
            return c[0:4] + 'Q3'
        elif '.3' in c: 
            return c[0:4] + 'Q4'  
        else:
            return c[0:4] + 'Q1'  
        
    for col in df_gdp: 
        df_gdp.rename(columns = {col: rename_cols(col)}, inplace = True)

    # reshape into a time series
    df_gdp = df_gdp.stack()
    df_gdp.columns = ['GDP']

    # drop first level of index
    df_gdp.index = df_gdp.index.get_level_values(1) 
    
    # make index date time
    df_gdp.index = pd.to_datetime(df_gdp.index)
    df_gdp.index = df_gdp.index.date

    # make GDP numeric
    df_gdp = pd.to_numeric(df_gdp)
    
    # no actual change here. but getting index into same format as HP data
    #df_gdp = df_gdp.resample('Q').mean()
    
    
    print(df_gdp.head())

    return df_gdp    


# return time value of recession start time: defined as two consecutive quarters of GDP decrease
def get_recession_start(df_gdp):
    
    # find every place where two consecutive quarters of GDP decline 
    # mark if difference from previous period is negative
    df_decrease = df_gdp.diff() < 0
    
    # append series 
    df_gdp = pd.concat([df_decrease, df_gdp], axis = 1)
    df_gdp.columns = ['decrease', 'GDP']
    
    # mark where two negative values in a row
    # specifically want the first period where this happens, so compare to the next (lead is shift of -1)
    df_gdp['beg_rec'] = (df_gdp.decrease == True) & (df_gdp.decrease.shift(-1) == True)
    
    # only one recession in this period: take the first instance where beg_rec == True
    # and return time period
    return df_gdp.beg_rec.eq(True).idxmax()

# return time value of recession end time: defined as two consecutive quarters of GDP increase
def get_recession_end(df_gdp,rec_start):

    # find every place where two consecutive quarters of GDP increase 
    # mark if difference from previous period is positive
    df_increase = df_gdp.diff() > 0
    
    # append series 
    df_gdp = pd.concat([df_increase, df_gdp], axis = 1)
    df_gdp.columns = ['increase', 'GDP']

    # mark where two positive values in a row. Want first instance after beginning of recession
    # specifically want the first period where this happens, so compare to the next (lead is shift of -1)
    df_gdp['end_rec'] = (df_gdp.increase == True) & (df_gdp.increase.shift(-1) == True) & (df_gdp.index > rec_start)

    # only one recession in this period: take the first instance where beg_rec == True
    # and return time period
    return df_gdp.end_rec.eq(True).idxmax()

# return time value of lowest GDP value during recession
def get_recession_bottom(df_gdp, rec_start, rec_end):
    
    # limit dataset to recession
    df_rec = df_gdp[(df_gdp.index >= rec_start) & (df_gdp.index <= rec_end)]
    
    # get minimum gdp value
    return df_rec.idxmin()

# get housing data and convert to quarterly 
def convert_housing_data_to_quarters():
    
    df_housing = pd.read_csv(data_dir + r'/City_Zhvi_AllHomes.csv', header = 0, index_col = 0)

    # multi index: state, region name
    df_housing.set_index(['State', 'RegionName'], inplace = True)
        
    # drop Metro, CountyName, SizeRank, State
    df_housing.drop(columns=['Metro', 'CountyName', 'SizeRank'], inplace = True)
    
    # limit columns to 2000 onwards 
    #for col in df_housing:
    #    if col[0] == '1':
    #        df_housing.drop(columns = [col], inplace = True)
        
    # reshape 
    df_housing = df_housing.stack()
    df_housing = pd.DataFrame(df_housing, index = df_housing.index) # make it a dataframe again 
        
    ### convert to quarterly data 
    # make single index. couldn't make this work with 3 multi index
    df_housing['state'] = df_housing.index.get_level_values(0)
    df_housing['region'] = df_housing.index.get_level_values(1)
    
    df_housing.set_index(df_housing.index.get_level_values(2), inplace = True)

    # make the time index datetime
    df_housing.index = pd.to_datetime(df_housing.index)    
    
    ## limit to 2000q1 to 2016q3
    df_housing = df_housing.loc['2000-01-01': '2016-09-01']
    #[(df_housing.index.year >= 2000) & (df_housing.index < 2016-06-01)]
            
    # quarterly
    df_housing = df_housing.groupby(['state', 'region']).resample('Q').mean()
    
    # take out of index again: easier 
    df_housing['state'] = df_housing.index.get_level_values(0)
    df_housing['region'] = df_housing.index.get_level_values(1)   
    df_housing.set_index(df_housing.index.get_level_values(2), inplace = True)

    df_housing.columns = ['price', 'state', 'region']
    
    # make index string. easier for later. 
    #df_housing.index = df_housing.index.strftime('%Y-%m')

    
    return df_housing
    
# find change in HP from recession start to recession bottom
def hp_ch_recession(df, start, bottom):
    
    # find price change from start of recession to bottom
    print(df.iloc[start, 0])
    #df['change'] = df.iloc[start, 0] - df.iloc[bottom, 0]
    
    print(df.head())
    
    
# merge HP and university town data
# inner merge
# will be only recession time period because that is what HP data is limited to
def merge_data(df_hp, df_univ):
    
    merged_df = pd.merge(df_hp, df_univ, how = 'inner', left_on = ['state', 'region'], right_on = ['state', 'region'])
    
    return merged_df
    
def main():
    
    # get datasets
    df_univ = get_list_of_university_towns()
    df_gdp = get_gdp()
    df_housing = convert_housing_data_to_quarters()

    # from GDP data, find start, end, and bottom of recession
    # each returns a datetime 
    rec_start = get_recession_start(df_gdp)
    rec_end = get_recession_end(df_gdp, rec_start)    
    rec_bottom = get_recession_bottom(df_gdp, rec_start, rec_end)
    print(rec_start, rec_end, rec_bottom)
    
    # calculate change in HP from recession start to recession bottom
    hp_ch_recession(df_housing, rec_start, rec_bottom)

    
    # merge HP and university town data
    # limited to recession like HP data is
    
    
    
main()