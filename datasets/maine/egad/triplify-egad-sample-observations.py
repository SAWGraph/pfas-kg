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


## data dictioaries -- for controlled vocabularies
with open(metadata_dir / 'analysis_lab.csv', mode='r') as infile:
    reader = csv.reader(infile)
    lab_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    material_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_collection_method.csv', mode='r') as infile:
    reader = csv.reader(infile)
    collection_method_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_location.csv', mode='r') as infile:
    reader = csv.reader(infile)
    location_type_dict = {rows[1]:rows[0] for rows in reader}

with open(metadata_dir / 'sample_point_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    point_type_dict = {rows[1]:rows[0] for rows in reader}
    
with open(metadata_dir / 'site_type.csv', mode='r') as infile:
    reader = csv.reader(infile)
    site_type_dict = {rows[1]:rows[0] for rows in reader}

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
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for EGAD sites and samples")

def main():
    egad_samples_df = pd.read_excel(data_dir / 'Statewide EGAD PFAS File March 2024.xlsx', sheet_name="PFAS Sample Data", header=0)
    logger = logging.getLogger('Data loaded to dataframe.')


    kg = triplify_egad_pfas_sample_data(egad_samples_df, _PREFIX)
    kg_turtle_file = "egad_samples_output.ttl".format(output_dir)
    kg.serialize(kg_turtle_file,format='turtle')
    logger = logging.getLogger('Finished triplifying EGAD PFAS sample data.')
    
def Initial_KG(_PREFIX):
    prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


## triplify the abox
def triplify_egad_pfas_sample_data(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    rowcount = df.shape[0]
    for idx, row in df.iterrows():
        if idx % 10000 == 0:
            print(idx, 'of', rowcount)
        ## sample point record details
        samplepoint_number = row['SAMPLE_POINT_NUMBER'] # sample point number
        samplepoint_webname = row['SAMPLE_POINT_WEB_NAME'] # sample point web name
        samplepoint_type = row['SAMPLE_POINT_TYPE'] # sample point type
        
        ## construct sample point IRI
        samplepoint_iri = _PREFIX["me_egad_data"][f"{'samplePoint'}.{samplepoint_number}"]
                
        ## specify sample point instance and it's data properties
        kg.add( (samplepoint_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SamplePoint"]) )
        kg.add( (samplepoint_iri, RDFS['label'], Literal('EGAD sample point '+ str(samplepoint_number))) )
        kg.add( (samplepoint_iri, _PREFIX["me_egad"]['samplePointNumber'], Literal(samplepoint_number, datatype = XSD.integer)) )
        kg.add( (samplepoint_iri, _PREFIX["me_egad"]['samplePointWebName'], Literal(samplepoint_webname, datatype = XSD.string)) )

        ## construct sample feature IRI
        samplefeature_iri = _PREFIX["me_egad_data"][f"{'sampledFeature'}.{samplepoint_number}"]
                
        ## specify sample feature instance and it's data properties
        kg.add( (samplefeature_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SampledFeature"]) )
        kg.add( (samplefeature_iri, RDFS['label'], Literal('EGAD sampled feature associated with sample point '+ str(samplepoint_number))) )

        samplepoint_type = point_type_dict[samplepoint_type]
        samplepoint_type = ''.join(e for e in samplepoint_type if e.isalnum())
        samplepoint_type_iri = _PREFIX["me_egad"][f"{'featureType'}.{samplepoint_type}"]
        
        kg.add( (samplefeature_iri, _PREFIX["me_egad"]['sampledFeatureType'], samplepoint_type_iri) )
        kg.add( (samplepoint_iri, _PREFIX["coso"]['pointFromFeature'], samplefeature_iri) )

        ## sample record and construct its IRI
        sample_id = row['SAMPLE_ID'] # sample point ID
        analysis_id = row['ANALYSIS_LAB_SAMPLE_ID'] # ID assigned by an analysis lab
        sampleobs_analysislab = row['ANALYSIS_LAB'] # sample analysis lab
        sampleobs_type = row['SAMPLE_TYPE_UPDATE'] # sample type
        sampleobs_parameter = row['PARAMETER_SHORTENED'] # pfas parameter
        
        
        sample_id_formatted = ''.join(e for e in sample_id if e.isalnum())
        sampleobs_parameter_formatted = ''.join(e for e in sampleobs_parameter if e.isalnum())

        analysis_id_formatted = ''.join(e for e in analysis_id if e.isalnum())

        sample_date = pd.to_datetime(row['SAMPLE_DATE']) #datetime.strptime(str(), '%m/%d/%Y') 
        sample_date = rem_time(sample_date)
        sample_date_formatted = ''.join(e for e in str(sample_date) if e.isalnum())
        samplematerial_iri = _PREFIX["me_egad"][f"{'sampleMaterialType'}.{material_type_dict[sampleobs_type]}"] 
        
        #sample_iri = _PREFIX["aik-pfas"][f"{'egad.sample'}.{samplepoint_number}.{analysis_id_formatted}.{sample_date_formatted}"]
        #sample_iri = _PREFIX["aik-pfas"][f"{'egad.sample'}.{sample_id_formatted}"]
        sample_iri = _PREFIX["me_egad_data"][f"{'sample'}.{analysis_id_formatted}.{lab_dict[sampleobs_analysislab]}.{sample_date_formatted}"]
        kg.add( (sample_iri, RDF.type, _PREFIX["me_egad"]["EGAD-Sample"]) )
        kg.add( (sample_iri, RDFS['label'], Literal('EGAD sample '+ str(sample_id))) )
        kg.add( (sample_iri, _PREFIX["me_egad"]['sampleID'], Literal(sample_id, datatype = XSD.string)) )
        if(str(row['SAMPLE_LOCATION']) != ''):
            samplelocation_iri = _PREFIX["me_egad"][f"{'sampleLocation'}.{location_type_dict[row['SAMPLE_LOCATION']]}"] 
            kg.add( (sample_iri, _PREFIX["me_egad"]['sampleCollectionLocation'], samplelocation_iri) )

        if(str(sampleobs_type) != ''):
            kg.add( (sample_iri, _PREFIX["coso"]['ofSampleMaterialType'], samplematerial_iri) )

        if(str(row['SAMPLE_COLLECTION_METHOD']) != ''):
            kg.add( (sample_iri, _PREFIX["me_egad"]['sampleCollectionMethod'], _PREFIX["me_egad"][f"{'samplingMethod'}.{collection_method_dict[row['SAMPLE_COLLECTION_METHOD']]}"]) )

        sample_treatment_status = row['TREATMENT_STATUS'] # sample treatment status
        if(str(sample_treatment_status) != '') and (str(sample_treatment_status) != 'nan'):
            sampletreatment_iri = _PREFIX["me_egad"][f"{'treatmentStatus'}.{treatment_status_dict[sample_treatment_status]}"] 
            kg.add( (sample_iri, _PREFIX["me_egad"]['sampleTreatmentStatus'], sampletreatment_iri) )

        #kg.add( (samplepoint_iri, _PREFIX["sosa"]['hasSample'], sample_iri) )
        #kg.add( (sample_iri, _PREFIX["sosa"]['isSampleOf'], samplepoint_iri) ) # materialize inverse relation


        ## construct sample observation IRI     
        chemical_number = row['CAS_NO']
        analysis_lab = row['ANALYSIS_LAB']
        ## sample results record details
        pfas_concentration = row['CONCENTRATION'] # concentration
        pfas_concentration_units = row['PARAMETER_UNITS'] # concentration-unit

        if is_valid(pfas_concentration):

            sampleobs_iri = _PREFIX["me_egad_data"][f"{'observation'}.{analysis_id_formatted}.{lab_dict[sampleobs_analysislab]}.{sample_date_formatted}.{chemical_number}"]
            #kg.add( (sampleobs_iri, _PREFIX["coso"]['analyzedBy'], Literal(analysis_lab , datatype = XSD.string)) )

            kg.add( (sampleobs_iri, RDF.type, _PREFIX["me_egad"]["EGAD-PFAS-Observation"]) )
            kg.add( (sampleobs_iri, RDFS['label'], Literal('EGAD PFAS observation for sample '+ str(sample_id))) )
            kg.add( (sampleobs_iri, _PREFIX["coso"]['observedAtSamplePoint'], samplepoint_iri) )
            kg.add( (sampleobs_iri, _PREFIX["coso"]['analyzedSample'], sample_iri) )

            kg.add( (sampleobs_iri, _PREFIX["coso"]['hasFeatureOfInterest'], samplefeature_iri) )
            

            analysis_date = row['ANALYSIS_DATE'] # analysis date
            if pd.isnull(analysis_date):
                #print(analysis_date)
                #print("Invalid analysis date:", analysis_date)
                pass
            else:
                analysis_date = pd.to_datetime(row['ANALYSIS_DATE']) #datetime.strptime(str(), '%m/%d/%Y')
                #analysis_date = rem_time(analysis_date)
                #analysis_date_formatted = ''.join(e for e in str(analysis_date) if e.isalnum())
                kg.add( (sampleobs_iri, _PREFIX["coso"]['analysisDate'], Literal(analysis_date , datatype = XSD.date)) )
                    
            sample_date = row['SAMPLE_DATE'] # sampled date
            if pd.isnull(sample_date):
                print("Invalid sample date")
            else:
                sample_date = pd.to_datetime(row['SAMPLE_DATE']) #datetime.strptime(str(row['SAMPLE_DATE']), '%m/%d/%Y')
                #sample_date = rem_time(sample_date)
                #sample_date_formatted = ''.join(e for e in str(sample_date) if e.isalnum())
                kg.add( (sampleobs_iri, _PREFIX["coso"]['sampledTime'], Literal(sample_date, datatype = XSD.date)) )
                    
            analysis_method = row['TEST_METHOD'] # analysis method
            if(str(analysis_method) != ''):
                analysis_method_iri = _PREFIX["me_egad"][f"{'testMethod'}.{test_method_dict[analysis_method]}"]
                kg.add( (sampleobs_iri, _PREFIX["coso"]['analysisMethod'], analysis_method_iri) )

            result_type = row['RESULT_TYPE'] # result type
            if(str(result_type) != ''):
                result_type_iri = _PREFIX["me_egad"][f"{'resultType'}.{result_type_dict[result_type]}"]
                kg.add( (sampleobs_iri, _PREFIX["me_egad"]['resultType'], result_type_iri) )

                    
            ## construct analysis lab, sample material and measured PFAS parameter IRI
            analysislab_iri = _PREFIX["me_egad_data"][f"{'organization.lab'}.{lab_dict[sampleobs_analysislab]}"]
            kg.add( (sampleobs_iri, _PREFIX["coso"]['analyzedBy'], analysislab_iri) )
            #kg.add( (sampleobs_iri, _PREFIX["sosa"]['hasFeatureOfInterest'], sample_iri) )
            kg.add( (sampleobs_iri, _PREFIX["me_egad"]['analyzedSample'], sample_iri) )
            kg.add( (sample_iri, _PREFIX["coso"]['fromSamplePoint'], samplepoint_iri) )
            #kg.add( (sample_iri, _PREFIX["coso"]['fromSamplePoint'], samplepoint_iri) )
            sampleparameter_iri = _PREFIX["me_egad"][f"{'parameter'}.{pfas_parameter_dict[sampleobs_parameter]}"]
            kg.add( (sampleobs_iri, _PREFIX["coso"]['ofSubstance'], sampleparameter_iri) )
            
            if (pfas_parameter_kind_dict[sampleobs_parameter] == 'Cumulative'):
                kg.add( (sampleparameter_iri, RDF.type, _PREFIX['coso']['SubstanceCollection']))
                kg.add( (sampleparameter_iri, _PREFIX["me_egad_data"]['dep_chemicalID'], Literal(chemical_number , datatype = XSD.string)) )
            else:
                kg.add( (sampleparameter_iri, _PREFIX["coso"]['casNumber'], Literal(chemical_number , datatype = XSD.string)) )


            pfas_rl = row['REPORTING_LIMIT'] # reporting limit
            pfas_mdl = row['MDL'] # method detection limit
            validation_level = str(row['VALIDATION_LEVEL']) # validation level
            validation_qualifier = row['VALIDATION QUALIFIER'] # validation qualifier
            lab_qualifier = row['LAB_QUALIFIER'] # lab qualifier
           
            units = row['PARAMETER_UNITS'] # units of measurement

           
            result_iri = _PREFIX["me_egad_data"][f"{'result'}.{analysis_id_formatted}.{lab_dict[sampleobs_analysislab]}.{sample_date_formatted}.{chemical_number}"]
            #kg.add( (result_iri, RDF.type, _PREFIX["me_egad"]["EGAD-PFAS-Concentration"]) )

            if (pfas_parameter_kind_dict[sampleobs_parameter] == 'Cumulative'):
                kg.add( (sampleparameter_iri, _PREFIX["me_egad_data"]['dep_chemicalID'], Literal(chemical_number , datatype = XSD.string)) )
                kg.add( (result_iri, RDF.type, _PREFIX["me_egad"]["EGAD-AggregatePFAS-Concentration"]) )
            else:
                kg.add( (sampleparameter_iri, _PREFIX["coso"]['casNumber'], Literal(chemical_number , datatype = XSD.string)) )
                kg.add( (result_iri, RDF.type, _PREFIX["me_egad"]["EGAD-SinglePFAS-Concentration"]) )


            kg.add( (result_iri, RDFS['label'], Literal('EGAD PFAS measurements for sample '+ str(sample_id))) )
            kg.add( (sampleobs_iri, _PREFIX["sosa"]['hasResult'], result_iri) )

            quantity_iri = _PREFIX["me_egad_data"][f"{'quantityValue'}.{analysis_id_formatted}.{lab_dict[sampleobs_analysislab]}.{sample_date_formatted}.{chemical_number}"]
            kg.add( (result_iri, _PREFIX["qudt"]['quantityValue'], quantity_iri) )

            #if is_valid(pfas_concentration):
            kg.add( (quantity_iri, _PREFIX["qudt"]['numericValue'], Literal(pfas_concentration , datatype = XSD.decimal)) )
            if pfas_concentration_units == "NG/G":
                unit_iri = _PREFIX["me_egad"]['unit.NG-G']
                kg.add( (unit_iri, RDF.type, _PREFIX["unit"]["Unit"]) )
                kg.add( (unit_iri, RDFS['label'], Literal('NANOGRAMS PER GRAM')) )
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], unit_iri) )
            elif pfas_concentration_units == "MG/KG":
                unit_iri = _PREFIX["me_egad"]['unit.MG-KG']
                kg.add( (unit_iri, RDF.type, _PREFIX["unit"]["Unit"]) )
                kg.add( (unit_iri, RDFS['label'], Literal('MILLIGRAMS PER KILOGRAM')) )
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], unit_iri) )
            elif pfas_concentration_units == "%":
                unit_iri = _PREFIX["me_egad"]['unit.percent']
                kg.add( (unit_iri, RDF.type, _PREFIX["unit"]["Unit"]) )
                kg.add( (unit_iri, RDFS['label'], Literal('PERCENT')) )
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], unit_iri) )
            elif pfas_concentration_units == "NG/L":
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], _PREFIX["unit"]['NanoGM-PER-L']) )
            elif pfas_concentration_units == "NG/ML":
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], _PREFIX["unit"]['NanoGM-PER-MicroL']) )
            elif pfas_concentration_units == "MG/L":
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], _PREFIX["unit"]['MilliGM-PER-L']) )
            elif pfas_concentration_units == "UG/KG":
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], _PREFIX["unit"]['MicroGM-PER-KiloGM']) )
            elif pfas_concentration_units == "UG/L":
                kg.add( (quantity_iri, _PREFIX["qudt"]['unit'], _PREFIX["unit"]['MicroGM-PER-L']) )
            #if is_valid(pfas_mdl):
            #    kg.add( (result_iri, _PREFIX["me_egad"]['egad_pfas_mdl'], Literal(str(pfas_mdl) + ' ' +units, datatype = cdt)) )
            #if is_valid(pfas_ql):
            #   kg.add( (result_iri, _PREFIX["me_egad"]['egad_pfas_ql'], Literal(str(pfas_ql) + ' ' +units, datatype = cdt)) )
            if (str(validation_level) != '') and (str(validation_level) != 'nan'): 
                #try:
                if (validation_level.startswith("Tier II: EPA-NE REGION 1 GUIDELINES")):
                    validation_string = 'TierII-EPA-NE-REGION-1-GUIDELINES'
                    validationLevel_iri = _PREFIX["me_egad"][f"{'validationLevel'}.{validation_string}"] 
                else:
                    validationLevel_iri = _PREFIX["me_egad"][f"{'validationLevel'}.{validation_level_dict[validation_level]}"] 
                kg.add( (result_iri, _PREFIX["me_egad"]['validationLevel'], validationLevel_iri) )
    ##            except KeyError as e:
    ##                print(validation_level)
    ##                print('Validation level - Key error')
                

            if (str(validation_qualifier) != '') and (str(validation_qualifier) != 'nan'):
                validation_qualifier = str(validation_qualifier).replace("/", "-").replace("*","star")
                validationQualifier_iri = _PREFIX["me_egad"][f"{'concentrationQualifier'}.{validation_qualifier}"] 
                kg.add( (result_iri, _PREFIX["me_egad"]['validationQualifier'], validationQualifier_iri) )

            if (str(lab_qualifier) != '') and (str(lab_qualifier) != 'nan'):
                lab_qualifier = str(lab_qualifier).replace("/", "-")
                lab_qualifier = _PREFIX["me_egad"][f"{'concentrationQualifier'}.{lab_qualifier}"] 
                kg.add( (result_iri, _PREFIX["me_egad"]['labQualifier'], lab_qualifier) )

            if (str(pfas_rl) != '') and (str(pfas_rl) != 'nan'):
                rl_iri = _PREFIX["me_egad_data"][f"{'rl'}.{analysis_id_formatted}.{lab_dict[sampleobs_analysislab]}.{sample_date_formatted}.{chemical_number}"]
                kg.add( (rl_iri, RDF.type, _PREFIX["me_egad"]["EGAD-ReportingLimit"]) )
                kg.add( (result_iri, _PREFIX["me_egad"]['reportingLimit'], rl_iri) )
                kg.add( (rl_iri, _PREFIX["qudt"]['numericValue'], Literal(pfas_rl , datatype = XSD.decimal)) )

            if (str(pfas_mdl) != '') and (str(pfas_mdl) != 'nan'):
                mdl_iri = _PREFIX["me_egad_data"][f"{'mdl'}.{analysis_id_formatted}.{lab_dict[sampleobs_analysislab]}.{sample_date_formatted}.{chemical_number}"]
                kg.add( (mdl_iri, RDF.type, _PREFIX["me_egad"]["EGAD-MethodDetectionLimit"]) )
                kg.add( (result_iri, _PREFIX["me_egad"]['methodDetectionLimit'], mdl_iri) )
                kg.add( (rl_iri, _PREFIX["qudt"]['numericValue'], Literal(pfas_mdl , datatype = XSD.decimal)) )
            

        
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
