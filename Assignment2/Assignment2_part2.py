# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 10:14:42 2018

@author: Gimli
"""

import pandas as pd
import numpy as np

# data dir 
data_dir = r'C:\Users\Gimli\Documents\coursera\data'

def get_data():
    
    #print(os.path.isfile(data_dir + r'\co-est2015-alldata.csv'))
    # import data 
    # state is index
    census_df = pd.read_csv(data_dir + r'\co-est2015-alldata.csv',  header = 0, encoding='cp1252', index_col = 5)
    
    # get rid of state aggregation level 
    census_df = census_df[census_df.SUMLEV == 50]
    
    # check types
    # print(census_df.dtypes)
    
    return census_df

###############################################################################
# which states has the most counties 
    
def max_counties(df):
    
    # count unique county names within a single state
    # count number of uniques within the index and assign to a variable
    df['numcounty'] = df.groupby(df.index).COUNTY.nunique()
        
    # get the state with max
    print(df[df['numcounty'] == df['numcounty'].max()].index)
    
    # OR
    print(df.groupby(df.index).COUNTY.nunique().idxmax())
        # idxmax returns the index of first occurance of maximum 

###############################################################################
# three most populous states only considering the three most populous counties 
        
def most_pop(df):
    
    # get the three most populous counties in each state 
    # sort on census2010pop within state 
    #df.CENSUS2010POP = df.groupby(df.index).CENSUS2010POP.apply(lambda x: x.sort_values())
    df['index_col'] = df.index
    df.sort_values(['index_col', 'CENSUS2010POP'], inplace = True)
    
    # take the last 3 
    df_3 = df.groupby(df.index).tail(3)

    # sum the couinty population within these three and get one dataset
    # could also apply this to one of the columns and it would fill all 3 values
    df_popsum = df_3.groupby(df_3.index).CENSUS2010POP.sum()

    # take the 3 larges in df_popsum
    df_popsum.sort_values(inplace = True)
    print(df_popsum.tail(3).index)
    
    ########
    # OR:
    df_3 = df.groupby(df.index).CENSUS2010POP.nlargest(3)
    df_popsum = df_3.groupby(level=0).sum()
    print(list(df_popsum.nlargest(3).index))
    
###############################################################################
# county with largest population change (max - min) between 2015 and 2010
    
def largest_ch(df):    
    
    # use function and apply or do directly as commented out below
    def min_max(row):
        row['max'] = row[['POPESTIMATE2010', 'POPESTIMATE2011','POPESTIMATE2012', 
             'POPESTIMATE2013', 'POPESTIMATE2014', 'POPESTIMATE2015']].max()
        row['min'] = row[['POPESTIMATE2010', 'POPESTIMATE2011','POPESTIMATE2012', 
             'POPESTIMATE2013', 'POPESTIMATE2014', 'POPESTIMATE2015']].min()
        return row # make sure to return the row. 
    
    # apply function on all rows of dataset 
    df = df.apply(min_max, axis = 1)

    # OR:  for each county, find the max and min value in POPESTIMATE2010 to 2015
    #df['max'] = df.loc[:,['POPESTIMATE2010', 'POPESTIMATE2011','POPESTIMATE2012', 
    #  'POPESTIMATE2013', 'POPESTIMATE2014', 'POPESTIMATE2015']].max(axis = 1)
    #df['min'] = df.loc[:,['POPESTIMATE2010', 'POPESTIMATE2011','POPESTIMATE2012', 
    #  'POPESTIMATE2013', 'POPESTIMATE2014', 'POPESTIMATE2015']].min(axis = 1)  
    

    # difference
    df['difference'] = df['max'] - df['min']
    
    # maximum difference
    print(df[df['difference'] == df['difference'].max()].CTYNAME)
    
###############################################################################
# dataset with counties in regions 1 or 2, name starts with Washington and POPESTIMATE2015 > POPESTIMATE2014

def df_subset_create(df):
    
   df_subset = df[(df['REGION'] == 1) | (df['REGION'] == 2)]
   df_subset = df_subset[df_subset.CTYNAME.str.startswith('Washington') == True]
   df_subset = df_subset[df_subset.POPESTIMATE2015 > df_subset.POPESTIMATE2014]
   
   # only CTYNAME column
   df_subset = df_subset.CTYNAME
   
   return df_subset
   
def main():
    
    census_df = get_data()
    
    max_counties(census_df)
    
    most_pop(census_df)
    
    # sort by county alphabetical again
    census_df.sort_values(['index_col', 'CTYNAME'], inplace = True)
    
    largest_ch(census_df)
    
    df_subset = df_subset_create(census_df)
    
    print(df_subset)
    
    # for own practice: calculate average county population in a state with for loop and groupby (2 ways)
    census_df['avg1'] = 0
    for st in census_df.index.unique():
        census_df.loc[st, 'avg1'] = (census_df[census_df.index == st].CENSUS2010POP.mean())
    
    census_df['avg2'] = census_df.groupby(census_df.index).CENSUS2010POP.mean()
    # OR: census_df['avg2'] = census_df.groupby(census_df.index).agg({'CENSUS2010POP': np.average})
    # OR: census_df['avg2'] = census_df.groupby(census_df.index).CENSUS2010POP.agg({'avg2': np.average})
    # same effect becaus assigning to a column, but doing slightly different things (see Week3 Notes. Or try printing them)
    
    # groupby in a loop
    census_df['avg3'] = 0
    for group, frame in census_df.groupby(census_df.index):
        census_df.loc[group, 'avg3'] = frame.CENSUS2010POP.mean()
        
    print(census_df.avg1, census_df.avg2, census_df.avg3, census_df.avg4)
    
    def fun(item):
        if item[0] < 'M':
            return 1
        elif item[0] < 'Q':
            return 2
        else:
            return 3 
    for group, frame in census_df.groupby(fun):
        print(group, frame.CENSUS2010POP)
        
    
main()
