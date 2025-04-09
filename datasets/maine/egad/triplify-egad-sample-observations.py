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
from pathlib import Path
from pyutil import *
from shapely.geometry import Point



## importing utility/variable file
sys.path.insert(0, 'C:/Users/Shirly/Documents/GitHub/kg-construction/datasets/maine/egad')
from variable import NAME_SPACE, _PREFIX


## declare variables
logname = "log"
cdt = URIRef("http://w3id.org/lindt/custom_datatypes#ucum")
lab_dict = []
material_type_dict = []
collection_method_dict = []
point_type_dict = []
location_type_dict = []
site_type_dict = []
pfas_parameter_dict = []


## data path
root_folder = Path(__file__).resolve().parent.parent.parent.parent
data_dir =  root_folder/ "datasets/data/egad-maine-samples/"
metadata_dir = root_folder /"datasets/maine/egad/metadata/"
output_dir = root_folder/ "datasets/maine/egad/egad-maine-samples/"


## data dictionaries -- for controlled vocabularies
with open(metadata_dir / 'analysis_lab.csv', mode='r') as infile:
    reader = csv.reader(infile)
    lab_dict = {rows[1]:rows[0] for rows in reader}
    lab_dict['NA'] = 'NA'

with open(metadata_dir / 'sample_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    material_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_type_qualifier.csv', mode='r') as infile:
    reader = csv.reader(infile)
    material_qualifier_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_collection_method.csv', mode='r') as infile:
    reader = csv.reader(infile)
    collection_method_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_location.csv', mode='r') as infile:
    reader = csv.reader(infile)
    location_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_point_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    point_type_dict = {rows[1]:rows[0] for rows in reader}
    
#with open(metadata_dir / 'site_type.csv', mode='r') as infile:
#    reader = csv.reader(infile)
#    site_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'pfas_parameter.csv', mode='r') as infile:
    reader = csv.reader(infile)
    pfas_parameter_dict = {rows[1]:rows[2] for rows in reader}

with open(metadata_dir / 'pfas_parameter.csv', mode='r') as infile:
    reader = csv.reader(infile)
    pfas_parameter_kind_dict = {rows[1]:rows[3] for rows in reader}

with open(metadata_dir / 'pfas_parameter.csv', mode='r') as infile:
    reader = csv.reader(infile)
    pfas_type_dict = {rows[1]:rows[3] for rows in reader}

with open(metadata_dir / 'test_method.csv', mode='r') as infile:
    reader = csv.reader(infile)
    test_method_dict = {rows[0]:rows[0] for rows in reader}

with open(metadata_dir / 'validation_level.csv', mode='r') as infile:
    reader = csv.reader(infile)
    validation_level_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'result_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    result_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_treatment_status.csv', mode='r') as infile:
    reader = csv.reader(infile)
    treatment_status_dict = {rows[1]:rows[0] for rows in reader}

    


## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for EGAD sites and samples")

def main():
    #ignore NOT APPLICABLE and UNKNOWN data values
    egad_samples_df = pd.read_excel(data_dir / 'Statewide EGAD PFAS File March 2024.xlsx', sheet_name="PFAS Sample Data", header=0, engine='openpyxl', na_values=['NOT APPLICABLE','UNKNOWN','UNK','NONE'])
    logger = logging.getLogger('Data loaded to dataframe.')
    print(egad_samples_df.info(verbose=True, show_counts=True))

    kg, kg_obs, kg_result = triplify_egad_pfas_sample_data(egad_samples_df, _PREFIX)
    kg_turtle_file = "egad_samples_output.ttl".format(output_dir)
    kg.serialize(kg_turtle_file,format='turtle')
    kg_obs.serialize("egad_observation_output.ttl".format(output_dir), format='turtle')
    kg_result.serialize('egad_result_output.ttl'.format(output_dir), format='turtle')
    logger = logging.getLogger('Finished triplifying EGAD PFAS sample data.')
    
def Initial_KG(prefixes: dict[str, str]) -> Graph:
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg

def get_attributes(row):
    """Select and format attributes from input data"""
    ## sample point record details
    samplepoint = {
        'number': row['SAMPLE_POINT_NUMBER'], # sample point number
        'webname': row['SAMPLE_POINT_WEB_NAME'], # sample point web name
    }

    if pd.notnull(row['SAMPLE_POINT_TYPE']):
       samplepoint['type'] = ''.join(e for e in point_type_dict[row['SAMPLE_POINT_TYPE']] if e.isalnum()) # sample point type

    ## sample record 
    sample = {
        'id': row['SAMPLE_ID'], # sample point ID
        'id_formatted': ''.join(e.upper() for e in row['SAMPLE_ID'] if e.isalnum())
    }

    if pd.notnull(row['SAMPLE_DATE']):
        sample['date'] = pd.to_datetime(row['SAMPLE_DATE'])
        sample['date_formatted'] = sample['date'].strftime('%Y%m%d')
    else:
        sample['date_formatted'] = ''
    if pd.notnull(row['SAMPLE_LOCATION']) and row['SAMPLE_LOCATION'] != "UNKNOWN":
        sample['location'] = row['SAMPLE_LOCATION']
    if pd.notnull(row['SAMPLE_COLLECTION_METHOD']) and row['SAMPLE_COLLECTION_METHOD'] != 'UNKNOWN':
        sample['collection_method'] = row['SAMPLE_COLLECTION_METHOD']
    if pd.notnull( row['TREATMENT_STATUS']) and row['TREATMENT_STATUS'] != 'UNKNOWN' and row['TREATMENT_STATUS'] != 'NOT APPLICABLE':
        sample['treatment_status'] = row['TREATMENT_STATUS'] # sample treatment status
    if pd.notnull(row['SAMPLED_BY']) and row['SAMPLED_BY'] != "????": 
        sample['sampled_by'] = row['SAMPLED_BY']
        sample['agent'] = ''.join(c for c in row['SAMPLED_BY'] if c.isalnum())

    
    ## observation
    sampleobs = {
        'analysislab': row['ANALYSIS_LAB'] if pd.notnull(row['ANALYSIS_LAB']) else 'NA', # sample analysis lab
        'parameter': row['PARAMETER_SHORTENED'], # pfas parameter    
        'parameter_formatted': ''.join(e for e in row['PARAMETER_SHORTENED'] if e.isalnum()),
        'chemical_number': row['CAS_NO'],
    }

    if pd.notnull(row['SAMPLE_TYPE_UPDATE']):
        sampleobs['type'] = row['SAMPLE_TYPE_UPDATE'] # sample type
    if pd.notnull(row['SAMPLE_TYPE_QUALIFIER']) and row['SAMPLE_TYPE_QUALIFIER'] not in ['NOT APPLICABLE']:
        sampleobs['typequalifier'] = row['SAMPLE_TYPE_QUALIFIER'] #sample type qualifier (species)

    ### analysis 
    sampleobs['analysis_id'] = row['ANALYSIS_LAB_SAMPLE_ID'] # ID assigned by an analysis lab
    sampleobs['analysis_id_formatted'] = ''.join(e for e in sampleobs['analysis_id'] if e.isalnum())
    if pd.notnull(row['ANALYSIS_DATE']):
        sampleobs['analysis_date'] = pd.to_datetime(row['ANALYSIS_DATE']) #datetime.strptime(str(), '%m/%d/%Y')  # analysis date

    if pd.notnull(row['TEST_METHOD']):
        sampleobs['analysis_method'] = row['TEST_METHOD'] # analysis method

    ## contaminant measurement (result) record details
    result = {}
    result['pfas_concentration'] = row['CONCENTRATION'] # concentration
    result['pfas_concentration_units'] = row['PARAMETER_UNITS'] # concentration-unit

    if pd.notnull(row['RESULT_TYPE']):
        result['type'] = row['RESULT_TYPE'] # result type

    if pd.notnull(row['REPORTING_LIMIT']):
        result['pfas_rl'] = row['REPORTING_LIMIT'] # reporting limit
    if  pd.notnull(row['MDL']):
        result['pfas_mdl'] = row['MDL'] # method detection limit
    if  pd.notnull(row['VALIDATION_LEVEL']):
        result['validation_level'] = str(row['VALIDATION_LEVEL']) # validation level
    if  pd.notnull(row['VALIDATION QUALIFIER']):
        result['validation_qualifier'] = str(row['VALIDATION QUALIFIER']).replace("/", "-").replace("*","s")  # validation qualifier
    if  pd.notnull(row['LAB_QUALIFIER']):
        result['lab_qualifier'] = str(row['LAB_QUALIFIER']).replace("/", "-").replace("*", "s") # lab qualifier
    result['units'] = row['PARAMETER_UNITS'] # units of measurement
            

    return samplepoint, sample, sampleobs, result

def get_iris(samplepoint, sample, sampleobs, result):
    """Build iris for any objects"""
    iris = {}
    ## main sample entity iris
    iris['samplepoint'] = _PREFIX["me_egad_data"][f"{'samplePoint'}.{samplepoint['number']}"]
    iris['samplefeature'] = _PREFIX["me_egad_data"][f"{'sampledFeature'}.{samplepoint['number']}"]
    iris['sample'] = _PREFIX["me_egad_data"][f"{'sample'}.{lab_dict[sampleobs['analysislab']]}{sampleobs['analysis_id_formatted']}.{sample['date_formatted']}"] #sample id is not unique
    iris['sampleobs'] = _PREFIX["me_egad_data"][f"{'observation'}.{lab_dict[sampleobs['analysislab']]}{sampleobs['analysis_id_formatted']}.{sample['date_formatted']}.{sampleobs['chemical_number']}"]
    if 'sampled_by' in sample.keys():
        iris['sample_agent'] = _PREFIX['me_egad_data'][f"{sample['agent']}"]
    # CV iris
    if 'type' in samplepoint.keys():
        iris['samplepoint_type'] = _PREFIX["me_egad_data"][f"{'featureType'}.{samplepoint['type']}"]
    
    if 'type' in sampleobs.keys():
        iris['samplematerial'] = _PREFIX["me_egad_data"][f"{'sampleMaterialType'}.{material_type_dict[sampleobs['type']]}"] 
    if 'typequalifier' in sampleobs.keys():
        iris['samplematerialqualifier'] = _PREFIX["me_egad_data"][f"{'sampleMaterialTypeQualifier'}.{material_qualifier_dict[sampleobs['typequalifier']]}"]

    if 'location' in sample.keys():
        iris['samplelocation'] = _PREFIX["me_egad_data"][f"{'sampleLocation'}.{location_type_dict[sample['location']]}"] 

    if 'treatment_status' in sample.keys():
        iris['sampletreatment'] = _PREFIX["me_egad_data"][f"{'treatmentStatus'}.{treatment_status_dict[sample['treatment_status']]}"]  
    
    if 'collection_method' in sample.keys():
        iris['samplecollectionmethod'] = _PREFIX["me_egad_data"][f"{'samplingMethod'}.{collection_method_dict[sample['collection_method']]}"]

    if 'analysis_method' in sampleobs.keys():
        iris['analysis_method'] = _PREFIX["me_egad_data"][f"{'testMethod'}.{test_method_dict[sampleobs['analysis_method']]}"]

    if 'type' in result.keys():
        iris['result_type'] = _PREFIX["me_egad_data"][f"{'resultType'}.{result_type_dict[result['type']]}"]

    ## construct analysis lab, sample material and measured PFAS parameter IRI
    iris['analysislab'] = _PREFIX["me_egad_data"][f"{'organization.lab'}.{lab_dict[sampleobs['analysislab']]}"]
    iris['substance'] = _PREFIX["me_egad"][f"{'parameter'}.{pfas_parameter_dict[sampleobs['parameter']]}"]
    iris['result'] = _PREFIX["me_egad_data"][f"{'result'}.{sampleobs['analysis_id_formatted']}.{lab_dict[sampleobs['analysislab']]}.{sample['date_formatted']}.{sampleobs['chemical_number']}"]
    iris['quantity'] = _PREFIX["me_egad_data"][f"{'quantityValue'}.{sampleobs['analysis_id_formatted']}.{lab_dict[sampleobs['analysislab']]}.{sample['date_formatted']}.{sampleobs['chemical_number']}"]

    ## unit qudt 
    if result['pfas_concentration_units'] == "NG/G":
        iris['unit'] = _PREFIX["coso"]['NanoGM-PER-GM'] #numerically equivalent to unit:MicroGM-PER-KiloGM, but different preferred label, etc. 
    elif result['pfas_concentration_units'] == "MG/KG":
        iris['unit'] = _PREFIX["me_egad"]['unit.MG-KG']
    elif result['pfas_concentration_units'] == "%":
        iris['unit'] = _PREFIX["me_egad"]['unit.percent'] #this could just be unit:PERCENT
    elif result['pfas_concentration_units'] == "NG/L":
        iris['unit'] = _PREFIX["unit"]['NanoGM-PER-L']
    elif result['pfas_concentration_units'] == "NG/ML":
        iris['unit'] = _PREFIX["unit"]['NanoGM-PER-MicroL']
    elif result['pfas_concentration_units'] == "MG/L":
        iris['unit'] = _PREFIX["unit"]['MilliGM-PER-L']
    elif result['pfas_concentration_units'] == "UG/KG":
        iris['unit'] =  _PREFIX["unit"]['MicroGM-PER-KiloGM']
    elif result['pfas_concentration_units'] == "UG/L":
        iris['unit'] = _PREFIX["unit"]['MicroGM-PER-L']

    # validation
    if 'validation_level' in result.keys(): 
        if (str(result['validation_level']).startswith("Tier II: EPA-NE REGION 1 GUIDELINES")):
            validation_string = 'TierII-EPA-NE-REGION-1-GUIDELINES'
            iris['validationLevel'] = _PREFIX["me_egad_data"][f"{'validationLevel'}.{validation_string}"] 
        else:
            iris['validationLevel'] = _PREFIX["me_egad_data"][f"{'validationLevel'}.{validation_level_dict[result['validation_level']]}"] 

    if 'validation_qualifier' in result.keys():
            iris['validationQualifier'] = _PREFIX["me_egad_data"][f"{'concentrationQualifier'}.{result['validation_qualifier']}"] 

    if 'lab_qualifier' in result.keys():
            iris['labQualifier'] = _PREFIX["me_egad_data"][f"{'concentrationQualifier'}.{result['lab_qualifier']}"] 

    #share quantities for rl and mdl based on values, precision, and units
    if 'pfas_rl' in result.keys():
            iris['rl'] = _PREFIX["me_egad_data"][f"rl.{result['pfas_rl']}.{result['pfas_concentration_units']}"]
    if 'pfas_mdl' in result.keys():
            iris['mdl'] = _PREFIX["me_egad_data"][f"mdl.{result['pfas_mdl']}.{result['pfas_concentration_units']}"]
            #[f"mdl.{sampleobs['analysis_id_formatted']}.{lab_dict[sampleobs['analysislab']]}.{sample['date_formatted']}.{sampleobs['chemical_number']}"]

    return iris



def triplify_egad_pfas_sample_data(df, _PREFIX):
    ## triplify the abox
    kg = Initial_KG(_PREFIX)
    kg_obs = Initial_KG(_PREFIX)
    kg_result = Initial_KG(_PREFIX)
    
    ## materialize each record
    rowcount = df.shape[0]
    for idx, row in df.iterrows():
        if idx % 10000 == 0:
            print(idx, 'of', rowcount)
            
        samplepoint, sample, sampleobs, result = get_attributes(row)
        iris = get_iris(samplepoint, sample, sampleobs, result)
                
        ## specify sample point instance and it's data properties
        kg.add( (iris['samplepoint'], RDF.type, _PREFIX["me_egad"]["EGAD-SamplePoint"]) )
        kg.add( (iris['samplepoint'], RDFS['label'], Literal('EGAD sample point '+ str(samplepoint['number']))) )
        kg.add( (iris['samplepoint'], _PREFIX["me_egad"]['samplePointNumber'], Literal(samplepoint['number'], datatype = XSD.integer)) )
        kg.add( (iris['samplepoint'], _PREFIX["me_egad"]['samplePointWebName'], Literal(samplepoint['webname'], datatype = XSD.string)) )
        kg.add( (iris['samplepoint'], _PREFIX["coso"]['pointFromFeature'], iris['samplefeature']) )

                
        ## specify sample feature instance and it's data properties
        kg.add( (iris['samplefeature'], RDF.type, _PREFIX["me_egad"]["EGAD-SampledFeature"]) )
        kg.add( (iris['samplefeature'], RDFS['label'], Literal('EGAD sampled feature associated with sample point '+ str(samplepoint['number']))) )
        if 'type' in samplepoint.keys():
            kg.add( (iris['samplefeature'], _PREFIX["me_egad"]['sampledFeatureType'], iris['samplepoint_type']) )
            kg.add((iris['samplepoint'], _PREFIX["me_egad"]['samplePointType'], iris['samplepoint_type']))
        
        ## material sample
        kg.add( (iris['sample'], RDF.type, _PREFIX["me_egad"]["EGAD-Sample"]) )
        kg.add( (iris['sample'], RDFS['label'], Literal('EGAD sample '+ str(sample['id']))) )
        kg.add( (iris['sample'], _PREFIX["me_egad"]['sampleID'], Literal(sample['id'], datatype = XSD.string)) )
        kg.add( (iris['sample'], _PREFIX["coso"]['fromSamplePoint'], iris['samplepoint']) )


        ### material sample type
        if 'type' in sampleobs.keys():
            kg.add( (iris['sample'], _PREFIX["coso"]['sampleOfMaterialType'], iris['samplematerial']) )

        if 'typequalifier' in sampleobs.keys():
            kg.add( (iris['sample'], _PREFIX["coso"]['sampleOfMaterialType'], iris['samplematerialqualifier']) )

        ### material sample annotations
        if 'samplelocation' in iris.keys():
            kg.add( (iris['sample'], _PREFIX["me_egad"]['sampleCollectionLocation'], iris['samplelocation']) )

        if 'collection_method' in sample.keys():
            kg.add( (iris['sample'], _PREFIX["me_egad"]['sampleCollectionMethod'], iris['samplecollectionmethod']) )

        if 'sampletreatment' in iris.keys():
            kg.add( (iris['sample'], _PREFIX["me_egad"]['sampleTreatmentStatus'], iris['sampletreatment']) )

        if 'sample_agent' in iris.keys():
            kg.add((iris['sample'], _PREFIX["prov"]['wasAttributedTo'], iris['sample_agent'] ))
            kg.add((iris['sample_agent'], RDF.type, _PREFIX["prov"]['Agent']))
            kg.add((iris['sample_agent'], RDFS.label, Literal(sample['sampled_by'], datatype=XSD.string)))

        


        ## Observation 
    
        kg_obs.add( (iris['sampleobs'], RDF.type, _PREFIX["me_egad"]["EGAD-PFAS-Observation"]) )
        kg_obs.add( (iris['sampleobs'], RDFS['label'], Literal('EGAD PFAS observation for sample '+ str(sample['id']))) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['observedAtSamplePoint'], iris['samplepoint']) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['analyzedSample'], iris['sample']) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['hasFeatureOfInterest'], iris['samplefeature']) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["prov"]['wasAttributedTo'], iris['analysislab']) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['analyzedSample'], iris['sample']) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['ofSubstance'], iris['substance']) )
        kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['hasResult'], iris['result']) )

        if 'analysis_date' in sampleobs.keys():
            kg_obs.add( (iris['sampleobs'], _PREFIX["sosa"]['resultTime'], Literal(sampleobs['analysis_date'] , datatype = XSD.date)) )

        if 'date' in sample.keys() and sample['date'] != '': #attach sample date to observation
            kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['observedTime'], Literal(sample['date'], datatype = XSD.date)) )
            # TODO full sosa:phenomenonTime pattern with owl:Time object
                
        if 'analysis_method' in sampleobs.keys():
            kg_obs.add( (iris['sampleobs'], _PREFIX["coso"]['analysisMethod'], iris['analysis_method']) )

        if 'type' in result.keys():
            kg_obs.add( (iris['sampleobs'], _PREFIX["me_egad"]['resultType'], iris['result_type']) )
        

        
        ## contaminantMeasurement (result) and substance and quantity kind
        kg_result.add( (iris['result'], RDFS['label'], Literal('EGAD PFAS measurements for sample '+ str(sample['id']))) )        
        kg_result.add( (iris['result'], _PREFIX["qudt"]['quantityValue'], iris['quantity']) )
        ### aggregate measurements
        if (pfas_parameter_kind_dict[sampleobs['parameter']] == 'Cumulative'):
            #kg.add( (iris['substance'], RDF.type, _PREFIX['coso']['SubstanceCollection']))
            kg_result.add( (iris['substance'], _PREFIX["me_egad"]['dep_chemicalID'], Literal(sampleobs['chemical_number'] , datatype = XSD.string)) )
            kg_result.add( (iris['result'], RDF.type, _PREFIX["me_egad"]["EGAD-AggregatePFAS-Concentration"]) )
            kg_result.add((iris['result'], _PREFIX['qudt']['hasQuantityKind'], _PREFIX['coso']['AggregateContaminantConcentrationQuantityKind']))
        ### single
        else:
            kg_result.add( (iris['substance'], _PREFIX["coso"]['casNumber'], Literal(sampleobs['chemical_number']  , datatype = XSD.string)) ) #TODO update to reused relation, ignore ones that are custom DEP
            kg_result.add( (iris['result'], RDF.type, _PREFIX["me_egad"]["EGAD-SinglePFAS-Concentration"]) )
            kg_result.add((iris['result'], _PREFIX['qudt']['hasQuantityKind'], _PREFIX['coso']['SingleContaminantConcentrationQuantityKind']))


        ## Quantity Value

        if is_valid(result['pfas_concentration']):  #only materialize quantity value if there is a concentration 
            #if is_valid(pfas_concentration):
            kg_result.add((iris['quantity'], RDF.type, _PREFIX['coso']['DetectQuantityValue']))
            kg_result.add( (iris['quantity'], _PREFIX["qudt"]['numericValue'], Literal(result['pfas_concentration'] , datatype = XSD.decimal)) )
            ## Unit
            kg_result.add( (iris['quantity'], _PREFIX["qudt"]['hasUnit'], iris['unit']) )
            ### describe units that arent in qudt
            if result['pfas_concentration_units'] == "NG/G":
                kg_result.add( (iris['unit'], RDF.type, _PREFIX["qudt"]["Unit"]) )
                kg_result.add( (iris['unit'], RDFS['label'], Literal('NANOGRAMS PER GRAM')) )
            elif result['pfas_concentration_units'] == "MG/KG":
                kg_result.add( (iris['unit'], RDF.type, _PREFIX["qudt"]["Unit"]) )
                kg_result.add( (iris['unit'], RDFS['label'], Literal('MILLIGRAMS PER KILOGRAM')) )
            elif result['pfas_concentration_units'] == "%":
                kg_result.add( (iris['unit'], RDF.type, _PREFIX["qudt"]["Unit"]) )
                kg_result.add( ( iris['unit'], OWL.sameAs, _PREFIX['unit']['PERCENT']))
                kg_result.add( (iris['unit'], RDFS['label'], Literal('PERCENT')) )

        else: #handling of non-detects
            kg_result.add((iris['quantity'], RDF.type, _PREFIX['coso']['NonDetectQuantityValue']))
            kg_result.add((iris['quantity'], _PREFIX['qudt']['enumeratedValue'], _PREFIX['coso']['non-detect']))
            
        if 'validationLevel' in iris.keys():
            kg_result.add( (iris['result'], _PREFIX["me_egad"]['validationLevel'], iris['validationLevel']) )
                
        if 'validationQualifier' in iris.keys():
            kg_result.add( (iris['result'], _PREFIX["me_egad"]['validationQualifier'], iris['validationQualifier']) )

        if 'labQualifier' in iris.keys():
            kg_result.add( (iris['result'], _PREFIX["me_egad"]['labQualifier'], iris['labQualifier']) )

        if 'rl' in iris.keys():
            kg_result.add( (iris['result'], _PREFIX["me_egad"]['reportingLimit'], iris['rl']) )
            kg_result.add( (iris['rl'], _PREFIX["qudt"]['numericValue'], Literal(result['pfas_rl'] , datatype = XSD.decimal)) )
            kg_result.add((iris['rl'], _PREFIX['qudt']['hasUnit'], iris['unit'])) #assume the reporting limit is same unit as result

        if 'mdl' in iris.keys():
            kg_result.add( (iris['result'], _PREFIX["me_egad"]['methodDetectionLimit'], iris['mdl']) )
            kg_result.add( (iris['mdl'], _PREFIX["qudt"]['numericValue'], Literal(result['pfas_mdl'] , datatype = XSD.decimal)) ) 
            kg_result.add((iris['mdl'], _PREFIX['qudt']['hasUnit'], iris['unit'])) #assume the method detection limit is same unit as result
            

        
    return kg, kg_obs, kg_result


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
