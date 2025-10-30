import os
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS, SKOS
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

metadata_files = ['analysis_lab', 'sample_collection_method', 'sample_location', 'sample_point_type', 'sample_type', 'sample_type_qualifier', 'site_type', 'pfas_parameter', 'test_method', 'concentration_qualifier', 'validation_level', 'result_type', 'sample_treatment_status', 'ChemicalMapping']
#this variable can be manipulated to only run some of the metadata
metadata_files = ['ChemicalMapping']

## data path
root_folder = Path(__file__).resolve().parent.parent.parent.parent
data_dir =  root_folder / "datasets/maine/egad/metadata/"
dataset_dir = root_folder / "datasets/data/egad-maine-samples/"
output_dir = root_folder / "datasets/maine/egad/controlledVocab/"


## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for EGAD metadata")

def main():
    #load data to learn which instances of the controlled vocabulary are actually used in pfas data
    egad_samples_df = pd.read_excel(dataset_dir / 'Statewide EGAD PFAS File March 2024.xlsx', sheet_name="PFAS Sample Data", usecols=['SAMPLE_POINT_TYPE', 'ANALYSIS_LAB','SAMPLE_TYPE_UPDATE', 'SAMPLE_TYPE_QUALIFIER', 'SAMPLE_LOCATION', 'TREATMENT_STATUS', 'SAMPLE_COLLECTION_METHOD',  'TEST_METHOD', 'RESULT_TYPE', 'PARAMETER_SHORTENED', 'PARAMETER_NAME','VALIDATION_LEVEL'], header=0, engine='openpyxl', na_values=['NOT APPLICABLE','UNKNOWN','UNK','NONE'])
    unq_sample_point_type = egad_samples_df['SAMPLE_POINT_TYPE'].unique()
    unq_analysis_lab = egad_samples_df['ANALYSIS_LAB'].unique()
    unq_sample_type_update = egad_samples_df['SAMPLE_TYPE_UPDATE'].unique()
    unq_sample_type_qualifier = egad_samples_df['SAMPLE_TYPE_QUALIFIER'].unique()
    unq_sample_location= egad_samples_df['SAMPLE_LOCATION'].unique()
    unq_treatment_status = egad_samples_df['TREATMENT_STATUS'].unique()
    unq_sample_collection_method = egad_samples_df['SAMPLE_COLLECTION_METHOD'].unique()
    unq_test_method = egad_samples_df['TEST_METHOD'].unique()
    unq_result_type = egad_samples_df['RESULT_TYPE'].unique()
    unq_param = egad_samples_df['PARAMETER_SHORTENED'].unique()
    unq_param_named = pd.read_csv(data_dir / f'pfas_parameter.csv', header=0, encoding='ISO-8859-1')
    unq_valid = egad_samples_df['VALIDATION_LEVEL'].unique()

    # load files and send each to its own triplification function 
    for filename in metadata_files:
        data_df = pd.read_csv(data_dir / f'{filename}.csv', header=0, encoding='ISO-8859-1')
        logger = logging.getLogger('Data loaded to dataframe')
        if filename == 'analysis_lab':
            kg = triplify_lab(data_df, _PREFIX, unq_analysis_lab)
        elif filename == 'sample_collection_method':
            kg = triplify_collection_method(data_df, _PREFIX, unq_sample_collection_method)
        elif filename == 'sample_location':
            kg = triplify_location(data_df, _PREFIX, unq_sample_location)
        elif filename == 'sample_point_type':
            kg = triplify_point_type(data_df, _PREFIX, unq_sample_point_type)
        elif filename == 'sample_type':
            kg = triplify_sample_type(data_df, _PREFIX, unq_sample_type_update)
        elif filename == 'sample_type_qualifier':
            kg = triplify_sample_type_qualifier(data_df, _PREFIX, unq_sample_type_qualifier)
        elif filename == 'site_type':
            kg = triplify_site_type(data_df, _PREFIX)
        elif filename == 'pfas_parameter':
            kg = triplify_pfas_parameter(data_df, _PREFIX, unq_param)
        elif filename == 'test_method':
            kg = triplify_test_method(data_df, _PREFIX, unq_test_method)
        elif filename == 'concentration_qualifier':
            kg = triplify_concentration_qualifier(data_df, _PREFIX)
        elif filename == 'validation_level':
            kg = triplify_validation_level(data_df, _PREFIX, unq_valid)
        elif filename == 'result_type':
            kg = triplify_result_type(data_df, _PREFIX, unq_result_type)
        elif filename == 'sample_treatment_status':
            kg = triplify_treatment_status(data_df, _PREFIX, unq_treatment_status)
        elif filename == 'ChemicalMapping':
            kg = triplify_param_mapping(data_df, _PREFIX, unq_param_named)


        # output the resulting triples for each metadata file
        data_df.iloc[0:0]
        kg_turtle_file = output_dir / f"{filename}.ttl"
        kg.serialize(kg_turtle_file,format='turtle')


def Initial_KG(_PREFIX):
    prefixes = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


## triplify the abox for labs
def triplify_lab(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## lab record details
        lab_value = row['VALUE'] # lab abbreviation
        lab_description = row['DESCRIPTION'] # lab description
        
        ## construct lab IRI
        lab_iri = _PREFIX["me_egad_data"][f"{'organization.lab'}.{lab_value}"]
                
        ## specify lab instance and it's data properties
        if pd.notnull(lab_value) and lab_value != 'ZZ' and lab_description in usage:
            kg.add( (lab_iri, RDF.type, _PREFIX["prov"]["Organization"]) )
            kg.add( (lab_iri, RDFS['label'], Literal(str(lab_description))) )
        #kg.add( (lab_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(lab_description, datatype = XSD.string)) )

   
    return kg

## triplify the abox for sample collection methods
def triplify_collection_method(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## collection record details
        collection_value = row['VALUE'] # collection abbreviation
        collection_description = row['DESCRIPTION'] # collection description
        
        ## construct collection IRI
        collection_iri = _PREFIX["me_egad_data"][f"{'samplingMethod'}.{collection_value}"]
                
        ## specify collection instance and it's data properties
        if collection_description in usage:
            kg.add( (collection_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (collection_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleCollectionMethod"]) )
            kg.add( (collection_iri, RDFS['label'], Literal(str(collection_description))) )
            #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg


## triplify the abox for sample location
def triplify_location(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## location record details
        location_value = row['VALUE'] # location abbreviation
        location_description = row['DESCRIPTION'] # location description
        
        ## construct collection IRI
        location_iri = _PREFIX["me_egad_data"][f"{'sampleLocation'}.{location_value}"]
                
        ## specify location instance and it's data properties
        if location_description in usage:
            kg.add( (location_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (location_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleDetailedLocation"]) )
            kg.add( (location_iri, RDFS['label'], Literal(str(location_description))) )
            #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg


## triplify the tbox for sample point type
def triplify_point_type(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## location record details
        point_value = row['VALUE'] # point abbreviation
        point_description = row['DESCRIPTION'] # point description
        point_value_formatted = ''.join(e for e in point_value if e.isalnum())
        
        ## construct point IRI
        point_iri = _PREFIX["me_egad_data"][f"{'featureType'}.{point_value_formatted}"]
                
        ## specify point instance and it's data properties
        if point_description in usage:
            #kg.add( (point_iri, RDFS.subClassOf, _PREFIX["me_egad"]["Feature"]) )
            kg.add( (point_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (point_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SamplePointType"]) )
            kg.add( (point_iri, RDFS['label'], Literal(str(point_description))) )
            #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg


## triplify the abox for sample material type
def triplify_sample_type(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## sample type record details
        type_value = row['VALUE'] # material abbreviation
        type_description = row['DESCRIPTION'] # material description
        
        ## construct type IRI
        type_iri = _PREFIX["me_egad_data"][f"{'sampleMaterialType'}.{type_value}"]
                
        ## specify type instance and it's data properties
        if type_description in usage:
            kg.add( (type_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (type_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleMaterialType"]) )
            kg.add( (type_iri, RDFS['label'], Literal(str(type_description))) )
            #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg

def triplify_sample_type_qualifier(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    ## materialize each record
    for idx, row in df.iterrows():
        type_value = row['VALUE'] # material abbreviation
        type_description = row['DESCRIPTION'] # material description

        ## construct type IRI
        type_iri = _PREFIX["me_egad_data"][f"{'sampleMaterialTypeQualifier'}.{type_value}"]
                
        ## specify type instance and it's data properties
        if type_description in usage:   #only create iris for the vocab terms that are used
            kg.add( (type_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (type_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampleMaterialTypeQualifier"]) )
            kg.add( (type_iri, RDFS['label'], Literal(str(type_description))) )
        
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
        site_iri = _PREFIX["me_egad_data"][f"{'siteType'}.{site_value_formatted}"]
                
        ## specify site instance and it's data properties
        
        #kg.add( (site_iri, RDFS.subClassOf, _PREFIX["me_egad"]["Feature"]) )
        kg.add( (site_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (site_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SiteType"]) )
        kg.add( (site_iri, RDFS['label'], Literal(str(site_description))) )
        kg.add( (site_iri, _PREFIX["skos"]['definition'], Literal(str(site_definition))) )
        #kg.add( (collection_iri, _PREFIX["aik-pfas-ont"]['labDescription'], Literal(collection_description, datatype = XSD.string)) )

   
    return kg

## triplify the abox for pfas parameters
def triplify_pfas_parameter(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    print(usage)
    #print(df.info(verbose=True))
    ## materialize each record
    for idx, row in df.iterrows():
        ## parameter record details
        parameter_name = row['Parameter'] # parameter name
        parameter_abbreviation = row['Abbreviation'] # parameter abbreviation
        
        ## construct type IRI
        parameter_iri = _PREFIX["me_egad_data"][f"{'parameter'}.{row['Abbreviation-aik-pfas-ont']}"]
                
        ## specify type instance and it's data properties
        kg.add( (parameter_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (parameter_iri, RDF.type, _PREFIX["me_egad"]["EGAD-PFAS-ParameterName"]) )
        kg.add( (parameter_iri, RDFS['label'], Literal(str(parameter_name))) )
        kg.add( (parameter_iri, _PREFIX["skos"]['altLabel'], Literal(parameter_abbreviation, datatype = XSD.string)) )
        #kg.add( (parameter_iri, _PREFIX["me_egad"]['parameterAbbreviation'], Literal(parameter_abbreviation, datatype = XSD.string)) )
        #kg.add( (parameter_iri, _PREFIX["me_egad"]['parameterName'], Literal(parameter_name, datatype = XSD.string)) )

        if (row['QuantityKind'] == 'Cumulative'):
            kg.add( (parameter_iri, RDF.type, _PREFIX['coso']['SubstanceCollection']))
        #kg.add( (iris['substance'], _PREFIX["me_egad_data"]['dep_chemicalID'], Literal(sampleobs['chemical_number'] , datatype = XSD.string)) )
        else:
            kg.add( (parameter_iri, RDF.type, _PREFIX['coso']['Substance']))
        #kg.add( (iris['substance'], _PREFIX["coso"]['casNumber'], Literal(sampleobs['chemical_number']  , datatype = XSD.string)) ) #TODO update to reused relation, ignore ones that are custom DEP
        
   
    return kg

def triplify_param_mapping(df:pd.DataFrame, _PREFIX, lookup:pd.DataFrame):
    kg = Initial_KG(_PREFIX)
    
    lookup = lookup.set_index('Parameter')
    combined = df.join(lookup, on='ï»¿INPUT', how='right')
    print(combined.info())
    for idx, row in combined.iterrows():
        id = row['DTXSID']
        parameter_iri = _PREFIX["me_egad_data"][f"{'parameter'}.{row['Abbreviation-aik-pfas-ont']}"]
        dtxsid_iri = _PREFIX['comptox'][f"CompTox_{id}"]

        if pd.notna(row['DTXSID']) and row['DTXSID'] != "-":
            kg.add((parameter_iri, _PREFIX['comptox']['sameAsComptoxSubstance'], dtxsid_iri))
            kg.add((dtxsid_iri, RDF.type, _PREFIX['comptox']['ChemicalEntity']))
            kg.add((dtxsid_iri, RDFS.label, Literal(row['PREFERRED_NAME'])))
        else:
            print('skipping ', row['Abbreviation-aik-pfas-ont'])

    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_6_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFHPA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_6_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFHXS']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_6_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFOA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_6_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFNA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_6_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFOS']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_6_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFDA']))

    kg.add((_PREFIX['me_egad_data']['parameter.SUM_PFOA_PFOS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFOA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_PFOA_PFOS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFOS']))

    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_5_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFHPA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_5_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFHXS']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_5_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFOA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_5_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFNA']))
    kg.add((_PREFIX['me_egad_data']['parameter.SUM_OF_5_PFAS'], _PREFIX['coso']['hasMember'], _PREFIX['me_egad_data']['parameter.PFOS']))


    return kg




## triplify the controlled vocabulary for test methods
def triplify_test_method(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    print(usage)
    print(df['VALUE'].unique())
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## method record details
        method_name = row['VALUE'] # method name
        method_description = row['DESCRIPTION'] # method description
        
        ## construct type IRI
        method_name = method_name.replace(' ', "")
        method_name = method_name.replace("/", "")
        method_iri = _PREFIX["me_egad_data"][f"{'testMethod'}.{method_name}"]
                
        ## specify type instance and it's data properties
        if method_name in usage:
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
        #qualfier_group = row['PARAMETER_GROUP'] # parameter group 
        qualfier_name = qualfier_name.replace("/", "-").replace('*', "s")
        
        ## construct type IRI
        qualfier_iri = _PREFIX["me_egad_data"][f"{'concentrationQualifier'}.{qualfier_name}"]
                
        ## specify type instance and it's data properties
        kg.add( (qualfier_iri, RDF.type, OWL.NamedIndividual) )
        kg.add( (qualfier_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ConcentrationQualifier"]) )
        #kg.add( (qualfier_iri, RDF.type, _PREFIX["me_egad"]["EGAD-LabQualifier"]) )
        kg.add( (qualfier_iri, RDFS['label'], Literal(str(qualfier_description))) )
       # kg.add( (qualfier_iri, _PREFIX["me_egad"]['parameterGroup'], Literal(str(qualfier_group))) )
   
    return kg


## triplify the controlled vocabulary for validation level
def triplify_validation_level(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## validation level record details
        validation_level_name = row['VALUE'] # validation level value
        validation_level_description = row['DESCRIPTION'] # validation level description
        
        ## construct type IRI
        validation_level_name = validation_level_name.replace(' ', "")
        validation_level_name = validation_level_name.replace("/", "")
        validation_level_iri = _PREFIX["me_egad_data"][f"{'validationLevel'}.{validation_level_name}"]
                
        ## specify type instance and it's data properties
        if validation_level_description in usage:
            kg.add( (validation_level_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (validation_level_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ValidationLevel"]) )
            kg.add( (validation_level_iri, RDFS['label'], Literal(str(validation_level_description))) )       
   
    return kg

## triplify the controlled vocabulary for result type
def triplify_result_type(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## result type record details
        result_type_value = row['VALUE'] # result type value
        result_type_description = row['DESCRIPTION'] # result type description
        
        ## construct type IRI
        result_type_value = result_type_value.replace(' ', "")
        result_type_value = result_type_value.replace("/", "")
        result_type_iri = _PREFIX["me_egad_data"][f"{'resultType'}.{result_type_value}"]
                
        ## specify type instance and it's data properties
        if result_type_description in usage:
            kg.add( (result_type_iri, RDF.type, OWL.NamedIndividual) )
            kg.add( (result_type_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ResultType"]) )
            kg.add( (result_type_iri, RDFS['label'], Literal(str(result_type_description))) )       
   
    return kg

## triplify the controlled vocabulary for treatment status
def triplify_treatment_status(df, _PREFIX, usage):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## treatment status record details
        treatment_status_value = row['VALUE'] # treatment status value
        treatment_status_description = row['DESCRIPTION'] # treatment status description
        
        ## construct type IRI
        treatment_status_iri = _PREFIX["me_egad_data"][f"{'treatmentStatus'}.{row['VALUE']}"]
                
        ## specify type instance and it's data properties
        if treatment_status_description in usage:
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
