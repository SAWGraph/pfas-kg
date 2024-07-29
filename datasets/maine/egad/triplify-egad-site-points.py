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
#import geopandas as gpd
from shapely.geometry import Point
import numpy


## importing utility/variable file
#sys.path.insert(0, 'C:/Users/Shirly/Documents/GitHub/kg-construction/datasets/maine/egad')
from variable import NAME_SPACE, _PREFIX


## declare variables
logname = "log"
point_type_dict = []
site_type_dict = []
precision = 7

## data path
root_folder = "C:/Users/Shirly/Documents/GitHub/kg-construction/"
data_dir =  root_folder + "datasets/maine/egad/data/"
metadata_dir = root_folder + "datasets/maine/egad/data/metadata/"
output_dir = root_folder + "datasets/maine/egad/egad-maine-samples/"


## data dictioaries -- for controlled vocabularies
with open(metadata_dir + 'sample_point_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    point_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir + 'site_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    site_type_dict = {rows[1]:rows[0] for rows in reader}


## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for EGAD sites and samples")

def main():
    egad_sites_df = pd.read_csv(data_dir + 'sites-samples-2024.csv', header=0, encoding='ISO-8859-1')
    logger = logging.getLogger('Data loaded to dataframe.')
    
    kg = triplify_egad_pfas_site_data(egad_sites_df, _PREFIX)
    kg_turtle_file = "egad_sites_samples_output.ttl".format(output_dir)
    kg.serialize(kg_turtle_file,format='turtle')
    logger = logging.getLogger('Finished triplifying EGAD PFAS site/sample point data.')

def Initial_KG(_PREFIX):
    prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


## triplify the abox
def triplify_egad_pfas_site_data(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## site record details
        site_number = row['SITE_NUMBER'] # site number
        site_name = row['SITE_NAME'] # site name
        site_type = row['SAMPLE_POINT_TYPE'] # site type
        pwsid_number = row['PWSID_NO'] # public water system ID     

        site_iri = _PREFIX["me_egad_data"][f"{'site'}.{site_number}"]
        kg.add( (site_iri, RDF.type, _PREFIX["me_egad"]["EGAD-Site"]) )
        kg.add( (site_iri, RDFS['label'], Literal('EGAD site '+ str(site_number))) )
        kg.add( (site_iri, _PREFIX["me_egad"]['siteNumber'], Literal(site_number, datatype = XSD.integer)) )
        kg.add( (site_iri, _PREFIX["me_egad"]['siteName'], Literal(site_name, datatype = XSD.string)) )
        if (len(str(pwsid_number)) != 0) and (str(pwsid_number) != 'nan'):
            kg.add( (site_iri, _PREFIX["sdwis"]['pwsidNumber'], Literal(pwsid_number, datatype = XSD.string)) )
        #town_name_formatted = row['MCD'].replace(' ', '_') 
        #town_iri = _PREFIX["me_egad_data"][f"{'town'}.{town_name_formatted}"]
        #kg.add( (site_iri, _PREFIX["me_egad"]['locatedIn'], town_iri))
        
        site_latitude = row['SITE_LATITUDE']
        site_longitude = row['SITE_LONGITUDE']
        if len(str(site_latitude)) != 0 and (str(site_latitude) != 'nan'):
            site_latitude = round(site_latitude, precision)
            #print(site_latitude)
            site_longitude = round(site_longitude, precision)
            site_geometry = Point(site_longitude, site_latitude)
            sitegeometry_iri = _PREFIX["me_egad_data"][f"{'site.geometry'}.{site_number}"]
            kg.add( (sitegeometry_iri, RDF.type, _PREFIX["geo"]["Geometry"]) )
            kg.add( (sitegeometry_iri, RDF.type, _PREFIX["sf"]["Point"]) )
            kg.add( (site_iri, _PREFIX['geo']['hasDefaultGeometry'], sitegeometry_iri) )
            kg.add( (site_iri, _PREFIX['geo']['hasGeometry'], sitegeometry_iri) )
            kg.add( (sitegeometry_iri, _PREFIX["geo"]["asWKT"], Literal(site_geometry, datatype=_PREFIX["geo"]["wktLiteral"])) )

        ## sample point record details
        samplepoint_number = row['SAMPLE_POINT_NUMBER'] # sample point number
        samplepoint_web_name = row['SAMPLE_POINT_WEB_NAME'] # sample point web name
        samplepoint_type = row['SAMPLE_POINT_TYPE'] # sample point type
        samplepoint_iri = _PREFIX["me_egad_data"][f"{'samplePoint'}.{samplepoint_number}"]
        kg.add( (samplepoint_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SamplePoint"]) )
        kg.add( (samplepoint_iri, RDFS['label'], Literal('EGAD sample point '+ str(samplepoint_number))) )
        samplepoint_type = point_type_dict[samplepoint_type]
        samplepoint_type = ''.join(e for e in samplepoint_type if e.isalnum())
        samplepoint_type_iri = _PREFIX["me_egad"][f"{'featureType'}.{samplepoint_type}"]
        kg.add( (samplepoint_iri, _PREFIX['me_egad']['samplePointType'], samplepoint_type_iri) )
        samplepoint_latitude = row['SAMPLE_POINT_LATITUDE']
        samplepoint_longitude = row['SAMPLE_POINT_LONGITUDE']
        kg.add( (samplepoint_iri, _PREFIX['me_egad']['associatedSite'], site_iri) )
##        if len(str(samplepoint_web_name)) != 0:
##            kg.add( (samplepoint_iri, _PREFIX["me_egad"]['samplePointWebName'], Literal(samplepoint_web_name, datatype = XSD.string)) )
##        
        if len(str(samplepoint_latitude)) != 0 and (str(samplepoint_latitude) != 'nan'):
            samplepoint_latitude = round(samplepoint_latitude, precision)
            samplepoint_longitude = round(samplepoint_longitude, precision)
            samplepoint_geometry = Point(samplepoint_longitude, samplepoint_latitude)
            samplepointgeometry_iri = _PREFIX["me_egad_data"][f"{'samplePoint.geometry'}.{samplepoint_number}"]

            kg.add( (samplepointgeometry_iri, RDF.type, _PREFIX["geo"]["Geometry"]) )
            kg.add( (samplepointgeometry_iri, RDF.type, _PREFIX["sf"]["Point"]) )
            kg.add( (samplepoint_iri, _PREFIX['geo']['hasDefaultGeometry'], samplepointgeometry_iri) )
            kg.add( (samplepoint_iri, _PREFIX['geo']['hasGeometry'], samplepointgeometry_iri) )
            kg.add( (samplepointgeometry_iri, _PREFIX["geo"]["asWKT"], Literal(samplepoint_geometry, datatype=_PREFIX["geo"]["wktLiteral"])) )
                
    return kg


## utility functions

def is_valid(value):
    if math.isnan(float(value)):
        return False
    else:
        return True

def rem_time(d):
    s = date(d.year,d.month, d.day)
    return s



if __name__ == "__main__":
    main()
