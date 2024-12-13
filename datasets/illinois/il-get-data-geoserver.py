import json
import geojson
import urllib3
import geopandas
from pathlib import Path

def dump_file(filename, geojson):
    '''Outputs the geojson to a file in data/maine_dep_esri_server directory'''
    # dump the geojson to data folder
    root_dir = Path(__file__).resolve().parent.parent.parent
    output = root_dir / "data" / "il-epa" / filename
    # print(output)
    with open(output, 'w') as outfile:
        json.dump(geojson, outfile, indent=1)

def get_layer(url):
    '''Requests the geojson from the illinois EPA web server by layer id
    Layers:
        0: IllinoisEpaPfasData'''
    # get the geojson for licensed fields from the web server
    location = url + f"query?where=OBJECTID+%3E+-1&outFields=*&f=pgeojson"
    print(location)
    resp = urllib3.request("GET", location)

    resp.data
    layer_geojson = geojson.loads(resp.data)
    #print(json.dumps(layer_geojson[0], indent=4))
    return(layer_geojson)

def get_results():
    """
    Request geojson from illinois epa web server by layer id
    Layers:

    """
    resp = urllib3.request("GET", f'https://services1.arcgis.com/qI0WaD4k85ljbKGT/ArcGIS/rest/services/IllinoisEpaPfasData/FeatureServer/0/query?where=OBJECTID+%3E+-1&&outFields=*&f=pgeojson')
    #resp.data
    layer_geojson = geojson.loads(resp.data)
    # print(json.dumps(layer_geojson[0], indent=4))
    return (layer_geojson)

def get_samples():
    #max record count is 1000 in get request, so have to do this multiple times
    url = f'https://geoservices.epa.illinois.gov/arcgis/rest/services/Water/PfasSamplePoints/MapServer/0/query?where=OBJECTID+%3E+-1&outFields=*&resultOffset=&resultRecordCount=800&f=geojson'
    print(url)
    resp = urllib3.request("GET", url)
    layer_geojson = geojson.loads(resp.data)

    #get remaining
    resp2 = urllib3.request("GET",
                           f'https://geoservices.epa.illinois.gov/arcgis/rest/services/Water/PfasSamplePoints/MapServer/0/query?where=OBJECTID+%3E+-1&outFields=*&resultOffset=800&resultRecordCount=800&f=json')

    layer_geojson2 = geojson.loads(resp2.data)

    for x in layer_geojson2['features']:
        layer_geojson['features'].append(x)
    return (layer_geojson)

def get_wells():
    check= urllib3.request("GET", 'https://maps.isgs.illinois.edu/arcgis/rest/services/ILWATER/Water_and_Related_Wells2/MapServer/2/query?where=OBJECTID+%3E+-1&returnCountOnly=true&f=geojson')
    feature_count = json.loads(check.data.decode())['count']
    print(feature_count, ' Wells')
    #This server also contains aquifers
    #max record count for requests is 3000
    f=0
    layers=[]
    while f < feature_count+3000:
        resp= urllib3.request("GET", f'https://maps.isgs.illinois.edu/arcgis/rest/services/ILWATER/Water_and_Related_Wells2/MapServer/2/query?where=OBJECTID+%3E+-1&outFields=*&resultOffset={f}&resultRecordCount=3000&f=geojson')
        layer_geojson = geojson.loads(resp.data)
        layers.append(layer_geojson)
        f+=3000

    layer_geojson = layers.pop(0)
    for subset in layers:
        for feature in subset['features']:
            layer_geojson['features'].append(feature)
    print(len(layer_geojson['features']))
    return (layer_geojson)

def get_updated():
    resp=urllib3.request("GET", 'https://geoservices.epa.illinois.gov/arcgis/rest/services/Water/PfasSamplingResults/MapServer/0/query?where=OBJECTID+%3E+-1&outFields=*&f=pjson')
    layer_geojson = geojson.loads(resp.data)
    return(layer_geojson)


if __name__ == "__main__":

    #tests = get_results()
    #dump_file("il-epa.geojson", tests)

    wells = get_wells()
    dump_file('il-wells.geojson', wells)

    #updated = get_updated()
    #dump_file('il-epa-updated.geojson', updated)

    #samples= get_samples()
    #dump_file('il-epa-samples.geojson', samples)