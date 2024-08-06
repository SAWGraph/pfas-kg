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

## data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/us-sdwis/"
metadata_dir = None
output_dir = root_folder / "federal/us-sdwis/"

##namespaces

prefixes = {}
prefixes['us_sdwis'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-sdwis#')
prefixes['us_sdwis_data'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-sdwis#')
#prefixes['us_frs'] = Namespace(f"http://sawgraph.spatialai.org/v1/us-frs#")
#prefixes['us_frs_data'] = Namespace(f"http://sawgraph.spatialai.org/v1/us-frs-data#")
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

    kg_turtle_file = f"us-sdwis-{state.strip()}.ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger('Finished triplifying ghg releases.')


def load_data():
    df = pd.read_csv(data_dir / 'SDWA_FACILITIES.csv', dtype=str) # , nrows=50
    df['State']= df['PWSID'].astype(str).str[0:2]
    print(df['State'].unique())
    #filter to just one state
    df = df[df['State'] == state]
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
    facility = {
        'PWSID': row['PWSID'],
        'Facility_Id': row['FACILITY_ID'],
        'Facility_Name': row['FACILITY_NAME'],
        'Active': row['FACILITY_ACTIVITY_CODE'], #A/I




    }
    if pd.notnull(row.STATE_FACILITY_ID):
        facility['State_Id']= row['STATE_FACILITY_ID']
    if pd.notnull(row.FACILITY_DEACTIVATION_DATE):
        facility['Deactivation_Date'] = row['FACILITY_DEACTIVATION_DATE']

    return facility


def get_iris(facility):
    iris = {}
    iris['PWS'] = prefixes['us_sdwis_data']['d.PublicWaterSystem.'+ facility['PWSID']]

    #print(iris)
    return iris


def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        facility = get_attributes(row)
        # get iris
        iris = get_iris(facility)
        #print(iris)

        #pws
        kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['PublicWaterSystem']))

    return kg


if __name__ == "__main__":
    main()
