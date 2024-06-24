### Overview of the raw dataset
* **Name of dataset:** Green House Gas Reporting Program 
* **Source Agency:** EPA
* **Data source location:** [US EPA PFAS analytic tools data ](https://echo.epa.gov/trends/pfas-tools#data) *only PFAS reporting under certain regulations
* **Additional Data Sources:** [FLIGHT Facility Level Information on GreenHouse Gasses Tool](https://ghgdata.epa.gov/ghgp/main.do)
[Greenhouse Gas Inventory Data Explorer](https://cfpub.epa.gov/ghgdata/inventoryexplorer/)
[GHG Query Builder](https://enviro.epa.gov/query-builder/ghg)
[State GHG Emissions and Removals](https://www.epa.gov/ghgemissions/state-ghg-emissions-and-removals) 
* **Metadata:** 
GHG regulations are only facilities that emit 25,000 mtons of CO2 per year. Only certain facility types require flourinated GHG reporting. 

[Frequently Requested Data](https://www.epa.gov/ghgreporting/data-sets)
[Flourinated GHG Emissions and Supplies](https://www.epa.gov/ghgreporting/fluorinated-greenhouse-gas-emissions-and-supplies-reported-ghgrp)
[](https://enviro.epa.gov/query-builder/ghg/SUBPART%20INFORMATION/RLPS_GHG_EMITTER_SUBPART)
* **Format of data:** xlsx (could use REST services)
* **Date update interval:** Weekly
* **Date range:** 2010 - present

## Schema Diagram
[Preliminary Diagram (GHG tab)](https://lucid.app/lucidchart/16e658ef-6f61-4ce3-a770-0c410ecb194a/edit?viewport_loc=-498%2C-32%2C3272%2C1614%2Cs_7G8ANWcwl4&invitationId=inv_ea094a2c-59da-4347-b175-700b91e5623d)

## Code 

## Raw Data Attribute List 

| Attribute                | Description                                             | Lift to graph         | Ontology property          |
|--------------------------|---------------------------------------------------------|-----------------------|----------------------------|
| Facility                 | name of Facility                                        | No (already from FRS) |                            |
| Year                     |                                                         | Yes                   |                            |
| GHG Facility Id          |                                                         | Yes                   |                            |
| ECHO Facility Report     |                                                         |                       |                            |
| FRS ID                   |                                                         | Yes                   | URI of us_frs:FRS-Facility |
| GHG Subpart              |                                                         | Yes                   |                            |
| Chemical Name            | *semicolon separated                                    | Yes                   |                            |
| Chemical Formula         | *comma separated                                        | Yes                   |                            |
| CAS Number               | *comma separated                                        | Yes                   |                            |
| Amount (metric tons)     | Total metric tons per year (sum of produced and vented) | Yes                   |                            |
| State Territory or Tribe |                                                         |                       |                            |
| EPA Region               |                                                         |                       |                            |
| Latitude                 | *not the same as facility coordinate in frs             | Yes                   |                            |
| Longitude                | *not the same as facility coordinate in frs             | Yes                   |                            |
| EJSCREEN Report          |                                                         |                       |                            |
| City                     |                                                         |                       |                            |
| ZIP Code                 |                                                         |                       |                            |



