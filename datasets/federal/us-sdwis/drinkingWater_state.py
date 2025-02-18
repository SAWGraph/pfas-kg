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
#state = False
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
prefixes['qudt'] = Namespace(f'http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://sawgraph.spatialai.org/v1/contaminoso#')
prefixes['pfas'] = Namespace(f'http://sawgraph.spatialai.org/v1/pfas#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['sosa'] = Namespace(f'http://www.w3.org/ns/sosa/')
prefixes['gcx']= Namespace(f'http://geoconnex.us/')

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for facilities")


def main():
    df = load_data()
    global state
    if state:
        #run just one state if state variable already set
        #filter to just one state
        df = df[df['State'] == state]
        print(df.info(verbose=True))
        kg, kg_pws = triplify(df)
        kg_turtle_file = f"us-pat-DrinkingWaterState-{state.strip()}.ttl".format(output_dir)
        kg.serialize(kg_turtle_file, format='turtle')
        file2 = f'us-pat-SDWIS-{state.strip()}.ttl'.format(output_dir)
        kg_pws.serialize(file2, format='turtle')
        logger = logging.getLogger(f'Finished triplifying sdwis samples for {state} .')
    else:
        #otherwise run all states
        for state in df['State'].unique():
            #filter to just one state
            state_df= df[df['State'] == state]
            print(state_df.info(verbose=True))
            kg = triplify(state_df)

            kg_turtle_file = f"us-pat-DrinkingWaterState-{state.strip()}.ttl".format(output_dir)
            kg.serialize(kg_turtle_file, format='turtle')
            logger = logging.getLogger(f'Finished triplifying sdwis samples for {state} .')


def load_data():
    df = pd.read_excel(data_dir / 'drinkingwater_state_bd611cce-c661-4b5b-bdb6-5c2d07a19098.xlsx', dtype=str) # , nrows=50
    print(df['State'].unique())
    
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
        'PWSID': str(row['PWSID']),
        'Name': row['PWS Name'],
        'PopServed': row['Population Served'],
        'SizeCat': row['Size'],

        'Date': datetime.strptime(row['Sample Date'],"%m/%d/%Y"),
        #'SampleType': row['Sample Type'], - for IL this just says its a special sample (SP) e.g. not routine
        'Substance': str(row['Contaminant']).strip().replace(" ",""),
        'Count': row['Results'],
        'Method': row['Method'],
        'RL': row['Reporting Level'],
        'Qualifier': row['MRL/MDL']
    }

    #substance 
    if "+" in row['Contaminant'] or "Total" in row['Contaminant']:
        #if substance contains + or Total, its an aggregate (substance collection)
        sample['SubstanceColl'] = True  
    
    count = int(sample['Substance'].count('+'))+1

    if count > 1:
        sample['SubstanceShort'] = 'sum' + str(count) #shorten substance name if aggregate with +
    else:
        sample['SubstanceShort'] = sample['Substance']
    
    #not all samples have ids
    if pd.notnull(row['Sample ID']):
        sample['SampleID'] = str(row['Sample ID']).replace(" ","")
    else:
        #construct from PWS(below), date, and sample location id (if exists)
        if pd.notnull(row['Sample Point ID']):
            sample['SampleID'] = str(row['Sample Date']).replace('/', '').replace(" ","") + '.'+str(row['Sample Point ID']).replace(" ","")
        else:
            sample['SampleID'] = str(row['Sample Date']).replace('/', '').replace(" ","")

    #if sample location has identifier
    if pd.notnull(row['Sample Point ID']):
        sample['SamplePointID'] = str(row['Sample Point ID']).replace(" ", "")
    else:  #if we don't know anything about the sample location don't include it
        #construct sample location identifier
        if pd.notnull(row['Sample ID']):
            sample['SamplePointID'] = str(row['Sample Date']).replace('/', '').replace(" ","") + '-' + str(row['Sample ID'])
        else:
            sample['SamplePointID'] = str(row['Sample Date']).replace('/', '').replace(" ","")

    #concentrations and NDs
    if row['Concentration'] != '-':
        sample['Conc'] = row['Concentration']
    if pd.notnull(row['Code']):
        sample['SubstanceCode'] = row['Code']

    #units conversion
    unitLookup = {
        'NG/L': 'NanoGM-PER-L',
        'ng/L': 'NanoGM-PER-L',
        'ng/l': 'NanoGM-PER-L',
        'mg/L': 'MilliGM-PER-L',
        'ppt': 'NanoGM-PER-L',
        'UG/L': 'MicroGM-PER-L'
    }
    if pd.notnull(row['Units']):
        sample['Unit'] = unitLookup[row['Units']]

    return sample


def get_iris(sample):
    iris = {}
    iris['sample'] = prefixes['us_sdwis_data']['d.PWS-Sample.'+ str(sample['PWSID'])+ '.'+ str(sample['SampleID'])]
    if 'SamplePointID' in sample.keys():
        iris['samplePoint'] = prefixes['us_sdwis_data']['d.PWS-SamplePoint.' + str(sample['PWSID'] )+ '.' + str(sample['SamplePointID'])]
    iris['observation'] = prefixes['us_sdwis_data']['d.PWS-Observation.' + sample['PWSID'] + '.' + sample['SampleID']+'.' + sample['SubstanceShort']]
    iris['measurement']= prefixes['us_sdwis_data']['d.PWS-PFASMeasurement.' + sample['PWSID'] + '.' + sample['SampleID'] + '.' + sample['SubstanceShort']]
    iris['amount'] = prefixes['us_sdwis_data']['d.QuantityValue.' + sample['PWSID'] + '.Sample-' + sample['SampleID']+'.Chemical-' + str(sample['SubstanceShort'])]
    iris['substance'] = prefixes['us_sdwis_data']['d.PWS-PFAS.' + str(sample['SubstanceShort'])]
    #TODO sample Material Type?
    iris['PWS'] = prefixes['gcx']['ref/pws/'+ sample['PWSID']]

    #print(iris)
    return iris


def triplify(df):
    kg = Initial_KG()
    kg_pws = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        sample = get_attributes(row)
        # get iris
        iris = get_iris(sample)
        #print(iris)

        #pws
        kg_pws.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['PublicWaterSystem']))
        kg_pws.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['SampledFeature']))
        kg_pws.add((iris['PWS'], prefixes['us_sdwis']['hasPWSID'], Literal(sample['PWSID'], datatype=XSD.string)))
        kg_pws.add((iris['PWS'], prefixes['us_sdwis']['pwsName'], Literal(sample['Name'], datatype=XSD.string)))
        kg_pws.add((iris['PWS'], RDFS.label, Literal(sample['Name'], datatype=XSD.string)))
        kg_pws.add((iris['PWS'], prefixes['us_sdwis']['populationServed'], Literal(sample['PopServed'], datatype=XSD.int)))
        kg_pws.add((iris['PWS'], prefixes['us_sdwis']['sizeCategory'], Literal(sample['SizeCat'], datatype=XSD.string)))

        #MaterialSample
        kg.add((iris['sample'], RDF.type, prefixes['us_sdwis']['PWS-Sample']))
        kg.add((iris['sample'], prefixes['us_sdwis']['sampleID'], Literal(sample['SampleID'], datatype=XSD.string)))
        kg.add((iris['sample'], prefixes['coso']['isSampleOf'], iris['PWS']))
        #TODO derive sample type from 'Sample Type'

        #sample point - TODO:how should this relate to PWS-Facility?
        if 'samplePoint' in iris.keys():
            kg.add((iris['samplePoint'], RDF.type, prefixes['us_sdwis']['PWS-SamplePoint']))
            kg.add((iris['samplePoint'], prefixes['us_sdwis']['samplePointID'], Literal(sample['SamplePointID'], datatype=XSD.string)))
            kg.add((iris['sample'], prefixes['coso']['fromSamplePoint'], iris['samplePoint']))

        #observation
        kg.add((iris['observation'], RDF.type, prefixes['us_sdwis']['PWS-Observation']))
        
        kg.add((iris['observation'], prefixes['coso']['sampledFeature'], iris['PWS']))
        kg.add((iris['observation'], prefixes['coso']['ofSubstance'], iris['substance']))
        kg.add((iris['observation'], prefixes['sosa']['hasResult'], iris['measurement']))
        kg.add((iris['observation'], prefixes['coso']['analyzedSample'], iris['sample']))
        kg.add((iris['observation'], prefixes['coso']['sampleTime'], Literal(sample['Date'].strftime("%Y-%m-%d"), datatype=XSD.date)))

        #measurement
        #TODO determine if single or aggregate observation based on 'Results' count and subsutanceColl
        kg.add((iris['measurement'], RDF.type, prefixes['us_sdwis']['PWS-PFASMeasurement']))
        if int(sample['Count']) > 1:
            kg.add((iris['measurement'], RDF.type, prefixes['us_sdwis']['PWS-AggregatePFASConcentrationMeasurement']))
            kg.add((iris['measurement'], RDF.type, prefixes['pfas']['AggregatePFASConcentrationMeasurement']))
            #TODO label as temporal aggregate
        elif 'SubstanceColl' in sample.keys():
            kg.add((iris['measurement'], RDF.type, prefixes['us_sdwis']['PWS-AggregatePFASConcentrationMeasurement']))
            kg.add((iris['measurement'], RDF.type, prefixes['pfas']['AggregatePFASConcentrationMeasurement']))
            #TODO label as substance aggregate
        else:
            kg.add((iris['measurement'], RDF.type, prefixes['pfas']['SinglePFASConcentrationMeasurement']))
        #TODO handle the non-detects

        #Amount quantity value - only create if there is a concentration? - need to handle nondetects above
        if 'Conc' in sample.keys():
            kg.add((iris['measurement'], prefixes['qudt']['quantityValue'], iris['amount']))
            kg.add((iris['amount'], RDF.type, prefixes['us_sdwis']['Amount']))
            kg.add((iris['amount'], prefixes['qudt']['numericValue'], Literal(sample['Conc'], datatype=XSD.float)))
            if 'Unit' in sample.keys():
                kg.add((iris['amount'], prefixes['qudt']['unit'], prefixes['qudt'][sample['Unit']]))

        #substance
        if 'SubstanceColl' in sample.keys():
            kg.add((iris['substance'], RDF.type, prefixes['coso']['SubstanceCollection']))
        else:
            kg.add((iris['substance'], RDF.type, prefixes['us_sdwis']['PWS-PFAS']))
        kg.add((iris['substance'], RDFS.label, Literal(sample['Substance'], datatype=XSD.string)))




    return kg, kg_pws


if __name__ == "__main__":
    main()
