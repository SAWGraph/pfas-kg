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
# print(code_dir)
# sys.path.insert(0, str(code_dir))
# from variable import NAME_SPACE, _PREFIX

## declare variables
logname = "log"

## data path
root_folder = Path(__file__).resolve().parent.parent.parent  # datasets folder
data_dir = root_folder / "data/il-epa/"
metadata_dir = None
output_dir = Path(__file__).resolve().parent

##namespaces
pfas = Namespace(f'http://sawgraph.spatialai.org/v1/pfas#')
coso = Namespace(f'http://sawgraph.spatialai.org/v1/contaminoso#')
geo = Namespace(f'http://www.opengis.net/ont/geosparql#')
il_isgs= Namespace(f'http://sawgraph.spatialai.org/v1/il-isgs#')

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for tests")


def main():
    '''main function initializes all other functions'''
    df = load_data()
    kg = triplify(df)

    kg_turtle_file = "il-isgs-wells.ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger('Finished triplifying Il wells.')


def load_data():
    json_path = data_dir / 'il-wells.geojson'
    df = gpd.read_file(json_path)
    print(df.info(verbose=True))
    print('Status:', df.STATUS.unique())
    print('Status:', df.STATUSLONG.unique())
    print('Formation:', df.WFORMATION.unique())
    logger = logging.getLogger('Data loaded to dataframe.')
    # print(df)
    return df


def Initial_KG():
    # prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    # for prefix in prefixes:
    #    kg.bind(prefix, prefixes[prefix])
    kg.bind('il_isgs', il_isgs)
    kg.bind('pfas', pfas)
    kg.bind('coso', coso)
    kg.bind('geo', geo)
    return kg


def get_attributes(row):
    # this is specific to the imported file
    well = {
        'id': row.API_NUMBER,
        'wellType': row.STATUS,
        'wkt': f'POINT({row.LONGITUDE} {row.LATITUDE})'  # replace this with geodataframe version?

    }

    if pd.notnull(row.ISWSPNUM):
        well['ISWS'] = row.ISWSPNUM

    if pd.notnull(row.OWNER):
        well['owner'] = row.OWNER

    if pd.notnull(row.FARM_NAME):
        well['name'] = row.FARM_NAME

    if pd.notnull(row.TOTAL_DEPTH):
        well['depth'] = row.TOTAL_DEPTH

    if pd.notnull(row.PUMPGPM):
        well['rate'] = row.PUMPGPM

    return well


def get_iris(facility):
    # build iris for any entities

    extra_iris = {}

    return extra_iris


def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        pass
        # get attributes
        well = get_attributes(row)
        # get iris
        iris = get_iris(well)

        # create facility
        # kg.add((facility_iri, RDF.type, us_frs["FRS-Facility"]))
        # kg.add((facility_iri, RDFS.label, Literal(facility['facility_name'], datatype= XSD.string)))

        # geometry
        # if 'WKT' in facility:
        #    kg.add((facility_iri, geo['hasGeometry'], geo_iri))
        #    kg.add((geo_iri, geo["asWKT"], Literal(facility['WKT'], datatype=geo["wktLiteral"])))
        #    kg.add((facility_iri, coso['locatedIn'], county_iri))

    return kg


## utility functions

def is_valid(value):
    if math.isnan(float(value)):
        return False
    else:
        return True


if __name__ == "__main__":
    main()