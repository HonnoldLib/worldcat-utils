# -*- coding: utf-8 -*-
"""
Use the OCLC Worldcat Knowledgebase API to access information about print and 
electronic resources.
Usage: %prog inputfile outputfile
"""
import json
import logging
import requests
import sys

json_data_format = 'application/json'
HEADERS_JSON = {'Accept' : json_data_format}
INST_ID = '5640'
MAX_RES = 100
ITEMS_PP = 50
CONTENT_TYPE = 'ebook'
URL_STUB_ENTRIES = 'http://worldcat.org/webservices/kb/rest/entries/search?'
URL_STUB_COLLECTIONS = 'http://worldcat.org/webservices/kb/rest/collections/search?q='
WSKEY='xAW2qDuioeBKBdIPHuUrBNPGqk78NmUsaB8LP2BERjpClphypY9Nn92E2tesAgCvmY0G6bbM5DzaQSPS'
info =[]

def print_status(numcodes, totalNum, msg): #progress indicator
    """print status message for long-running scripts"""
    print('{} {} {}\r'.format(numcodes, totalNum, msg), end='\r'),
    sys.stdout.flush() 
    
def get_URL(start_pos, url):
    """build a URL string that includes the starting position in the search result."""
    url += 'institution_id={}&start-index={}&max-results={}&itemsPerPage={}' \
            '&content={}&wskey={}'.format(INST_ID,start_pos,MAX_RES,
                      ITEMS_PP,CONTENT_TYPE,WSKEY)
    return url

def get_KB_Data(url):
    """submit a URL request and return the result (or error message) """
    try:
        q = requests.get(url, headers=HEADERS_JSON)
        return q
    except:
        #print('error in request: {}'.format(sys.exc_info()[0]))
        logging.exception('unexpected error getting data at url')
        return ''
    
def parse_json_to_dict(text_data):
    """parse json-containing text, return a python dictionary"""
    try:
        results = json.loads(text_data)
        return results
    except:
        #print('error parsing json result: {}'.format(sys.exc_info()[0]))
        logging.exception('unexpected error parsing json result')
        return {}        

if __name__ == '__main__':
    with open('delme.txt', 'w', encoding='utf-8') as result_file:
        for start_i in range(0,MAX_RES,ITEMS_PP):
            #build a URL with updated values for start-index (and others as wanted)
            url = get_URL(start_i,URL_STUB_ENTRIES) #use for Entries 
            q = get_KB_Data(url)
            results = parse_json_to_dict(q.text)
            #add results to a dictionary, and finally to a file
            for i, entry in enumerate(results['entries']):
                try:
                    info.append('{}{}{}'.format(str(entry['title']).strip(),'|',
                                entry['kb:provider_name']))
                    print_status(start_i, i, MAX_RES)
                except AttributeError as ae:
                    print(ae, entry)
                except KeyError as ke: #todo: add a null value for missing keys
                    print(ke, entry)

        result_file.write('\n'.join(info))
