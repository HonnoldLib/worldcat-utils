# worldcat-utils
Utility scripts for using Worldcat APIs

## search_wc_kb 

Use the OCLC Worldcat Knowledgebase API to access information about print and 
electronic resources.

Usage: %prog inputfile outputfile

## wc_get_workid_rdf-style 

Provide a file of oclc numbers or workids as the first parameter and a 
filename to receive results as a second parameter. 

Results will be the workids associated with the oclcnumbers

Usage: %prog [inputfile] [outputfile] [logfile]]]

## References:
[Collection Resource](https://www.oclc.org/developer/develop/web-services/worldcat-knowledge-base-api/collection-resource.en.html)

[Entry Resource](https://www.oclc.org/developer/develop/web-services/worldcat-knowledge-base-api/entry-resource.en.html)