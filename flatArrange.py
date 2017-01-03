# -*- coding: utf-8 -*-

import os
from lxml import etree as ET
import time
import shortuuid
import uuid
import shutil
import sys
import traceback
import csv

reload(sys)
sys.setdefaultencoding('UTF8')
print sys.getdefaultencoding()

workDir = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395"
inputDir = os.path.join(workDir, "flatBatches")
parser = ET.XMLParser(remove_blank_text=True)
arrangementList = []
titleList = ["NewPath", "Name", "Description", "Scope", "Date", "FileCount", "Path", "ID", "File"]
arrangementList.append(titleList)

albumCount = 0

jobNumberCount = 0
noNumberCount = 0

for metadataFile in os.listdir(inputDir):
	#print inputDir
	if metadataFile.endswith(".xml"):
		print metadataFile
		metaInput = ET.parse(os.path.join(inputDir, metadataFile), parser)
		meta = metaInput.getroot()
		
		
		for job in meta:
			if job.tag == "folder":
				
				albumCount = albumCount + 1
				
				if job.attrib["name"].isdigit() and job.attrib["name"].startswith("200"):
					jobNumberCount = jobNumberCount + 1
				else:
					noNumberCount = noNumberCount + 1
				
				jobList = [""]
				jobList.append(job.attrib["name"])
				jobList.append(job.find("description").text)
				jobList.append("") #scope
				if job.find("recordEvents/timestamp") is None:
					jobList.append("")
					print "no timestamp for " + job.attrib["name"]
				else:
					if job.find("recordEvents/timestamp").text is None:
						jobList.append("")
						print "no timestamp for " + job.attrib["name"]
					else:
						if "T" in job.find("recordEvents/timestamp").text:
							jobList.append(job.find("recordEvents/timestamp").text.split("T")[0].replace("-", ":"))
						else:
							jobList.append(job.find("recordEvents/timestamp").text.split(" ")[0].replace("-", ":"))
				fileCount = len(job.findall("file"))
				jobList.append(str(fileCount))
				jobList.append(job.find("path").text)
				jobList.append(job.find("id").text)
				jobList.append(metadataFile)
				
				uniList = []
				for asciiItem in jobList:
					uniList.append(asciiItem.encode(sys.getdefaultencoding()))
				
				arrangementList.append(uniList)
				

				
print str(albumCount) + " total albums"
print str(jobNumberCount) + " with job numbers"
print str(noNumberCount) + " without job numbers"

with open(os.path.join(workDir, "arrangmentDraft2.csv"), "wb") as f:
	writer = csv.writer(f, delimiter='|')
	writer.writerows(arrangementList)
	
	#writer.writerow([unicode(s).encode(getdefaultencoding()) for s in arrangementList])