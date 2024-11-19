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
state = "IL"
state_fips = {'IL':'17'}

## data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/us-sdwis/"
metadata_dir = None
output_dir = root_folder / "federal/us-sdwis/"

##namespaces

prefixes = {}
prefixes['us_sdwis'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-sdwis#')
prefixes['us_sdwis_data'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-sdwis#')
prefixes['kwg-ont']= Namespace(f'http://stko-kwg.geog.ucsb.edu/lod/ontology/')
prefixes['qudt'] = Namespace(f'https://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://sawgraph.spatialai.org/v1/contaminoso#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['sosa'] = Namespace(f'http://www.w3.org/ns/sosa/')

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for facilities")


def main():
    df = load_data()
    kg = triplify(df)

    kg_turtle_file = f"us-sdwis-geographicarea-{state.strip()}.ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger('Finished triplifying sdwis geographic areas.')


def load_data():
    df = pd.read_csv(data_dir / 'SDWA_GEOGRAPHIC_AREAS.csv', dtype=str) # , nrows=50
    #filter to just one state
    #get the state from first two characters of pwsid
    df['state'] = df['PWSID'].str[:2]
    #filter
    df = df[df['state'] == state]
    print(df.info(verbose=True))
    logger = logging.getLogger('Data loaded to dataframe.')
    return df


def Initial_KG():
    # prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


def get_attributes(row):
    pws = {
        'PWSID': row['PWSID'],
        'TYPE': row['AREA_TYPE_CODE']
        

    }
    #county service
    if row.AREA_TYPE_CODE == 'CN':
        pws['county_fips'] = str(state_fips[state]) + row['ANSI_ENTITY_CODE']

    #if pd.notnull(row.PWS_NAME):
    #    pws['Name'] = row['PWS_NAME']
    

    return pws


def get_iris(pws):
    iris = {}
    iris['PWS'] = prefixes['us_sdwis_data']['d.PublicWaterSystem.'+ pws['PWSID']]
    #county iri
    if pws['TYPE'] == 'CN':
        iris['admin2'] = prefixes['kwgr']['administrativeRegion.USA.'+str(pws['county_fips'])]
    #zip
    #tribal
    #city

    #print(iris)
    return iris


def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        pws = get_attributes(row)
        # get iris
        iris = get_iris(pws)
        #print(iris)

        #pws
        kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['PublicWaterSystem']))
        if 'admin2' in iris.keys():
            kg.add((iris['PWS'], prefixes['kwg-ont']['sfWithin'], iris['admin2']))
    return kg


if __name__ == "__main__":
    main()
