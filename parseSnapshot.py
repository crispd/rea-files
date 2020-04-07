import sys
import csv
import re

dictfile = "ReA3_JENSA.lat"
snapshot_upstream = "EBIT-RFQentrance_Setpoints.snp"
snapshot_downstream = "RFQ-JENSA_Setpoints.snp"

with open(dictfile, 'r') as f1:
	dictfile = csv.DictReader(f1,fieldnames=['old','new'])
	
	with open(newfile, 'w') as outfile, open(oldfile) as infile:
		
		text = infile.read()		
		
		for ele in dictfile:
			old_str = ele['old']
			new_str = ele['new']
			print old_str, new_str
			txt = txt.replace(old_str, new_str)
			
		outfile.write(txt)