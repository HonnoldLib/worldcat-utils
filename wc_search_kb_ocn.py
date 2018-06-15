# -*- coding: utf-8 -*-
"""
Use the OCLC Worldcat Knowledgebase API to access information about print and 
electronic resources.
Usage: %prog inputfile outputfile
See: https://www.oclc.org/developer/develop/web-services/worldcat-knowledge-base-api/entry-resource.en.html
"""
import csv
import json
import logging
import os 
import requests
import sys
import yaml #cfg file in yaml format. See: 

#anything above def is global variable
#config file (yaml) - should be in the same directory as application.
CFGFILENAME = os.path.dirname(os.path.realpath(__file__))+\
os.sep+os.path.basename(__file__)[:-3]+'_settings.cfg' # should work on any OS

def getYAMLConfig(fname):
    try:
        with open(fname,'r') as ymlf:
            config = yaml.load(ymlf)
    except Exception as e:
        logging('Error accessing config: ',e)
    return config

def print_status(numcodes, totalNum, msg): #progress indicator
    """print status message for long-running scripts"""
    print('{} {} {}\r'.format(numcodes, totalNum, msg), end='\r'),
    sys.stdout.flush() 
    
def set_URL(oclcnum, baseurl, wskey):
    """build a URL string that includes the starting position in the search result."""
    snoopy=baseurl+ '&wskey={}&oclcnum={}'.format(wskey,oclcnum)
    return snoopy

def get_KB_Data(url,req_headers):
    """submit a URL request and return the result (or error message) """
    try:
        q = requests.get(url, headers=req_headers)
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
    inputs_file=sys.argv[1]
    outputs_file = sys.argv[2]
    config = getYAMLConfig(CFGFILENAME) #get the config file values
    wskey = config['Auth']['WSKEY']
    request_data_format = config['Config']['JSON_DATA_FORMAT']
    request_header = {'Accept' : request_data_format}
    institution_id = config['Config']['INST_ID']# don't need?
    url_base = config['Config']['URL_BASE_ENTRIES']
    content_type = config['Config']['CONTENT_TYPE']
    info =[]
    with open(inputs_file,'r') as inputs, open(outputs_file, 'w', newline='') as outputs:
        csvwriter = csv.writer(outputs, delimiter='\t', quoting=csv.QUOTE_MINIMAL, quotechar="'", escapechar='') #csv file writing machine
        for line in inputs.readlines():
            clean_line = line.strip()# clean up possible whitespace issues
            # build a URL with updated values for start-index (and others as wanted)
            url = set_URL(clean_line,url_base, wskey) 
            # retreive data from the url
            q = get_KB_Data(url, request_header)
            # parse the data into json
            results = parse_json_to_dict(q.text)
            collection_name = set('') # default collection name (set)
            # each request may contain multiple items; step through them
            for entry in results['entries']:
                try:
                    collection_name.add(entry['kb:collection_name'])
                except AttributeError as ae:
                    logging.exception('No attribute?')
                    collection_name.add('')
                    #print(ae, entry)
                except KeyError as ke: #todo: add a null value for missing keys
                    logging.exception('No key?')
                    collection_name.add('Collection Name Not Found')
                    #print('ke',results['os:totalResults'], ke, entry.keys())
            #print(clean_line,str(results['os:totalResults']).strip(),'\t'.join(sorted(collection_name)))
            # make a list of the values to write to csv file
            info=[clean_line,str(results['os:totalResults']).strip()]
            info+=(sorted(collection_name))
            print(info)
            csvwriter.writerow(info) #write the list to the csv file
    print('Completed.')