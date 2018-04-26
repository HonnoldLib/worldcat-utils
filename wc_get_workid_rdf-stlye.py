#! /usr/bin/env python
import csv
import sys
import requests
from rdflib import Graph, URIRef

# retrieving data from the linked data...thing. API?
url_stub_oclcnum = 'http://www.worldcat.org/oclc/' # API URL for oclcnum
url_stub_isbn = 'http://worldcat.org/isbn/'
url_stub_workid = 'http://worldcat.org/entity/work/id/' # API URL for workid

# result formats for ease of use
rdf_data_format = 'application/rdf+xml'
json_data_format = 'application/ld+json'
# request headers for ease of use
headers_json = {'Accept' : json_data_format} # a default format for the OCLC data
headers_rdf = {'Accept': rdf_data_format}
# some subject/predicate/objects for ease of use
pred_workid = URIRef(u'http://schema.org/exampleOfWork')
pred_workExample = URIRef(u'http://schema.org/workExample')
pred_bookFormat = URIRef(u'http://schema.org/bookFormat')
obj_ebook = URIRef(u'http://schema.org/EBook')

""" 
Usage: provide a file of oclc numbers or workids as the first parameter and a 
filename to receive results as a second parameter. 
Results will be the workids associated with the oclcnumbers
%prog [inputfile] [outputfile] [logfile]]]
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

def print_status(numcodes, totalNum, msg): #progress indicator
    """status printing utility for long-running scripts"""
    print('Record: {} / {} {:>20}\r'.format(numcodes, totalNum, msg), end='\r'),
    sys.stdout.flush() 
    
def get_DOM(query_url, headers):
    """Accept a URL, retrieve the contents at the URL, return the values. """
    #to do: 
    q = requests.get(query_url, headers=headers)
    dom = q.text
    return dom

def get_work_IDs(ocns):
    """Accept a list of item (oclcnum) codes, loop through the list,
    search Worldcat, return workids. """
    print('Retrieving OCLC workids')
    work_ids = {}
    #Get the workids
    for oclc_sym in ocns:
        uri = url_stub_oclcnum+oclc_sym
        rdf_triple_data = get_DOM(uri,headers_rdf)
        graph = Graph()
        try: 
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for oclcnum, workid in graph.subject_objects(pred_workid):
                work_ids[oclc_sym]=workid.split('/')[-1]
        except TypeError as te: #occasionally saw this error.
            print("TypeError ",uri, te)
            print(rdf_triple_data)
    return work_ids

def get_OCLC_Nums(workids):
    """Loop through workids list, return a dictionary of {oclcnum:workid} """
    print('Retrieving OCLC Numbers for Work')
    oclc_nums = {}
    graph = Graph()
    for workid in workids.values():
        uri = url_stub_workid + workid
        rdf_triple_data = get_DOM(uri,headers_rdf)
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)
            for wid, ocn in graph.subject_objects(pred_workExample):
                w = wid.split('/')[-1]# take just the workid off the uri
                o = ocn.split('/')[-1] # take just the ocn off the uri
                #add them to a dictionary to de-dupe
                oclc_nums[o] = w
                #print(oclcnum, oclc_nums[oclcnum])
        except:
            e = sys.exc_info()[0]
            print('Error: %s' %e)
    return oclc_nums        

def get_bookFormat(wk_id_ocn_pairs,log_file=None):
    """Loop through oclcnums dictionary, look for bookFormat"""
    print('Retrieving ebook workExample numbers')
    ebook_ocns = {}
    graph = Graph()
    num_ids = len(wk_id_ocn_pairs)
    for i, oclc_num in enumerate(wk_id_ocn_pairs.keys()):#Dictionary of key: oclcnum, value: workid
        print_status(i,num_ids,oclc_num) # give a progress status
        uri = url_stub_oclcnum+oclc_num
        rdf_triple_data = get_DOM(uri,headers_rdf)
        try:
            graph.parse(data=rdf_triple_data, format=rdf_data_format)                
            for subj, pred, obj in graph.triples((None,pred_bookFormat,None)):
                s= subj.split('/')[-1]
                o= obj.split('/')[-1]
                ebook_ocns[s]=[o,wk_id_ocn_pairs[s]]

        except:
            e = sys.exc_info()[0]
            print('Error: %s' %e)
    return ebook_ocns

def log_data(file_handle, rdf_data):
        """A generic file writer for logging generic data (debugging)"""
        with open(file_handle,'a') as fo:
            fo.writelines(rdf_data)

def pretty_print_graph(file_handle, graph):
    """print rdf graph to a human readable file for convenience/debugging""" 
    with open(file_handle, 'a') as fh:
        for subj, pred, obj in graph: 
            t= 's: ' + subj + '\np: ' + pred + '\no: ' + obj+ '\n\n'
            fh.write(t)
    
def write_csv_file(field_names,file_handle, dict_data):
    """A generic csv file writer for logging dictionary data"""
    with open(file_handle,'w', newline='') as fo:
        writer = csv.writer(fo, delimiter='|')
        writer.writerow(field_names)
        for key in dict_data:
            try:
                if isinstance(dict_data[key],str):#is the value a string?
                    writer.writerow([key,dict_data[key]])
                else:
                    writer.writerow([key,*dict_data[key]])# if not, it's probably a list                    
            except: 
                e = sys.exc_info()[0]
                print('Error: %s' %e)


if __name__ == "__main__":
    file_in = sys.argv[1] # the input data
    file_out = sys.argv[2]# for the output
    rdf_test_out = sys.argv[3] # a file to stash debugging (rdf) data
    ocns=[]
    with open(file_in, 'r') as f_oclc_nums:
        oList = codesList(f_oclc_nums) # read all the OCLC numbers into a list
        ocns = oList.listed()
        workids = get_work_IDs(ocns) # get the workid associated with each oclcnum
        write_csv_file(['ocn','workid'],'source_ocn_workid.csv',workids)
        oclc_nums = get_OCLC_Nums(workids) # get the oclc numbers associated with workids
        print('Found %s items' % len(oclc_nums))
        write_csv_file(['ocn','workid'],'oclc_nums_workids.csv', oclc_nums)
        oclcnum_ebooks = get_bookFormat(oclc_nums,rdf_test_out)  # get the oclc numbers of ebooks
        write_csv_file(['ocn','bookFormat','workid'],file_out, oclcnum_ebooks)  # write ebook oclc numbers to a csv file
        print('The End')

