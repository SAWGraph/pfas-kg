## Data Source
* [Maine Geological Survey Water Well Database]([https://www.maine.gov/dacf/mgs/pubs/digital/well.htm](https://mgs-maine.opendata.arcgis.com/datasets/maine::maine-well-database-well-depth/about))


## Code
* 

## Mapping

| Raw data attribute | Lift to graph | Additional comment                                      | 
| --- | --- |---------------------------------------------------------|
| X* | --- | Only in located wells table                             | 
| Y* | --- | Only in located wells table                             | 
| WELLNO         | YES | Well Number                                             | 
| WELL_LOCATION_TOWN  | YES | match to towns?                                         | 
| WELL_LOCATION_ADDRESS            | --- | match to parcels?                                       | 
| TAX_MAP_NO | --- | match to parcels?                                       | 
| TAX_LOT_NO | --- | match to parcels?                                       | 
| DRILL_DATE | --- | ---                                                     | 
| DRILL_DATE_ESTIMATED | --- | Drill Date Estimated - Boolean                          | 
| WELL_DRILLER_COMPANY | --- | ---                                                     | 
| WELL_USE| YES | controlled vocabulary                                   | 
| WELL_TYPE | YES | controlled vocabulary                                   | 
| WELL_CONSTRUCTION | YES | controlled vocabulary                                   |
| WELL_DEVELOPMENT |? | sparse data, controlled vocabulary                      |
| CASING_LENGTH_FT | --- | sparse data in unlocated wells                          |
| OVERBURDEN_THICKNESS_FT | --- | [sparse data] thickness of earth material until bedrock |
| WELL_DEPTH_FT | YES | ---                                                     |
| WELL_YIELD_MODIFIER | --- | sparse                                                  | 
| WELL_YIELD_GPM | ? | sparse in unlocated wells                               | 
| YIELD_DATE | --- | sparse                                                  |
| WELL_STATIC_LEVEL_FT | ? | ---                                                     |
| WELL_STATIC_DATE | --- | ---                                                     |
| VEIN1_DEPTH_FT| --- | ---                                                     |
| VEIN1_YIELD_GPM | --- | ---                                                     |
| VEIN2_DEPTH_FT| --- | ---                                                     |
| VEIN2_YIELD_GPM | --- | ---                                                     |
| VEIN3_DEPTH_FT| --- | ---                                                     |
| VEIN3_YIELD_GPM | --- | ---                                                     |
| VEIN4_DEPTH_FT| --- | ---                                                     |
| VEIN4_YIELD_GPM | --- | ---                                                     |
| REPLACEMENT_WELL  | ? | boolean, sparse                                         |
| GEOTHERMAL_WELL | ? | boolean                                                 | 
| WELL_COMMENT | --- | ---                                                     | 
| LOCATION_METHOD*| --- | controlled vocabulary                                   | 
| LOCATION_ACCURACY* | --- | ---                                                     | 
| LOCATION_DATE*| --- | ---                                                     |
| LOCATION_UPDATED_DATE*| --- | ---                                                     | 
| LATITUDE* | --- | ---                                                     | 
| LONGITUDE *| --- | ---                                                     | 
| WELL_YIELD_CLASS *| --- | ---                                                     |
| WELL _DEPTH_CLASS* | --- | ---                                                     | 
| WELL_OVERBURDEN_THICKNESS_CLASS *| --- | ---                                                     | 
| WELLCARDNO | --- | ---                                                     |
| HYDROFRACTURE| --- | ---                                                     | 
| ERROR_REPORT_URL | --- |
| DATE_ENTERED *| --- | ---                                                     |
| DATE_EDITED *| --- | ---                                                     |



## Schema Diagram

## Controlled Vocabularies
**List 1. Well Use**
* Domestic
* Commercial
* Other
* Municipal
* Farm, Domestic
* Institutional
* Test
* Geothermal
* Industrial
* Irrigation
* Farm
* Observation
* Monitoring

**List 2. Well Type**
* Bedrock
* Gravel
* Overburden
* Spring
* Other
* Gravel Packed
* Dug
* Observation

**List 3. Well Construction**
* Drilled
* Rotary Drilled
* Dug
* Hammer Drilled
* Cable Tool
* Driven Point
* Jet
* Auger
* Drilled Overburden

**List 4. Well Development** 
* None
* Air
* Air/Water
* Other
* Jetting
* Blasting
* Dry Ice
* Dynamite
* Not Sure

**List 5. Location_Method**
* TAX MAP AND LOT
* GEOCODED STREET ADDRESS MAINE E911
* GPS
* DRILLER PROVIDED - OK	
* GEOCODED ADDRESS POINT MAINE E911	
* GEOCODED STREET ADDRESS OTHER	
* OWNER PROVIDED - OK	
* DRILLER PROVIDED - CORRECTED BY MGS	
* ORTHOIMAGERY	
* DRILLER PROVIDED - INCORRECT	
* OWNER PROVIDED - CORRECTED BY MGS

## Sample Data


## Competency Questions 


## Contributors
* 
