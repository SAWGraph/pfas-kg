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
state = ' ME'

## data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/epa_pfas_analytic_tool/"
metadata_dir = None
output_dir = root_folder / "federal/us-ghg/"

##namespaces
us_epa_ghg = Namespace(f'http://sawgraph.spatialai.org/v1/us-epa-ghg#')
us_epa_ghg_data = Namespace(f'http://sawgraph.spatialai.org/v1/us-epa-ghg-data#')
us_frs = Namespace(f"http://sawgraph.spatialai.org/v1/us-frs#")
us_frs_data = Namespace(f"http://sawgraph.spatialai.org/v1/us-frs-data#")
qudt = Namespace(f'https://qudt.org/schema/qudt/')
unit = Namespace(f'https://qudt.org/vocab/unit')
coso = Namespace(f'http://sawgraph.spatialai.org/v1/contaminoso#')
geo = Namespace(f'http://www.opengis.net/ont/geosparql#')

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info(f"Running triplification for ghg {state}")


def main():
    df = load_data()
    kg = triplify(df)

    kg_turtle_file = "us-epa-ghg-releases-"+state.strip()+".ttl".format(output_dir)
    kg.serialize(kg_turtle_file, format='turtle')
    logger = logging.getLogger(f'Finished triplifying ghg releases for {state}.')


def load_data():
    df = pd.read_excel(data_dir / 'greenhousegas_cb4421f2-1c5c-473b-a175-9c785c2a752c.xlsx', dtype=str)
    #filter to just one state
    df = df[df['State Territory or Tribe'] == state]
    print(df.info(verbose=True))
    logger = logging.getLogger('Data loaded to dataframe.')
    return df


def Initial_KG():
    # prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    # for prefix in prefixes:
    #    kg.bind(prefix, prefixes[prefix])
    kg.bind('us_epa_ghg', us_epa_ghg)
    kg.bind('us_epa_ghg_data', us_epa_ghg_data)
    kg.bind('us_frs', us_frs)
    kg.bind('us_frs_data', us_frs_data)
    kg.bind('qudt', qudt)
    kg.bind('unit', unit)
    kg.bind('coso', coso)
    kg.bind('geo', geo)
    return kg


def get_attributes(row):
    release = {
        'Year': row['Year'],
        'GHG_id': row['GHG Facility ID'],
        'GHG_subpart': row['GHG Subpart'],
        'Chemical': row['Chemical Name'],
        'Amount': row['Amount (metric tons)'],
        'Latitude': row['Latitude'],
        'Longitude': row['Longitude'],
        'City': row['City']
    }

    if row['FRS ID'] != '-':
        release['FRS_ID'] = row['FRS ID']

    if row['Chemical Formula'] != '-':
        release['ChemicalFormula'] = row['Chemical Formula']

    if row['CAS Number'] != '-':
        release['CAS'] = row['CAS Number']

    return release


def get_iris(release):
    extra_iris = {}

    chemicalName = str(release['Chemical']).replace(' ', '').replace('(', "_").replace(')', '_').replace(',',
                                                                                                          '_').replace(';', '_').replace('[', '_').replace(']', '_').replace('/', '_')
    facilityId = 'GHGFacility-' + str(release['GHG_id']) + '.Year-' + str(release['Year']) + '.Chemical-' + chemicalName

    extra_iris['ReleaseObservation'] = us_epa_ghg[
        'd.ReleaseObservation.' + facilityId]
    extra_iris['Chemical'] = us_epa_ghg['d.Chemical.' + chemicalName]
    extra_iris['Measurement'] = us_epa_ghg['d.ContaminantMeasurement.' + facilityId + '.Chemical-' + chemicalName]
    extra_iris['Amount'] = us_epa_ghg['d.Amount.' + facilityId + '.Chemical-' + chemicalName]

    if 'FRS_ID' not in release.keys():
        #hard coding the 6 facilities that don't have FRS_ID from ezquery match
        frs_lookup = {'1009613': '110071161007',  #IL
                      '1009615': '110071161008',  #IL
                      '1010204': '110071160336',  #CT
                      '1010145': '110071160378',  #OH
                      '1005459': '110071160973',  #PA
                      '1010134': '110070082061'  #TX
                      }
        release['FRS_ID'] = frs_lookup[str(release['GHG_id'])]
        #print(release['FRS_ID'], release['GHG_id'])
    if 'FRS_ID' in release.keys():
        extra_iris['FRS_Facility'] = us_frs_data['d.FRS-Facility.' + str(release['FRS_ID'])]
    else:
        print('Missing FRS id for GHG id:', release['GHG_id'])
        #extra_iris['GHG_Facility'] = us_epa_ghg['d.GHG-Facility.' + str(release['GHG_id'])] #TODO it would be better to use FRS api to look up FRS_ID based on GHG_ID
    extra_iris['TimeInterval'] = us_frs_data['d.TimeInterval.Year-' + str(release['Year'])]
    return extra_iris


def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        release = get_attributes(row)
        # get iris
        extra_iris = get_iris(release)
        #print(extra_iris)

        #observation
        kg.add((extra_iris['ReleaseObservation'], RDF.type, us_epa_ghg['ReleaseObservation']))
        kg.add((extra_iris['ReleaseObservation'], coso['hasTemporalCoverage'],
                extra_iris['TimeInterval']))  #TODO this needs beginning and end attributes
        kg.add((extra_iris['ReleaseObservation'], us_epa_ghg['GHG-Subpart'], Literal(release['GHG_subpart'],
                                                                                     datatype=XSD.string)))  #TODO this should be done as a controlled vocabulary

        #facility
        if 'FRS_Facility' in extra_iris.keys():
            kg.add((extra_iris['ReleaseObservation'], coso['hasFeatureOfInterest'], extra_iris['FRS_Facility']))
            kg.add((extra_iris['FRS_Facility'], RDF.type, us_frs['FRS-Facility']))
            kg.add((extra_iris['FRS_Facility'], us_frs['hasGHGId'], Literal(release['GHG_id'], datatype=XSD.string)))
        elif 'GHG_Facility' in extra_iris.keys():
            kg.add((extra_iris['ReleaseObservation'], coso['hasFeatureOfInterest'], extra_iris['GHG_Facility']))
            kg.add((extra_iris['GHG_Facility'], us_frs['hasGHGId'], Literal(release['GHG_id'], datatype=XSD.string)))
            #TODO GHG facilities should get geometry

        #substance
        kg.add((extra_iris['ReleaseObservation'], coso['ofSubstance'], extra_iris['Chemical']))
        kg.add((extra_iris['Chemical'], RDF.type, us_epa_ghg['Chemical']))
        if 'ChemicalFormula' in release.keys():
            kg.add((extra_iris['Chemical'], us_epa_ghg['chemicalFormula'],
                    Literal(release['ChemicalFormula'], datatype=XSD.string)))
        if 'CAS' in release.keys():
            kg.add((extra_iris['Chemical'], us_epa_ghg['casNumber'], Literal(release['CAS'], datatype=XSD.string)))

        #measurement
        kg.add((extra_iris['ReleaseObservation'], coso['hasResult'], extra_iris['Measurement']))
        kg.add((extra_iris['Measurement'], qudt['quantityKind'], extra_iris['Amount']))
        kg.add((extra_iris['Measurement'], RDF.type, us_epa_ghg['Measurement']))

        #amount

        kg.add((extra_iris['Amount'], RDF.type, us_epa_ghg['Amount']))
        kg.add((extra_iris['Amount'], qudt['numericValue'], Literal(release['Amount'], datatype=XSD.float)))
        kg.add((extra_iris['Amount'], qudt['unit'], unit['TON_Metric']))
    return kg


if __name__ == "__main__":
    main()
