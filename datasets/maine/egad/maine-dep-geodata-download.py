import json
import geojson
import urllib3
import re
import geopandas
from pathlib import Path

def dump_file(filename, geojson):
    '''Outputs the geojson to a file in data/maine_dep_esri_server directory'''
    # dump the geojson to data folder
    output = root_dir / "data" / "maine_dep_esri_server" / filename
    # print(output)
    with open(output, 'w') as outfile:
        json.dump(geojson, outfile)

def get_layer(layer):
    '''Requests the geojson from the Maine DEP web server by layer id
    Layers:
        PFAS Groundwater Results (0)
        Licensed Field (1)
        Installed Water Treatment System (2)
        Soil Sample Areas (3)
        Soil Sample Location (4)
        Non-LD1600 PFAS Groundwater Results (8)
        PFAS_LD1600_Soil_Sample_Polygons (6)
        LD1911_Sample_Locations (7)'''
    # get the geojson for licensed fields from the web server
    resp = urllib3.request("GET",
                           f"https://gis.maine.gov/arcgis/rest/services/dep/MaineDEP_PFAS_Investigation/MapServer/{layer}/query?where=OBJECTID+%3E+-1&outFields=*&returnGeometry=true&featureEncoding=esriDefault&f=geojson")

    resp.data
    layer_geojson = geojson.loads(resp.data)
    #print(json.dumps(layer_geojson[0], indent=4))
    return(layer_geojson)

def get_source_layer(layer):
    """
    Request geojson from Maine DEP web server by layer id
    Layers:
    Layers:
        Agriculture Nitrate/Bacteria (0)
        Agriculture Chemical Use (1)
        Ash Utilization Site (2)
        Automobile Graveyard/Junkyard (3)
        Brownfields (4)
        Compost Site (5)
        Construction/Demolition Site (6)
        Dioxin Monitoring Program (7)
        Dry Cleaner (8)
        Engineered SWDS (9)
        Estuarine (10)
        Industrial Complex (11)
        Infiltration/Retention Basin (12)
        Lake/Pond (13)
        Landfill Commercial (14)
        Landfill Municipal (15)
        Landfill Special Waste (16)
        Large Bulk Fuel Storage (17)
        Leaking Aboveground Storage Tank (18)
        Leaking Underground Storage Tank (19)
        Marina/Boatyard (20)
        Marine (21)
        Mystery Spill (22)
        Non-Point Source (23)
        RCRA Remediation (24)
        RCRA Large Quantity Generator (25)
        RCRA Medium Quantity Generator (26)
        RCRA Small Quantity Generator (27)
        Residuals Utilization Site (28)
        Resource Extraction (Groundwater) (29)
        Resource Extraction Activity (30)
        River/Stream (31)
        Sand/Salt Storage (32)
        Sanitary & Industrial WWTF (33)
        Septage Land Application Site (34)
        Sludge Utilization Site (35)
        Small Bulk Fuel Storage (36)
        Storm Sewer (37)
        Stream/River Biomonitoring (38)
        Surface Impoundment Assessment Site (39)
        Surface Spill (40)
        SWAT - Lakes (41)
        SWAT - Marine (42)
        SWAT - Rivers & Streams (43)
        Transfer Station (44)
        Uncontrolled Site, All Other (45)
        Uncontrolled Site, DOD (46)
        Uncontrolled Site, NPL (47)
        Underground Injection Site (48)
        Universal Waste Handler (49)
        Unsewered Subdivision (50)
        VRAP Program Site (51)
        Wetland (52)
        Wood Products Facility (53)
        MaineDEP EGAD Site Types (54)
    """
    getCount = urllib3.request("GET", f'https://gis.maine.gov/arcgis/rest/services/dep/MaineDEP_EGAD_Site_Types/MapServer/{layer}/query?where=OBJECTID+>+-1&text=&returnIdsOnly=false&returnCountOnly=true&returnDistinctValues=false&resultOffset=&f=pjson')
    #print(getCount.data)
    count = re.findall(r'\d+', str(getCount.data))
    print(count)
    n = 0
    i = 0
    json_dump = []
    while n < int(count[0]):
        resp = urllib3.request("GET", f'https://gis.maine.gov/arcgis/rest/services/dep/MaineDEP_EGAD_Site_Types/MapServer/{layer}/query?where=OBJECTID+%3E+-1&outFields=*&returnGeometry=true&featureEncoding=esriDefault&resultOffset={n}&f=geojson')
        type(resp.data)
        n += 3000
        json_dump.append(resp.data)
    while i < len(json_dump):
        layer_geojson = geojson.loads(json_dump[i])
        dump_file(f"egad_sites_{i}.geojson", layer_geojson)
        i += 1
    # print(json.dumps(layer_geojson[0], indent=4))
    return (json_dump)

if __name__ == "__main__":
    # set the project root for relative paths
    root_dir = Path(__file__).resolve().parent.parent.parent
    print(root_dir)

    #get licensed fields
    #licensed_fields = get_layer(1) #get licensed fields data
    # max record count 2000
    #dump_file("licensed_fields.geojson", licensed_fields)

    #get soil sample areas
    #soil_sample_areas = get_layer(3)
    #print(json.dumps(soil_sample_areas[0], indent=4))
    #dump_file("soil_sample_areas.geojson", soil_sample_areas)

    #get septage and sludge sites
    #septage = get_source_layer(34)
    #sludge = get_source_layer(35)

    #dump_file("septage_land_application_site.geojson", septage)
    #dump_file("sludge_utilization_site.geojson", sludge)

    all_sites = get_source_layer(54)
    #dump file is called automatically
