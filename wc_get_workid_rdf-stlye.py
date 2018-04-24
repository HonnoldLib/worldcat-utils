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
pred_ebook_format = URIRef(u'http://schema.org/EBook')


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
    print('Retrieving OCLC workids')
    work_ids = []
    #Get the workids
    for oclcSym in lCodes:
        uri = url_stub_oclcnum+oclcSym
        rdf_triple_data = get_DOM(uri,headers_rdf)
        graph = Graph()
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for oclcnum, workid in graph.subject_objects(pred_workid):
                #print(oclcnum.split('/')[-1],workid.split('/')[-1])
                work_ids.append(workid.split('/')[-1])
        except TypeError as te:
            print("TypeError ",uri, te)
            print(rdf_triple_data)
    return work_ids

def get_OCLC_Nums(workids):
    """Loop through workids, get oclcnums """
    print('Retrieving OCLC Numbers')
    oclc_nums = {}
    graph = Graph()
    for workid in workids:
        uri = url_stub_workid+workid
        rdf_triple_data = get_DOM(uri,headers_rdf)
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for workid, oclcnum in graph.subject_objects(pred_oclcnum):
                workid = workid.split('/')[-1]
                oclcnum = oclcnum.split('/')[-1]
                #add them to a dictionary to de-dupe
                oclc_nums[oclcnum] = workid
        except:
            print('error')
    return oclc_nums        

def get_eBook_status(wk_id_ocn_pairs,log_file):
    """Loop through oclcnums dictionary, look for ebook bookFormat"""
    print('Retrieving ebook OCLC numbers')
    ebook_ocns = {}
    graph = Graph()
    for oclcnum, workid in wk_id_ocn_pairs.items():#Dictionary of key: oclcnum, value: workid
        uri = url_stub_oclcnum+oclcnum
        rdf_triple_data = get_DOM(uri,headers_rdf)
        #log_rdf_data(log_file, rdf_triple_data)
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for subj, pred in graph.subject_predicates(pred_ebook_format):
                ocn = subj.split('/')[-1]
                #add them to a dictionary to de-dupe
                ebook_ocns[ocn] = workid
        except AttributeError as e:
            #e = sys.exc_info()[0]
            print('Error: %s' %e)
    return ebook_ocns

def log_rdf_data(file_handle, rdf_data):
        """A generic file writer for logging generic data (debugging)"""
        with open(file_handle,'a') as fo:
            fo.writelines(rdf_data)
    
if __name__ == "__main__":
    fileIn = sys.argv[1] # the input data
    fileOut = sys.argv[2]# for the output
    rdf_test_out = sys.argv[3] # a file to stash debugging (rdf) data
    lCodes=[]
    with open(fileIn, 'r') as f_oclc_nums, open(fileOut, 'w', newline='') as \
    f_out:
        csv_writer = csv.writer(f_out)
        oList = codesList(f_oclc_nums) # read all the OCLC numbers into a list
        lCodes = oList.listed()
        workids = get_work_IDs(lCodes) # get the workid associated with each oclcnum
        oclcnums = get_OCLC_Nums(workids) # get the oclc numbers associated with workids
        oclcnum_ebooks = get_eBook_status(oclcnums,rdf_test_out)  # get the oclc numbers of ebooks
        csv_writer.writerows(oclcnum_ebooks.items())  # write ebook oclc numbers to a csv file
        print('The End')

