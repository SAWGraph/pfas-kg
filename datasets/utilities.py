
import requests
import json
def resolvePlaceName(string, dominantType=''):
    key = 'L4Qn6dH7FvYNuLOwJBCwq8GU7jTLGZ5T0EkA5O7SdoMt6EyH'
    property = f'%3C-description{dominantType}-%3Edcid'
    res = requests.get(f"https://api.datacommons.org/v2/resolve?key={key}&nodes={string}&property={property}")
    return res

if __name__ == '__main__':
    result = resolvePlaceName('POLAND town, MAINE')   #{typeOf:CensusCountyDivision}
    print(result.text)
    print(result.json())
    print(result.json()['entities'][0]['resolvedIds'])