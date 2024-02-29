## Overview of the raw dataset
* **Name of dataset:** WQP water-quality data
* **Source Agency:** [NATIONAL WATER QUALITY MONITORING COUNCIL](https://www.waterqualitydata.us/#advanced=true)
* **Data source location:** https://www.waterqualitydata.us/#advanced=true
* **Data Location on Github:** [Excel spreadsheet](https://github.com/shirlysteph/AlKnowsPFAS/tree/main/data/water-quality-data-portal/metadata)
* **Metadata description:** [Data user manual](https://www.waterqualitydata.us/portal_userguide/#location-parameters)
* **Other metadata (for PFAS):** [Water Quality eXchange (WQX) data elements (provided by EPA)](https://www.epa.gov/waterdata/storage-and-retrieval-and-water-quality-exchange-domain-services-and-downloads)
* **Format of data returned:** Excel (converted to cvs for easy data triplification)
* **Data update interval:** ?? 
* **Volume of raw data**: ??
* **General comments**: We only include a subset of attributes of the output json in AIKnowsPFAS (see mapping tables below).

## Code
* [Code Directory](../../code/water-quality-data-portal)
* [GDrive Output Directory](https://drive.google.com/drive/folders/18HynzQhZStMQj-CuM2U0NUtLUdBybWEx)

## Raw Data Attribute List and Mapping with Ontology Concepts
| Site/Station data attribute | Description | Lift to graph | Ontology property |
| --- | --- | --- |--- |
| OrganizationIdentifier | | Yes | Have to decide |
| MonitoringLocationIdentifier | | Yes | egad_siteNumber |
| MonitoringLocationName | | Yes | egad_siteName |
| MonitoringLocationTypeName | | es | |
| HUCEightDigitCode | | Yes | |
| LatitudeMeasure | Site latitude | Yes | geo:Geometry; sf:Point |
| LongitudeMeasure | Site longitude | Yes | geo:Geometry; sf:Point |
| CountyCode | | Yes | |
| ProviderName | Sample number[^1] | Yes | egad_samplePointNumber |


## Schema Diagram
![Schema Diagram](./wqp_sites_samples_schema_diagram.png)

**Legend description:**
- Yellow boxes - classes specific for _egad-maine-sample_ dataset.
- Pink boxes - classes in the generic PFAS schema
- Blue boxes - classes from external standard ontologies (e.g., SOSA, GeoSPARQL, OWL-Time, PROV)
- Purple boxes - classes specific for _egad-maine-sample_ dataset that are also controlled vocabularies
- Dark grey boes - the controlled vocabularies presented as examples from the EGAD lookup tables
- arrow with filled ends - object/data properties
- arrow with unfilled ends - subclass relation
- arrow with unfilled ends and a short line - instance (rdf:type) relation

## Sample Data

## Competency Questions


## Contributors
* [Shirly Stephen](https://github.com/shirlysteph)
