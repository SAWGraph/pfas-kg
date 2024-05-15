import os
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
import pandas as pd
import geopandas as gpd
import json
import encodings
import logging
import csv
from datetime import datetime
import sys
import math
import numpy as np
from datetime import date
from pyutil import *
from pathlib import Path
from shapely.geometry import Point

code_dir = Path(__file__).resolve().parent.parent
#print(code_dir)
#sys.path.insert(0, str(code_dir))
#from variable import NAME_SPACE, _PREFIX

## declare variables
logname = "log"

## data path
root_folder =Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/frs_echo/"
metadata_dir = None
output_dir = root_folder / "code/us-pat-is/"

##namespaces
us_frs = Namespace(f"http://sawgraph.spatialai.org/v1/us-frs#")
us_frs_data = Namespace(f"http://sawgraph.spatialai.org/v1/us-frs-data#")
fio = Namespace(f"http://sawgraph.spatialai.org/v1/fio#")
naics = Namespace(f"http://sawgraph.spatialai.org/v1/fio/naics#")
sic = Namespace(f"http://sawgraph.spatialai.org/v1/fio/sic#")
aik_pfas_ont = Namespace(f"http://aiknowspfas.skai.maine.edu/lod/ontology/")  #this will be replaced with something for sawgraph, but unsure of namespace for geospatial entities
coso = Namespace(f'http://sawgraph.spatialai.org/v1/contaminoso#')
geo = Namespace(f'http://www.opengis.net/ont/geosparql#')

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for facilities")

def main():
    '''main function initializes all other functions'''
    df = load_data()
    kg = triplify(df)

    kg_turtle_file = "us-frs-data-echo.ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger('Finished triplifying pfas analytics tool facilities.')

def load_data():
    #df = pd.read_csv(data_dir / "industrysectors_ME.csv")
    df = pd.read_csv(data_dir / 'state_combined_me' / 'ME_FACILITY_FILE.CSV', low_memory=False)
    df_federal = pd.read_csv(data_dir /'state_combined_me'/'222910070_ME_FEDERAL.CSV') #this was a custom ezquery to get agency codes
    print(df_federal.info())
    df = df.set_index('REGISTRY_ID', drop=False)
    df_federal = df_federal.set_index('REGISTRY_ID')
    df = df.join(df_federal, how='left', rsuffix='_FEDERAL')
    #replace - with nan
    print(df.info(verbose=True))
    #print(df[df.REGISTRY_ID_FEDERAL > 0])
    #print(df.describe())
    logger = logging.getLogger('Data loaded to dataframe.')
    #print(df)
    return df


def Initial_KG():
    #prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    #for prefix in prefixes:
    #    kg.bind(prefix, prefixes[prefix])
    kg.bind('fio', fio)
    kg.bind('us_frs', us_frs)
    kg.bind('us_frs_data', us_frs_data)
    kg.bind('naics', naics)
    kg.bind('sic', sic)
    kg.bind('coso', coso)
    kg.bind('geo', geo)
    return kg


def get_attributes(row):
    #this is specific to the imported file
    facility = {
        'facility_id': row.REGISTRY_ID,
        'facility_name': row.PRIMARY_NAME,
        'county_fips': row.FIPS_CODE,

    }
    ## additional attributes that do not appear for all facilities
    #geometry
    if pd.notnull(row['LATITUDE83']):
        shape_pt = Point([row.LONGITUDE83, row.LATITUDE83])
        facility['WKT'] = shape_pt.wkt
    #REF_POINT_DESC ,

    #identify federal facilities
    if row.FEDERAL_FACILITY_CODE == 'Yes':
        facility['federal_bool'] = True
        if pd.notnull(row.FEDERAL_AGENCY_CODE):
            facility['federalAgency'] = row.FEDERAL_AGENCY_NAME #don't need this if find a lookup table
            facility['federalAgencyCode'] = row.FEDERAL_AGENCY_CODE #this will be used in the iri
    else:
        facility['federal_bool'] = False

    if pd.notnull(row['TRIBAL_LAND_CODE']):
        facility['tribal_bool'] = True  # row.TRIBAL_LAND_NAME (rarely filled in)
    if pd.notnull(row.HUC_CODE):
        facility['HUC'] = row.HUC_CODE
    if pd.notnull(row.SITE_TYPE_NAME):
        facility['siteType'] = str(row.SITE_TYPE_NAME).title().replace(" ", "")

    return facility

def get_iris(facility):
    #build iris for any entities
    facility_iri = us_frs_data['d.FRS-Facility.'+str(facility['facility_id'])]
    county_iri = aik_pfas_ont['County.01'+str(facility['county_fips'])] #namespace needs to be replaced
    geo_iri = us_frs_data['d.FRS-Facility-Geometry.'+str(facility['facility_id'])]
    extra_iris ={}
    #TODO agency codes need labels  FRS_PROGRAM_FACILITY.FEDERAL_AGENCY_CODE
    if 'federalAgencyCode' in facility.keys():
        agency_iri = fio['d.Agency.'+str(facility['federalAgencyCode'])]
        extra_iris['agency'] = agency_iri
    
    #siteType to class
    if 'siteType' in facility.keys():
        if facility['siteType'] != 'Facility':
            extra_iris['type'] = us_frs[facility['siteType']+'-Facility']



    return facility_iri, county_iri, geo_iri, extra_iris


def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        #get attributes
        facility = get_attributes(row)
        #get iris
        facility_iri, county_iri, geo_iri, extra_iris = get_iris(facility)

        #create facility
        kg.add((facility_iri, RDF.type, us_frs["FRS-Facility"]))
        kg.add((facility_iri, RDFS.label, Literal(facility['facility_name'], datatype= XSD.string)))

        #geometry
        if 'WKT' in facility:
            kg.add((facility_iri, geo['hasGeometry'], geo_iri))
            kg.add((geo_iri, geo["asWKT"], Literal(facility['WKT'], datatype=geo["wktLiteral"])))
            kg.add((facility_iri, coso['locatedIn'], county_iri))
        if 'tribal_bool' in facility.keys():
            #kg.add((facility_iri, coso['locatedIn'], ))
            pass
        #TODO huc code
        

        #federal
        if facility['federal_bool'] == True :
            kg.add((facility_iri, RDF.type, us_frs['Federal-Facility']))
            if 'agency' in extra_iris.keys():
                kg.add((facility_iri, fio['ofAgency'], extra_iris['agency']))
        #siteType
        if 'type' in extra_iris.keys():
            kg.add((facility_iri, RDF.type, extra_iris['type']))



    return kg

## utility functions

def is_valid(value):
    if math.isnan(float(value)):
        return False
    else:
        return True


if __name__ == "__main__":
    main()