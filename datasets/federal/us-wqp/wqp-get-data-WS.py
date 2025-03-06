import json
import geojson
import urllib3
from urllib import parse
import geopandas
from pathlib import Path

def write_json(filename, data):
    '''Outputs the geojson to a file in data/ directory'''
    # dump the geojson to data folder
    root_dir = Path(__file__).resolve().parent.parent.parent
    output = root_dir / "data" / "water-quality-data-portal" / filename
    geojson = geojson.loads(data)
    print(len(geojson['features']), " Features")
    with open(output, 'w') as outfile:
        json.dump(geojson, outfile, indent=1)

def write_csv(filename, csv):
    root_dir = Path(__file__).resolve().parent.parent.parent
    output = root_dir / "data" / "water-quality-data-portal" / filename
    with open(output, 'w') as outfile:
        outfile.write(csv.decode())

def get_station(statecode):
    old_url = f'https://www.waterqualitydata.us/data/Station/search?countrycode=US&statecode=US%3A{statecode}&mimeType=geojson'
    url = "https://www.waterqualitydata.us/wqx3/Station/search?countrycode=US&statecode=US%3A{statecode}&mimeType=csv"
    resp = urllib3.request("GET",url )
    stations = resp.data
    return stations

def get_pfas_station(statecode):
    types = ["Organics, PFAS","PFAS,Perfluorinated Alkyl Substance","PFOA, Perfluorooctanoic Acid","PFOS, Perfluorooctane Sulfonate"]
    type = ""
    for characteristic in types:
        type+=parse.quote_plus(characteristic)
        type+=";"
    print(type)
    old_url =f'https://www.waterqualitydata.us/beta/data/Station/search?countrycode=US&statecode=US%3A{statecode}&characteristicType={type}&mimeType=geojson' 
    url=f'https://www.waterqualitydata.us/wqx3/Station/search?countrycode=US&statecode=US%3A{statecode}&mimeType=xml'
    print(url)
    resp = urllib3.request("GET", url, timeout=60.0)
    stations = resp.data
    return stations

def get_result(statecode):
    """"""
    types = ["Stable Isotopes"] #,"PFOA, Perfluorooctanoic Acid","PFOS, Perfluorooctane Sulfonate", PFAS,Perfluorinated Alkyl Substance
    type = ""
    for characteristic in types:
        type+=parse.quote_plus(characteristic)
        type+=";"
    old_url = f'https://www.waterqualitydata.us/data/Result/search?countrycode=US&statecode=US%3A{statecode}&characteristicType={type}'
    url = f'https://www.waterqualitydata.us/wqx3/Result/search?statecode=US%3A{statecode}&characteristicType={type}&mimeType=csv'
    print(url)
    resp = urllib3.request("GET", url)
    results = resp.data #this returns a csv
    
    return results

if __name__ == "__main__":
    #stations = get_station('23')
    #write_json('ME-All-stations.geojson', stations)
    
    #stations = get_pfas_station('23')
    #write_json('ME-pfas-stations.geojson', stations) #this only works with the old url
    #write_csv('ME-pfas-stations.csv', stations)
    
    results = get_result('23')
    write_csv("ME-pfas-results_WS.csv", results) #This service is not currently working  and the file was instead manually downloaded from wqx3.0 as fullphysicalchemical profile