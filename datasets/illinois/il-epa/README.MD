 ##Overview
 * **Name of dataset:** IL EPA PFAs Data 2021
 * **Source Agency:** Illinois Epa
 * **Data source location:**  https://maps.isgs.illinois.edu/arcgis/rest/services/ILWATER/Water_and_Related_Wells2/MapServer
 * 
 * https://services1.arcgis.com/qI0WaD4k85ljbKGT/ArcGIS/rest/services/IllinoisEpaPfasData/FeatureServer/0
 * **Metadata description:** https://prairie-research.maps.arcgis.com/apps/webappviewer/index.html?id=e06b64ae0c814ef3a4e43a191cb57f87
 * 
 * Results from the Illinois EPA's 2021 sampling event of Community Water Supplies across the state. This includes both groundwater and surface water sources
                            https://epa.illinois.gov/topics/water-quality/pfas/pfas-statewide-investigation-network.html
                        https://pubs.usgs.gov/publication/sir20235078/full
 * **Format:**
 * **Data update interval:**


## Raw Data Attributes


il-wells

| attributes   | Description                      | Lift to graph | Ontology Property |
|--------------|----------------------------------|---------------|-------------------| 
| OBJECTID     | *                                |               |                   |
| API_NUMBER   | *                                | Yes           |                   |
| ISWSPNUM     | 152051 of 379496                 | Yes           |                   |
| STATUS       |                                  | Yes           |                   |
| STATUSLONG   | Status description               | Yes           |                   |
| LATITUDE     | *                                | Yes           |                   |
| LONGITUDE    | *                                | Yes           |                   |
| LOCATION     | ?mapsheet                        |               |                   |
| OWNER        |                                  | Yes           |                   |
| FARM_NAME    | Well Name                        | Yes           |                   |
| WELL         | matches FARM_NAME                |               |                   |
| DRILLER      | Drilling company                 |               |                   |
| DATE_DRILLED |                                  | ?             |                   |
| ELEVATION    |                                  | ?             |                   |
| ELEVREF      |                                  | ?             |                   |
| ELEVREFLONG  | Elevation reference description  | ?             |                   |
| TOTAL_DEPTH  |                                  | Yes           |                   |
| WFORMATION   | Formation                        | ?             |                   |
| FORM_TOP     | Formation Top                    | ?             |                   |
| FORM_BOTTOM  | Formation Bottom                 | ?             |                   |
| PUMPGPM      | Pumping Rate                     | Yes           |                   |
| FLAG_LAS     | Digitized Well Log               |               |                   |
| FLAG_LOG     | Scanned Well Log                 |               |                   |
| FLAG_CORE    | Core at ISGS                     | ?             |                   |
| FLAG_SAMPLES | Samples at ISGS                  | ?             |                   |
| DataSummary  | Data summary sheet (url to  pdf) | ?             |                   |

| attributes | Description                                                                                                                    | Lift to graph | Ontology Property |
|------------|--------------------------------------------------------------------------------------------------------------------------------|---------------|-------------------|   
| OBJECTID   |                                                                                                                                |               |                   |
| PWS_ID     | Public Water system identification number assigned by the state, territory, or EPA Region plus seven digits (e.g., IN2750869). |               |                   |
| PWS_NAME   | Names of the public water system                                                                                               |               |                   |
| ENTRY_PT   |                                                                                                                                |               |                   |
| TYPE       | Groundwater,  Surface Water , Mixed                                                                                            |               |                   |
| MORE_INFO  |                                                                                                                                |               |                   |
| PFOA       |                                                                                                                                |               |                   |
| PFOS       |                                                                                                                                |               |                   |
| PFBS       |                                                                                                                                |               |                   |
| PFHxA      |                                                                                                                                |               |                   |
| PFHxS      |                                                                                                                                |               |                   |
| PFHpA      |                                                                                                                                |               |                   |
| PFNA       |                                                                                                                                |               |                   |
| DETECT     |                                                                                                                                |               |                   |
| LATITUDE   |                                                                                                                                |               |                   |
| LONGITUDE  |                                                                                                                                |               |                   |
| TextPFOA   |                                                                                                                                |               |                   |
| TextPFOS   |                                                                                                                                |               |                   |
| TextPFBS   |                                                                                                                                |               |                   |
| TextPFHxA  |                                                                                                                                |               |                   |
| TextPFHxS  |                                                                                                                                |               |                   |
| TextPFHpA  |                                                                                                                                |               |                   |
| TextPFNA   |                                                                                                                                |               |                   |
| Units      |                                                                                                                                |               |                   |
| geometry   |                                                                                                                                |               |                   |

RT Routine, RP Repeat, CO Confirmation, MR Maximum Residence Time, DU Duplicate, PE Performance Evaluation, SB Shipping Blanks, SL Split, SP Special, ST Split Blanks https://water.epa.state.il.us/dww/Help/html_Sample_Type.htm

