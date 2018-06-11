# -*- coding: utf-8 -*-
"""
Use the OCLC Worldcat Knowledgebase API to access information about print and 
electronic resources.
Usage: %prog inputfile outputfile
"""
import json
import requests
import sys

json_data_format = 'application/json'
HEADERS_JSON = {'Accept' : json_data_format}
INST_ID = '5640'
MAX_RES = 100
ITEMS_PP = 50
CONTENT_TYPE = 'ebook'
URL_STUB = 'http://worldcat.org/webservices/kb/rest/entries/search?'
WSKEY='xAW2qDuioeBKBdIPHuUrBNPGqk78NmUsaB8LP2BERjpClphypY9Nn92E2tesAgCvmY0G6bbM5DzaQSPS'
info =[]

def get_URL(inst_id,start_pos):
    url = URL_STUB+'institution_id={}&start-index={}&max-results={}&itemsPerPage={}' \
            '&content={}&wskey={}'.format(inst_id,start_pos,MAX_RES,
                      ITEMS_PP,CONTENT_TYPE,WSKEY)
    return url

def get_KB_Data(url, headers):
    try:
        q = requests.get(url, headers)
        return q
    except:
        print('error in request: {}'.format(sys.exc_info()[0]))
        return ''
    
if __name__ == '__main__':
    with open('delme.txt', 'w', encoding='utf-8') as result_file:
        for start_i in range(0,MAX_RES,ITEMS_PP):
            #build a URL with updated values for start-index (and others as wanted)
            institution_id = INST_ID
            url = get_URL(institution_id, start_i)
            q = requests.get(url,headers=HEADERS_JSON)
            results = json.loads(q.text)
            for i, entry in enumerate(results['entries']):
                try:
                    info.append('{}{}{}'.format(str(entry['title']).strip(),'|',
                                entry['kb:provider_name']))
                except AttributeError as ae:
                    print(ae, entry)
                except KeyError as ke:
                    print(ke, entry)
        result_file.write('\n'.join(info))
            #    for e, key in enumerate(entry.keys()):
            #        print('{}:{}: {}'.format(i,key,entry[key]))
                #print('{}: {}{}'.format(str(i), entry['title'],'\n'))