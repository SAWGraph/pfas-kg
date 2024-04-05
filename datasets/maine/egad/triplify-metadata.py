import os
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
import pandas as pd
import encodings
import logging
import math
import numpy as np
#from pyutil import *
import sys

## importing utility/variable file
sys.path.insert(0, 'C:/Users/Shirly/Documents/GitHub/kg-construction/datasets/maine/egad')
from variable import NAME_SPACE, _PREFIX

## declare variables
logname = "log"

metadata_files = ['analysis_lab', 'sample_collection_method', 'sample_location', 'sample_point_type', 'sample_type', 'site_type', 'pfas_parameter']

#metadata_files = ['pfas_parameter']

## data path
root_folder = "C:/Users/Shirly/Documents/GitHub/kg-construction/"
data_dir =  root_folder + "datasets/maine/egad/data/metadata/"
output_dir = root_folder + "datasets/maine/egad/output-ttl/"


## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for EGAD metadata")

def main():
    # iterate over files in data directory
    for filename in metadata_files:
        data_df = pd.read_csv(data_dir + filename +'.csv', header=0, encoding='ISO-8859-1')
        logger = logging.getLogger('Data loaded to dataframe')
        if filename == 'analysis_lab':
            kg = triplify_lab(data_df, _PREFIX)
        elif filename == 'sample_collection_method':
            kg = triplify_collection_method(data_df, _PREFIX)
        elif filename == 'sample_location':
            kg = triplify_location(data_df, _PREFIX)
        elif filename == 'sample_point_type':
            kg = triplify_point_type(data_df, _PREFIX)
        elif filename == 'sample_type':
            kg = triplify_sample_type(data_df, _PREFIX)
        elif filename == 'site_type':
            kg = triplify_site_type(data_df, _PREFIX)
        elif filename == 'pfas_parameter':
            kg = triplify_pfas_parameter(data_df, _PREFIX)
        data_df.iloc[0:0]
        kg_turtle_file = filename+".ttl".format(output_dir)
        kg.serialize(kg_turtle_file,format='turtle')


def Initial_KG(_PREFIX):
    prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


## triplify the abox for labs
def triplify_lab(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## lab record details
        lab_value = row['VALUE'] # lab abbreviation
        lab_description = row['DESCRIPTION'] # lab description
        
        ## construct lab IRI
        lab_iri = _PREFIX["me_egad_data"][f"{'organization.lab'}.{lab_value}"]
                
        ## specify lab instance and it's data properties
        kg.add( (lab_iri, RDF.type, _PREFIX["me_egad"]["AnalysisLab"]) )
        kg.add( (lab_iri, RDFS['label'], Literal(str(lab_description))) )
        #kg.add( (lab_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(lab_description, datatype = XSD.string)) )

   
    return kg

## triplify the abox for sample collection methods
def triplify_collection_method(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## collection record details
        collection_value = row['VALUE'] # collection abbreviation
        collection_description = row['DESCRIPTION'] # collection description
        
        ## construct collection IRI
        collection_iri = _PREFIX["me_egad_data"][f"{'samplingMethod'}.{collection_value}"]
                
        ## specify collection instance and it's data properties
        kg.add( (collection_iri, RDF.type, _PREFIX["me_egad"]["EGAD_SampleCollectionMethod"]) )
        kg.add( (collection_iri, RDFS['label'], Literal(str(collection_description))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg


## triplify the abox for sample location
def triplify_location(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## location record details
        location_value = row['VALUE'] # location abbreviation
        location_description = row['DESCRIPTION'] # location description
        
        ## construct collection IRI
        location_iri = _PREFIX["me_egad_data"][f"{'sampleLocation'}.{location_value}"]
                
        ## specify location instance and it's data properties
        kg.add( (location_iri, RDF.type, _PREFIX["me_egad"]["EGAD_SampleDetailedLocation"]) )
        kg.add( (location_iri, RDFS['label'], Literal(str(location_description))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg


## triplify the tbox for sample point type
def triplify_point_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## location record details
        point_value = row['VALUE'] # point abbreviation
        point_description = row['DESCRIPTION'] # point description
        point_value_formatted = ''.join(e for e in point_value if e.isalnum())
        
        ## construct point IRI
        point_iri = _PREFIX["me_egad"][point_value_formatted]
                
        ## specify point instance and it's data properties
        kg.add( (point_iri, RDFS.subClassOf, _PREFIX["me_egad"]["Feature"]) )
        kg.add( (point_iri, RDFS['label'], Literal(str(point_description))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg


## triplify the abox for sample material type
def triplify_sample_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## sample type record details
        type_value = row['VALUE'] # material abbreviation
        type_description = row['DESCRIPTION'] # material description
        
        ## construct type IRI
        type_iri = _PREFIX["me_egad_data"][f"{'sampleMaterialType'}.{type_value}"]
                
        ## specify type instance and it's data properties
        kg.add( (type_iri, RDF.type, _PREFIX["me_egad"]["EGAD_SampleMaterialType"]) )
        kg.add( (type_iri, RDFS['label'], Literal(str(type_description))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg

## triplify the tbox for site type
def triplify_site_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## site record details
        site_value = row['VALUE'] # point abbreviation
        site_description = row['DESCRIPTION'] # point description
        site_value_formatted = ''.join(e for e in site_value if e.isalnum())
        
        ## construct site IRI
        site_iri = _PREFIX["me_egad_data"][site_value_formatted]
                
        ## specify site instance and it's data properties
        kg.add( (site_iri, RDFS.subClassOf, _PREFIX["me_egad"]["Feature"]) )
        kg.add( (site_iri, RDFS['label'], Literal(str(site_description))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg

## triplify the abox for pfas parameters
def triplify_pfas_parameter(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## sample type record details
        parameter_name = row['Parameter'] # parameter name
        parameter_abbreviation = row['Abbreviation'] # parameter abbreviation
        
        ## construct type IRI
        parameter_iri = _PREFIX["me_egad_data"][f"{'parameter'}.{row['Abbreviation-aik-pfas-ont']}"]
                
        ## specify type instance and it's data properties
        kg.add( (parameter_iri, RDF.type, _PREFIX["me_egad"]["EGAD-PFAS"]) )
        kg.add( (parameter_iri, RDFS['label'], Literal(str(parameter_name))) )
        kg.add( (parameter_iri, _PREFIX["me_egad"]['parameterAbbreviaion'], Literal(parameter_abbreviation, datatype = XSD.string)) )
        kg.add( (parameter_iri, _PREFIX["me_egad"]['parameterName'], Literal(parameter_name, datatype = XSD.string)) )
        if is_valid(row['FunctionalGroup']):
            kg.add( (parameter_iri, _PREFIX["me_egad"]['functionalGroup'], Literal(row['FunctionalGroup'], datatype = XSD.string)) )
        if is_valid(row['IonicProperty']):
            kg.add( (parameter_iri, _PREFIX["me_egad"]['ionicProperty'], Literal(row['IonicProperty'], datatype = XSD.string)) )
        if is_valid(row['CarbonCount']): 
            kg.add( (parameter_iri, _PREFIX["me_egad"]['carbonCount'], Literal(row['CarbonCount'], datatype = XSD.integer)) )
        if is_valid(row['PFAS_Type']): 
            kg.add( (parameter_iri, _PREFIX["me_egad"]['pfasType'], Literal(row['PFAS_Type'], datatype = XSD.string)) )
        if is_valid(row['Specific_PFAS_Type']):
            print(row['Specific_PFAS_Type'])
            kg.add( (parameter_iri, _PREFIX["me_egad"]['pfasSubType'], Literal(row['Specific_PFAS_Type'], datatype = XSD.string)) )
        if is_valid(row['Structure']): 
            kg.add( (parameter_iri, _PREFIX["me_egad"]['chemicalStructure'], Literal(row['Structure'], datatype = XSD.string)) )   
   
    return kg

def is_valid(value):
    if (str(value) == 'Missing'):
        return False
    else:
        return True
    
if __name__ == "__main__":
    main()
