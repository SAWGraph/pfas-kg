## Overview of the raw dataset
* **Name of dataset:** EGAD (Environmental and Geographic Analysis Database) PFAS sites and samples 
* **Source Agency:** [Maine Department of Environmental Protection (DEP)](https://www.maine.gov/dep/maps-data/egad/)
* **Data source location:** ??
* **Metadata description:** [Data user manual](https://www.maine.gov/dep/maps-data/egad/documents/Maine%20DEP%20EGAD%20EDD%20v6.0%20User%20Manual_2022%20(Final).pdf)
* **Other metadata (for PFAS):** [EGAD lookup tables](https://www.maine.gov/dep/maps-data/egad/documents/EGAD_Lookup_Tables.xlsx)
* **Format of data returned:** ??
* **Data update interval:** ?? 
* **General comments**: We only include a subset of attributes of the original data in SAWGraph (see mapping tables below).

## Schema Diagram
[**Link to schema diagram on lucid chart**](https://lucid.app/lucidchart/a9330f5f-14bb-430b-b734-dd37626284e7/edit?viewport_loc=-805%2C-12%2C2587%2C1150%2C0_0&invitationId=inv_9a3f9eda-0d3a-4243-a695-481a17d294b8)

## Code (TO UPDATE)
* [Code Directory](../../code/egad-maine-samples)
* [GDrive Output Directory](https://drive.google.com/drive/folders/18HynzQhZStMQj-CuM2U0NUtLUdBybWEx)

## Raw Data Attribute List and Mapping with Ontology Concepts (TO UPDATE)
| Sheet 2 attribute | Description | Lift to graph | Ontology property | Ontology Class |
| --- | --- | --- |--- | --- |
| MCD | Administrative region ||  | |
| SITE_NUMBER | Site number | Yes | egad_siteNumber | Literal |
| SITE_NAME | Site name | Yes | egad_siteName | Literal | 
| SITE_UTM_X | | No | |
| SITE_UTM_Y | | No | |
| SITE_LATITUDE | Site latitude | Yes | geo:Geometry |
| SITE_LONGITUDE | Site longitude | Yes | geo:Geometry|
| PWSID_NO | | Yes | |
| SAMPLE_POINT_NUMBER | Sample number[^1] | Yes | egad_samplePointNumber |
| SAMPLE_POINT_WEB_NAME | Sample name | Yes | egad_samplePointWebName |
| SAMPLE_POINT_TYPE | Type of sampled point (see List 1) | Yes | rdf:type |
| SP_X | | No | |
| SP_Y | | No | |
| SAMPLE_POINT_LATITUDE | Sampled latitude | Yes | geo:Geometry; sf:Point |
| SAMPLE_POINT_LONGITUDE | Sampled longitude | Yes | geo:Geometry; sf:Point |

[^1]: SAMPLE_POINT_NAME is a DEP defined ID used in uploading and storing data in EGAD. It is important that this ID be exact and consistent. It is a location identifier, not a sample ID. In contrast, SAMPLE_ID is an all-purpose identifier field that can vary from sample to sample and event to event. Samplers, labs, consultants, etc. are free to use the SAMPLE_ID field as they choose, or as defined on a chain of custody form. For many DEP projects/sample events, the Sample Point Name and the Sample ID will be the same, but it does not have to be. 
 

| Sheet 3 attribute | Description | Lift to graph | Ontology property | Ontology Class
| --- | --- | --- | --- |
| SAMPLE_POINT_NUMBER | Sample number[^1] | Yes | *samplePointNumber | Literal |
| SAMPLE_POINT_WEB_NAME | Sample name | Yes | *samplePointWebName | Literal xsd:string |
| SAMPLE_POINT_TYPE | Type of sampled point (see List 1) | Yes | me_egad:sampledFeatureType, me_egad:samplePointType | me_egad:EGAD-SamplePointType |
| ANALYSIS_LAB | | Yes | prov:wasAttributedTo | prov:Organization
| SAMPLE_ID | Sample ID | No | egad_sampleID | 
| ANALYSIS_LAB_SAMPLE_ID | | No | |
| QC_TYPE | | No | |
| RESULT_TYPE | | No | |
| SAMPLE_TYPE | Type of sample (see List 2) | No | |
| SAMPLE_TYPE_UPDATE | Updated type of sample | Yes | egad_sampleID |
| SAMPLED_BY | Person who sampled | No | |
| SAMPLE_DATE | Date of sampling | Yes | prov:atTime |
| CAS_NO | | No | |
| PARAMETER_NAME | Type of chemical detected/sampled (see List 3) | Yes | sosa:observedProperty |   
| PARAMETER_SHORTENED | Abbreviated chemical name | Yes | sosa:observedProperty |
| CONCENTRATION | Concentrationo of chemical | Yes | egad_pfas_concentration |
| PARAMETER_UNITS | Units of measured chemical | Yes | appended with measurment |
| LAB_QUALIFIER | | No | |
| VALIDATION QUALIFIER | | No | |
| VALIDATION_LEVEL | | No | |
| QUANTITATION_LIMIT | | Yes | egad_pfas_ql |
| TEST_METHOD | | No | |
| PARAMETER_QUALIFIER | | No | |
| PARAMETER_FILTERED | | No | |
| SAMPLE_COLLECTION_METHOD | Sampling method (see table 4) | Yes | sosa:madeBySampler |
| SAMPLE_LOCATION | | Yes | sampleLocation |
| TREATMENT_STATUS | | ?? | |
| MDL | Method Detection Limit | Yes | egad_pfas_mdl |
| ANALYSIS_DATE | | Yes | sosa:ResultTime |
| PREP_METHOD | | ?? | |
| PREP_METHOD2 | | ?? | |
| DILUTION_FACTOR | | ?? | |
| WEIGHT_BASIS | | ?? | |
| BATCH_ID | | ?? | |
| SAMPLE_DELIVERY_GROUP | | ?? | |
| DEPTH | | ?? | |
| DEPTH_UNITS | | ?? | |
| SAMPLE_COMMENT | | ?? | |
| PARAMETER_SEQ | | ?? | |

**Notes on the data:**
- Site and Sample Point have 1:n relationship
- Sample Point and Sample have 1:n relationship
- Sample and PFAS_Parameter have 1:n relationship (therefore sample and result have 1:n relationship)
- Sample time and analysis time are very different (which is why we disinguish them using two temporal properties)

## Schema Diagram
![Schema Diagram](./egad_sites_samples-schema-diagram.png)

**Legend description:** (TO UPDATE)
- Yellow boxes - classes specific for _egad-maine-sample_ dataset.
- Pink boxes - classes in the generic PFAS schema
- Blue boxes - classes from external standard ontologies (e.g., SOSA, GeoSPARQL, OWL-Time, PROV)
- Purple boxes - classes specific for _egad-maine-sample_ dataset that are also controlled vocabularies
- Dark grey boes - the controlled vocabularies presented as examples from the EGAD lookup tables
- arrow with filled ends - object/data properties
- arrow with unfilled ends - subclass relation
- arrow with unfilled ends and a short line - instance (rdf:type) relation

## Controlled Vocabularies 
See [EGAD lookup tables](https://www.maine.gov/dep/maps-data/egad/documents/EGAD_Lookup_Tables.xlsx) for controlled vocabularies for the following terms/concepts
- Analysis Labs
- PFAS Parameters
- Sample Collection Methods
- Sample Locations
- Sample Point Types
- Site Types
- Sample Material Types

**Notes(changes that I made to the Lookup Tables so they were comprehensive with the PFAS data):**
1. Added the following two records to List 1:
	 - CONTEST ANALYTICAL LABORATORY- EAST LONGMEADOW, MA (Value: CON)
	 - COLUMBIA ANALYTICAL- KELSO, WA (Value: COL)
2. Changed spelling of 'Fillet' in List 4 to 'Filet'
3. Added DRINKING WATER in List 4 (VALUE: DW)

## Sample Data

## Competency Questions 

## Contributors
* [Shirly Stephen](https://github.com/shirlysteph)
* [Katrina Schweikert](https://github.com/)
