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
from pathlib import Path

## importing utility/variable file
sys.path.insert(0, 'C:/Users/Shirly/Documents/GitHub/kg-construction/datasets/maine/egad')
from variable import NAME_SPACE, _PREFIX

## declare variables
logname = "log"

metadata_files = ['analysis_lab', 'sample_collection_method', 'sample_location', 'sample_point_type', 'sample_type', 'site_type', 'pfas_parameter', 'test_method', 'concentration_qualifier', 'validation_level', 'result_type', 'sample_treatment_status']

#metadata_files = ['pfas_parameter']

## data path
root_folder = Path(__file__).resolve().parent.parent.parent.parent
data_dir =  root_folder / "datasets/maine/egad/metadata/"
output_dir = root_folder / "datasets/maine/egad/output/"


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
        data_df = pd.read_csv(data_dir / f'{filename}.csv', header=0, encoding='ISO-8859-1')
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
        elif filename == 'test_method':
            kg = triplify_test_method(data_df, _PREFIX)
        elif filename == 'concentration_qualifier':
            kg = triplify_concentration_qualifier(data_df, _PREFIX)
        elif filename == 'validation_level':
            kg = triplify_validation_level(data_df, _PREFIX)
        elif filename == 'result_type':
            kg = triplify_result_type(data_df, _PREFIX)
        elif filename == 'sample_treatment_status':
            kg = triplify_treatment_status(data_df, _PREFIX)

            
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
        kg.add( (lab_iri, RDF.type, _PREFIX["prov"]["Organization"]) )
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
        collection_iri = _PREFIX["me_egad"][f"{'samplingMethod'}.{collection_value}"]
                
        ## specify collection instance and it's data properties
        kg.add( (collection_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (collection_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleCollectionMethod"]) )
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
        location_iri = _PREFIX["me_egad"][f"{'sampleLocation'}.{location_value}"]
                
        ## specify location instance and it's data properties
        kg.add( (location_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (location_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleDetailedLocation"]) )
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
        point_iri = _PREFIX["me_egad"][f"{'featureType'}.{point_value_formatted}"]
                
        ## specify point instance and it's data properties
        #kg.add( (point_iri, RDFS.subClassOf, _PREFIX["me_egad"]["Feature"]) )
        kg.add( (point_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (point_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SamplePointType"]) )
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
        type_iri = _PREFIX["me_egad"][f"{'sampleMaterialType'}.{type_value}"]
                
        ## specify type instance and it's data properties
        kg.add( (type_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (type_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleMaterialType"]) )
        kg.add( (type_iri, RDFS['label'], Literal(str(type_description))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg

## triplify the tbox for site type
def triplify_site_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## site record details
        site_value = row['VALUE'] # site-type abbreviation
        site_description = row['DESCRIPTION'] # site-type description
        site_definition = row['DEFINITION'] # site-type definition
        site_value_formatted = ''.join(e for e in site_value if e.isalnum())
        
        ## construct site IRI
        site_iri = _PREFIX["me_egad"][f"{'siteType'}.{site_value_formatted}"]
                
        ## specify site instance and it's data properties
        #kg.add( (site_iri, RDFS.subClassOf, _PREFIX["me_egad"]["Feature"]) )
        kg.add( (site_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (site_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SiteType"]) )
        kg.add( (site_iri, RDFS['label'], Literal(str(site_description))) )
        kg.add( (site_iri, _PREFIX["skos"]['definition'], Literal(str(site_definition))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg

## triplify the abox for pfas parameters
def triplify_pfas_parameter(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## parameter record details
        parameter_name = row['Parameter'] # parameter name
        parameter_abbreviation = row['Abbreviation'] # parameter abbreviation
        
        ## construct type IRI
        parameter_iri = _PREFIX["me_egad"][f"{'parameter'}.{row['Abbreviation-aik-pfas-ont']}"]
                
        ## specify type instance and it's data properties
        kg.add( (parameter_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (parameter_iri, RDF.type, _PREFIX["me_egad"]["EGAD-PFAS-ParameterName"]) )
        kg.add( (parameter_iri, RDFS['label'], Literal(str(parameter_name))) )
        kg.add( (parameter_iri, _PREFIX["me_egad"]['parameterAbbreviation'], Literal(parameter_abbreviation, datatype = XSD.string)) )
        kg.add( (parameter_iri, _PREFIX["me_egad"]['parameterName'], Literal(parameter_name, datatype = XSD.string)) )
       
   
    return kg


## triplify the controlled vocabulary for test methods
def triplify_test_method(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## method record details
        method_name = row['VALUE'] # method name
        method_description = row['DESCRIPTION'] # method description
        
        ## construct type IRI
        method_name = method_name.replace(' ', "")
        method_name = method_name.replace("/", "")
        method_iri = _PREFIX["me_egad"][f"{'testMethod'}.{method_name}"]
                
        ## specify type instance and it's data properties
        kg.add( (method_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (method_iri, RDF.type, _PREFIX["me_egad"]["EGAD-AnalysisMethod"]) )
        kg.add( (method_iri, RDFS['label'], Literal(str(method_description))) )       
   
    return kg

## triplify the controlled vocabulary for concentration qualifiers
def triplify_concentration_qualifier(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## qualfier record details
        qualfier_name = row['VALUE'] # qualfier value
        qualfier_description = row['DESCRIPTION'] # qualfier description
        qualfier_group = row['PARAMETER_GROUP'] # parameter group 
        qualfier_name = qualfier_name.replace("/", "-")
        
        ## construct type IRI
        qualfier_iri = _PREFIX["me_egad"][f"{'concentrationQualifier'}.{qualfier_name}"]
                
        ## specify type instance and it's data properties
        kg.add( (qualfier_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (qualfier_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ValidationQualifier"]) )
        kg.add( (qualfier_iri, RDF.type, _PREFIX["me_egad"]["EGAD-LabQualifier"]) )
        kg.add( (qualfier_iri, RDFS['label'], Literal(str(qualfier_description))) )
        kg.add( (qualfier_iri, _PREFIX["me_egad"]['parameterGroup'], Literal(str(qualfier_group))) )
   
    return kg


## triplify the controlled vocabulary for validation level
def triplify_validation_level(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## validation level record details
        validation_level_name = row['VALUE'] # validation level value
        validation_level_description = row['DESCRIPTION'] # validation level description
        
        ## construct type IRI
        validation_level_name = validation_level_name.replace(' ', "")
        validation_level_name = validation_level_name.replace("/", "")
        validation_level_iri = _PREFIX["me_egad"][f"{'validationLevel'}.{validation_level_name}"]
                
        ## specify type instance and it's data properties
        kg.add( (validation_level_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (validation_level_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ValidationLevel"]) )
        kg.add( (validation_level_iri, RDFS['label'], Literal(str(validation_level_description))) )       
   
    return kg

## triplify the controlled vocabulary for result type
def triplify_result_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## result type record details
        result_type_value = row['VALUE'] # result type value
        result_type_description = row['DESCRIPTION'] # result type description
        
        ## construct type IRI
        result_type_value = result_type_value.replace(' ', "")
        result_type_value = result_type_value.replace("/", "")
        result_type_iri = _PREFIX["me_egad"][f"{'resultType'}.{result_type_value}"]
                
        ## specify type instance and it's data properties
        kg.add( (result_type_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (result_type_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ResultType"]) )
        kg.add( (result_type_iri, RDFS['label'], Literal(str(result_type_description))) )       
   
    return kg

## triplify the controlled vocabulary for treatment status
def triplify_treatment_status(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## treatment status record details
        treatment_status_value = row['VALUE'] # treatment status value
        treatment_status_description = row['DESCRIPTION'] # treatment status description
        
        ## construct type IRI
        treatment_status_iri = _PREFIX["me_egad"][f"{'treatmentStatus'}.{row['VALUE']}"]
                
        ## specify type instance and it's data properties
        kg.add( (treatment_status_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (treatment_status_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleTreatmentStatus"]) )
        kg.add( (treatment_status_iri, RDFS['label'], Literal(str(treatment_status_description))) )       
   
    return kg

def is_valid(value):
    if (str(value) == 'Missing'):
        return False
    else:
        return True
    
if __name__ == "__main__":
    main()
