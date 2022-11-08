import requests
import re
import json
import time
import sys
import csv
import warnings

warnings.filterwarnings('ignore')


def writeData(fileName, resulList, page_number, wr):
    for listing in resultList:
        wr.writerow(extractData(listing) + [page_number])


def getResultList(r):
    data = json.loads(re.search(r'!--(\{"queryState".*?)-->', r.text).group(1))
    resultList = data['cat1']['searchResults']['listResults']
    return resultList


def extractData(listing):
    # listing: element from the resultList returned from Zillow
    homeInfoKeys = ['unit', 'homeType', 'dateSold', 'latitude', 'longitude',
                    'livingArea', 'price', 'rentZestimate', 'zestimate', 'taxAssessedValue',
                    'zpid', 'priceForHDP']
    listingKeys = ['addressCity', 'addressState', 'addressStreet', 'addressZipcode',
                   'baths', 'beds', 'brokerName', 'unformattedPrice']

    hdpData = listing.get('hdpData')
    if hdpData:
        homeInfo = hdpData.get('homeInfo')
    else:
        return None

    if homeInfo:
        homeInfoData = [homeInfo.get(k, '') for k in homeInfoKeys]
    else:
        return None

    listingData = [listing.get(k, '') for k in listingKeys]

    variableData = listing.get('variableData')
    if variableData:
        sell_date = variableData.get('text', '')
    else:
        sell_date = ''

    return listingData + homeInfoData + [sell_date]


out_file_name = 'recently_sold.csv'
page_number = int(sys.argv[1])
page_offset = int(sys.argv[2])
sleep_minutes = 15


city_state = 'boston-ma/'
base_url = 'https://www.zillow.com/homes/recently_sold/' + city_state

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


with requests.Session() as s:
    r = s.get(base_url, headers=req_headers)
    print("r is ok: ", r.ok)
    resultList = getResultList(r)
    with open(out_file_name, 'at') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        writeData(out_file_name, resultList, page_number, wr)
    while True:
        page_number += page_offset
        print("page number: ", page_number)
        url = base_url + str(page_number) + '_p/'
        r = s.get(url, headers=req_headers)
        if r.ok:
            resultList = getResultList(r)
            with open(out_file_name, 'at') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                writeData(out_file_name, resultList, page_number, wr)
        print("r is ok: ", r.ok)
        else:
            break
        time.sleep(60*sleep_minutes)
