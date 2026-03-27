import os
from rdflib.namespace import OWL, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import Literal
import pandas as pd
import re
import json
import logging
import urllib
from datetime import datetime
from datetime import date
from pyutil import *
from shapely.geometry import Point
from pathlib import Path

## declare variables
logname = "log"
code_dir = Path(__file__).resolve().parent.parent
#state=input("state abbreviation?")

##data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/us-epa-ucmr5/"
# metadata_dir = root_folder / "federal/us-ucmr/metadata/"
output_dir = root_folder / "federal/us-ucmr/triples/"

##namespaces
prefixes = {}
prefixes['us_ucmr'] = Namespace(f'http://w3id.org/sawgraph/v1/us-ucmr#')
prefixes['us_ucmr_data'] = Namespace(f'http://w3id.org/sawgraph/v1/us-ucmr-data#')
prefixes['us_sdwis'] = Namespace('http://sawgraph.spatialai.org/v1/us-sdwis#')
prefixes['us_sdwis_data'] = Namespace('http://sawgraph.spatialai.org/v1/us-sdwis-data#')
prefixes['gcx']= Namespace(f'http://geoconnex.us/')
prefixes['qudt'] = Namespace(f'http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://w3id.org/coso/v1/contaminoso#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['gcx_wqp'] = Namespace(f'https://geoconnex.us/iow/wqp/')
prefixes["unit"] = Namespace("http://qudt.org/vocab/unit/")
prefixes['prov'] =  Namespace("http://www.w3.org/ns/prov#")
prefixes['sosa'] = Namespace("http://www.w3.org/ns/sosa/")
prefixes['spatial'] = Namespace("http://purl.org/spatialai/spatial/spatial-full#")

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info(f"Running triplification for UCMR")

def main():
    df = load_data()
    print(df.info(show_counts=True))
    global cv
    #cv = get_controlledvocabs()
    kg = triplify(df)
    kg.serialize(output_dir /f'UCMR5_observations.ttl', format='turtle')

def load_data():
    df = pd.read_csv(data_dir / f'UCMR5_All_MA_WY.txt', sep = '\t', encoding='mbcs', low_memory=False)
    
    df = df.dropna(axis='columns', how='all') #drop columns that are all NA
    #drop rows that aren't PFAS related
    df = df[df['Contaminant'].isin(['PFBS','PFHpA','PFHxS', 'PFNA','PFOS','PFOA', 'HFPO-DA','PFBA', 'PFHxA', 'PFDA', '11Cl-PF3OUdS', '8:2 FTS', '4:2 FTS', '6:2 FTS', 'ADONA', '(9ClPF3ONS', 'NFDHA', 'PFEESA', 'PFMPA', 'PFMBA', 'PFDoA', 'PFHpS', 'PFHpA', 'PFPeS', 'PFPeA', 'PFUnA', 'NEtFOSAA', 'NMeFOSAA', 'PFTA', 'PFTrDA'])]
    #df= df[df['Result_CharacteristicGroup'].isin(['PFAS,Perfluorinated Alkyl Substance', 'PFOA, Perfluorooctanoic Acid','PFOS, Perfluorooctane Sulfonate', "Organics, PFAS"]) | df['Result_Characteristic'].isin(['13C3-PFBS', '13C2-4:2 FTS', '13C3-PFPeA', '13C3-PFBA', '13C3-HFPO-DA', '13C4-PFBA', '13C5-PFHxA', '13C5-PFPeA', '13C6-PFDA', '13C7-PFUnA', '13C8-PFOA', '13C9-PFNA', 'D3-N-MeFOSA', 'D5-N-EtFOSA', 'd7-NMe-FOSE', 'd9-NEt-FOSE', '13C2-PFTeDA', '13C2-PFDoA', '13C2-PFUnA', 'd5-EtFOSAA', 'd3-MeFOSAA',  '13C2-8:2 FTS', '13C2-PFDA', '13C8-PFOS', '13C8-PFOSA', '13C5-PFNA', '13C2-PFOA', '13C2-6:2 FTS', '13C3-PFHxS', '13C4-PFHpA', '13C2-PFHxA', 'CFC-12'])]
    return df

def Initial_KG():
    # prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
        
    #for ns in kg.namespaces():
    #    print(ns)    
    return kg

def camel_case(s):
  return ''.join([s[0].lower(), s[1:]])


def get_attributes(row):
    'interpret attributes from the raw data and do any data formatting'
    #row.dropna()
    #sample -  mostly info from WQX Activity
    sample = {
        'id':str(row['SampleID']), # sample ID (stripped to only numbers, letters dashes and underscores)
        'activity_id': row['SampleEventCode'], 
        'media': row['SamplePointType'] , # sample type id (concatenated name)
        'type_bysource':row['FacilityWaterType'], # SW / GW
        'sample_date': datetime.strptime(str(row['CollectionDate']), "%m/%d/%Y"), #date of sample collection
        'sample_date_formatted': datetime.strptime(str(row['CollectionDate']), "%m/%d/%Y").strftime("%Y%m%d"), #integer only date
    }
    
    #Sample point - 
    samplepoint = {
        'id': str(row['SamplePointID']) , # PWS sub facility + sample point id for unique identifier
        'name': row['SamplePointName'], # sample point name
        'sub_facility': row['FacilityID'], # PWS sub facility id
        'sub_facility_name': row['FacilityName'],
        'pwsid': row['PWSID'], # PWS id
        'pwsname': row['PWSName']
    }
    ## no coordinates available for privacy 

    unit_lu = {
        'µg/L': 'MicroGM-PER-L',
              }
    # Observation
    # Result from UCMR 
    result = {
        'id':f"{''.join(row['SampleID'].split(' '))}.{''.join(row['Contaminant'].split(' '))}", #unique result id
        'substance_id': ''.join(row['Contaminant'].split(" ")),  #chemical identifier from CV
        'analytical_method':''.join(str(row['MethodID']).split(" ")),
        'unit_label': row['Units'],
        'unit': unit_lu[row['Units']] if pd.notnull(row['Units']) else '', #unit from CV
        'mql':float(row['MRL']),
    }
   
    if pd.isnull(row['AnalyticalResultValue']) and row['AnalyticalResultsSign'] == '<': 
        result['non-detect'] = True
    if pd.notnull(row['AnalyticalResultValue']):  #only valid floats are converted
        try :
            result['measure'] = float(row['AnalyticalResultValue'])
        except:
            print(row['AnalyticalResultValue'], " cannot be converted to float")

    return sample, samplepoint, result



def get_iris(sample, samplepoint, result):
    '''build iris for any named values (excludes classes and predicates)'''
    iris = {}
    #samples and features
    iris['sample'] = prefixes["us_ucmr_data"][f"d.ucmr.sample.{''.join(sample['id'].split())}"]
   
    iris['sdwis_subfeature'] = prefixes['us_sdwis_data'][f"d.PWS-SubFeature.{samplepoint['pwsid']}.{samplepoint['sub_facility']}"] #these don't match up to SDWIS ids
    iris['feature'] = prefixes['gcx'][f'ref/pws/{samplepoint['pwsid']}']

    iris['samplepoint'] = prefixes['us_ucmr_data'][f'd.ucmr.SamplePoint.{samplepoint['pwsid']}.{samplepoint['sub_facility']}.{samplepoint['id']}']
    iris['media'] = prefixes['us_ucmr_data'][f"samplePointType.{sample['media']}"] #infers sample type in dataset ontology
    iris['source'] = prefixes['us_ucmr_data'][f'sampleType.{sample['type_bysource']}']
    #observations and measurements
    iris['observation'] = prefixes['us_ucmr_data'][f"d.ucmr.observation.{'_'.join(result['id'].replace("/", "_").split())}"]
    iris['substance'] = prefixes['us_ucmr_data'][f"contaminant.{result['substance_id']}"]
    iris['analytical_method'] = prefixes['us_ucmr_data'][f"analyticalMethod.{result['analytical_method']}"] 
    iris['measurement'] = prefixes['us_ucmr_data'][f"d.ucmr.measurement.{result['id']}"]
    iris['quantityValue'] = prefixes['us_ucmr_data'][f"d.ucmr.quantityValue.{result['id']}"]
    iris['property'] = prefixes['coso']['SingleContaminantConcentrationQuantityKind'] #TODO double check these are single results
    iris['unit'] = prefixes['unit'][result['unit']] 
    iris['mql'] = prefixes['us_ucmr_data'][f'd.ucmr.mrl.{result['mql']}.{result['unit']}']
    
    return iris


def triplify(df):
    '''build the triples based on each row of the input dataset'''
    characteristic_set = set()


    kg = Initial_KG()
    for idx, row in df.iterrows():
        if idx % 10000 == 0:
            print(idx)
        # get attributes
        sample, samplepoint, result = get_attributes(row)
        # get iris
        iris = get_iris(sample, samplepoint, result)

        #triplify sample
        kg.add((iris['sample'], RDF.type, prefixes["us_ucmr"]["Sample"]) )
        if 'sample_date' in sample.keys():
            kg.add(( iris['sample'], RDFS['label'], Literal(f'UCMR PFAS Sample {str(sample['id'])} for {samplepoint['pwsname']} on {sample['sample_date_formatted']}', datatype=XSD.string ))) 
            
            #TODO add sample date
        kg.add(( iris['sample'], prefixes['coso']['fromSamplePoint'], iris['samplepoint']))
       
        sample_po = { #list predicates and objects for each attribute
            'id': (prefixes['us_ucmr']['sampleID'], Literal(sample['id'], datatype=XSD.string)),
            'media': (prefixes['coso']['sampleOfMaterialType'], iris['media']),
            'type_bysource':(prefixes['coso']['sampleOfMaterialType'], iris['source'])
        }
        #add any attributes that don't exist for all samples based on the above triple mappings
        for key in sample.keys():
            if key in sample_po.keys():
                kg.add(( iris['sample'], sample_po[key][0], sample_po[key][1]))

        #triplify sample point
        kg.add((iris['samplepoint'], RDF.type, prefixes['us_ucmr']['SamplePoint']))
        kg.add((iris['samplepoint'], RDFS.label, Literal(f"UCMR Sample Point {samplepoint['name']} {samplepoint['id']} for PWS {samplepoint['pwsid']} {samplepoint['pwsname']} at facility {samplepoint['sub_facility_name']} {samplepoint['sub_facility']}", datatype=XSD.string)))
        kg.add((iris['samplepoint'], prefixes['spatial']['connectedTo'], iris['sdwis_subfeature']))
        #TODO relate to pws sub-facility and pws entities
            
        #triplify observation
        kg.add((iris['observation'], RDF.type, prefixes['us_ucmr']['Observation']))
        kg.add((iris['observation'], RDFS.label, Literal(f"UCMR PFAS Sample {str(sample['id'])}  {result['substance_id']}  for {samplepoint['pwsname']} on {sample['sample_date_formatted']}", datatype=XSD.string)))
        kg.add((iris['observation'], prefixes['coso']['analyzedSample'], iris['sample']))
        kg.add((iris['observation'], prefixes['coso']['observedTime'], Literal(sample['sample_date_formatted'], datatype=XSD.dateTime)))
        kg.add(( iris['observation'], prefixes['coso']['hasFeatureOfInterest'], iris['feature']))
        kg.add((iris['observation'], prefixes['coso']['ofDatasetSubstance'], iris['substance']))

        characteristic_set.add(result['substance_id'])
        kg.add((iris['observation'], prefixes['coso']['hasResult'], iris['measurement']))
        kg.add((iris['observation'], prefixes['coso']['observedAtSamplePoint'], iris['samplepoint']))
        kg.add((iris['observation'], prefixes['coso']['observedProperty'], iris['property']))
        kg.add((iris['observation'],prefixes['coso']['analysisMethod'], iris['analytical_method']))

    

        #triplify measurement
        kg.add((iris['measurement'], RDF.type, prefixes['us_ucmr']['Single-PFAS-Concentration'])) # TODO are they all single measurements?
        kg.add((iris['measurement'], prefixes['qudt']['quantityValue'], iris['quantityValue']))
        ## TODO do we need a quantity value specific to every observation if the values are the same?
        
        if 'non-detect' in result.keys():
            kg.add((iris['quantityValue'], RDF.type, prefixes['coso']['NonDetectQuantityValue']))
            #kg.add((iris['quantityValue'], prefixes['qudt']['enumeratedValue'], prefixes['coso']['non-detect'])) #Literal('non-detect', datatype=XSD.string)))
        elif 'measure' in result.keys():
            kg.add((iris['quantityValue'], RDF.type, prefixes['coso']['DetectQuantityValue']))
            kg.add((iris['quantityValue'], prefixes['qudt']['numericValue'], Literal(result['measure'], datatype=XSD.float)))
            if 'unit' in result.keys():
                kg.add((iris['quantityValue'], prefixes['qudt']['hasUnit'], iris['unit']))
       
        if 'mql' in result.keys():
            kg.add((iris['measurement'], prefixes['coso']['hasResultQualifier'], iris['mql']))
            kg.add((iris['mql'], RDF.type, prefixes['us_ucmr']['MRL']))
            kg.add((iris['mql'], prefixes['qudt']['numericValue'], Literal(result['mql'], datatype=XSD.float)))
            kg.add((iris['mql'], prefixes['qudt']['hasUnit'], iris['unit']))
    
    #report which CV metadata values are used. 
    
    print('Characteristic', characteristic_set)
    #with open(output_dir / f'ucmr_used_contaminant.txt', 'r') as f:
    #    l = eval(f.read())
    #    for t in l:
    #        characteristic_set.add(t)
    # with open(output_dir / f'ucmr_used_contaminant.txt', 'w+') as f:
    #    f.writelines(str(list(characteristic_set)))

    return kg

#utility functions
def rem_time(d):
    s = date(d.year,d.month, d.day)
    return s

if __name__ == "__main__":
    main()
