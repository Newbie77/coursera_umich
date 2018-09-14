# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 11:06:21 2018

@author: Gimli
"""

import pandas as pd
import re
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import numpy as np


data_dir = r'C:\Users\Gimli\Documents\coursera\data'

def get_energy_data():
    
    energy = pd.read_excel(data_dir + r'\Energy Indicators.xls', skiprows = 17, skipfooter = 38, 
        usecols = 'C:F', na_values = '...')
    energy.columns = ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']

    # check datatypes
    print(energy.dtypes)
    
    # convert energy supply from pentajules to gigajules
    energy['Energy Supply'] = energy['Energy Supply'] * 1000000
    
    # replace numbers in country names to blank
    energy.Country = energy.Country.apply(lambda x: re.sub('[0-9]', '', str(x)))
    
    # get rid of everything in parentheses in name
    energy.Country = energy.Country.apply(lambda x: x.split('(')[0])
    
    # strip all white space at ends
    energy.Country = energy.Country.apply(lambda x: x.strip())
    
    # rename some countries
    energy.Country.replace('Republic of Korea', 'South Korea', inplace = True)
    energy.Country.replace('United States of America', 'United States', inplace = True)
    energy.Country.replace('United Kingdom of Great Britain and Northern Ireland', 'United Kingdom', inplace = True)
    energy.Country.replace('China, Hong Kong Special Administrative Region', 'Hong Kong', inplace = True)
    
    # sort on country name and reset index
    energy.sort_values('Country', inplace = True)
    energy.reset_index()
        
    return energy
    
def get_gdp_data():
    
    gdp = pd.read_csv(data_dir + r'/world_bank.csv', skiprows = 3)
    
    gdp.rename(columns = {'Country Name': 'Country'}, inplace = True)
    
    # rename some countries
    gdp.Country.replace('Korea, Rep.', 'South Korea', inplace = True)
    gdp.Country.replace('Iran, Islamic Rep.', 'Iran', inplace = True)
    gdp.Country.replace('Hong Kong SAR, China', 'Hong Kong', inplace = True)

    # sort on country name and reset index
    gdp.sort_values('Country', inplace = True)
    gdp.reset_index()
    
    # check datatypes
    print(gdp.dtypes)

    return gdp

def get_sci_data():
    
    ScimEm = pd.read_excel(data_dir + r'/scimagojr.xlsx')
    
    # check datatypes
    print(ScimEm.dtypes)
    
    return ScimEm

# inner merge databases. Make index country name. Find how many data points we lost
# then limit to the top 15 ranked countries in publication
def merge_df(energy, gdp, ScimEm):
    
    # gdp: only keep last 10 years
    gdp = gdp.filter(['Country', '2006', '2007', '2008', '2009', '2010', '2011', 
                      '2012', '2013', '2014', '2015'])
    
    merged_df = pd.merge(energy, gdp, how = 'inner', left_on = 'Country', right_on = 'Country')
    merged_df = pd.merge(merged_df, ScimEm, how = 'inner', left_on = 'Country', right_on = 'Country')

    # make index country name
    merged_df.index = merged_df.Country
    merged_df.drop(['Country'], axis = 1, inplace = True)
    
    # how many data points did we lose? Do outer join - innter join
    merged_df_outer = pd.merge(energy, gdp, how = 'outer', left_on = 'Country', right_on = 'Country')
    merged_df_outer = pd.merge(merged_df_outer, ScimEm, how = 'outer', left_on = 'Country', right_on = 'Country')        
    
    print(len(merged_df_outer) - len(merged_df) + 1) # add one because inclusive
    
    # top 15 ranked countries
    merged_df = merged_df[merged_df.Rank <= 15]
    
    return merged_df

# get average GDP over past 10 years for each of the top 15 ranked country
# return a series 
def get_avg_gdp(df):
    
    avg_gdp = df[['2006', '2007', '2008', '2009', '2010', '2011', 
                  '2012', '2013', '2014', '2015']].mean(axis = 1)
    
    # sort in descending order 
    avg_gdp.sort_values()
    
    print(avg_gdp)
    return avg_gdp

# get GDP change over past 10 years of one country
def get_gdp_ch_6(df, country):

    df_country = df[df.index == country]
    gdp_ch = df_country['2015'] - df_country['2006']

    return gdp_ch

# mean of energy supply per capita
def get_energy_mean(df):
    
    return df['Energy Supply per Capita'].mean()
    
# get max renewable percentage and country
# return as a tuple
def get_max_renewable(df):
    
    # find max
    max_renewable = df['% Renewable'].max()
    
    # find country with that max
    max_renewable_country = df['% Renewable'].idxmax()
   
    return max_renewable, max_renewable_country

# create column: ratio of self citations to total citations
# and return tuple with max value and country
def get_max_cit_ratio(df):
    
    # add column
    df['cit_ratio'] = df['Self-citations'] / df['Citations']
    
    # find max 
    max_cit_ratio = df['cit_ratio'].max()
    
    # country with max 
    max_cit_ratio_country = df['cit_ratio'].idxmax()
    
    return max_cit_ratio, max_cit_ratio_country

# estimate population and return most populous country
def get_pop(df):
    
    # estimate population and add column
    df['pop'] = df['Energy Supply'] / df['Energy Supply per Capita']
    
    # find most populous country
    return df['pop'].idxmax()

# add column with estimate of citable documents per person
# return correlation between energy per capita and citable docs per capita
def get_corr(df):
    
    # add column with citable documents per person
    df['cit_capita'] = df['Citable documents'] / df['pop']
    
    # graph 
    df.plot.scatter(x = 'cit_capita', y = 'Energy Supply per Capita', xlim = [0, .0007])
    print(df['cit_capita'].max())
    print(df['cit_capita'].min())
    plt.close()
    
    # return correlation 
    return df['cit_capita'].corr(df['Energy Supply per Capita'])

    
# add dummy column: 1 if % Renewable at or above median. 0 if below. 
# return series sorted in ascending order of rank
def get_dummy_renewable(df):

    # dummy variable 
    df['HighRenew'] = [1 if renewable >= df['% Renewable'].median() else 0 for renewable in df['% Renewable']] 
    
    # sort by rank
    df.sort_values(['Rank'], inplace = True)
    
    return df['HighRenew']


# sort countries into continents
# return dataframe with statistics about each continent
def get_continent_df(df):
    
    continent_dict  = {'China':'Asia', 
                  'United States':'North America', 
                  'Japan':'Asia', 
                  'United Kingdom':'Europe', 
                  'Russian Federation':'Europe', 
                  'Canada':'North America', 
                  'Germany':'Europe', 
                  'India':'Asia',
                  'France':'Europe', 
                  'South Korea':'Asia', 
                  'Italy':'Europe', 
                  'Spain':'Europe', 
                  'Iran':'Asia',
                  'Australia':'Australia', 
                  'Brazil':'South America'}
    
    # create continent column
    #df['continent'] = np.nan
    #for key, value in continent_dict.items(): 
    #    for index, row in df.iterrows(): 
    #        if index == key:
    #            df.loc[index, 'continent'] = value 
                
    # OR
    df['continent'] = [continent_dict[country] for country in df.index]

    # create pivot table
    # number of countries per continent
    # mean, sum, and std of population per continent 
    df_piv = df.pivot_table(values = 'pop', columns = 'continent',  aggfunc = [np.count_nonzero, np.mean, np.sum, np.std])

    return df_piv
    
# Cut % Renewable into 5 bins. 
# Group by the Continent, as well as these new % Renewable bins. 
# return series with multiindex
def get_renewable_bins(df):
    
    # cut into bins and collapse by bin 
    # count to get number of countries in each bin 
    df_bins = df.groupby([df.continent, pd.cut(df['% Renewable'], 5)]).count()
    
    # drop rows with NaNs - bin doesnt exist
    df_bins.dropna(axis = 0, inplace = True)
    
    # keep only one column and rename 
    df_bins = df_bins.filter(['2006'])
    df_bins.rename(columns =  {'2006': 'Number of Countries'}, inplace = True)
    
    return df_bins
    
# format pop column with commas
# return this series 
def get_str_pop(df):
    
    # format pop column
    df['pop'] = df['pop'].map('{:,}'.format)
    
    return df['pop']

def main():
    
    # get three data bases and clean
    energy = get_energy_data()
    gdp = get_gdp_data()
    ScimEm = get_sci_data()
   
    # inner merge and take top 15 ranked 
    # also find number of observations lost 
    merged_df = merge_df(energy, gdp, ScimEm)
    
    # get average GDP for the top 15 counties over the past 10 years
    # returns a series 
    avg_gdp = get_avg_gdp(merged_df)
    
    # get GDP change over past 10 years of country with 6th largest average GDP
    # country with 6th largest 
    country_6 = avg_gdp.index[-6]
    
    print(get_gdp_ch_6(merged_df, country_6))
    
    # find mean energy supply per capita
    print(get_energy_mean(merged_df))
    
    # find max renewable percentage and country
    # return tuble
    print(get_max_renewable(merged_df))
    
    # create column: ratio of self citations to total citations
    # and return tuple with max value and country
    print(get_max_cit_ratio(merged_df))
    
    # add column with estimate population using energy supply and energy supply per capita
    # return most populous country
    print(get_pop(merged_df))
    
    # add column with estimate of citable documents per person
    # return correlation between energy per capita and citable docs per capita
    print(get_corr(merged_df))
    
    # add dummy column: 1 if % Renewable at or above median. 0 if below. 
    # return series sorted in ascending order of rank
    print(get_dummy_renewable(merged_df))
    
    # sort countries into continents
    # return dataframe with statistics about each continent
    print(get_continent_df(merged_df))
    
    # Cut % Renewable into 5 bins. 
    # Group by the Continent, as well as these new % Renewable bins. 
    # return series with multiindex
    print(get_renewable_bins(merged_df))
    
    # format pop column with commas
    # return this series 
    print(get_str_pop(merged_df))

    
    
    
main()