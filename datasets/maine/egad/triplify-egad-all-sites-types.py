from pathlib import Path
import geopandas
import pandas as pd

import os
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
import pandas as pd
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

# This script triplifies all EGAD sites that have a PFAS result and adds site type information (comparing it to the latest PFAS samples excel file). 
# this script should be run after the site type jsons are downloaded in maine-dep-geodata-download.py


## importing utility/variable file
code_dir = Path(__file__).resolve().parent.parent
#print(code_dir)
sys.path.insert(0, str(code_dir))
from variable import NAME_SPACE, _PREFIX
#import spatial_contains as sc

## declare variables
logname = "log"

## data path
root_folder =Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/maine_dep_esri_server/"
reference_dir = root_folder / "data/egad-maine-samples/"
metadata_dir = root_folder / "maine/egad/metadata/"
output_dir = root_folder / "maine/egad/"

## data dictioaries -- for controlled vocabularies

# with open(metadata_dir + 'analysis_lab.csv', mode='r') as infile:
#     reader = csv.reader(infile)
#     lab_dict = {rows[1]: rows[0] for rows in reader}


## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for egad sites")


def main():
    #load data to df
    sites_df = geopandas.read_file( data_dir / f"egad_sites_0.geojson")
    i = 1
    while i < 11:
        df = geopandas.read_file( data_dir / f"egad_sites_{i}.geojson")
        sites_df = pd.concat((sites_df,df), ignore_index=True)
        i += 1

    sites_df.sindex
    print(len(sites_df))

    # see which sites are actually pfas associated
    egad_sites_df = pd.read_excel( reference_dir / 'Statewide EGAD PFAS File March 2024.xlsx', sheet_name="PFAS Sites and Sample Points", usecols=['SITE_NUMBER', 'SITE_NAME'], header=0)
    #print(egad_sites_df.info())
    pfas_sites = egad_sites_df['SITE_NUMBER'].unique()
    #print(pfas_sites)
    #print(sites_df['EGAD_SEQ'])
    
    #limit to only pfas sites
    sites_df = sites_df[sites_df['EGAD_SEQ'].isin(pfas_sites)]

    #lookup site type shortnames
    vocab_df = pd.read_csv(metadata_dir / 'site_type.csv', header=0, encoding='ISO-8859-1') #, index_col='DESCRIPTION'
    #print('SITE TYPES: ', vocab_df.info())
    #print(vocab_df['DESCRIPTION'].unique())
    logger = logging.getLogger('Data loaded to dataframe.')


    kg = triplify_data(sites_df, vocab_df, _PREFIX)
    kg_turtle_file = "egad_sites_types.ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger('Finished triplifying DEP sites.')


def Initial_KG(_PREFIX):
    prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


## triplify the abox
def triplify_data(df, vocab, _PREFIX):
    kg = Initial_KG(_PREFIX)

    ## materialize each site
    pd.set_option('display.max_columns', 15)
    print(df.info())
    #print(df['SITE_TYPE'].unique())

    for idx, row in df.iterrows():
        ## load values and format
        
        site_type = row['SITE_TYPE'] 
        #get value of site type
        site_value = vocab.loc[vocab['DESCRIPTION'] == site_type]['VALUE'].item()
        site_value_formatted = ''.join(e for e in site_value if e.isalnum()) #remove spaces and special characters
        
        site = row['EGAD_SEQ']
        site_geometry = Point(row['LONGITUDE'], row['LATITUDE'])

        narrative = row['NARATIVE_SUMMARY']
        desc = row['SITE_DESCRIPTION']
        address = row['ADDRESS_LINE']
        
        
        ## iris
        type_iri = _PREFIX["me_egad_data"][f"{'siteType'}.{site_value_formatted}"]
        egad_site_iri = _PREFIX["me_egad_data"][f'site.{site}']
        egad_geometry_iri = _PREFIX["me_egad_data"][f'egad.site.geometry.{site}']

        #triplifty

        kg.add((egad_site_iri, RDF.type, _PREFIX["me_egad"][f'EGAD-Site']))
        kg.add((egad_site_iri, _PREFIX["me_egad"]['siteNumber'], Literal(int(row['EGAD_SEQ']), datatype = XSD.integer)))
        kg.add((egad_site_iri, RDFS['label'], Literal(row['CURRENT_SITE_NAME'], datatype=XSD.string)))
        #kg.add((egad_site_iri, RDFS['label'], Literal('EGAD site ' + str(row['EGAD_SEQ']))))
        kg.add((egad_site_iri, _PREFIX["me_egad"]['siteType'], type_iri))

        if str(site_geometry) != "POINT EMPTY":
            kg.add((egad_site_iri, _PREFIX['geo']['hasDefaultGeometry'], egad_geometry_iri))
            kg.add((egad_site_iri, _PREFIX['geo']['hasGeometry'], egad_geometry_iri))

            kg.add((egad_geometry_iri, RDF.type, _PREFIX["geo"]["Geometry"]))
            kg.add((egad_geometry_iri, RDF.type, _PREFIX["sf"]["Point"]))
            kg.add((egad_geometry_iri, _PREFIX["geo"]["asWKT"], Literal(site_geometry, datatype=_PREFIX["geo"]["wktLiteral"])))


        #other attributes
        #kg.add((_PREFIX["aik-pfas-ont"][f'{site_type}'], RDFS.subClassOf, _PREFIX["aik-pfas-ont"]['EGAD_Site']))

       # if address != 'UNKNOWN':
       #     kg.add((egad_site_iri, _PREFIX["me_egad"]['address'], Literal(address, datatype=XSD.string)))
        #kg.add((egad_site_iri, _PREFIX["aik-pfas-ont"]['egad_site_description'], Literal(desc, datatype=XSD.string)))
       # if isinstance(narrative, str) :
            #print('narrative ', narrative)
      #      kg.add((egad_site_iri, _PREFIX["me_egad"]['egad_narrative'], Literal(narrative, datatype=XSD.string)))
      #  if isinstance(desc, str) and desc != narrative:
      #      kg.add((egad_site_iri, _PREFIX["me_egad"]['egad_description'], Literal(desc, datatype=XSD.string)))


    return kg


if __name__ == '__main__':
    main()
