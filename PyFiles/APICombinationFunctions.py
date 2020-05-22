# -*- coding: utf-8 -*-
"""
Created on Fri May 15 10:34:21 2020

@author: nhell
"""
import requests
import json
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np

def startScreen():
    print("______________________________________________________")
    print("|                                                    |")
    print("|             Welcome to the Realtor API             |")
    print("|                                                    |")
    print("|____________________________________________________|")


def isPurchasing():
    """
    Returns
    -------
    purch : Bool
        Asks the User whether or not they are wishing to purchase or rent a home through single character input.

    """
    print("Task 1: Are you wanting to purchase or rent a home?")
    choice = input("Type 'b' to buy or 'r' to rent: ")
    done = False
    while not done: #Ensure user input is usable
        if choice == 'b':
            purch = True
            done = True
        elif choice == 'r':
            purch = False
            done = True
        else:
            print("Your input is not one of the choices above...")
            choice = input("Type 'b' to buy or 'r' to rent: ")

    return purch

def get_User_Input():
    """
    Returns
    -------
    city : String
        Asks the User which City they would like to search for a home in.
    state : String
        Asks the User which State they would like to search for a home in.
        NOTE: This is State Code. Therefore, OH must be typed instead of Ohio (as far as I believe)
    results : Int
        Asks the User how many results they would like to see
    
    FUNCTION NOTE: This function is not optimized to handle incorrect values as well as mixmatched values (Cleveland, TX???)
    """
    print("Task 2: Enter the following information...")
    done = False
    while not done:
        city = input("City: ")
        state = input("State Code: ")
        while True:
            try:
                results = input("How many results would you like to receive?\nInputting an incorrect value will default to 5 results: ")
                results = int(results)
            except ValueError:
                print("This is not a valid number. Number of results defaulted to 5.")
                results = 5
                break
            else:
                break
        if results < 1:
            print("This is not a valid number. Number of results defaulted to 5.")
            results = 5
        print("You are looking for", results, "results in", city, ",", state, "Is this correct? [y/n]")
        answ = input()
        if answ == 'y':
            done = True
        elif answ != 'n':
            print("You did not input a correct value.")
            
        print()
    return city, state, results

def soldHomes():
    print("Looking for homes that have been previously sold...")
    city, state, results = get_User_Input()
    url = "https://realtor.p.rapidapi.com/properties/v2/list-sold"
    
    querystring = {"sort":"sold_date","city":city,"offset":"0","state_code":state,"limit":results}

    headers = {
            'x-rapidapi-host': "realtor.p.rapidapi.com",
            'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2"
    }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    myarray = []
    for line in response.iter_lines(decode_unicode=True):
        if line:
            myline=json.loads(line)
            myarray.append(myline)

    #Normalize JSON data into dataframe for general property information
    properties = json_normalize(myarray, 'properties')
    return properties

def soldHomesTableResults(properties):
    """
    Parameters
    ----------
    properties : DataFrame


    Returns
    -------
    table : DataFrame
        Simple table showing home information (purchasing option) obtained using PropertyIDs

    """
    print("Preparing Table Containing Home Information...")
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    headers = {
            'x-rapidapi-host': "realtor.p.rapidapi.com",
            'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
    }

    rows = [] #Create data array
    for i in properties['property_id']:
        querystring = {"property_id":i}
        response = requests.request("GET", url, headers=headers, params=querystring)
        #Insert JSON data into array
        myarray = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                myline=json.loads(line)
                myarray.append(myline)
                
        #Normalize JSON data into dataframe for general property information
        df = json_normalize(myarray, 'properties')
        #Grab all the data
        row = [df.at[0, 'property_id'], df.at[0, 'listing_id'], df.at[0, 'prop_status'],
              df.at[0, 'prop_type'], df.at[0, 'list_date'], df.at[0, 'last_update'],
              df.at[0, 'beds'], df.at[0, 'baths'], df.at[0, 'stories'],
              df.at[0, 'cooling'],
              df.at[0, 'address.line'], df.at[0, 'price'], df.at[0, 'building_size.size'],
              df.at[0, 'year_built']]
          
        rows.append(row)
        
    columns = ['PropertyID', 'ListingID', 'PropStatus', 'PropType', 'ListDate', 
               'LastUpdate', 'Beds', 'Baths', 'Stories', 
               'Cooling', 'AddressLine', 'Price', 'BuildingSize', 
               'YearBuilt']
    table = pd.DataFrame(rows, columns=columns) #Convert to DataFrame
    return table
      
    
def searchResults(purch = True): #Make the purchasing choice True by default; assume user wants to buy
    """
    Parameters
    ----------
    purch : Boolean (Retrieve from isPurchasing() function)
    
    
    Returns
    -------
    properties : DataFrame of rental or purchasing option decided by get_User_Input()
    """
    if not purch:
        print("You have chosen to rent a home.")
        city, state, results = get_User_Input()
        url = "https://realtor.p.rapidapi.com/properties/v2/list-for-rent"

        querystring = {"sort":"relevance","city":city,"state_code":state,"limit":results,"offset":"0"}
        headers = {
                'x-rapidapi-host': "realtor.p.rapidapi.com",
                'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
        }
    else:
        print("You have chosen to buy a home.")
        city, state, results = get_User_Input()
        url = "https://realtor.p.rapidapi.com/properties/v2/list-for-sale"
        
        querystring = {"sort":"relevance","city":city,"limit":results,"offset":"0","state_code":state}
        headers = {
                'x-rapidapi-host': "realtor.p.rapidapi.com",
                'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
        }
        
    response = requests.request("GET", url, headers=headers, params=querystring)

    myarray = []
    for line in response.iter_lines(decode_unicode=True):
        if line:
            myline=json.loads(line)
            myarray.append(myline)

    #Normalize JSON data into dataframe for general property information
    properties = json_normalize(myarray, 'properties')
    return properties        

def get_Descriptions(properties):
    """
    Parameters
    ----------
    properties : DataFrame


    Returns
    -------
    Printed output of PropertyIDs as well as a text description of home/rental as you would likely see online

    """
    print("Preparing List Of Descriptions...")
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    headers = {
        'x-rapidapi-host': "realtor.p.rapidapi.com",
        'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
    }

    for i in properties['property_id']:
        print(i)
        querystring = {"property_id":i}
        response = requests.request("GET", url, headers=headers, params=querystring)
        #Insert JSON data into array
        myarray = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                myline=json.loads(line)
                myarray.append(myline)
        #Normalize JSON data into dataframe for general property information
        df = json_normalize(myarray, 'properties')
        description = df.at[0, 'description']
        print(description)
        print()
        
 
def nearbyRestaurants(properties):
    """
    Parameters
    ----------
    properties : DataFrame

    Returns
    -------
    Printed output of lat/long
    Table of Restaurant Results
    """
    print("Preparing Table Containing Nearby Restaurants...")
    url = "https://tripadvisor1.p.rapidapi.com/restaurants/list-by-latlng"

    headers = {
        'x-rapidapi-host': "tripadvisor1.p.rapidapi.com",
        'x-rapidapi-key': "e3bf3719c0msh2279903cd2d3765p1c38bajsn42dd6c3f2d2c" #Noah.Hellenthal@fortisureit.com
    }
    lats = []
    for lat in properties['address.lat']:
        lats.append(lat)
    lons = []
    for lon in properties['address.lon']:
        lons.append(lon)

    
    rows = []
    limit = 3 #Mult. with results input to get number of rows
    for r in range(0, len(lats)):
        print(lats[r])
        print(lons[r])
        print()
        querystring = {"limit": limit, "currency":"USD", "distance":"3", "lunit":"mi", "lang":"en_US", "latitude":lats[r], "longitude":lons[r]}
        for i in range(0, limit):
            response = requests.request("GET", url, headers=headers, params=querystring)
            #Insert JSON data into array
            myarray = []
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    myline = json.loads(line)
                    myarray.append(myline)
            #Normalize JSON data into dataframe for general property information
            df = json_normalize(myarray, 'data')
                   
            #Grab all the data (3 locations [limit] per each lat/lon combo)
            row = [df.at[i, 'location_id'], df.at[i, 'name'], df.at[i, 'latitude'], df.at[i, 'longitude'], df.at[i, 'timezone'], df.at[i, 'location_string'], 
                   df.at[i, 'ranking_position'], df.at[i, 'ranking_denominator'], df.at[i, 'rating'], df.at[i, 'distance'], df.at[i, 'price_level'], 
                   df.at[i, 'phone'], df.at[i, 'address']]
            rows.append(row)
        
    columns = ['LocationID', 'Name', 'Latitude', 'Longitude', 'Timezone', 'Location', 'RankingPosition', 'RankingDenominator', 'Rating', 'Distance',
                   'PriceLevel', 'Phone', 'Address']
    table = pd.DataFrame(rows, columns=columns) #Convert to DataFrame
    table = table.drop_duplicates() #If two homes are close, they may be close to the same restaurants, so drop copies
    return table


def nearbyAttractions(properties):
    """
    Parameters
    ----------
    properties : DataFrame

    Returns
    -------
    Printed output of lat/long
    Table of Attraction Results
    """
    print("Preparing Table Containing Nearby Attractions...")
    url =  "https://tripadvisor1.p.rapidapi.com/attractions/list-by-latlng"

    headers = {
        'x-rapidapi-host': "tripadvisor1.p.rapidapi.com",
        'x-rapidapi-key': "e3bf3719c0msh2279903cd2d3765p1c38bajsn42dd6c3f2d2c" #Noah.Hellenthal@fortisureit.com
    }
    lats = []
    for lat in properties['address.lat']:
        lats.append(lat)
    lons = []
    for lon in properties['address.lon']:
        lons.append(lon)

    
    rows = []
    limit = 10 #Mult. with results input to get number of rows
    for r in range(0, len(lats)):
        print(lats[r])
        print(lons[r])
        print()
        querystring = {"lunit":"mi","currency":"USD","limit":limit,"distance":"10","lang":"en_US","longitude":lons[r],"latitude":lats[r]}
        for i in range(0, limit):
            response = requests.request("GET", url, headers=headers, params=querystring)
            #Insert JSON data into array
            myarray = []
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    myline = json.loads(line)
                    myarray.append(myline)
            #Normalize JSON data into dataframe for general property information
            df = json_normalize(myarray, 'data')
                   
            #Grab all the data (3 locations [limit] per each lat/lon combo)
            row = [df.at[i, 'location_id'], df.at[i, 'name'], df.at[i, 'latitude'], df.at[i, 'longitude'], df.at[i, 'timezone'], df.at[i, 'location_string'], df.at[i, 'distance'], df.at[i, 'address_obj.street1'], df.at[i, 'address_obj.postalcode'], df.at[i, 'num_reviews']]
            rows.append(row)
        
    columns = ['LocationID', 'Name', 'Latitude', 'Longitude', 'Timezone', 'Location', 'Distance', 'StreetAddress', 'ZipCode', 'NumReviews']
               
    table = pd.DataFrame(rows, columns=columns) #Convert to DataFrame
    table = table.drop_duplicates() #If two homes are close, they may be close to the same restaurants, so drop copies
    table = table[(table[['LocationID']] != '0').all(axis=1)] #Drop entries where id = 0
    table.dropna(inplace=True) #Drop rows with a bunch of missing data
    return table

def homeResultsTable(properties):
    """
    Parameters
    ----------
    properties : DataFrame


    Returns
    -------
    table : DataFrame
        Simple table showing home information (purchasing option) obtained using PropertyIDs

    """
    print("Preparing Table Containing Home Information...")
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    headers = {
            'x-rapidapi-host': "realtor.p.rapidapi.com",
            'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
    }

    rows = [] #Create data array
    for i in properties['property_id']:
        querystring = {"property_id":i}
        response = requests.request("GET", url, headers=headers, params=querystring)
        #Insert JSON data into array
        myarray = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                myline=json.loads(line)
                myarray.append(myline)
                
        #Normalize JSON data into dataframe for general property information
        df = json_normalize(myarray, 'properties')
        #Grab all the data
        row = [df.at[0, 'property_id'], df.at[0, 'listing_id'], df.at[0, 'prop_status'],
              df.at[0, 'prop_type'], df.at[0, 'list_date'], df.at[0, 'last_update'],
              df.at[0, 'beds'], df.at[0, 'baths'], df.at[0, 'stories'],
              #df.at[0, 'garage'], 
              df.at[0, 'heating'], df.at[0, 'cooling'],
              df.at[0, 'address.line'], df.at[0, 'price'], df.at[0, 'building_size.size'],
              df.at[0, 'lot_size.size'], df.at[0, 'year_built']]
          
        rows.append(row)
        
    columns = ['PropertyID', 'ListingID', 'PropStatus', 'PropType', 'ListDate', 
               'LastUpdate', 'Beds', 'Baths', 'Stories', 
               #'Garage', 
               'Heating', 
               'Cooling', 'AddressLine', 'Price', 'BuildingSize', 'LotSize', 
               'YearBuilt']
    table = pd.DataFrame(rows, columns=columns) #Convert to DataFrame
    return table

def getTaxInfo(properties):
    """
    Parameters
    ----------
    properties : DataFrame

    Returns
    -------
    finalTaxTable : DataFrame
        Return a dataframe where the years are now the column names, renamed as "2018_Tax", and the values are transposed taxes        
    """
    print("Obtaining Tax Details...")
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    headers = {
        'x-rapidapi-host': "realtor.p.rapidapi.com",
        'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
    }
    df = pd.DataFrame()
    for i in properties['property_id']:
        querystring = {"property_id":i}
        response = requests.request("GET", url, headers=headers, params=querystring)

        #Insert JSON data into array
        myarray = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                myline=json.loads(line)
                myarray.append(myline)

        #Normalize JSON data into dataframe for general property information
        properties = json_normalize(myarray, 'properties')
        
        #Parse properties to create dataframe for tax history information
        tax_json = properties['tax_history'].to_json(orient ='index')
        tax_nm = pd.read_json(tax_json, orient='columns')
        tax = json_normalize(tax_nm[0])
        frames = [df, tax]
        df = pd.concat(frames)
    
    info = df.drop(columns = ['assessment.building', 'assessment.land', 'assessment.total'])
    
    resultsCount = 0
    newIndex = []
    years = []
    for i in info.index:
        if i == 0:
            resultsCount += 1
        newIndex.append(resultsCount-1)
        year = info.year.iloc[i]
        newYear = year + "_Tax"
        years.append(newYear)
    
    info['NewIndex'] = newIndex
    info['year'] = years

    finalTaxTable = info.pivot(index = 'NewIndex', columns = 'year', values = 'tax')
    
    return finalTaxTable


def getTaxRatio(df):
    """
    Parameters
    ----------
    df : DataFrame
        Contains price and tax columns
    Returns
    -------
    df : DataFrame
        new df with Tax Ratio column added
    """
    
    price = df['Price']
    recentTaxes = df.iloc[:, -1]
    df['TaxRatio'] = recentTaxes/price
    
    return df
    

def rentalBuildingInfo(properties):
    """
    Parameters
    ----------
    properties : DataFrame


    Returns
    -------
    firstPart : DataFrame
        The "first half" of the rental options dataset. The API for rentals is more nested than it is for purchasing options.
        Therefore, it is easier to cut it up.
        
    """
    print("Preparing Table Containing Rental Information...")
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    headers = {
            'x-rapidapi-host': "realtor.p.rapidapi.com",
            'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
    }

    rows = [] #Create data array
    for i in properties['property_id']:
        querystring = {"property_id":i}
        response = requests.request("GET", url, headers=headers, params=querystring)
        #Insert JSON data into array
        myarray = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                myline=json.loads(line)
                myarray.append(myline)
                
        #Normalize JSON data into dataframe for general property information
        df = json_normalize(myarray, 'properties')
        #Grab all the data
        row = [df.at[0, 'property_id'], df.at[0, 'listing_id'], df.at[0, 'prop_status'],
              df.at[0, 'prop_type'], df.at[0, 'list_date'], df.at[0, 'last_update'],
              df.at[0, 'address.line'],  df.at[0, 'year_built']]
          
        rows.append(row)
        
    columns = ['PropertyID', 'ListingID', 'PropStatus', 'PropType', 'ListDate', 
               'LastUpdate', 'AddressLine', 'YearBuilt']
    firstPart = pd.DataFrame(rows, columns=columns) #Convert to DataFrame
        
    return firstPart

def rentalRoomInfo(properties):
    """
    Parameters
    ----------
    properties : DataFrame


    Returns
    -------
    info : DataFrame
        The "second half" of the rental options dataset. The API for rentals is more nested than it is for purchasing options.
        Therefore, it is easier to cut it up.
        
    """
    print("Obtaining Floor Details...")
    url = "https://realtor.p.rapidapi.com/properties/v2/detail"

    headers = {
        'x-rapidapi-host': "realtor.p.rapidapi.com",
        'x-rapidapi-key': "efecd4bcfemshd20188d5bcafb66p14fd77jsnb8685b9debc2" #nhellenthal@outlook.com
    }
    df = pd.DataFrame()
    for i in properties['property_id']:
        querystring = {"property_id":i}
        response = requests.request("GET", url, headers=headers, params=querystring)

        #Insert JSON data into array
        myarray = []
        for line in response.iter_lines(decode_unicode=True):
            if line:
                myline=json.loads(line)
                myarray.append(myline)

        #Normalize JSON data into dataframe for general property information
        properties = json_normalize(myarray, 'properties')
        
        #Parse properties to create dataframe for school information
        floors_json = properties['floor_plans'].to_json(orient ='index')
        floors_nm = pd.read_json(floors_json, orient='columns')
        floors = json_normalize(floors_nm[0])
        frames = [df, floors]
        df = pd.concat(frames)
    
    info = df.drop(columns = ['photo_count', 'type', 'availability.available', 'availability.date', 'availability.href',
                'availability.text', 'availability.status', 'photo.href'])
    return info

def combineRentals(df1, df2):
    """
    Parameters
    ----------
    df1 : DataFrame
    df2 : DataFrame

    Returns
    -------
    final : DataFrame
        Combine two DataFrames with different shapes by uniting on the "PropertyID" column.

    """
    print("Generating Final Rental Dataset...")
    #Duplicate Rows in DF1 to match available rooms
    j = -1
    rows = []
    
    for i in df2.index:
        if i == 0:
            j += 1
        rows.append(df1.iloc[j])
    revisedf1 = pd.DataFrame(rows, columns=df1.columns)
    idList = np.asarray(revisedf1['PropertyID'])
    df2.insert(loc = 0, column = 'PropertyID', value = idList)
    
    final = pd.merge(revisedf1, df2, on='PropertyID')
    final = final.drop_duplicates()
    return final
    

#-----------------------------------------------------------------------------
#Runable functions
startScreen()

#Block for Sold Homes
prop = soldHomes()
sold = soldHomesTableResults(prop)
print(sold)
tax = getTaxInfo(prop)
print(tax)
combo = pd.concat([sold, tax], axis=1)
final = getTaxRatio(combo)
print(final)
final.to_csv("SoldHomes.csv", header=True, index=False)

#Block for Purchasing or buying a home
"""
purch = isPurchasing()
prop = searchResults(purch)
if purch:
    homes = homeResultsTable(prop)
    print(homes)
    tax = getTaxInfo(prop)
    print(tax)
    combo = pd.concat([homes, tax], axis=1)
    print(combo)
    final = getTaxRatio(combo)
    print(final)
    final.to_csv("HomesForSale.csv", header=True, index=False)
else:
    df1 = rentalBuildingInfo(prop)
    print(df1)
    df2 = rentalRoomInfo(prop)
    print(df2)
    final = combineRentals(df1, df2)
    print(final)
    final.to_csv("RentalsForSale.csv", header=True, index=False)
"""

#TripAdvisor Restaurants and Attractions
"""
restaurants = nearbyRestaurants(prop)
print(restaurants)
restaurants.to_csv("Restaurants.csv", header=True, index=False)

attractions = nearbyAttractions(prop)
print(attractions)
attractions.to_csv("Attractions.csv", header=True, index=False)
"""
