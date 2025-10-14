import os
from rdflib.namespace import OWL, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import Literal
import pandas as pd
import re
import json
import logging
from datetime import datetime
from datetime import date
from pyutil import *
from shapely.geometry import Point
from pathlib import Path

## declare variables
logname = "log"
code_dir = Path(__file__).resolve().parent.parent
state=input("state abbreviation?")
fips_lookup = {'AL':'01','AK':'02','AZ':'04',
'AR':'05','CA':'06','CO':'08','CT':'09','DE':'10','DC':'11',
'FL':'12','GA':'13','HI':'15','ID':'16','IL':'17','IN':'18',
'IA':'19','KS':'20','KY':'21','LA':'22','ME':'23','MD':'24',
'MA':'25','MI':'26','MN':'27','MS':'28','MO':'29','MT':'30',
'NE':'31','NV':'32','NH':'33','NJ':'34','NM':'35','NY':'36',
'NC':'37','ND':'38','OH':'39','OK':'40','OR':'41','PA':'42',
'PR':'72','RI':'44','SC':'45','SD':'46','TN':'47','TX':'48',
'UT':'49','VT':'50','VA':'51','VI':'78','WA':'53','WV':'54',
'WI':'55','WY':'56'} #FIPS for each state can be used for web retrival
statecode = f"US%3A{fips_lookup[state]}"

##data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir = root_folder / "data/water-quality-data-portal/"
metadata_dir = root_folder / "federal/us-wqp/metadata_3/"
output_dir = root_folder / "federal/us-wqp/triples/"

##namespaces
prefixes = {}
prefixes['us_wqp'] = Namespace(f'http://w3id.org/sawgraph/v1/us-wqp#')
prefixes['us_wqp_data'] = Namespace(f'http://w3id.org/sawgraph/v1/us-wqp-data#')
prefixes['geoconnex'] = Namespace(f'http://geoconnex.us/')
prefixes['qudt'] = Namespace(f'http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://w3id.org/coso/v1/contaminoso#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['gcx']= Namespace(f'http://geoconnex.us/')
prefixes["unit"] = Namespace("http://qudt.org/vocab/unit/")
prefixes['prov'] =  Namespace("http://www.w3.org/ns/prov#")
prefixes['sosa'] = Namespace("http://www.w3.org/ns/sosa/")

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info(f"Running triplification for WQP stations {state}")

def main():
    df = load_data()
    print(df.info(show_counts=True))
    global cv
    cv = get_controlledvocabs()
    kg = triplify(df)
    kg.serialize(output_dir /f'{state}_wqp_observations.ttl', format='turtle')

def load_data():
    df = pd.read_csv(data_dir / f'{state}-pfas-results.csv')
    df = df.dropna(axis='columns', how='all') #drop columns that are all NA
    return df

def Initial_KG():
    # prefixes: Dict[str, str] = _PREFIX
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg

def camel_case(s):
  s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
  return ''.join([s[0].lower(), s[1:]])


def get_controlledvocabs():
    '''Get unique identifiers and other attributes for controlled vocabularies that use a enumeration code'''
    metadata_files = ['Characteristic', 'Taxon', 'Analytical Method'] #'Activity Media', 'Sample Collection Method', 'Activity Media Subdivision', 'Analytical Method',  "Organization", 'Monitoring Location Type'
    cv = {}

    for filename in metadata_files:
        #print(filename)
        data_df = pd.read_csv(metadata_dir / f"{filename}.csv", header=0, encoding='ISO-8859-1', index_col='Name') #index by the name
        data_df = data_df.rename(columns={'Unique Identifier':'id'})
        data_df = data_df[~data_df.index.duplicated(keep='first')] # Keep first occurrence of name if they are not unique 
        metadata_dict = data_df.to_dict(orient='index')
        cv[filename] = metadata_dict
    #print(json.dumps(cv['Characteristic'], indent=4))
    return cv

def get_attributes(row):
    'interpret attributes from the raw data and do any data formatting'
    #row.dropna()
    #sample -  mostly info from WQX Activity
    sample = {
        'id':re.sub('[^A-Za-z0-9_\-]+', '', row['Activity_ActivityIdentifier'].replace(":", "-")), # sample ID (stripped to only numbers, letters dashes and underscores)
        'activity_id': row['Activity_ActivityIdentifier'], 
        'sample_date': datetime.strptime(row['Activity_StartDate'], '%Y-%m-%d'), #date
        'media': (''.join(e for e in str(row['Activity_Media']) if e.isalnum())).lower() , # sample media id (concatenated name)
        'project_id': ''.join(e for e in str(row['Project_Identifier']) if e.isalnum()), # annotation for sampling project (could be sampling collection)
        'org_id': row['Org_Identifier'].replace(' ', ''), #organization that does sampling
        'org_name': row['Org_FormalName'], #organization name
        'provider':row['ProviderName'],
        
    }
    if 'org_conducting' in row.keys() and pd.notnull(row['org_conduting']):
        sample['org_conducting'] = row['Activity_ConductingOrganization'], #team/ program conducting activity
    
    sample['sample_date_formatted'] = sample['sample_date'].strftime("%Y%m%d") #integer only date
    #if pd.notnull(row['Activity_ActivityIdentifierUserSupplied']):
    #    sample['sample_id_user'] = row['Activity_ActivityIdentifierUserSupplied'] #these are not currently helping alignment with state data, just another id for some federal data
    if pd.notnull(row['SampleCollectionMethod_Identifier']): 
        sample['sample_method'] = row['SampleCollectionMethod_Identifier'] # sampling method
    if pd.notnull(row['Project_Name']):
        sample['project_name'] = row['Project_Name'].replace('["',"").replace('"]', "")
    if pd.notnull(row['ResultBiological_Taxon']):
        sample['taxon'] = row['ResultBiological_Taxon']
        sample['taxonID'] = cv['Taxon'][sample['taxon']]['id'] #lookup id based on the taxon name
    if pd.notnull(row['Activity_Comment']):
        try:
            comments = json.loads(row['Activity_Comment'])
            for key in comments.keys():
                sample[key]=comments[key]
                #CommonName, CompositeClassification, FishTypeClassification, deviation, instructions, epa_sample_id
                #TODO check other states
        except:
            sample['comment'] = row['Activity_Comment']

    #if pd.notnull(row['SampleCollectionMethod_IdentifierContext']) and row['SampleCollectionMethod_IdentifierContext'] != 'nan':
    #    sample['collectionMethod']['source'] = row['SampleCollectionMethod_IdentifierContext']
    #if pd.notnull(row['SampleCollectionMethod_Description']):
    #    sample['collectionMethod']['description'] = row['SampleCollectionMethod_Description']
    #if pd.notnull(row['SampleCollectionMethod_EquipmentName']):
    #    sample['collectionMethod']['equipment'] = row['SampleCollectionMethod_EquipmentName']

    
    #Sample point -  from WQX location (also called site or station)
    samplepoint = {
        'id': row['Location_Identifier'], # station where sample was taken
        'type': row['Activity_TypeCode']
    }
    ## Get coordinates (prefer standardized if they exist)
    if pd.notnull(row['Location_Latitude']):
        if pd.notnull(row['Location_LatitudeStandardized']):
             samplepoint['wkt'] = Point(row['Location_LongitudeStandardized'], row['Location_LatitudeStandardized'])
        else: 
            samplepoint['wkt'] = Point(row['Location_Longitude'], row['Location_Latitude'])
            if row['Location_HorzCoordReferenceSystemDatum'] != "UNKWN":  #will assume these are all wgs84. 
                print(row['Location_HorzCoordReferenceSystemDatum'], " Location_HorzCoordReferenceSystemDatum")
    
    # Observation
    # Result from WQX Result
    result = {
        'id':row['Result_MeasureIdentifier'], #unique result id
        'type_annotation': row['Activity_TypeCode'], #Routine or QC sample 
        'substance_id': [v['id'] for k,v in cv['Characteristic'].items() if row['Result_Characteristic'] in k][0], #chemical identifier from CV (based on start of name because of deprecated names)
        
    }
    #replace retired characteristics with updated code
    #if  '***retired***' in row['Result_Characteristic']:
    #    characteristic = row['Result_Characteristic'].split("***retired***use ")[1] #take only the updated name
    #    print(characteristic)
    #    result['substance_id'] = [v['id'] for k,v in cv['Characteristic'].items() if characteristic in k][0]
    if pd.notnull(row['Result_ResultDetectionCondition']) and row['Result_ResultDetectionCondition'] == 'Not Detected': #TODO there are additional values in CV that should be considered here
        result['non-detect'] = True
    if 'ResultAnalyticalMethod_Identifier' in row.keys() and pd.notnull(row['ResultAnalyticalMethod_Identifier']):
        result['analytical_method'] = row['ResultAnalyticalMethod_Identifier']# cv['Analytical Method'][row['ResultAnalyticalMethod_Identifier']]['id'] #get id for analytical method
    if pd.notnull(row['LabInfo_Name']):
        result['lab'] = row['LabInfo_Name']
        result['lab_id'] = ''.join(e for e in str(row['LabInfo_Name']) if e.isalnum())
    if 'LabInfo_AnalysisStartDate' in row.keys() and pd.notnull(row['LabInfo_AnalysisStartDate']):
        result['analysis_date'] = pd.to_datetime(row['LabInfo_AnalysisStartDate']).date()
    if pd.notnull(row['Result_Measure']):
        result['measure'] = row['Result_Measure']
    unit_lu = {
        'ng/g': 'NanoGM-PER-GM', #this equivalent to MicroGM-PER-KiloGM
        'ng/L': 'NanoGM-PER-L',
        'ng/mL': 'NanoGM-PER-MilliL',
        '%': 'PERCENT',
        'pg/L': 'PicoGM-PER-L',
    }
    if pd.notnull(row['Result_MeasureUnit']):
        result['unit_label'] = row['Result_MeasureUnit']
        result['unit'] = unit_lu[row['Result_MeasureUnit']]     

    if pd.notnull(row['DetectionLimit_MeasureA']) and pd.notnull(row['DetectionLimit_MeasureUnitA']):
        result['dl_type_A'] = str(row['DetectionLimit_TypeA']).replace(" ", "")
        result['dl_measure_A'] = row['DetectionLimit_MeasureA']
        result['dl_unit_A'] = unit_lu[row['DetectionLimit_MeasureUnitA']]
    if 'DetectionLimit_TypeB' in row.keys() and pd.notnull(row['DetectionLimit_TypeB']):
        result['dl_type_B'] = str(row['DetectionLimit_TypeB']).title().replace(" ", "")
        result['dl_measure_B'] = row['DetectionLimit_MeasureB']
        result['dl_unit_B'] = unit_lu[row['DetectionLimit_MeasureUnitB']]

    return sample, samplepoint, result



def get_iris(sample, samplepoint, result):
    '''build iris for any named values (excludes classes and predicates)'''
    iris = {}
    #samples and features
    iris['sample'] = prefixes["us_wqp_data"][f"d.wqp.sample.{sample['id']}"]
    iris['wqp_site'] = prefixes['gcx'][f"wqp/{sample['provider']}/{sample['org_id']}/{samplepoint['id']}"]
    iris['SampleCollectionMethod'] = prefixes["us_wqp_data"][f"d.wqp.sampleCollectionMethod.{sample['sample_method']}"] if 'sample_method' in sample.keys() else ''
    iris['media'] = prefixes['us_wqp_data'][f"d.wqp.sampleMedia.{camel_case(sample['media'])}"] #could turn this into a subclass designation for tissue and water
    iris['organization'] = prefixes["us_wqp_data"][f"{'d.wqp.organizaton'}.{sample['org_id']}"]
    iris['project'] = prefixes['us_wqp_data'][f"d.wqp.project.{sample['project_id']}"]
    if 'taxon' in sample.keys():
        iris['taxon'] = prefixes['us_wqp_data'][f"d.wqp.biologicalTaxon.{sample['taxonID']}"]
    else:
        iris['taxon'] = ''

    #observations and measurements
    iris['observation'] = prefixes['us_wqp_data'][f"d.wqp.observation.{result['id']}"]
    iris['substance'] = prefixes['us_wqp_data'][f"d.wqp.substance.{result['substance_id']}"]
    iris['analytical_method'] = prefixes['us_wqp_data'][f"d.wqp.analyticalMethod.{result['analytical_method']}"] if 'analytical_method' in result.keys() else ''
    iris['measurement'] = prefixes['us_wqp_data'][f"d.wqp.measurement.{result['id']}"]
    iris['quantityValue'] = prefixes['us_wqp_data'][f"d.wqp.quantityValue.{result['id']}"] #TODO is this necessary to tie with observation id? Especially for non-detects
    iris['property'] = prefixes['coso']['SingleContaminantConcentrationQuantity']
    if 'lab_id' in result.keys():
        iris['lab'] = prefixes['us_wqp_data'][f"d.wqp.lab.{result['lab_id']}"]
    if 'unit' in result.keys():
        if result['unit'] == 'NanoGM-PER-GM':
            iris['unit'] = prefixes['coso'][result['unit']]
        else:
            iris['unit'] = prefixes['unit'][result['unit']] 
    if 'dl_unit_A' in result.keys():
        if result['dl_unit_A'] == 'NanoGM-PER-GM':
            iris['unit_A'] = prefixes['coso'][result['dl_unit_A']]
        else:
            iris['unit_A'] = prefixes['unit'][result['dl_unit_A']]
        iris['dl_A'] = prefixes['us_wqp_data'][f"d.wqp.{result['dl_type_A']}.{result['id']}"]
    if 'dl_unit_B' in result.keys():
        if result['dl_unit_B']  == 'NanoGM-PER-GM':
            iris['unit_B'] = prefixes['coso'][result['dl_unit_B']]
        else:
            iris['unit_B'] = prefixes['unit'][result['dl_unit_B']]
        iris['dl_B'] = prefixes['us_wqp_data'][f"d.wqp.{result['dl_type_B']}.{result['id']}"]
    
    return iris


def triplify(df):
    '''build the triples based on each row of the input dataset'''
    taxon_set = set()
    characteristic_set = set()
    smethod_set = set()
    organization_set = set()

    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        sample, samplepoint, result = get_attributes(row)
        # get iris
        iris = get_iris(sample, samplepoint, result)

        #triplify sample
        kg.add((iris['sample'], RDF.type, prefixes["us_wqp"]["WQP-Sample"]) )
        kg.add(( iris['sample'], RDFS['label'], Literal('WQP PFAS Sample '+ str(sample['activity_id']) +' collected at site '+ str(samplepoint['id']) + ' on ' + sample['sample_date'].strftime("%Y-%m-%d"))) )
        kg.add(( iris['sample'], prefixes['coso']['fromSamplePoint'], iris['wqp_site']))
        sample_po = { #list predicates and objects for each attribute
            'id': (prefixes['us_wqp']['sampleID'], Literal(sample['activity_id'], datatype=XSD.string)),
            'sample_method': (prefixes['us_wqp']['sampleCollectionMethod'], iris['SampleCollectionMethod']),
            'media': (prefixes['coso']['sampleOfMaterialType'], iris['media']),
            'taxon': (prefixes['coso']['sampleOfMaterialType'], iris['taxon']),
            'project_id': (prefixes['us_wqp']['hasProjectId'], iris['project'])
            
        }
        #add any attributes that don't exist for all samples based on the above triple mappings
        for key in sample.keys():
            if key in sample_po.keys():
                kg.add(( iris['sample'], sample_po[key][0], sample_po[key][1]))

        #project info
        if 'project_name' in sample.keys():
            kg.add(( iris['project'], RDFS.label, Literal(sample['project_name'], datatype=XSD.string)))

        #metadata subset detection
        if 'taxonID' in sample.keys():
            taxon_set.add(sample['taxonID'])
        if 'sample_method' in sample.keys():
            smethod_set.add(sample['sample_method'])
        organization_set.add(sample['org_id'])
            

        #triplify observation
        kg.add((iris['observation'], RDF.type, prefixes['us_wqp']['WQP-PFAS-Observation']))
        kg.add((iris['observation'], prefixes['coso']['analyzedSample'], iris['sample']))
        kg.add((iris['observation'], prefixes['coso']['ofSubstance'], iris['substance']))
        characteristic_set.add(result['substance_id'])
        kg.add((iris['observation'], prefixes['coso']['hasResult'], iris['measurement']))
        kg.add((iris['observation'], prefixes['coso']['observedProperty'], iris['property']))
        observation_po = { #list of optional triples for each observation (based on data)
            'analytical_method': (prefixes['coso']['usedAnalysisMethod'], iris['analytical_method']),
            'analysis_date': (prefixes['sosa']['resultTime'], Literal(str(result['analysis_date']), datatype=XSD.date)) if 'analysis_date' in result.keys() else '',
            'lab_id':(prefixes['prov']['wasAttributedTo'], iris['lab']) if 'lab' in iris.keys() else '',
        }

        for key in result.keys():
            if key in observation_po.keys():
                kg.add(( iris['observation'], observation_po[key][0], observation_po[key][1]))
        if 'lab' in result.keys():
            kg.add((iris['lab'], RDFS.label, Literal(result['lab'], datatype=XSD.string)))

        #triplify measurement
        kg.add((iris['measurement'], RDF.type, prefixes['us_wqp']['WQP-Single-PFAS-Concentration'])) # TODO are they all single measurements?
        kg.add((iris['measurement'], prefixes['qudt']['quantityValue'], iris['quantityValue']))
        ## TODO do we need a quantity value specific to every observation if the values are the same?
        if 'measure' in result.keys():
            kg.add((iris['quantityValue'], RDF.type, prefixes['coso']['DetectQuantityValue']))
            kg.add((iris['quantityValue'], prefixes['qudt']['numericValue'], Literal(result['measure'], datatype=XSD.float)))
        if 'unit' in result.keys():
            kg.add((iris['quantityValue'], prefixes['qudt']['unit'], iris['unit']))
        if 'non-detect' in result.keys():
            kg.add((iris['quantityValue'], RDF.type, prefixes['coso']['NonDetectQuantityValue']))
            kg.add((iris['quantityValue'], prefixes['qudt']['enumeratedValue'], Literal('non-detect', datatype=XSD.string)))
        if 'dl_type_A' in result.keys():
            kg.add((iris['measurement'], prefixes['coso']['hasResultQualifier'], iris['dl_A']))
            kg.add((iris['dl_A'], RDF.type, prefixes['us_wqp'][result['dl_type_A']]))
            kg.add((iris['dl_A'], prefixes['qudt']['quantityValue'], Literal(result['dl_measure_A'], datatype=XSD.float)))
            kg.add((iris['dl_A'], prefixes['qudt']['unit'], iris['unit_A']))
        if 'dl_type_B' in result.keys():
            kg.add((iris['measurement'], prefixes['coso']['hasResultQualifier'], iris['dl_B']))
            kg.add((iris['dl_B'], RDF.type, prefixes['us_wqp'][result['dl_type_B']]))
            kg.add((iris['dl_B'], prefixes['qudt']['quantityValue'], Literal(result['dl_measure_B'], datatype=XSD.float)))
            kg.add((iris['dl_B'], prefixes['qudt']['unit'], iris['unit_B']))
    
    #report which CV metadata values are used. 
    print('Taxon:', taxon_set)
    print('Characteristic', characteristic_set)
    print('Sample Method:', smethod_set)
    print('Organization', organization_set)
    return kg

#utility functions
def rem_time(d):
    s = date(d.year,d.month, d.day)
    return s

if __name__ == "__main__":
    main()
