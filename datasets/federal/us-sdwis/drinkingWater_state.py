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
state = " ME"

## data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/epa_pfas_analytic_tool/"
metadata_dir = None
output_dir = root_folder / "federal/us-sdwis/"

##namespaces

prefixes = {}
prefixes['us_sdwis'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-sdwis#')
prefixes['us_sdwis_data'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-sdwis-data#')
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

    kg_turtle_file = f"us-pat-DrinkingWaterState-{state.strip()}.ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger('Finished triplifying ghg releases.')


def load_data():
    df = pd.read_excel(data_dir / 'drinkingwater_state_bd611cce-c661-4b5b-bdb6-5c2d07a19098.xlsx', dtype=str) # , nrows=50
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
    sample = {
        'PWSID': row['PWSID'],
        'Name': row['PWS Name'],

        'PopServed': row['Population Served'],
        'SizeCat': row['Size'],


        'Date': datetime.strptime(row['Sample Date'],"%m/%d/%Y"),
        #'SampleType': row['Sample Type'], - for IL this just says its a special sample (SP) e.g. not routine
        'Count': row['Results'],

        'Substance': str(row['Contaminant']).replace('+', '-'),

        'Method': row['Method'],
        'RL': row['Reporting Level'],
        'Qualifier': row['MRL/MDL']
    }

    #not all samples have ids
    if pd.notnull(row['Sample ID']):
        sample['SampleID'] = row['Sample ID']
    else:
        #construct from PWS(below), date, and sample location id (if exists)
        if pd.notnull(row['Sample Point ID']):
            sample['SampleID'] = str(row['Sample Date']).replace('/', '') + '.'+str(row['Sample Point ID'])
        else:
            sample['SampleID'] = str(row['Sample Date']).replace('/', '')

    #if sample location has identifier
    if pd.notnull(row['Sample Point ID']):
        sample['SamplePointID'] = str(row['Sample Point ID']).replace(" ", "")
    else:  #if we don't know anything about the sample location don't include it
        #construct sample location identifier
        if pd.notnull(row['Sample ID']):
            sample['SamplePointID'] = str(row['Sample Date']).replace('/', '') + '.' + str(row['Sample ID'])
        else:
            sample['SamplePointID'] = str(row['Sample Date']).replace('/', '')

    #concentrations and NDs
    if row['Concentration'] != '-':
        sample['Conc'] = row['Concentration']
    if pd.notnull(row['Code']):
        sample['SubstanceCode'] = row['Code']

    #units conversion
    unitLookup = {
        'NG/L': 'NanoGM-PER-L',
        'mg/L': 'MilliGM-PER-L',
        'ppt': 'NanoGM-PER-L',
        'UG/L': 'MicroGM-PER-L'
    }
    if pd.notnull(row['Units']):
        sample['Unit'] = unitLookup[row['Units']]

    return sample


def get_iris(sample):
    iris = {}
    iris['sample'] = prefixes['us_sdwis_data']['d.PWS-Sample.'+ sample['PWSID']+ '.'+ sample['SampleID']]
    if 'SamplePointID' in sample.keys():
        iris['samplePoint'] = prefixes['us_sdwis_data']['d.PWS-SamplePoint.' + sample['PWSID'] + '.' + sample['SamplePointID']]
    iris['observation'] = prefixes['us_sdwis_data']['d.PWS-Observation.' + sample['PWSID'] + '.' + sample['SampleID']+'.' + sample['Substance']]
    iris['measurement']= prefixes['us_sdwis_data']['d.PWS-PFASConcentration.' + sample['PWSID'] + '.' + sample['SampleID'] + '.' + sample['Substance']]
    iris['amount'] = prefixes['us_sdwis_data']['d.Amount.' + sample['PWSID'] + '.Sample-' + sample['SampleID']+'.Chemical-' + sample['Substance']]
    if 'SubstanceCode' in sample.keys():
        iris['substance'] = prefixes['us_sdwis_data']['d.PWS-PFAS.'+str(sample['SubstanceCode'])]
    else:
        iris['substance'] = prefixes['us_sdwis_data']['d.PWS-PFAS.' + str(sample['Substance'])]
    #sample Material Type?
    iris['PWS'] = prefixes['us_sdwis_data']['d.PublicWaterSystem.'+sample['PWSID']]

    #print(iris)
    return iris


def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        sample = get_attributes(row)
        # get iris
        iris = get_iris(sample)
        #print(iris)

        #pws
        kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['PublicWaterSystem']))
        kg.add((iris['PWS'], prefixes['us_sdwis']['hasPWSID'], Literal(sample['PWSID'], datatype=XSD.string)))
        kg.add((iris['PWS'], prefixes['us_sdwis']['hasName'], Literal(sample['Name'], datatype=XSD.string)))
        kg.add((iris['PWS'], prefixes['us_sdwis']['populationServed'], Literal(sample['PopServed'], datatype=XSD.int)))
        kg.add((iris['PWS'], prefixes['us_sdwis']['sizeCategory'], Literal(sample['SizeCat'], datatype=XSD.string)))

        #MaterialSample
        kg.add((iris['sample'], RDF.type, prefixes['us_sdwis']['PWS-Sample']))
        kg.add((iris['sample'], prefixes['us_sdwis']['sampleID'], Literal(sample['SampleID'], datatype=XSD.string)))
        #TODO derive sample type from 'Sample Type'

        #sample point - TODO:how should this relate to PWS-Facility?
        if 'samplePoint' in iris.keys():
            kg.add((iris['samplePoint'], RDF.type, prefixes['us_sdwis']['PWS-SamplePoint']))
            kg.add((iris['samplePoint'], prefixes['us_sdwis']['SamplePointID'], Literal(sample['SamplePointID'], datatype=XSD.string)))
            kg.add((iris['sample'], prefixes['coso']['fromSamplePoint'], iris['samplePoint']))

        #observation
        kg.add((iris['observation'], RDF.type, prefixes['us_sdwis']['PWS-Observation']))
        #TODO determine if single or aggregate observation based on 'Results' count
        kg.add((iris['observation'], prefixes['coso']['sampledFeature'], iris['PWS']))
        kg.add((iris['observation'], prefixes['coso']['ofSubstance'], iris['substance']))
        kg.add((iris['observation'], prefixes['sosa']['hasResult'], iris['measurement']))
        kg.add((iris['observation'], prefixes['coso']['analyzedSample'], iris['sample']))
        kg.add((iris['observation'], prefixes['coso']['sampleTime'], Literal(sample['Date'].strftime("%Y-%m-%d"), datatype=XSD.date)))

        #measurement
        kg.add((iris['measurement'], RDF.type, prefixes['us_sdwis']['PWS-PFASConcentration']))

        #TODO handle the non-detects

        #Amount quanity value - only create if there is a concentration? - need to handle nondetects above
        if 'Conc' in sample.keys():
            kg.add((iris['measurement'], prefixes['qudt']['quantityValue'], iris['amount']))
            kg.add((iris['amount'], RDF.type, prefixes['us_sdwis']['Amount']))
            kg.add((iris['amount'], prefixes['qudt']['numericValue'], Literal(sample['Conc'], datatype=XSD.float)))
            if 'Unit' in sample.keys():
                kg.add((iris['amount'], prefixes['qudt']['unit'], prefixes['qudt'][sample['Unit']]))

        #substance
        kg.add((iris['substance'], RDF.type, prefixes['us_sdwis']['PWS-PFAS']))
        kg.add((iris['substance'], RDFS.label, Literal(sample['Substance'], datatype=XSD.string)))




    return kg


if __name__ == "__main__":
    main()
