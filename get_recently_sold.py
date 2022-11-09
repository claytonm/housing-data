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


page_number = int(sys.argv[1])
page_offset = int(sys.argv[2])
neighborhood = sys.argv[3]
out_file_name = 'recently_sold_' + neighborhood + '.csv'
sleep_minutes = 5


city_state = neighborhood + '%20boston%20ma/'
base_url = 'https://www.zillow.com/homes/recently_sold/' + city_state

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

iters = 1
url = base_url
with requests.Session() as s:
    while iters <= 50:
        r = s.get(url, headers=req_headers)
        if r.ok:
            resultList = getResultList(r)
            with open(out_file_name, 'at') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                writeData(out_file_name, resultList, page_number, wr)
        else:
            break
        iters += 1
        time.sleep(60*sleep_minutes)
        page_number += page_offset
        print("page number: ", page_number)
        url = base_url + str(page_number) + '_p/'

