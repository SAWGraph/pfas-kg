import json
import geojson
import urllib3
from urllib import parse
import geopandas
from pathlib import Path
import warnings

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
    for characteristicType in types:
        type+=parse.quote_plus(characteristicType)
        type+=";"
    print(type)
    old_url =f'https://www.waterqualitydata.us/beta/data/Station/search?countrycode=US&statecode=US%3A{statecode}&characteristicType={type}&mimeType=geojson' 
    url=f'https://www.waterqualitydata.us/wqx3/Station/search?countrycode=US&statecode=US%3A{statecode}&&characteristicType={type}&mimeType=csv'
    print(url)
    resp = urllib3.request("GET", url, timeout=60.0)
    stations = resp.data
    return stations

def get_result(statecode):
    """"""
    types = ["PFAS,Perfluorinated Alkyl Substance","PFOA, Perfluorooctanoic Acid","PFOS, Perfluorooctane Sulfonate", "Stable Isotopes"] #,"PFOA, Perfluorooctanoic Acid","PFOS, Perfluorooctane Sulfonate", Stable Isotopes,
    type = ""
    for characteristic in types:
        type+=parse.quote_plus(characteristic)
        type+=";"
    #old_url = f'https://www.waterqualitydata.us/data/Result/search?countrycode=US&statecode=US%3A{statecode}&characteristicType={type}'
    url = f'https://www.waterqualitydata.us/wqx3/Result/search?statecode=US%3A{statecode}&characteristicType={type}&dataProfile=fullPhysChem&mimeType=csv'
    print(url, len(url))
    if len(url) > 2048:
        raise Warning('The request may be too long to process')
    resp = urllib3.request("GET", url, timeout=60)
    results = resp.data #this returns a csv
    
    return results

fips_lookup = {
'AL':1,
'AK':2,
'AZ':4,
'AR':5,
'CA':6,
'CO':8,
'CT':9,
'DE':10,
'DC':11,
'FL':12,
'GA':13,
'HI':15,
'ID':16,
'IL':17,
'IN':18,
'IA':19,
'KS':20,
'KY':21,
'LA':22,
'ME':23,
'MD':24,
'MA':25,
'MI':26,
'MN':27,
'MS':28,
'MO':29,
'MT':30,
'NE':31,
'NV':32,
'NH':33,
'NJ':34,
'NM':35,
'NY':36,
'NC':37,
'ND':38,
'OH':39,
'OK':40,
'OR':41,
'PA':42,
'PR':72,
'RI':44,
'SC':45,
'SD':46,
'TN':47,
'TX':48,
'UT':49,
'VT':50,
'VA':51,
'VI':78,
'WA':53,
'WV':54,
'WI':55,
'WY':56
}

if __name__ == "__main__":

    state=input("State abbreviation?")
    fips = str(fips_lookup[state])

    stations = get_pfas_station(fips)
    write_csv(f'{state}-pfas-stations.csv', stations)

    results = get_result(fips)
    write_csv(f'{state}-pfas-results.csv', results) 