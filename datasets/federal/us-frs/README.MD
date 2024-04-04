## Overview of the raw dataset
* **Name of dataset:** Facility Registry Service
* **Source Agency:** EPA
* **Data source location:** [FRS State Downloads](https://www.epa.gov/frs/epa-state-combined-csv-download-files)
*note: there are many ways to access FRS data, such as via ECHO, state downloads contain industry codes*
* **Additional Data source:** [Industry Sectors Data](https://echo.epa.gov/trends/pfas-tools#data)
*note: this identifies facilities the epa suspects are using pfas*
* **Metadata description:** [Facility State File Documentation 1132012_new]() (comes with state download)
* **Format of data returned:**
* **Data update interval:**
* **General Comments**:

##Schema Diagram

## Code
*  

## Raw Data Attribute List and Mappings with Ontology
FRS State Downloads
ME_FACILITY_FILE.csv


|Attribute | Description                                                                                                                                                                                | Lift to Graph | Ontology Property |
| --- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| --- | --- |
| FRS_FACILITY_DETAIL_REPORT_URL | report url                                                                                                                                                                                 | |
| REGISTRY_ID| registry id to uniquely identify facility                                                                                                                                                  | | 
|PRIMARY_NAME | public or commercial name                                                                                                                                                                  | |
| LOCATION_ADDRESS|                                                                                                                                                                                            | |
| SUPPLEMENTAL_LOCATION|                                                                                                                                                                                            | |
| CITY_NAME| locality name - nameof city, town village or other locality within whose boundaries (the majority of) the facility site is located.                                                        | | COUNTY_NAME| | | 
|FIPS_CODE| county fips code (state and county)                                                                                                                                                        | | 
|STATE_CODE| USPS abbreviation for state                                                                                                                                                                | | 
|STATE_NAME|                                                                                                                                                                                            | | 
|COUNTRY_NAME|                                                                                                                                                                                            | | 
|POSTAL_CODE| 5 digit zip code and 4 digit extension code (if available)                                                                                                                                 | | 
|FEDERAL_FACILITY_CODE| Yes/No the facility is property of the Federal Government                                                                                                                                  | | 
|FEDERAL_AGENCY_NAME| name of federal agency (derived from FEDERAL_AGENCY_CODE lookup)                                                                                                                           | | 
|TRIBAL_LAND_CODE| Yes if tribal land                                                                                                                                                                         | | 
|TRIBAL_LAND_NAME| Name of Tribal Reservation, statistical area, or Public Domain Allotment.                                                                                                                  | | 
|CONGRESSIONAL_DIST_NUM|                                                                                                                                                                                            | | 
|CENSUS_BLOCK_CODE|                                                                                                                                                                                            | | 
|HUC_CODE| The Hydrologic Unit Code (HUC) that represents a geographic area representing part or all of a surface drainage basin, a combination of drainage basins, or a distinct hydrologic feature. | | 
|EPA_REGION_CODE| The code that represents an EPA Region.                                                                                                                                                    | | 
|SITE_TYPE_NAME| Allowable Values: [ Stationary, Monitoring Site, Brownfields Site, Water System ,  Contamination Addressed,  Contaminated Site,  Potentially Contaminated Site  ]                          | | 
|LOCATION_DESCRIPTION| Descriptive information about location of facility, including directions.                                                                                                                  | | 
|CREATE_DATE| date first posted to database                                                                                                                                                              | | 
|UPDATE_DATE| most recent calendar update                                                                                                                                                                | | 
|US_MEXICO_BORDER_IND| An indicator that the facility is located within 62.5 miles (100 km) of the United States - Mexico Border. Only applicable to facilities in California, Arizona, New Mexico, and Texas.    | | 
|PGM_SYS_ACRNMS| list of program acronyms the facility is tracked by                                                                                                                                        | | 
|LATITUDE83|                                                                                                                                                                                            | | 
|LONGITUDE83|                                                                                                                                                                                            | | 
|CONVEYOR| Identification of the party that transmitted the latitude and longitude                                                                                                                    | | 
|COLLECT_DESC| Method used to determine Lat/Long                                                                                                                                                          | | 
|ACCURACY_VALUE| Measure of accuracy in meters of latitude/longitude                                                                                                                                        | | 
|REF_POINT_DESC| Name that identifies the place for which geographic coordinates were established                                                                                                           | | 
|HDATUM_DESC| Horizontal reference datum used in determining latitude longitude coordinates                                                                                                              | | 
|SOURCE_DESC| Name of party responsible for providing lat/long coordinates                                                                                                                               | |
