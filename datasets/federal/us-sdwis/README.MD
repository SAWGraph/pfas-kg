#

## Overview of the raw dataset

* **Name of dataset:** Safe Drinking Water Information System SDWIS
* **Source Agency:** EPA
* **Data source location:**
  * [Drinking Water State | EPA Pfas analytic tools downloads](https://echo.epa.gov/trends/pfas-tools#data)
* **Additional data sources:**
  * [SDWIS Federal Reports Search](https://sdwis.epa.gov/ords/sfdw_pub/r/sfdw/sdwis_fed_reports_public/200)

* **Metadata description:**
  * [Envirofacts model](https://enviro.epa.gov/envirofacts/metadata/model/sdwis)
  * [SDWA download summary](https://echo.epa.gov/tools/data-downloads/sdwa-download-summary#sdwis)
  * [Community Water System Service Area Boundaries](https://www.epa.gov/ground-water-and-drinking-water/community-water-system-service-area-boundaries?tab=map) , [Water System Boundaries](https://epa.maps.arcgis.com/home/item.html?id=80c6912ef14f46e480f5afd807767b4b), [ORB_SAB_Model Github](https://github.com/USEPA/ORD_SAB_Model)
* **Format of data returned:** XLSX, CSV, (API available with json but has less tables), esri rest service (CWS boundaries)
* **General Comments:**

## Schema Diagram

[draft](https://lucid.app/lucidchart/16e658ef-6f61-4ce3-a770-0c410ecb194a/edit?viewport_loc=2887%2C55%2C2505%2C1076%2CO.sGt549hds0&invitationId=inv_ea094a2c-59da-4347-b175-700b91e5623d)

## Code

## Raw Data Attribute List and Ontology Mappings

### Drinking Water State Download from PFAS Analytic Tools

code: drinkingWater_state.py

| Attribute| Description | Lift to Graph | Ontology | Property |
|---------|-------------|------------|-------|--------|
| PWSID    | Uniquely identifies the water system within a specific state.Format: SSXXXXXXXXXX where: SS = the Federal Information Processing Standard (FIPS) Pub 5-2 State abbreviation in which the water system is located, or the region number of the EPA region responsible for an Indian reser vation, and XXXXXXXXXX = the water system identification code assigned by the State. | YES         | |us_sdwis:PublicWaterSystem us_sdwis:pwsId and in URI|
| PWS Name | The name of the water system. The name can be the formal, legal, or common name that is used most generally in referring to the water system. When multiple facilities exist for the water system at different physical locations, the name identifies the means by which the system, as a whole, is generally known.       | YES         | us_sdwis | us_sdwis:PublicWaterSystem us_sdwis:pwsName xsd:string |
| State    |       |   |||
| Region   |       |   |||
| County   |       |   |||
| Tribal Name        |       | ?  |||
| Population Served  | A system-generated count of the total retail population served by a water system.     | YES         | us_sdwis| us_sdwis:PublicWaterSystem us_sdwis:populationServed xsd:Int |
| Size     | Five main water system size categories, based on retail population served. Very small <=500, Small 501-3,300, Medium 3,301-10,000, Large 10,001-100,000, Very Large >100,000.   | YES         || us_sdwis:PublicWaterSystem us_sdwis:sizeCategory xsd:string|
| Cities Served      |       | Use from API instead  |||
| Zip Codes Served   |       | Use from API instead  |||
| Sample ID|       | Yes         || us_sdwis:PWS-SamplePoint iri and us_sdwis:PWS-SamplePoint us_sdwis:samplePointId xsd:string|
| Sample Point ID    |       | Yes         ||us_sdwis:SamplePoint us_sdwis:samplePointID xsd:string|
| Code     | Contaminant Code| Yes         ||us_sdwis:PWS-PFAS iri|
| Contaminant        |       | pull from code lookup |||
| Method   | Text field of method - needs cleaning         | TODO         |||
| Detected |       | ?         |||
| Concentration      |       | Yes         ||qudt:QuantityValue qudt:numericValue xsd:float|
| Units    |       | Yes         || qudt:QuantityValue qudt:unit qudt:Unit (mapped to) |
| Concentration (ng/l)         |       | ?        |||
| Reporting Level    |       | TODO        |||
| Health Advisory Level (ng/L) |       | ? |||
| Sample Date        |       | Yes         || us_sdwis:PWS-Observation coso:sampleTime xsd:Date|
| Compliance Period Begin Date |       |   |||
| Compliance Period End Date   |       |   |||
| Sample Type        |       | ?         |||
| MRL/MDL  | Categorical MRL or MDL    | TODO         |||
| Reporting| Automated/Manual|   |||
| Comment  |       |   |||
| Most Recent Sample | Yes/No|   |||
| Results  | Count of results?         |   |||
