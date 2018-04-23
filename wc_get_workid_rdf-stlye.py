#! /usr/bin/env python
import csv
import sys
import requests
from rdflib import Graph, URIRef, Literal, BNode

# retrieving data from the linked data...thing. API?
url_stub_oclcnum = 'http://www.worldcat.org/oclc/' # API URL for oclcnum
url_stub_workid = 'http://worldcat.org/entity/work/id/' # API URL for workid
rdf_data_format = 'application/rdf+xml'
json_data_format = 'application/ld+json'
headers_json = {'Accept' : json_data_format} # a default format for the OCLC data
headers_rdf = {'Accept': rdf_data_format}
pred_workid = URIRef(u'http://schema.org/exampleOfWork')
pred_oclcnum = URIRef(u'http://schema.org/workExample')
pred_format = URIRef('http://schema.org/bookFormat')


""" 
Usage: provide a file of oclc numbers or workids as the first parameter and a 
filename to receive results as a second parameter. 
Results will be the workids associated with the oclcnumbers
%prog [inputfile] [outputfile]]
"""

class codesList:
    """Accept a plaintext file, return a list of the lines stripped of leading 
    or trailing whitespace """
    def __init__(self, fh):
        self.codeFile = fh
    def listed(self):
        lines=[]
        for line in self.codeFile.readlines():
            lines.append(line.strip())
        return lines

def get_DOM(query_url, headers):
    """Accept a URL, retrieve the contents at the URL, return the values. """
    #to do: 
    q = requests.get(query_url, headers=headers)
    dom = q.text
    return dom

def get_work_IDs(lCodes):
    """Accept a list of item (oclcnum) codes, loop through the list,
    search Worldcat, return workids. """
    work_ids = []
    #Get the workids
    for oclcSym in lCodes:
        uri = url_stub_oclcnum+oclcSym
        rdf_triple_data = get_DOM(uri,headers_rdf)
        graph = Graph()
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for oclcnum, workid in graph.subject_objects(pred_workid):
                print(oclcnum.split('/')[-1],workid.split('/')[-1])
                work_ids.append(workid.split('/')[-1])
        except TypeError as te:
            print("TypeError ",uri, te)
            print(rdf_triple_data)
    return work_ids

def getOCLC_ISBN_Nums(workids):
    """Loop through workids, get oclcnums
    Loop through oclcnums, look for ebook bookFormat"""
    oclc_nums = []
    for workid in workids:
        uri = url_stub_workid+workid
        print(uri)
        rdf_triple_data = get_DOM(uri,headers_rdf)
        
        #print(rdf_triple_data)
        graph = Graph()
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for oclcnum, isbn in graph.subject_objects(pred_oclcnum):
                #print(oclcnum.split('/')[-1], isbn.split('/')[-1])
                oclc_nums.append([oclcnum.split('/')[-1], isbn.split('/')[-1]])
        except:
            print('error')
    return oclc_nums        
        
if __name__ == "__main__":
    fileIn = sys.argv[1]
    fileOut = sys.argv[2]    
    lCodes=[]
    with open(fileIn, 'r') as f_oclc_nums, open(fileOut, 'w', newline='') as \
    f_out:
        csv_writer = csv.writer(f_out)
        oList = codesList(f_oclc_nums) #read all the OCLC numbers into a list
        lCodes = oList.listed()
        workids = get_work_IDs(lCodes)
        oclcnums = getOCLC_ISBN_Nums(workids)
        print('OCLC Numbers:\n',oclcnums)
        #csv_writer.writerows(results)
        #print(results)
        #write results to a csv(?) file

