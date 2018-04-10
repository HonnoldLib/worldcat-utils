#! /usr/bin/env python

import sys
import requests
import csv
import json

urlStub = "http://www.worldcat.org/oclc/"
headers = {"Accept":"application/ld+json"}

doc=""" 
Usage: provide a file of oclc numbers as the first parameter and a filename to receive results as a second parameter. 
Results will be the workids associated withthe oclcnumbers
%prog [inputfile] [outputfile]]
"""

class codesList:
    def __init__(self, fh):
        self.codeFile = fh
    def listed(self):
        lines=[]
        for line in self.codeFile.readlines():
            lines.append(line.strip())
        return lines
    
def look_up_OCLCNum(query_url):
    q = requests.get(query_url, headers=headers) 
    dom = q.text
    return True, dom

def search(lCodes):
    #loop through the list of book codes, search WC, write results to output file
    for oclcSym in lCodes:
        found = False
        print('code: ',oclcSym)
        #query = urlStub+oclcSym+'?wskey='+wsKey+"&oclcsymbol="+urllib.quote(libs)
        query = urlStub+oclcSym
        #print query,        
        found, dom = look_up_OCLCNum(query)
        if found:
            try:
                graph = json.loads(dom)['@graph']
                for key in graph:
                    try:
                        print(key['@type'], '\n\t',key['@id'])
                    except NoneType:
                        print('no type?')
            except NameError:
                print("can't deal with these data: ", dom)
                #raise
        else:
            print('{},{}').format(str(oclcSym), " lookup failed.")

if __name__ == "__main__":
    fileIn = sys.argv[1]
    fileOut = sys.argv[2]    
    lCodes=[]
    with open(fileIn, 'r') as f_oclc_nums, open(fileOut, 'wb') as work_ids:
        oList = codesList(f_oclc_nums) #read all the OCLC numbers into a list
        lCodes = oList.listed()
        results = search(lCodes)
        print(results)
        #write results to a csv(?) file

