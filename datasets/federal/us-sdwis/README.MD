## Overview of the raw dataset
* **Name of dataset:** Safe Drinking Water Information System SDWIS
* **Source Agency:** EPA
* **Data source location:** 
  * [Drinking Water State | EPA Pfas analytic tools downloads ]() 
  * [SDWA Dataset | ECHO data downloads](https://echo.epa.gov/tools/data-downloads)
* **Additional data sources:** 
  * [SDWIS Federal Reports Search](https://sdwis.epa.gov/ords/sfdw_pub/r/sfdw/sdwis_fed_reports_public/200) 
  * [CWS Service Area Boundaries](https://services.arcgis.com/cJ9YHowT8TU7DUyn/arcgis/rest/services/Water_System_Boundaries/FeatureServer)
* **Metadata description:** 
  * [Envirofacts model](https://enviro.epa.gov/envirofacts/metadata/model/sdwis)
  * [SDWA download summary](https://echo.epa.gov/tools/data-downloads/sdwa-download-summary#sdwis)
* **Format of data returned:** XLSX, CSV,  (API available with json but has less tables)
* **General Comments:**

## Schema Diagram
[draft](https://lucid.app/lucidchart/16e658ef-6f61-4ce3-a770-0c410ecb194a/edit?viewport_loc=2887%2C55%2C2505%2C1076%2CO.sGt549hds0&invitationId=inv_ea094a2c-59da-4347-b175-700b91e5623d)

## Code

## Raw Data Attribute List and Ontology Mappings
Drinking Water State Download from PFAS Analytic Tools

| Attribute                    | Description                                                                                                                                                                                                                                                                                                                                                                   | Lift to Graph         | Ontology | Property |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------|----------|----------| 
| PWSID                        | Uniquely identifies the water system within a specific state.Format: SSXXXXXXXXXX where: SS = the Federal Information Processing Standard (FIPS) Pub 5-2 State abbreviation in which the water system is located, or the region number of the EPA region responsible for an Indian reser vation, and XXXXXXXXXX = the water system identification code assigned by the State. | YES                   |          |          |
| PWS Name                     | The name of the water system. The name can be the formal, legal, or common name that is used most generally in referring to the water system. When multiple facilities exist for the water system at different physical locations, the name identifies the means by which the system, as a whole, is generally known.                                                         | YES                   |          |          |
| State                        |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| Region                       |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| County                       |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| Tribal Name                  |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| Population Served            | A system-generated count of the total retail population served by a water system.                                                                                                                                                                                                                                                                                             | YES                   |          |          |
| Size                         | Five main water system size categories, based on retail population served. Very small <=500, Small 501-3,300, Medium 3,301-10,000, Large 10,001-100,000, Very Large >100,000.                                                                                                                                                                                                 | YES                   |          |          |
| Cities Served                |                                                                                                                                                                                                                                                                                                                                                                               | Use from API instead  |          |          | 
| Zip Codes Served             |                                                                                                                                                                                                                                                                                                                                                                               | Use from API instead  |          |          | 
| Sample ID                    |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          |
| Sample Point ID              |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          |
| Code                         | Contaminant Code                                                                                                                                                                                                                                                                                                                                                              | Yes                   |          |          | 
| Contaminant                  |                                                                                                                                                                                                                                                                                                                                                                               | pull from code lookup |          |          | 
| Method                       | Text field of method - needs cleaning                                                                                                                                                                                                                                                                                                                                         | Yes                   |          |          | 
| Detected                     |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          | 
| Concentration                |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          | 
| Units                        |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          | 
| Concentration (ng/l)         |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          |
| Reporting Level              |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          | 
| Health Advisory Level (ng/L) |                                                                                                                                                                                                                                                                                                                                                                               | ?                     |          |          |
| Sample Date                  |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          | 
| Compliance Period Begin Date |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| Compliance Period End Date   |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| Sample Type                  |                                                                                                                                                                                                                                                                                                                                                                               | Yes                   |          |          |
| MRL/MDL                      | Categorical MRL or MDL                                                                                                                                                                                                                                                                                                                                                        | Yes                   |          |          |
| Reporting                    | Automated/Manual                                                                                                                                                                                                                                                                                                                                                              |                       |          |          | 
| Comment                      |                                                                                                                                                                                                                                                                                                                                                                               |                       |          |          |
| Most Recent Sample           | Yes/No                                                                                                                                                                                                                                                                                                                                                                        |                       |          |          | 
| Results                      | Count of results?                                                                                                                                                                                                                                                                                                                                                             |                       |          |          | 

SDWIS download tables
Table: geographic_area  (one to many with PWSID)

| Attribute           | Description | Lift to Graph | Ontology | Property |
|---------------------|-------------|---------------|----------|----------| 
| ansi_entity_code    | American National Standards Institute (ANSI) code for the county, city, or legal statistical area. Taken with the ANSI state code, uniquely identifies a county (or other area) within the country. See the U.S. Census Bureau webpage for more information about ANSI codes.            |               |          |          |
| area_type_code      | Indicates the area type, which is TR (Tribal), CN (County), ZC (Zip Code), CT (City), or IR (Indian Reservation)            |               |          |          |
| city_served         |             |               |          |          |
| county_served       |             |               |          |          |
| epa_region          |             |               |          |          |
| geo_id              |             |               |          |          |
| primacy_agency_code |             |               |          |          |
| pws_activity_code   |             |               |          |          |
| pws_type_code       | A system-generated coded value which classifies the water system according to federal requirements. It includes Community Water Systems (CWS), Non-Transient Non-Community Water Systems (NTNCWS), and Transient Non-Community Water Systems (TNCWS).            |               |          |          |
| pwsid               |             |               |          |          |
| state_served        |             |               |          |          |
| tribal_code         |             |               |          |          |
| zip_code_served     |             |               |          |          |

Table: service_area (one to many with PWSID)

| Attribute                    | Description                                                                                                                                                                                                                                                                                                     | Lift to Graph | Ontology | Property |
|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------|----------| 
| epa_region                   |                                                                                                                                                                                                                                                                                                                 |               |          |          |
| is_primary_service_area_code | Code indicating the type of primary service area served by the water system.                                                                                                                                                                                                                                    |               |          |          |
| primacy_agency_code          | Two character postal code for the state or territory having regulatory oversight for the water system. If the water system is regulated directly by EPA, this code will consist of the two-digit EPA Region number (01â€¦10). The Navajo Nation has primacy over its water systems, so NN is used in this case. |               |          |          |
| pws_activity_code            | Code that indicates the activity status of the public water system.                                                                                                                                                                                                                                             |               |          |          |
| pws_type_code                | A system-generated coded value which classifies the water system according to federal requirements. It includes Community Water Systems (CWS), Non-Transient Non-Community Water Systems (NTNCWS), and Transient Non-Community Water Systems (TNCWS).                                                           |               |          |          |
| pwsid                        |                                                                                                                                                                                                                                                                                                                 |               |          |          |
| service_area_type_code       | Service area type code. (Dispenser, Hotel/Motel, School, Residential Area, etc.)                                                                                                                                                                                                                                |               |          |          |
|                              |                                                                                                                                                                                                                                                                                                                 |               |          |          |

Table: sdwa_facilities.csv 

| Attribute                  | Description | Lift to Graph | Ontology | Property |
|----------------------------|-------------|---------------|----------|----------| 
| SUBMISSIONYEARQUARTER      
| PWSID                      
| FACILITY_ID                
| FACILITY_NAME              
| STATE_FACILITY_ID          
| FACILITY_ACTIVITY_CODE     
| FACILITY_DEACTIVATION_DATE 
| FACILITY_TYPE_CODE         | Code identifying the type of facility.
| SUBMISSION_STATUS_CODE     
| IS_SOURCE_IND              
| WATER_TYPE_CODE            
| AVAILABILITY_CODE          
| SELLER_TREATMENT_CODE      
| SELLER_PWSID               
| SELLER_PWS_NAME            
| FILTRATION_STATUS_CODE     
| IS_SOURCE_TREATED_IND      
| FIRST_REPORTED_DATE        
| LAST_REPORTED_DATE         

Sample Material Type

Controlled Vocabulary - 
Facility_type_Code
* CC - Consecutive Connection
* CH - Common Headers
* CS - Cistern
* CW - Clear Well
* DS - Distribution System System/Zone
* IG - Infiltration Gallery
* IN - Intake
* NN - Non-piped, Non-purchased
* NP - Non-piped
* OT - Other
* PC - Pressure Control
* PF - Pump Facility
* RC - Roof Catchment
* RS - Reservoir
* SI - Surface Impoundment
* SP - Spring
* SS - Sampling Station
* ST - Storage
* TM - Transmission Main (Manifold)
* TP - Treatment Plant
* WH - Wellhead
* WL - Well