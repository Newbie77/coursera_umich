# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 11:16:55 2018

@author: Gimli
"""
## NOT WORKING
# I think the housing DF is t
# subtraction for change from recession start to bottom isn't working
    # maybe rename all time columns to 2016Q1 or something???

# once do this and finish t-test, recommit this folder to github and say reshaped HP wide and finished problem

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import math 

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
        
    # create a dummy that is always 1 for yes university town
    # when merge with HPs
    df_univ['univ_town'] = 1
        
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

    return df_gdp       

def dt_to_strqtr(dt):
    year = dt.year
    month = dt.month
    qtr = math.ceil(month/3)
    
    return str(year) + 'Q' + str(qtr)
    
'''
:returns
    datetime of first quarter of recession
    string in format yyyyQqq of first quarter of recession
Need datetime to use in other GDP functions and string to use in housing dataset
'''
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
    return df_gdp.beg_rec.eq(True).idxmax(), dt_to_strqtr(df_gdp.beg_rec.eq(True).idxmax())

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
    return df_gdp.end_rec.eq(True).idxmax(), dt_to_strqtr(df_gdp.end_rec.eq(True).idxmax())

# return time value of lowest GDP value during recession
def get_recession_bottom(df_gdp, rec_start, rec_end):
    
    # limit dataset to recession
    df_rec = df_gdp[(df_gdp.index >= rec_start) & (df_gdp.index <= rec_end)]
    
    # get minimum gdp value
    return df_rec.idxmin(), dt_to_strqtr(df_rec.idxmin())


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
     
    # 2D list that groups the three months that contribute to each column
    qs = [list(df_housing.columns)[x:x+3] for x in range(0, len(list(df_housing.columns)), 3)]
      
    # create list of column names we can loop through
    col_names = []
    for q in qs:
        if q[0][6] == '1':
            col_names.append(q[0][0:4] + 'Q1')
        if q[0][6] == '4':
            col_names.append(q[0][0:4] + 'Q2')        
        if q[0][6] == '7':
            col_names.append(q[0][0:4] + 'Q3')  
        if q[0][5:7] == '10':
            col_names.append(q[0][0:4] + 'Q4')  
            
    # create new columns that average those three months and have new column names
    for i in range(len(qs)):
        df_housing[col_names[i]] = df_housing[qs[i]].mean(axis=1)
    
    # drop the old columns
    old_cols = [c for c in df_housing.columns if 'Q' not in c ]
    df_housing.drop(old_cols, axis = 1, inplace = True)
    
    # limit to 2000q1 to 2016q3
    start_index = df_housing.columns.get_loc('2000Q1')
    end_index = df_housing.columns.get_loc('2016Q3')
    df_housing = df_housing.iloc[:,start_index:end_index+1]
        
    # move index state and region name to columns and reset index
    df_housing['state'] = df_housing.index.get_level_values(0)
    df_housing['regions'] = df_housing.index.get_level_values(1)
    df_housing.reset_index(drop = True, inplace = True)
          
    return df_housing
    
# find change in HP from recession start to recession bottom
def hp_gr_recession(df, start, bottom):
    
    # find price change from start of recession to bottom
    df['gr'] = (df[start] - df[bottom]) / df[bottom]    
    
# merge HP and university town data
# left merge. Want to include non-university towns
def merge_data(df_hp, df_univ):
    
    merged_df = pd.merge(df_hp, df_univ, how = 'left', left_on = ['state', 'regions'], right_on = ['state', 'regions'])
    
    return merged_df

def t_test(df):
    
    # seperate datasets for university and non-univeresity towns
    df_u = df[df.univ_town == 1]
    df_nu = df[df.univ_town == 0]
    
    # t-test
    pvalue = list(ttest_ind(df_u.gr, df_nu.gr))[1]
    different = True if pvalue < .01 else False
    
    # which has lower mean price ratio
    better = 'university-town' if df_u.gr.mean() > df_nu.gr.mean() else 'non-university town'
    
    return (different, pvalue, better)

def main():
    
    # get datasets
    df_univ = get_list_of_university_towns()
    df_gdp = get_gdp()
    df_housing = convert_housing_data_to_quarters()

    # from GDP data, find start, end, and bottom of recession
    # each returns a datetime 
    rec_start_dt, rec_start_str = get_recession_start(df_gdp)
    rec_end_dt, rec_end_str = get_recession_end(df_gdp, rec_start_dt)    
    rec_bottom_dt, rec_bottom_str = get_recession_bottom(df_gdp, rec_start_dt, rec_end_dt)
    print(rec_start_str, rec_end_str, rec_bottom_str)

    # calculate change in HP from recession start to recession bottom
    hp_gr_recession(df_housing, rec_start_str, rec_bottom_str)

    # merge HP and university town data, left merge
    df_merge = merge_data(df_housing, df_univ)
    df_merge.univ_town.fillna(0, inplace = True) # make university town dummy. if didn't merge, value is 0

    # drop NA from growth and reindex
    df_merge.dropna(axis = 0, inplace = True)
    df_merge.reset_index(drop = True, inplace = True)
    #print(df_merge[df_merge.gr.isnull()])

    # t-test
    print(t_test(df_merge))
    
    
    
main()