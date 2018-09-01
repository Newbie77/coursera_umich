# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 21:05:07 2018

@author: Gimli
"""


# packages
import pandas as pd

###############################################################################
# import and clean 

def data_get():
    # read in data from wikipedia
    df = pd.read_html('https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table', header = 0)
    df = df[1]
    
    # rename columns
    df.columns = ['Countries', 'SummerNo', 'Gold_s', 'Silver_s', 'Bronze_s', 'Medals_s', 'WinterNo', 'Gold_w', 'Silver_w', 'Bronze_w', 'Medals_w', 'TotalNo', 'Gold_t', 'Silver_t', 'Bronze_t', 'Medals_t']
     
    
    # strip the weird stuff off the end of country names
    
    def country_strip(x):
         x = x.split('(')[0]
         x = x.strip()
         return x
     
    df['Countries'] = df['Countries'].apply(country_strip)

    # get index and drop first column (countries)
    df.index = df.iloc[:,0]
    df.drop(df.columns[0], axis = 1, inplace = True) 

    # drop first two rows 
    df  = df[1:]
    
    # convert all data into numbers
    for col in df: 
        df[col] = pd.to_numeric(df[col])
        
    # drop totals row - difficult when trying to pick out countries with the most x 
    df = df[df.index.str.contains('Totals') == False]
    
    return df


###############################################################################
# What is the first country in the df (series)
#  print first row
def first_country(df):
    
    print(df.iloc[0])

###############################################################################
# which country has won the most summer golds (single answer)
    
def most_gold_summer(df):
        
    # sort 
    df.sort_values(by = ['Gold_s'], inplace = True)

    # take the last value 
    country = df[-1:]
    print(country.index)
    
    # ALTERNATIVE: take max
    # make mask of where gold_s = max of gold_s
    print(df[df['Gold_s'] == df['Gold_s'].max()].index)
    
###############################################################################
# Which country has the biggest difference between their summer gold medal counts and winter gold medal counts relative to their total gold medal count?
# Only include countries that have won at least 1 gold in both summer and winter.

def sum_wint_diff(df):
    
    # only include countries with at lesat 1 gold in both summer and winter
    df_gold = df[(df.Gold_s >= 1 ) & (df.Gold_w >= 1)]
    
    # new column = summer gold - winter gold / total gold
    # indices that don't exist in df_gold will be NaN for this new column 
    df['sum_wint_diff'] = (df_gold.Gold_s - df_gold.Gold_w) / df_gold.Gold_t
    
    # find maximum 
    print(df[df['sum_wint_diff'] == df['sum_wint_diff'].max()].index)
    
###############################################################################
# Points function: weighted average of gold, silver, and bronze medals
    
def points(df):
    df['points'] = df.Gold_t * 3 + df.Silver_t * 2 + df.Bronze_t * 1
    print(df.points)
    
def main():
    
    df = data_get()
    
    first_country(df)
    
    most_gold_summer(df)
    
    # resort alphabetical (function sorted by summer gold)
    df.sort_index(inplace = True)
    
    sum_wint_diff(df)
    
    points(df)    
    
main()