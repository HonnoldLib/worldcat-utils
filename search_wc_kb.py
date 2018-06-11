# -*- coding: utf-8 -*-
"""
Use the OCLC Worldcat Knowledgebase API to access information about print and 
electronic resources.
Usage: %prog inputfile outputfile
"""
import json
import requests

json_data_format = 'application/json'
headers_json = {'Accept' : json_data_format}
institution = '5640'
#start_pos = 1
max_results = 1000
items_per_page = 50
content_type = 'ebook'
wskey='xAW2qDuioeBKBdIPHuUrBNPGqk78NmUsaB8LP2BERjpClphypY9Nn92E2tesAgCvmY0G6bbM5DzaQSPS'
info =[]

with open('delme.txt', 'w', encoding='utf-8') as result_file:
    for start_i in range(0,max_results,items_per_page):
        #build a URL with updated values for start-index (and others as wanted)
        url = 'http://worldcat.org/webservices/kb/rest/entries/search?' \
        'institution_id={}&start-index={}&max-results={}&itemsPerPage={}' \
        '&content={}&wskey={}'.format(institution,start_i,max_results,
                  items_per_page,content_type,wskey)
        q = requests.get(url,headers=headers_json)
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