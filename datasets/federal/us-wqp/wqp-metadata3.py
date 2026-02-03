import os
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS, DCTERMS
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
import urllib3
from urllib import parse
import json
import pandas as pd
import encodings
import urllib
import logging
import math
from pathlib import Path
import numpy as np
from pyutil import *
import sys
import re
import pprint

## declare variables
logname = "log"

metadata_files = [ 'Activity Media', 'Analytical Method', 'Characteristic', 'Sample Collection Method', "Organization", 'Monitoring Location Type', 'Taxon', 'Taxon Group', 'Quantitation Limit Type', 'Analytical Method', 'Result Measure Qualifier'] #'Activity Media Subdivision',


## data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir =  root_folder / "federal/us-wqp/metadata_3/"
output_dir = root_folder / "federal/us-wqp/controlledVocab"
triples_dir = root_folder / "federal/us-wqp/triples/"

##namespaces
prefixes = {}
prefixes['us_wqp'] = Namespace(f'http://w3id.org/sawgraph/v1/us-wqp#')
prefixes['us_wqp_data'] = Namespace(f'http://w3id.org/sawgraph/v1/us-wqp-data#')
prefixes['qudt'] = Namespace(f'http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://w3id.org/coso/v1/contaminoso#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['gcx']= Namespace(f'https://geoconnex.us/')
prefixes["prov"] = Namespace("http://www.w3.org/ns/prov#")
prefixes['dsstox'] = Namespace(f'http://w3id.org/DSSTox/v1/')

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running triplification for WQP metadata")

def main():
    # iterate over files in data directory
    for filename in metadata_files:
        data_df = pd.read_csv(data_dir / f"{filename}.csv", header=0, encoding='ISO-8859-1')
        logger = logging.getLogger('Data loaded to dataframe')
        if filename == 'Activity Media Subdivision':
            kg = triplify_media_subdivision(data_df, prefixes)
        elif filename == 'Activity Media':
            kg = triplify_media(data_df, prefixes)
        elif filename == 'Analytical Method':
            kg = triplify_analytical_method(data_df, prefixes)
        elif filename == 'Characteristic':
            with open(triples_dir / f'wqp_used_characteristics.txt', 'r') as f:
                l = eval(f.read())
                data_df = data_df[data_df['Unique Identifier'].isin(l)] #filter to only used characteristics
            kg = triplify_characteristic(data_df, prefixes)
        elif filename == 'Sample Collection Method':
            with open(triples_dir / f'wqp_used_samplemethods.txt', 'r') as f:
                l = eval(f.read())
                data_df = data_df[data_df['ID'].isin(l)] #filter to only used sample methods
            kg = triplify_sample_collection_method(data_df, prefixes)
        elif filename == 'Organization':
            with open(triples_dir / f'wqp_used_organizations.txt', 'r') as f:
                l = eval(f.read())
                data_df = data_df[data_df['ID'].isin(l)] #filter to only used organizations
            kg = triplify_organization(data_df, prefixes)
        elif filename == 'Monitoring Location Type':
            kg = triplify_monitoring_location_type(data_df, prefixes)
        elif filename == 'Taxon':
            with open(triples_dir / f'wqp_used_taxa.txt', 'r') as f:
                l = eval(f.read())
                data_df = data_df[data_df['Unique Identifier'].isin(l)] #filter to only used taxa
            kg = triplify_taxon(data_df, prefixes)
        elif filename == 'Taxon Group':
            kg= triplify_taxon_group(data_df, prefixes)
        elif filename == 'Quantitation Limit Type':
            kg = triplify_quantitation_limit_type(data_df, prefixes)
        elif filename == 'Result Measure Qualifier':
            kg = triplify_result_measure_qualifier(data_df, prefixes)

            
        data_df.iloc[0:0]
        filename = (filename.lower()).replace(" ", "_")
        kg_turtle_file = output_dir / f"{filename}.ttl"
        kg.serialize(kg_turtle_file,format='turtle')


def Initial_KG(prefixes: dict[str, str]):
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg

def camel_case(s):
  s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
  return ''.join([s[0].lower(), s[1:]])


## triplify the abox for media
def triplify_media(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## media record details
        media_name = row['Name'] # name
        media_description = row['Description'] # description
        
        ## construct media IRI
        media_iri = prefixes['us_wqp_data'][f"{'sampleMedia'}.{camel_case(media_name)}"]
                
        ## specify media instance and it's data properties
        kg.add((media_iri, RDF.type, _PREFIX["us_wqp"]["SampleMedia"]) )
        kg.add((media_iri, RDFS['label'], Literal(str(media_name))) )
        kg.add((media_iri, RDFS['comment'], Literal(media_description, datatype = XSD.string)) )

   
    return kg

## triplify the abox for media subdivisions
def triplify_media_subdivision(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## media record details
        media_name = row['Name'] # name
        media_description = row['Description'] # description
        media_name = ''.join(e for e in str(media_name) if e.isalnum())
        media_name = media_name.replace(' ', '')
        ## construct media IRI
        media_iri = _PREFIX["us_wqp_data"][f"{'sampleMedia'}.{camel_case(media_name)}"]
                
        ## specify media instance and it's data properties
        kg.add( (media_iri, RDF.type, _PREFIX["us_wqp"]["SampleMedia"]) )
        kg.add( (media_iri, RDFS['label'], Literal(str(media_name))) )
        kg.add( (media_iri, RDFS['comment'], Literal(media_description, datatype = XSD.string)) )

   
    return kg


## triplify the abox for analytical method
def triplify_analytical_method(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
       if ("retired" in row['ID']):
           #logging.info("Deprecated data")
           pass
    #    elif :
    #        ## method record details
    #        method_unique_id = row['Unique Identifier'] # unique ID
    #        method_id = row['ID'] # ID
    #        method_name = row['Name'] # name
    #        method_context = row['Context Code'] # context
    #        method_url = row['URL'] # URL
           
    #         # method IRI
    #        method_iri = _PREFIX["us_wqp_data"][f"{'d.wqp.analyticalMethod'}.{method_unique_id}"]
                    
    #         # specify method instance and it's data properties
    #        kg.add( (method_iri, RDF.type, _PREFIX["us_wqp"]["AnalyticalMethod"]) )
    #        kg.add( (method_iri, RDFS['label'], Literal(str(method_name))) )
    #        if not method_context:
    #            kg.add( (method_iri, _PREFIX["us_wqp"]['contextCode'], Literal(method_context, datatype = XSD.string)) )
    #        if not method_url:
    #            kg.add( (method_iri, _PREFIX["us_wqp"]['url'], Literal(method_url, datatype = XSD.anyURI)) )

    #manually add unreferenced method from Maine data
    method_iri = _PREFIX["us_wqp_data"][f"{'analyticalMethod'}.LM102"]
    kg.add( (method_iri, RDF.type, _PREFIX["us_wqp"]["AnalyticalMethod"]) )
    kg.add( (method_iri, RDFS['label'], Literal(str("PFAS SPE/LC/MS/MS SGS FL EPA537M"))) )
    kg.add( (method_iri, RDFS.comment, Literal("DESCRIPTION: Linear and branched perfluorinated alkyl acids (PFAS) by solid phase extraction (SPE) and liquid chromatography/tandem mass spectrometry (EPA Method 537 as modified by SGS Orlando [FL-SGSEL]); CITATION(S): USEPA | 537"))) 
   
    return kg

def get_dsstox(srs_id):
    #print(int(srs_id))
    url = f'https://cdxapps.epa.gov/oms-substance-registry-services/rest-api/substance/itn/{int(srs_id)}'
    resp = urllib3.request("GET", url, timeout=300.0)
    substance = resp.data
    substance = json.loads(substance)
    for synonym in substance[0]['synonyms']:
        if synonym['listName'] == 'OAR_Per- and polyfluoroalkyl Substances':
            print(synonym['synonymName'], ' - ',synonym['listName'])
    return substance

def get_inchi(dtxsid):
    url = f'https://hcd.rtpnc.epa.gov/api/search/download/properties'  #&properties=InChI,InChIKey,SMILES'
    id = dtxsid.replace("DTXSID","")
    header = {
              "ids": [{"id": id, "sim": 0.1}],
              "format": "string",
              "query": "string"}
    #print(header)
    resp=urllib3.request("POST", url, json=header, timeout=300.0)
    substance = resp.data
    substance = json.loads(substance)
    #print(substance[0]['inchiKey'])
    inchi = substance[0]['inchiKey']
    
    return substance

def from_inchi(inchi):
    url = f'https://hcd.rtpnc.epa.gov/api/resolver/classyfire?query={inchi}&idType=InChIKey&fuzzy=Not&page=0&size=1000'
    resp=urllib3.request("GET", url, timeout=300.0)
    substance = resp.data
    substance = json.loads(substance)
    #print(substance)
    
    return substance


## triplify the abox for pfas parameter
def triplify_characteristic(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        #only characteristics used in ME, IL pfas data
        #if row['Unique Identifier'] in [20865, 18826, 19467, 20877, 18574, 18191, 62354, 22803, 9364, 8083, 9235, 18456, 6681, 9368, 8091, 6680, 19739, 18078, 19482, 8096, 8097, 8095, 3112, 3113, 64556, 3117, 
        #                                16303, 19762, 19383, 20794, 18755, 8004, 20426, 3281, 3282, 18897, 18521, 3291, 3292, 19292, 64478, 16351, 18908, 64483, 19684, 19043, 18024, 19176, 9450, 62959, 19823, 19698, 9458, 18813,
        #                                19594, 17683, 8097, 64556, 19505, 16586, 17614, 18785, 8168, 8169, 8170, 8173, 20082, 21754, 3114]:
            if '***retired***' in row['Name']:
                #don't triplify retired substances
                pass

            else: #if row['Group Name'] in ['PFAS,Perfluorinated Alkyl Substance', 'PFOA, Perfluorooctanoic Acid','PFOS, Perfluorooctane Sulfonate', "Organics, PFAS"] or (row['Group Name'] == 'Stable Isotopes' and row['Name'] in ['13C3-PFBS', '13C2-4:2 FTS', '13C3-PFPeA', '13C3-PFBA', '13C3-HFPO-DA', '13C4-PFBA', '13C5-PFHxA', '13C5-PFPeA', '13C6-PFDA', '13C7-PFUnA', '13C8-PFOA', '13C9-PFNA', 'D3-N-MeFOSA', 'D5-N-EtFOSA', 'd7-NMe-FOSE', 'd9-NEt-FOSE', '13C2-PFTeDA', '13C2-PFDoA', '13C2-PFUnA', 'd5-EtFOSAA', 'd3-MeFOSAA',  '13C2-8:2 FTS', '13C2-PFDA', '13C8-PFOS', '13C8-PFOSA', '13C5-PFNA', '13C2-PFOA', '13C2-6:2 FTS', '13C3-PFHxS', '13C4-PFHpA', '13C2-PFHxA', 'CFC-12']):
                ## Get DTXSID and other attributes from SRS 
                if pd.notnull(row['SRS ID']):
                    substance = get_dsstox(row['SRS ID']) 
                    if len(substance)> 0 and substance[0]['dtxsid'] != None:
                        print(substance[0]["epaName"]," : ", substance[0]['dtxsid'])
                        #pprint.pp(substance[0]['synonyms'])
                      

                
                ## parameter record details
                parameter_unique_id = row['Unique Identifier'] # unique ID
                parameter_group = row['Group Name'] # group name
                parameter_name = row['Name'] # name
                #if '***retired***' in row['Name']:
                #    parameter_supercede = row['Name'].split('***retired***')[1]
                #    print(parameter_supercede)
                parameter_cas_no = str(row['CAS Number']) if pd.notnull(row['CAS Number']) else False # Chemical Abstracts Service (CAS) number
                parameter_srd_id = int(row['SRS ID']) if pd.notnull(row['SRS ID']) else False # Substance Registry Services (SRS) ID
                
                ## parameter IRI
                parameter_iri = _PREFIX["us_wqp_data"][f"{'characteristic'}.{parameter_unique_id}"]
                        
                ## specify parameter instance and it's data properties
                kg.add( (parameter_iri, RDF.type, _PREFIX["us_wqp"]["Characteristic"]) )
                kg.add( (parameter_iri, RDFS['label'], Literal(str(parameter_name))) )
                if parameter_group:
                    kg.add( (parameter_iri, _PREFIX["us_wqp"]['groupName'], Literal(parameter_group, datatype = XSD.string)) )
                if parameter_cas_no:
                    kg.add( (parameter_iri, _PREFIX["coso"]['casNumber'], Literal(parameter_cas_no, datatype = XSD.string)) )
                if parameter_srd_id:
                    kg.add( (parameter_iri, _PREFIX["us_wqp"]['srsID'], Literal(str(parameter_srd_id), datatype = XSD.string)) )
                    if len(substance)> 0 and substance[0]['dtxsid'] != None:
                        #check to make sure substance is neutral form
                        sub_inchi = get_inchi(substance[0]['dtxsid'])
                        inchi = sub_inchi[0]['inchiKey']
                        if inchi.endswith('-N'):
                            kg.add((parameter_iri, _PREFIX['dsstox']['sameAsDSSToxSubstance'], _PREFIX['dsstox'][f"{substance[0]['dtxsid']}"]))
                            kg.add((_PREFIX['dsstox'][f"{substance[0]['dtxsid']}"], RDF.type , _PREFIX['dsstox']['ChemicalEntity']))
                            kg.add((_PREFIX['dsstox'][f"{substance[0]['dtxsid']}"], DCTERMS.alternative , Literal(substance[0]['systematicName'])))
                        else:
                            #replace with Neutral version of InChIKey
                            inchi = inchi[:-1] + 'N'
                            #lookup dsstox again by inchikey
                            substance0 = from_inchi(inchi)
                            if 'content' in substance0.keys():
                                kg.add((parameter_iri, _PREFIX['dsstox']['sameAsDSSToxSubstance'], _PREFIX['dsstox'][f"{substance0['content'][0]['sid']}"]))
                    if len(substance)> 0 and substance[0]['synonyms']:
                        #check the synonyms for DTXSID entries
                        for syn in substance[0]['synonyms']:
                            if len(syn['alternateIds']) >0 :
                                for synonym in syn['alternateIds']:
                                    if synonym['alternateIdTypeName']== 'DTXSID' or synonym['alternateIdTypeId']=='108':
                                       #pprint.pp(synonym)
                                       substance = get_inchi(synonym['alternateId'])
                                       inchi = substance[0]['inchiKey']
                                       if inchi.endswith('-N'):
                                            #these link to the correct substances
                                            kg.add((parameter_iri, _PREFIX['dsstox']['sameAsDSSToxSubstance'], _PREFIX['dsstox'][f"{synonym['alternateId']}"]))
                                       else:
                                           #replace with Neutral version of InChIKey
                                           inchi = inchi[:-1] + 'N'
                                           #lookup dsstox again by inchikey
                                           substance1 = from_inchi(inchi)
                                           if 'content' in substance1.keys():
                                               kg.add((parameter_iri, _PREFIX['dsstox']['sameAsDSSToxSubstance'], _PREFIX['dsstox'][f"{substance1['content'][0]['sid']}"]))
                                       #kg.add((_PREFIX['dsstox'][f"{synonym['alternateId']}"], RDF.type , _PREFIX['dsstox']['ChemicalEntity']))
                                       #kg.add((_PREFIX['dsstox'][f"{synonym['alternateId']}"], RDFS.label , Literal(syn['synonymName'])))
                                       kg.add((parameter_iri, _PREFIX['dsstox']['hasInChiKey'], Literal(inchi, datatype=XSD.string)))


    return kg


## triplify the abox for sample collection method
def triplify_sample_collection_method(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        #if row['ID'] in ['NRSA_Seine_Dipnet', 'CS', '4040', 'Seine_Dipnet','XAD-2', 'Ponar-grab', 'NRSA_Seine_Dipnet', 'Seine_Dipnet', 'NPS_3P_WSAMPLE', 'NPS_3P_FDBLANK']:
            ## sample collection method record details
            method_unique_id = row['Unique Identifier'] # unique ID
            #if not method_unique_id:
            method_ID = row['ID'] # ID
            method_context = row['Context'] # context
            method_name = row['Name'] # name
            method_description = row['Description'] # description
            method_local_context = row['Local Context'] # local context
            method_unique_id_formatted = ''.join(e for e in str(method_unique_id) if e.isalnum())   
            ## method IRI
            method_iri = _PREFIX["us_wqp_data"][f"{'sampleCollectionMethod'}.{method_unique_id_formatted}"]
                            
            ## specify method instance and it's data properties
            kg.add( (method_iri, RDF.type, _PREFIX["us_wqp"]["SampleCollectionMethod"]) )
            kg.add( (method_iri, RDFS['label'], Literal(str(method_ID))) )
            kg.add( (method_iri, _PREFIX["us_wqp"]['wqp_samplingMethodContext'], Literal(method_context, datatype = XSD.string)) )
            kg.add( (method_iri, _PREFIX["us_wqp"]['wqp_samplingMethodName'], Literal(method_name, datatype = XSD.anyURI)) )

            kg.add( (method_iri, _PREFIX["us_wqp"]['wqp_samplingDescription'], Literal(method_description, datatype = XSD.string)) )
            kg.add( (method_iri, _PREFIX["us_wqp"]['wqp_samplingMethodLocalContext'], Literal(method_local_context, datatype = XSD.anyURI)) )
            kg.add( (method_iri, _PREFIX["us_wqp"]['wqp_samplingMethodID'], Literal(method_ID, datatype = XSD.string)) )
            #TODO none of these datatypeproperties exist in the schema (methods dont exist in current controlled vocab)

   
    return kg

## triplify the abox for organization
def triplify_organization(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        #if row['ID'] in ['USGS', 'MEDEP_WQX', 'OST_SHPD','EPA_GLNPO', 'AZDEQ_WPD', '11NPSWRD_WQX', 'GLEC', 'AZDEQ_GW', 'AZDEQ_SW']:
            ## organization details
            organization_unique_id = row['Unique Identifier'] # unique ID
            organization_ID = row['ID'] # ID
            organization_name = row['Name'] # name
            organization_description = row['Description'] # description
            organization_type = str(row['Type']).replace("/", "_").replace("*", "").replace(" ", "") #organization type

            organization_ID_formatted = organization_ID.replace(" ", '') #''.join(e for e in str(organization_ID) if e.isalnum())
            ## organization IRI
            organization_iri = _PREFIX["us_wqp_data"][f"{'organization'}.{organization_ID_formatted}"]
                        
            ## specify organization instance and it's data properties
            kg.add( (organization_iri, RDF.type, _PREFIX["prov"]["Organization"]) )
            if pd.notnull(row['Type']):
                kg.add( (organization_iri, RDF.type, _PREFIX["us_wqp"][f'{organization_type}_Organization']) )
                kg.add((_PREFIX["us_wqp"][f'{organization_type}_Organization'], RDFS.subClassOf, _PREFIX["us_wqp"]["Organization"]))
            kg.add( (organization_iri, RDFS['label'], Literal(str(organization_name))) )
            kg.add( (organization_iri, _PREFIX["us_wqp"]['organizationId'], Literal(organization_ID, datatype = XSD.string)) )
            if pd.notnull(row['Description']):
                kg.add( (organization_iri, _PREFIX["us_wqp"]['organizationDescription'], Literal(organization_description, datatype = XSD.anyURI)) )

       
    return kg

## triplify the abox for monitoring location type
def triplify_monitoring_location_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        ## location type details
        location_unique_id = row['Unique Identifier'] # unique ID
        location_name = row['Name'] # name
        location_description = row['Description'] # description

        location_name_formatted = ''.join(e for e in str(location_name) if e.isalnum())
            
        ## location IRI
        location_iri = _PREFIX["us_wqp_data"][f"{'featureType'}.{location_name_formatted}"]
                    
        ## specify location type instance and it's data properties   
        kg.add( (location_iri, RDF.type, _PREFIX["us_wqp"]["LocationType"]) )
        if location_name_formatted in ['Ocean', 'OtherSurfaceWater', 'Lake','WetlandUndifferentiated', 'RiverStream', 'LakeReservoirImpoundment', 'BEACHProgramSiteOcean', 'Stream',
                            'Reservoir', 'Tidalstream', 'Estuary', 'Coastal', 'Pavement', 'Hyporheiczonewell', 'CollectororRanneytypewell', 'BEACHProgramSiteChannelizedstream', 'BEACHProgramSiteEstuary',
                            'BEACHProgramSiteGreatLake', 'BEACHProgramSiteLake', 'BEACHProgramSiteLandrunoff', 'BEACHProgramSiteOcean', 'BEACHProgramSiteRiverStream', 'Estuary-Freshwater']:
            kg.add( (location_iri, RDF.type, _PREFIX["us_wqp"]["DefWQPSurfaceWaterFeatureType"]) )
        if location_name_formatted in ['Well', 'Spring', 'Testholenotcompletedasawell', 'Hyporheiczonewell', 'CollectororRanneytypewell', 'Ditch', 'Multiplewells', 'Aggregategroundwateruse', 'Borehole']:
            kg.add( (location_iri, RDF.type, _PREFIX["us_wqp"]["DefWQPGroundWaterFeatureType"]) )
        if location_name_formatted in ['Outfall', 'Combinedsewer', 'Septicsystem', 'BEACHProgramSiteStormsewer', 'BEACHProgramSiteWastesewer' ,'Combined Sewer', 'FacilityMunicipalSewagePOTW']:
            kg.add( (location_iri, RDF.type, _PREFIX["us_wqp"]["DefWQPWasteWaterFeatureType"]) )
        kg.add( (location_iri, RDFS.label, Literal(str(location_name))) )
        kg.add( (location_iri, RDFS.comment, Literal(location_description, datatype = XSD.string)) )

       
    return kg

#triplify taxon
def triplify_taxon(df, _PREFIX):
    kg = Initial_KG(_PREFIX)

    for idx, row in df.iterrows():
        #if row['Unique Identifier'] in [13166, 13170, 15717, 18441, 23065, 25364, 3757, 7587, 7588, 818, 14727, 17772, 3725, 13166, 18416, 10582, 13370, 13374,
         #                               1447, 17772, 10575, 13169, 13370, 40317, 817, 11868, 3757, 13166, 817, 1447, 10575, 13169, 13370, 40317, 11871, 6302
         #                               ]: # filter to only used taxon (ME, IL, KS, MA, NH)
        #if row['Domain Value Status'] == 'Accepted': #ignore deprecated taxon
            taxon_id = row['Unique Identifier']
            taxon_name = row['Name']
            taxon_rank = row['Rank']
            taxon_group = ''.join(e for e in str(row['Group Name']) if e.isalnum())

            taxon_iri = _PREFIX['us_wqp_data'][f"biologicalTaxon.{taxon_id}"]

            kg.add((taxon_iri, RDF.type, _PREFIX ['us_wqp']['Taxon']))
            kg.add((taxon_iri, RDFS.label, Literal(taxon_name, datatype=XSD.string)))
            kg.add((taxon_iri, _PREFIX['us_wqp']['rank'], Literal(taxon_rank, datatype=XSD.string)))
            if pd.notnull(row['Group Name']) and taxon_group != 'NotAssigned':
                kg.add((taxon_iri, RDF.type, _PREFIX['us_wqp'][f'TaxonGroup.{taxon_group}']))

    return kg

def triplify_taxon_group(df, _PREFIX):
    kg = Initial_KG(_PREFIX)

    for idx, row in df.iterrows():
        taxon_group_name = ''.join(e for e in str(row['Name']) if e.isalnum())
        taxon_group_iri = _PREFIX['us_wqp'][f'TaxonGroup.{taxon_group_name}']

        if len(taxon_group_name)> 1 and 'retired' not in taxon_group_name and taxon_group_name != 'NotAssigned':
            kg.add((taxon_group_iri, RDFS.subClassOf, _PREFIX['us_wqp']['Taxon']))

    return kg


def triplify_quantitation_limit_type(df, _PREFIX):
    kg = Initial_KG(_PREFIX)

    for idx, row in df.iterrows():
        ql_name = row['Name']
        ql_shortname = str(row['Name']).title().replace(" ", "").replace("%", "percent")
        ql_description = row['Description']

        ql_iri = _PREFIX['us_wqp'][ql_shortname]
        if ql_shortname in ['Sample-SpecificQuantitationLimit', 'InstrumentDetectionLevel', 'LaboratoryReportingLevel', 'CensoringLevel', 'MethodDetectionLevel', 'LowerQuantitationLimit','LowerReportingLimit'] :
            kg.add((ql_iri, RDFS.subClassOf, _PREFIX['coso']['ResultQualifier'])) #also make instance of pfas classes based on values
            kg.add((ql_iri, RDFS.label, Literal(ql_name, datatype=XSD.string)))
            kg.add((ql_iri, RDFS.comment, Literal(ql_description, datatype=XSD.string)))
        else:
            #print('unused quantitation:', ql_shortname)
            pass

    return kg

def triplify_result_measure_qualifier(data_df, prefixes):
    kg = Initial_KG(prefixes)

    for idx, row in data_df.iterrows():
        code = row['Code']
        code_uri = urllib.parse.quote(str(code), safe='')
        #id = row['Unique Identifier']
        desc = row['Description']
        iri = prefixes['us_wqp_data'][f'resultMeasureQualifier.{code_uri}']
        kg.add((iri, RDF.type, prefixes['us_wqp']['ResultMeasureQualifier']))
        kg.add((iri, RDFS.label, Literal(f"Result Measure Qualifier {code}", datatype=XSD.string)))
        kg.add((iri, RDFS.comment, Literal(desc, datatype=XSD.string)))

    return kg

if __name__ == "__main__":
    main()
