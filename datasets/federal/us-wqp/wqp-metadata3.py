import os
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import Namespace
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
import pandas as pd
import encodings
import logging
import math
from pathlib import Path
import numpy as np
from pyutil import *
import sys
import re

## declare variables
logname = "log"

metadata_files = [ 'Activity Media', 'Analytical Method', 'Characteristic', 'Sample Collection Method', "Organization", 'Monitoring Location Type', 'Taxon', 'Taxon Group', 'Quantitation Limit Type', 'Analytical Method'] #'Activity Media Subdivision',


## data path
root_folder = Path(__file__).resolve().parent.parent.parent
data_dir =  root_folder / "federal/us-wqp/metadata_3/"
output_dir = root_folder / "federal/us-wqp/controlledVocab"

##namespaces
prefixes = {}
prefixes['us_wqp'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-wqp#')
prefixes['us_wqp_data'] = Namespace(f'http://sawgraph.spatialai.org/v1/us-wqp-data#')
prefixes['qudt'] = Namespace(f'http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace(f'http://sawgraph.spatialai.org/v1/contaminoso#')
prefixes['pfas'] = Namespace(f'http://sawgraph.spatialai.org/v1/pfas#')
prefixes['geo'] = Namespace(f'http://www.opengis.net/ont/geosparql#')
prefixes['gcx']= Namespace(f'http://geoconnex.us/')
prefixes["prov"] = Namespace("http://www.w3.org/ns/prov#")

## initiate log file
logging.basicConfig(filename=logname,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
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
            kg = triplify_characteristic(data_df, prefixes)
        elif filename == 'Sample Collection Method':
            kg = triplify_sample_collection_method(data_df, prefixes)
        elif filename == 'Organization':
            kg = triplify_organization(data_df, prefixes)
        elif filename == 'Monitoring Location Type':
            kg = triplify_monitoring_location_type(data_df, prefixes)
        elif filename == 'Taxon':
            kg = triplify_taxon(data_df, prefixes)
        elif filename == 'Taxon Group':
            kg= triplify_taxon_group(data_df, prefixes)
        elif filename == 'Quantitation Limit Type':
            kg = triplify_quantitation_limit_type(data_df, prefixes)
            
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
        media_iri = prefixes['us_wqp_data'][f"{'d.wqp.sampleMedia'}.{camel_case(media_name)}"]
                
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
        media_iri = _PREFIX["us_wqp_data"][f"{'wqp.sampleMedia'}.{camel_case(media_name)}"]
                
        ## specify media instance and it's data properties
        kg.add( (media_iri, RDF.type, _PREFIX["us_wqp"]["SampleMedia"]) )
        kg.add( (media_iri, RDFS['label'], Literal(str(media_name))) )
        kg.add( (media_iri, RDFS['comment'], Literal(media_description, datatype = XSD.string)) )

   
    return kg


## triplify the abox for analytical method
def triplify_analytical_method(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    #for idx, row in df.iterrows():
    #    if ("retired" in row['ID']):
    #        logging.info("Deprecated data")
    #    else:
    #        ## method record details
    #        method_unique_id = row['Unique Identifier'] # unique ID
    #        method_id = row['ID'] # ID
    #        method_name = row['Name'] # name
    #        method_context = row['Context Code'] # context
    #        method_url = row['URL'] # URL
    #        
            ## method IRI
    #        method_iri = _PREFIX["us_wqp_data"][f"{'d.wqp.analyticalMethod'}.{method_unique_id}"]
                    
            ## specify method instance and it's data properties
    #        kg.add( (method_iri, RDF.type, _PREFIX["us_wqp"]["AnalyticalMethod"]) )
    #        kg.add( (method_iri, RDFS['label'], Literal(str(method_name))) )
    #        if not method_context:
    #            kg.add( (method_iri, _PREFIX["us_wqp"]['contextCode'], Literal(method_context, datatype = XSD.string)) )
    #        if not method_url:
    #            kg.add( (method_iri, _PREFIX["us_wqp"]['url'], Literal(method_url, datatype = XSD.anyURI)) )

    #manually add unreferenced method from Maine data
    method_iri = _PREFIX["us_wqp_data"][f"{'d.wqp.analyticalMethod'}.LM102"]
    kg.add( (method_iri, RDF.type, _PREFIX["us_wqp"]["AnalyticalMethod"]) )
    kg.add( (method_iri, RDFS['label'], Literal(str("PFAS SPE/LC/MS/MS SGS FL EPA537M"))) )
    kg.add( (method_iri, RDFS.comment, Literal("DESCRIPTION: Linear and branched perfluorinated alkyl acids (PFAS) by solid phase extraction (SPE) and liquid chromatography/tandem mass spectrometry (EPA Method 537 as modified by SGS Orlando [FL-SGSEL]); CITATION(S): USEPA | 537"))) 
   
    return kg



## triplify the abox for pfas parameter
def triplify_characteristic(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        if row['Unique Identifier'] in [20865, 18826, 19467, 20877, 18574, 18191, 62354, 22803, 9364, 8083, 9235, 18456, 6681, 9368, 8091, 6680, 19739, 18078, 19482, 8096, 8097, 8095, 3112, 3113, 64556, 3117, 16303, 19762, 19383, 20794, 18755, 8004, 20426, 3281, 3282, 18897, 18521, 3291, 3292, 19292, 64478, 16351, 18908, 64483, 19684, 19043, 18024, 19176, 9450, 62959, 19823, 19698, 9458, 18813]:
            if '***retired***' in row['Name']:
                #don't triplify retired substances
                pass
            
            else:
                #if row['Group Name'] in ['PFAS,Perfluorinated Alkyl Substance', 'PFOA, Perfluorooctanoic Acid','PFOS, Perfluorooctane Sulfonate', 'Stable Isotopes', "Organics, PFAS"]:
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
                parameter_iri = _PREFIX["us_wqp_data"][f"{'wqp.substance'}.{parameter_unique_id}"]
                        
                ## specify parameter instance and it's data properties
                kg.add( (parameter_iri, RDF.type, _PREFIX["us_wqp"]["Characteristic"]) )
                kg.add( (parameter_iri, RDFS['label'], Literal(str(parameter_name))) )
                if parameter_group:
                    kg.add( (parameter_iri, _PREFIX["us_wqp"]['groupName'], Literal(parameter_group, datatype = XSD.string)) )
                if parameter_cas_no:
                    kg.add( (parameter_iri, _PREFIX["coso"]['casNumber'], Literal(parameter_cas_no, datatype = XSD.string)) )
                if parameter_srd_id:
                    kg.add( (parameter_iri, _PREFIX["us_wqp"]['srsID'], Literal(parameter_srd_id, datatype = XSD.int)) )


    return kg


## triplify the abox for sample collection method
def triplify_sample_collection_method(df, _PREFIX):
    kg = Initial_KG(_PREFIX)
    
    ## materialize each record
    for idx, row in df.iterrows():
        if row['ID'] in ['NRSA_Seine_Dipnet', 'CS', '4040', 'Seine_Dipnet']:
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
            method_iri = _PREFIX["us_wqp_data"][f"{'wqp.sampleCollectionMethod'}.{method_unique_id_formatted}"]
                            
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
        if row['ID'] in ['USGS', 'MEDEP_WQX', 'OST_SHPD']:
            ## organization details
            organization_unique_id = row['Unique Identifier'] # unique ID
            organization_ID = row['ID'] # ID
            organization_name = row['Name'] # name
            organization_description = row['Description'] # description
            organization_type = str(row['Type']).replace("/", "_").replace("*", "").replace(" ", "") #organization type

            organization_ID_formatted = organization_ID.replace(" ", '') #''.join(e for e in str(organization_ID) if e.isalnum())
            ## organization IRI
            organization_iri = _PREFIX["us_wqp_data"][f"{'d.wqp.organizaton'}.{organization_ID_formatted}"]
                        
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
        location_iri = _PREFIX["us_wqp_data"][f"{'feature'}.{location_name_formatted}"]
                    
        ## specify location type instance and it's data properties   #this
        kg.add( (location_iri, RDF.type, _PREFIX["us_wqp"]["WQP-Location_Type"]) )
        kg.add( (location_iri, RDFS.label, Literal(str(location_name))) )
        kg.add( (location_iri, _PREFIX["us_wqp"]['featureDescription'], Literal(location_description, datatype = XSD.string)) )

       
    return kg

#triplify taxon
def triplify_taxon(df, _PREFIX):
    kg = Initial_KG(_PREFIX)

    for idx, row in df.iterrows():
        if row['Unique Identifier'] in [13166, 13170, 15717, 18441, 23065, 25364, 3757, 7587, 7588, 818]: # filter to only used taxon (ME)
        #if row['Domain Value Status'] == 'Accepted': #ignore deprecated taxon
            taxon_id = row['Unique Identifier']
            taxon_name = row['Name']
            taxon_rank = row['Rank']
            taxon_group = ''.join(e for e in str(row['Group Name']) if e.isalnum())

            taxon_iri = _PREFIX['us_wqp_data'][f"d.wqp.biologicalTaxon.{taxon_id}"]

            kg.add((taxon_iri, RDF.type, _PREFIX ['us_wqp']['Taxon']))
            kg.add((taxon_iri, RDFS.label, Literal(taxon_name, datatype=XSD.string)))
            kg.add((taxon_iri, _PREFIX['us_wqp']['rank'], Literal(taxon_rank, datatype=XSD.string)))
            if pd.notnull(row['Group Name']) and taxon_group != 'NotAssigned':
                kg.add((taxon_iri, RDF.type, _PREFIX['us_wqp'][f'taxonGroup.{taxon_group}']))

    return kg

def triplify_taxon_group(df, _PREFIX):
    kg = Initial_KG(_PREFIX)

    for idx, row in df.iterrows():
        taxon_group_name = ''.join(e for e in str(row['Name']) if e.isalnum())
        taxon_group_iri = _PREFIX['us_wqp'][f'taxonGroup.{taxon_group_name}']

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

        kg.add((ql_iri, RDFS.subClassOf, _PREFIX['coso']['ResultQualifier'])) #also make instance of pfas classes based on values
        kg.add((ql_iri, RDFS.label, Literal(ql_name, datatype=XSD.string)))
        kg.add((ql_iri, RDFS.comment, Literal(ql_description, datatype=XSD.string)))

    return kg

if __name__ == "__main__":
    main()
