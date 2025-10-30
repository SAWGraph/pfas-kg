import os
from rdflib.namespace import OWL, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import Literal
import pandas as pd
import re
import json
import ast
import logging
from datetime import datetime
from datetime import date
from pyutil import *
from shapely.geometry import Point
from pathlib import Path

## declare variables
logname = "log"
code_dir = Path(__file__).resolve().parent.parent
state=input("state code?")
fips_lookup = {'AL':'01','AK':'02','AZ':'04',
'AR':'05','CA':'06','CO':'08','CT':'09','DE':'10','DC':'11',
'FL':'12','GA':'13','HI':'15','ID':'16','IL':'17','IN':'18',
'IA':'19','KS':'20','KY':'21','LA':'22','ME':'23','MD':'24',
'MA':'25','MI':'26','MN':'27','MS':'28','MO':'29','MT':'30',
'NE':'31','NV':'32','NH':'33','NJ':'34','NM':'35','NY':'36',
'NC':'37','ND':'38','OH':'39','OK':'40','OR':'41','PA':'42',
'PR':'72','RI':'44','SC':'45','SD':'46','TN':'47','TX':'48',
'UT':'49','VT':'50','VA':'51','VI':'78','WA':'53','WV':'54',
'WI':'55','WY':'56'}
statecode = f"US%3A{fips_lookup[state]}"

##data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/water-quality-data-portal/"
metadata_dir = root_folder / "federal/us-wqp/metadata_3/"
output_dir = root_folder / "federal/us-wqp/triples/"

##namespaces
prefixes = {}
prefixes['us_wqp'] = Namespace(f'http://w3id.org/sawgraph/v1/us-wqp#')
prefixes['us_wqp_data'] = Namespace(f'http://w3id.org/sawgraph/v1/us-wqp-data#')
prefixes['geoconnex'] = Namespace(f'http://geoconnex.us/')
prefixes['qudt'] = Namespace(f'http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://w3id.org/coso/v1/contaminoso#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['gcx_wqp']= Namespace(f'https://geoconnex.us/iow/wqp/')
prefixes['wbd_data']= Namespace(f'http://w3id.org/hyfo/wbd/v1/wbd-data#')
prefixes["unit"] = Namespace("http://qudt.org/vocab/unit/")
prefixes['kwg-ont'] = Namespace("http://stko-kwg.geog.ucsb.edu/lod/ontology/")
prefixes['prov'] =  Namespace("http://www.w3.org/ns/prov#")

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info(f"Running triplification for WQP stations {state}")

def main():
    df = load_data()
    print(df.info(show_counts=True))
    global cv
    cv = get_controlledvocabs() #these build to a global variable
    kg = triplify(df)
    kg.serialize(output_dir /f'{state}_wqp_sites.ttl', format='turtle')

def load_data():
    df = pd.read_csv(data_dir / f'{state}-pfas-stations.csv', dtype={'Location_CountyCode': str, 'Location_HUCEightDigitCode': str, 'Location_HUCTwelveDigitCode': str})
    #df = df.dropna(axis='columns', how='all') #drop columns that are all NA
    ## TODO This is a temporary filter to reduce to only likely pfas sites in Maine based on organization (PFAS data only had 3)
    #if state == 'ME':
    #    df = df[df['Org_Identifier'].isin(['MEDEP_WQX', 'OST_SHPD', 'USGS'])]
    print('types', df['Location_Type'].unique())
    return df

def Initial_KG():
    # prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg

def get_controlledvocabs():
    cv= {}
    metadata_files = []
    return cv

def get_attributes(row):
    site = {'id': row['Location_Identifier'].replace(" ", ""),
            'provider':'NWIS' if row['ProviderName']=='USGS' else row['ProviderName'],
            'org_id': f"{row['Org_Identifier']}-{row['Location_StatePostalCode']}" if row['Org_Identifier'] == 'USGS' else row['Org_Identifier'], #add state to org id to make unique except for USGS
            'name': row['Location_Name'],
            'geom': Point(row['Location_Longitude'], row['Location_Latitude']),
            'lat':row['Location_Latitude'],
            'long':row['Location_Longitude']
            }
    if pd.notnull(row['Org_FormalName']):
        site['org_name'] = row['Org_FormalName']
  
    
    if pd.notnull(row['Location_Type']):
        site['type_label'] = row['Location_Type']
        site['type'] = ''.join(e for e in str(row['Location_Type']) if e.isalnum()) 
    
    #additional location information varies by data provider. Sometimes contains a list or dictionary of attributes. 
    #if pd.notnull(row['Location_Description']):
    #    try:
    #        site['description'] = ast.literal_eval(row['Location_Description'])
    #    except:
    #        if ";" in row['Location_Description']:
    #            site['description'] = row['Location_Description'].split(";")
    #        else: 
    #            site['description'] = row['Location_Description']
        #if type(site['description'])== dict:
        #    print(site['description'].keys())
        #if type(site['description']) == list:
        #        print(site['description'])

    if pd.notnull(row['Location_HUCTwelveDigitCode']):
        site['huc12'] = row['Location_HUCTwelveDigitCode']


    
    return site

def get_iris(site: dict)-> dict:
    #print(site)
    iris = {
        #'wqp_site': prefixes['gcx'][f"wqp/{site['provider']}/{site['org_id']}/{site['id']}"],
        'wqp_site': prefixes['gcx_wqp'][f"{site['id']}"],
        'wqp_site_geom':prefixes['us_wqp_data'][f"d.wqp.SiteGeometry.iow.wqp.{site['id']}"],  #TODO how to create geometry for gcx features?
        'organization': prefixes['us_wqp_data'][f"organization.{site['org_id']}"],
        'feature': prefixes['us_wqp_data'][f"d.wqp.SampledFeature.{site['id']}"],
        'featureType': prefixes['us_wqp_data'][f"{'featureType'}.{site['type']}"]
        
    }
    if 'huc12' in site.keys():
        iris['huc12'] = prefixes['wbd_data'][f"d.HUC12.{site['huc12']}"]
        
    return iris

def triplify(df: pd.DataFrame):
    kg = Initial_KG()

    for idx, row in df.iterrows():
        site = get_attributes(row)
        iris = get_iris(site)

        #triplify Sample Point
        kg.add((iris['wqp_site'], RDF.type, prefixes['us_wqp']['Site']))
        kg.add((iris['wqp_site'], RDFS.label, Literal(f"{site['name']} ({site['id']}) site data in the Water Quality Portal", datatype=XSD.string)))
        kg.add((iris['wqp_site'], prefixes['us_wqp']['siteId'], Literal(site['id'], datatype=XSD.string)))
        kg.add((iris['wqp_site'], prefixes['us_wqp']['siteName'], Literal(site['name'], datatype=XSD.string)))
        kg.add((iris['wqp_site'], prefixes['prov']['wasAttributedTo'], iris['organization']))
        kg.add((iris['wqp_site'], prefixes['coso']['pointFromFeature'], iris['feature']))

        #triplify sample point geometry
        kg.add((iris['wqp_site'], prefixes['geo']['hasGeometry'], iris['wqp_site_geom']))
        kg.add((iris['wqp_site_geom'], RDF.type, prefixes['geo']['Geometry']))
        kg.add((iris['wqp_site_geom'], prefixes['geo']['asWKT'],  Literal(site['geom'],  datatype=prefixes["geo"]["wktLiteral"])))

       

        #triplify Feature
        kg.add((iris['feature'], RDF.type, prefixes['us_wqp']['SampledFeature']))
        kg.add((iris['feature'], RDFS.label, Literal(f"{site['type_label']}: from {site['provider']} {site['org_id']} {site['name']}", datatype=XSD.string)))
        kg.add((iris['feature'], prefixes['us_wqp']['locationType'], iris['featureType']))
        #TODO add feature geometry

        if 'huc12' in iris.keys():
            kg.add((iris['wqp_site'], prefixes['kwg-ont']['sfWithin'], iris['huc12']))
            kg.add((iris['huc12'], RDF.type, prefixes['us_wqp']['SampledFeature']))
            #TODO huc12 as sampled feature instead of using spatial relation (link back to sample)

    return kg


if __name__ == "__main__":
    main()