# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import pandas as pd #importing the Pandas Library as 'pd'
import numpy as np

#Imports spatial libraries
from keplergl import KeplerGl #importing KeplerGl
import geopandas as gpd #importing geopandas as 'gpd'
from shapely.geometry import Point
from shapely.geometry import box
import shapely.wkt
from geopy.geocoders import Nominatim # Imports the geopy for the geocoding
import geojson
from geojson import Point, Feature, FeatureCollection, dump

import xml.etree.ElementTree as ET

import requests

from time import time
# -

# This map reads in data on (from the Data folder)
# 1. Lower super output areas and the index of multiple deprivation
# 2. Food outlets data
# 3. The location of foodbanks
# 4. Ward area data of Liverpool and associated data
#
# and processes it 
# - geocoding of point data - of food banks and food outlets 
# - matches the ward area data to the ward shape files
# - Converts the layer data (lsoas and wards) into qunitiles
#
#
# and writes it out as four geojson files to the Out folder in the Data folder

# # Reads in the Liverpool Lower Super Output Areas (lsoas) with index of multiple deprivation and creates quintile variables

filename = "Data/Liverpool_lsoa.geojson"
file = open(filename)
Liverpool_lsoa = gpd.read_file(file)

list(Liverpool_lsoa)

metrics=['Total population: mid 2015 (excluding prisoners)',
 'Dependent Children aged 0-15: mid 2015 (excluding prisoners)',
 'Population aged 16-59: mid 2015 (excluding prisoners)',
 'Older population aged 60 and over: mid 2015 (excluding prisoners)',
 'Working age population 18-59/64: for use with Employment Deprivation Domain (excluding prisoners)',
    'Income Domain numerator',
 'Income Deprivation Affecting Children Index (IDACI) numerator',
 'Income Deprivation Affecting Older People Index (IDAOPI) numerator',
 'Employment Domain numerator',
 'Staying on in education post 16 indicator',
 'Entry to higher education indicator',
 'Adult skills and English language proficiency indicator',
 'Years of potential life lost indicator',
 'Comparative illness and disability ratio indicator',
 'Acute morbidity indicator',
 'Mood and anxiety disorders indicator',
 'Road distance to a post office indicator (km)',
 'Road distance to a primary school indicator (km)',
 'Road distance to general store or supermarket indicator (km)',
 'Road distance to a GP surgery indicator (km)',
 'Household overcrowding indicator',
 'Homelessness indicator (rate per 1000 households)',
 'Owner-occupation affordability (component of housing affordability indicator)',
 'Private rental affordability (component of housing affordability indicator)',
 'Housing affordability indicator',
 'Housing in poor condition indicator',
 'Houses without central heating indicator',
 'Road traffic accidents indicator',
 'Nitrogen dioxide (component of air quality indicator)',
 'Benzene (component of air quality indicator)',
 'Sulphur dioxide (component of air quality indicator)',
 'Particulates (component of air quality indicator)',
 'Air quality indicator',
        ]

# +
# Reads in the etl data 

efdi_engwales=pd.read_csv("Data/efdi_england.csv")
# -

efdi_engwales.head(n=5)

#Merge with the lsoa data
Liverpool_lsoa=Liverpool_lsoa.merge(efdi_engwales, how='inner', left_on='LSOA code (2011)', right_on='LSOA or DZ')

Liverpool_lsoa.head()

Liverpool_lsoa = gpd.GeoDataFrame(Liverpool_lsoa, geometry=Liverpool_lsoa["geometry"], crs = 'WGS84' )

# +
# Adds data to the Kepler map
#map.add_data("Liverpool_lsoa", name="Liverpool_lsoa")
# -

metrics=metrics+['Score']

# +
data_ranked=pd.DataFrame(Liverpool_lsoa["LSOA code (2011)"])

for measure in metrics:
# rank(pct=True), gives the percentile mul is multiply by 5
   new_col=pd.DataFrame(np.ceil(Liverpool_lsoa[measure].rank(pct=True).mul(5)).astype('Int64')).rename(columns={measure: measure+"_rank"})
   data_ranked=pd.concat([data_ranked, new_col], axis=1)



#Liverpool_lsoa=gç(lsoa)
#Merge with the lsoa data


Liverpool_lsoa=Liverpool_lsoa.merge(data_ranked, how='inner', left_on='LSOA code (2011)', right_on='LSOA code (2011)')
#Liverpool_lsoa=Liverpool_lsoa.merge(data_ranked,how='inner', on='LSOA code (2011)')

#Liverpool_lsoa = gpd.GeoDataFrame(Liverpool_lsoa, geometry=Liverpool_lsoa["geometry"], crs ='4326')



# -

data_ranked

# Write out the food outlets location as a geojson for use in the mapbox map
Liverpool_lsoa.to_file("Data/Out/Liverpool_lsoa.geojson", driver='GeoJSON')

list(Liverpool_lsoa)

# # The geocoding function (to code the food outlets data and the food banks data)

# Initialises the geocoding
geolocator = Nominatim(user_agent="Liverpool_analysis")


# +
# The geocoding function

def long_lat_func(x):
  try:
    location = geolocator.geocode(str(x))
    # Parse the tuple
    return location.latitude , location.longitude
  except:
    return None, None


# -

# Code to speed up the geocoding
'''


import multiprocessing from geopy.geocoders 
import Nominatim geocoder = Nominatim() 
def worker(address):
    return geocoder.geocode(address) 

pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()) 
addresses = ['58 Victoria Embankment, London', 'Ferry Road, Edinburgh'] l
ocations = pool.map(worker, addresses) '''

# # Adding in the restaurant locations

# Example of the xml that is being parsed
'''
<Header>
    <ExtractDate>2021-01-27</ExtractDate>
    <ItemCount>3959</ItemCount>
    <ReturnCode>Success</ReturnCode>
  </Header>
  <EstablishmentCollection>
    <EstablishmentDetail>
      <FHRSID>1264123</FHRSID>
      <LocalAuthorityBusinessID>78306</LocalAuthorityBusinessID>
      <BusinessName>@Desserts</BusinessName>
      <BusinessType>Takeaway/sandwich shop</BusinessType>
      <BusinessTypeID>7844</BusinessTypeID>
      <AddressLine1>17, Central Shopping Centre Ranelagh Street</AddressLine1>
      <AddressLine3>Liverpool</AddressLine3>
      <AddressLine4>Liverpool</AddressLine4>
      <PostCode>L1 1QE</PostCode>
      <RatingValue>AwaitingInspection</RatingValue>
      <RatingKey>fhrs_awaitinginspection_en-GB</RatingKey>
      <RatingDate xsi:nil="true"/>
      <LocalAuthorityCode>414</LocalAuthorityCode>
      <LocalAuthorityName>Liverpool</LocalAuthorityName>
      <LocalAuthorityWebSite>http://www.liverpool.gov.uk</LocalAuthorityWebSite>
      <LocalAuthorityEmailAddress>environmental.health@liverpool.gov.uk</LocalAuthorityEmailAddress>
      <Scores/>
      <SchemeType>FHRS</SchemeType>
      <NewRatingPending>False</NewRatingPending>
      <Geocode>
      
      '''

# +
tree = ET.parse('Data/Liverpool_food_outlets.xml')
root = tree.getroot()



df_cols = ["LocalAuthorityBusinessID", "BusinessName","BusinessAddress","BusinessType","BusinessTypeID", "RatingKey", "Postcode"]
rows = []

food_outlets_df  = pd.DataFrame(rows, columns = df_cols)

for neighbor in root.iter('EstablishmentCollection'):
   for node in neighbor:
       bus_laid=node.find("LocalAuthorityBusinessID").text  if node is not None else None
       bus_rate=node.find("RatingKey").text if node is not None else None  
       bus_address=""
       try:
        bus_address=bus_address+" "+node.find('AddressLine1').text 
       except:
        bus_address=bus_address     
       try:
        bus_address=bus_address+" "+node.find('AddressLine2').text 
       except:
        bus_address=bus_address 
       try:
        bus_address=bus_address+" "+node.find('AddressLine3').text 
       except:
        bus_address=bus_address
       try:
         bus_postcode=node.find("PostCode").text if node is not None else None
         bus_address=bus_address+" "+bus_postcode+ " "+"UK" 
       except:
          bus_postcode=("missing")    
       bus_type=node.find("BusinessType").text if node is not None else None
       bus_name=node.find("BusinessName").text  if node is not None else None
       bus_type_id=node.find("BusinessTypeID").text if node is not None else None
       try:
         bus_postcode=node.find("PostCode").text if node is not None else None
       except:
          bus_postcode=("missing") 
       rows.append({"LocalAuthorityBusinessID": bus_laid, "BusinessName": bus_name, "BusinessAddress": bus_address,
                  "BusinessType": bus_type,"BusinessTypeID":bus_type_id, "Postcode": bus_postcode, "RatingValue": bus_rate})

food_outlets_df = pd.DataFrame(rows, columns = df_cols)

food_outlets_df.head(n=5)
# -

pd.DataFrame(food_outlets_df["BusinessType"].value_counts())

# +
# Applies the geocoding function

start_time = time()
food_outlets_df["lat"] , food_outlets_df["lon"] = zip(*food_outlets_df["BusinessAddress"].apply(long_lat_func))

time_elapsed= round((time() - start_time)/60,2)
print("--- %s minutes ---" % (time_elapsed))
# -

food_outlets_df.head(n=5)

# +
# Subsets to drop the na terms
food_outlets_df=food_outlets_df.dropna(subset=['lon', 'lat'])


# Subsets to drop the na terms
food_outlets_df =food_outlets_df[food_outlets_df["Postcode"]!="missing"]

#Converts the longitude and latitude as points data to give the geocoordinates for the data frame
geometry = [Point(xy) for xy in zip(food_outlets_df['lon'], food_outlets_df['lat'])]



# Create a GeoDataFrame from art and verify the type
food_outlets_geo = gpd.GeoDataFrame(food_outlets_df, crs = 'epsg:4326' , geometry = geometry)


# Write out the food outlets location as a geojson for use in the mapbox map
food_outlets_geo.to_file("Data/Out/Food_outlets_geo.geojson", driver='GeoJSON')


# -

# # Adding in food initatives

# ls Data/

# !pip3 install openpyxl

Affordable_food_sheet = pd.ExcelFile('Data/Affordable_food_inititives_Liverpool.xlsx')

Affordable_food_sheet.sheet_names

# +
Pantrys=pd.read_excel(Affordable_food_sheet, 'Pantrys, Com markets, Com Shops')
Pantrys=Pantrys.iloc[0:27] # avoid the numbers that has slipped down the sheet
Pantrys=Pantrys.rename(columns=lambda x: x.strip())

Community_cafes=pd.read_excel(Affordable_food_sheet, 'Community cafes ')
Community_cafes=Community_cafes.dropna(how='all')
Community_cafes=Community_cafes.rename(columns=lambda x: x.strip())

Free_food_inititives=pd.read_excel(Affordable_food_sheet, 'Free food inititives ')
Free_food_inititives=Free_food_inititives.dropna(how='all')
Free_food_inititives=Free_food_inititives.rename(columns=lambda x: x.strip())

Pantrys['Category']='Pantry'
Community_cafes['Category']='Community_cafes'
Free_food_inititives['Category']='Free_food_inititives'

Affordable_food_outlets_df = pd.concat([Pantrys,Community_cafes,Free_food_inititives] , ignore_index=True)


# -

 Affordable_food_outlets_df=Affordable_food_outlets_df.rename(columns=lambda x: x.strip())

list(Affordable_food_outlets_df)

Affordable_food_outlets_df['Addresses']=Affordable_food_outlets_df['Address']+" "+Affordable_food_outlets_df["Postcode"]+" "+"Liverpool UK"

Affordable_food_outlets_df['Category'].value_counts()

# +
# Applies the geocoding function

start_time = time()
Affordable_food_outlets_df["lat"] , Affordable_food_outlets_df["lon"] = zip(*Affordable_food_outlets_df["Addresses"].apply(long_lat_func))

time_elapsed= round((time() - start_time)/60,2)
print("--- %s minutes ---" % (time_elapsed))

# +
# Subsets to drop the na terms
Affordable_food_outlets_df=Affordable_food_outlets_df.dropna(subset=['lon', 'lat'])
Affordable_food_outlets_df=Affordable_food_outlets_df.dropna(subset=['Name'])
Affordable_food_outlets_df=Affordable_food_outlets_df.dropna(subset=['Address'])

#Converts the longitude and latitude as points data to give the geocoordinates for the data frame
geometry = [Point(xy) for xy in zip(Affordable_food_outlets_df['lon'], Affordable_food_outlets_df['lat'])]



# Create a GeoDataFrame from art and verify the type
Affordable_food_outlets = gpd.GeoDataFrame(Affordable_food_outlets_df, crs = 'epsg:4326' , geometry = geometry)
# -

Affordable_food_outlets_df

Affordable_food_outlets.plot()

# Write out the food initatives location as a geojson for use in the mapbox map
Affordable_food_outlets.to_file("Data/Out/Affordable_food_iniatives.geojson", driver='GeoJSON')

# # Emergency food initatives

Emergency_food_sheet = pd.ExcelFile('Data/emergency_food_providers.xlsx')

Emergency_food_sheet.sheet_names

# +
Food_parcel=pd.read_excel(Emergency_food_sheet, 'Sheet1')
Food_parcel=Food_parcel.dropna(how='all')
Food_parcel=Food_parcel.rename(columns=lambda x: x.strip())
Food_parcel=Food_parcel.rename(columns={'Emergency food parcel provider':'Name'})

Meal_providers=pd.read_excel(Emergency_food_sheet, 'Sheet2')
Meal_providers=Meal_providers.dropna(how='all')
Meal_providers=Meal_providers.rename(columns=lambda x: x.strip())
Meal_providers=Meal_providers.rename(columns={'Emergency meal provider':'Name'})


Food_parcel['Category']='Food_parcels'
Meal_providers['Category']='Meal_providers'


Emergency_food_suppliers = pd.concat([Food_parcel,Meal_providers] , ignore_index=True)


# -

Emergency_food_suppliers 


Emergency_food_suppliers['Addresses']=Emergency_food_suppliers['Address']+" "+Emergency_food_suppliers["Postcode"]+" "+" UK"

# +
# Drop the mobile food suppliers
Emergency_food_suppliers=Emergency_food_suppliers[Emergency_food_suppliers['Address']!="Mobile "]

start_time = time()
Emergency_food_suppliers["lat"] , Emergency_food_suppliers["lon"] = zip(*Emergency_food_suppliers["Addresses"].apply(long_lat_func))

time_elapsed= round((time() - start_time)/60,2)
print("--- %s minutes ---" % (time_elapsed))

# +
# Subsets to drop the na terms
Emergency_food_suppliers=Emergency_food_suppliers.dropna(subset=['lon', 'lat'])
Emergency_food_suppliers=Emergency_food_suppliers.dropna(subset=['lon', 'lat'])
Emergency_food_suppliers=Emergency_food_suppliers.dropna(subset=['Name'])
Emergency_food_suppliers=Emergency_food_suppliers.dropna(subset=['Address'])

#Converts the longitude and latitude as points data to give the geocoordinates for the data frame
geometry = [Point(xy) for xy in zip(Emergency_food_suppliers['lon'], Emergency_food_suppliers['lat'])]



# Create a GeoDataFrame from the data
Emergency_food_suppliers= gpd.GeoDataFrame(Emergency_food_suppliers, crs = 'epsg:4326' , geometry = geometry)
# -

Emergency_food_suppliers.plot()

Emergency_food_suppliers.to_file("Data/Out/Emergency_food_suppliers.geojson", driver='GeoJSON')

# # Extract the ward area boundaries from the API

# +
URL = "http://statistics.data.gov.uk/resource.json?uri=http%3A%2F%2Fstatistics.data.gov.uk%2Fid%2Fstatistical-geography%2F{code}%2Fgeometry"

# Function to call the API with the geography codes and return the shape files using the API
def get_shape(gss_code):
    return requests.get(URL.format(code=gss_code)).json()


# +
# Import the ward codes
# -

food_poverty_stats=pd.read_csv("Data/Food_Poverty_Health_stats.csv")
food_poverty_stats.tail(n=5)

# Subsets so we look just at 2020 data and drop the general all Liverpool data
food_poverty_stats2020=food_poverty_stats[(food_poverty_stats['Year']==2020) & (food_poverty_stats['WardName']!="Liverpool")]
food_poverty_stats2020.head(n=5)

# +
#Create a list of features to stick the different wards together into a single geojson
features = []


for ward in food_poverty_stats2020['WardCode']:
       boundary=get_shape(ward)
       # Extract the polygon coordinates from geojson
       polygon_boundary=boundary[0]["http://www.opengis.net/ont/geosparql#asWKT"][0]['@value']
       # Use shapely to load into the geometry
       features.append(Feature(geometry=shapely.wkt.loads(polygon_boundary),properties={"WardCode": ward }))
        
        
Liverpool_wards = FeatureCollection(features)


# Write it out as a geojson
with open('Data/Liverpool_wards.geojson', 'w') as f:
   dump(Liverpool_wards, f)

# Read in the geojson
filename = "Data/Liverpool_wards.geojson"
file = open(filename, encoding='latin1')
Liverpool_wards = gpd.read_file(file)



# -

# Merge with the other ward data, seems simpler to do it this way, but maybe not
Liverpool_wards=Liverpool_wards.merge(food_poverty_stats2020, how='inner', on='WardCode')

list(Liverpool_wards)

measures=["Ward_DASR_Cancers_Under75","Ward_DASR_cvd_Under754" ,
          "Ward_Reception_Overweight_Obese", 
         "Ward_Year6_Overweight_obese" , 
          "Ward_alcohol_specific_admissions"]


# +
wards_ranked=pd.DataFrame(food_poverty_stats2020["WardCode"])


# converts the variables into quintiles and then adds to the original Geodataframe (adding as a straight dataframe causes problems)
for measure in measures: 
    new_col=pd.DataFrame(np.ceil(food_poverty_stats2020[measure].rank(pct=True).mul(5)).astype('Int64')).rename(columns={measure: measure+"_rank"})
    wards_ranked=pd.concat([wards_ranked, new_col], axis=1)


# -

# Merge with the other ward data, seems simpler to do it this way, but maybe not
Liverpool_wards=Liverpool_wards.merge(wards_ranked, on='WardCode')

Liverpool_wards

Liverpool_wards.to_file("Data/Out/Liverpool_wards.geojson", driver='GeoJSON')

# # Extracting the Liverpool border area file

# +
features=[]

Liv=food_poverty_stats[(food_poverty_stats['WardName']=="Liverpool") & (food_poverty_stats['Year']==2020) ]
# Get the shape file for the Liverpool city code
boundary=get_shape("E08000012")
# -

polygon_boundary=boundary[0]["http://www.opengis.net/ont/geosparql#asWKT"][0]['@value']
# Use shapely to load into the geometry
features.append(Feature(geometry=shapely.wkt.loads(polygon_boundary),properties={"WardCode": "E08000012" }))

Liverpool_boundary = FeatureCollection(features)

# Write it out as a geojson, note this may require reformatting to reload into mapbox
with open('Data/Out/Liverpool_boundary.geojson', 'w') as f:
    dump( Liverpool_boundary, f)

# # Adding in the foodbank information

foodbanks=pd.read_csv("Data/Liverpool_foodbanks_geocode_input.csv")

foodbanks.head(n=3)


# +
# Adjust the coding of the address to make the geocoding more accurate

def complete_address(x):
  if "Bootle" in x:
    return x+", Bootle, UK"
  if "Waterloo" in x:
    return x+", Waterloo, UK"
  if "Speke" in x:
    return x+", Speke, UK"
  else:
    return x+", Liverpool, UK"


foodbanks["full_address"]=foodbanks["name"].apply(complete_address)

# +
# Applies the geocoding function

start_time = time()

foodbanks["lat"] , foodbanks["lon"] = zip(*foodbanks["full_address"].apply(long_lat_func))


time_elapsed= round((time() - start_time)/60,2)
print("--- %s minutes ---" % (time_elapsed))

# +
# Subsets to drop the na terms
foodbanks=foodbanks.dropna(subset=['lon', 'lat'])

# Foodbanks remove Bootle
foodbanks=foodbanks[~foodbanks["full_address"].str.contains('Bootle')]

#Converts the longitude and latitude as points data to give the geocoordinates for the data frame
geometry = [Point(xy) for xy in zip(foodbanks['lon'], foodbanks['lat'])]


# Create a GeoDataFrame 
foodbanks_geo = gpd.GeoDataFrame(foodbanks, crs = 'epsg:4326' , geometry = geometry)

from shapely.ops import cascaded_union
#Liverpool_boundary = Liverpool_wards.dissolve(by='continent', aggfunc='sum')


# +
# Selects the points that fall within Liverpool

PointInPoly = gpd.sjoin(foodbanks_geo,Liverpool_lsoa, how='left',op='within') 

# +
# Create a GeoDataFrame from art and verify the type
foodbanks_geo = gpd.GeoDataFrame(PointInPoly, crs = 'epsg:4326' , geometry = geometry)


#map.add_data(data=foodbanks_geo, name="food_banks")



# -

foodbanks_geo.plot()

foodbanks_geo.to_file("Data/Out/Foodbanks.geojson", driver='GeoJSON')


# # Get a bounding box

# This expands the bounding box around Liverpool so that the map border is wider than the area of the Liverpool shape file

Liverpool_wards_expand=Liverpool_wards

Liverpool_wards_expand.total_bounds

Liverpool_wards_expand.geometry.iloc[0] = shapely.affinity.scale(Liverpool_wards_expand.geometry.iloc[0], xfact=1.05, yfact=1.05, origin='center')

Liverpool_wards_expand.total_bounds

# Check that everything has been written out
# ! ls Data


pwd

# ls

