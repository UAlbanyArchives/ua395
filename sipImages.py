# coding: utf-8

import os
from lxml import etree as ET
import time
import shortuuid
import uuid
from PIL import Image
import exifread
import shutil
import sys
import traceback
from subprocess import Popen, PIPE

#from http://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes
suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
	if nbytes == 0: return '0 B'
	i = 0
	while nbytes >= 1024 and i < len(suffixes)-1:
		nbytes /= 1024.
        i += 1
	f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
	return '%s %s' % (f, suffixes[i])

noDateCount = 0

#batchDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/fromDVDs"
#batchDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/fromDVDs2"
#batchDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/fromDVDs3"
batchDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/fromDVDs4"
descDir = "/home/bcadmin/Desktop/Processing/ua395"
accessionDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/toSIP"

startTime = time.time()
startTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
print "Start Time: " + startTimeReadable


folderTotal = 0
for image in os.listdir(batchDir):
	folderTotal = folderTotal + 1

totalVerified = 0

diskStartTime = time.time()
totalTime = 0

parser = ET.XMLParser(remove_blank_text=True)
Order1Input = ET.parse(os.path.join(descDir, "OrderEntry.xml"), parser)
Order2Input = ET.parse(os.path.join(descDir, "OrderEntry2.xml"), parser)
OrderEntry = Order1Input.getroot()
OrderEntry2 = Order2Input.getroot()


#make SIP metadata file
collectionID = "ua395"
accessionNumber = collectionID + "-" + str(shortuuid.uuid())
sipRoot = ET.Element("accession")
sipRoot.set("version", "0.1")
sipRoot.set("number", accessionNumber)
submitTime = time.time()
submitTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
sipRoot.set("submitted", submitTimeReadable)
sipRoot.set("submittedPosix", str(submitTime))

#create profile
profileXML = ET.SubElement(sipRoot, "profile")
notesXML = ET.SubElement(profileXML, "notes")
notesXML.text = ""
creatorXML = ET.SubElement(profileXML, "creator")
creatorXML.text = "Digital Media Unit"
creatorIdXML = ET.SubElement(profileXML, "creatorId")
creatorIdXML.text = collectionID
donorXML = ET.SubElement(profileXML, "donor")
donorXML.text = "Mark Schmidt"
roleXML = ET.SubElement(profileXML, "role")
roleXML.text = "Campus Photographer"
emailXML = ET.SubElement(profileXML, "email")
emailXML.text = "pmiller2@albany.edu"
officeXML = ET.SubElement(profileXML, "office")
officeXML.text = "University Hall 202"
address1XML = ET.SubElement(profileXML, "address1")
address1XML.text = "1400 Washington Ave"
address2XML = ET.SubElement(profileXML, "address2")
address2XML.text = "Albany, NY 12222"
address3XML = ET.SubElement(profileXML, "address3")
address3XML.text = ""
methodXML = ET.SubElement(profileXML, "method")
methodXML.text = "Imaged from DVD and CD-R and extracted from raw files into JPGs with ImageMagick(https://github.com/UAlbanyArchives/ua395)"
locationXML = ET.SubElement(profileXML, "location")
locationXML.text = batchDir
extentXML = ET.SubElement(profileXML, "extent")

#create accession folder
accession = os.path.join(accessionDir, accessionNumber)
if not os.path.isdir(accession):
	os.mkdir(accession)
dataDir = os.path.join(accession, "data")
if not os.path.isdir(dataDir):
	os.mkdir(dataDir)
metadataString = ET.tostring(sipRoot, pretty_print=True, xml_declaration=True, encoding="utf-8")
metadataFile = open(os.path.join(accession, accessionNumber + ".xml"), "w")
metadataFile.write(metadataString)
metadataFile.close()



totalSize = 0
folderCount = 0
for folderName in os.listdir(batchDir):
	folderCount = folderCount + 1
	folderPath = os.path.join(batchDir, folderName)

	print "reading " + folderName

	print str(folderCount) + " of " + str(folderTotal)
	
	for job in os.listdir(folderPath):

		jobDir = os.path.join(folderPath, job)

		#special fix for incorrect job number for John Lewis photos
		if job == "20000935":
			job = "20001244"

		jobMove = os.path.join(dataDir, job)
		if not os.path.isdir(jobMove):
			os.mkdir(jobMove)
		
		jobRecord = ET.Element("folder")
		idXML = ET.SubElement(jobRecord, "id")
		idXML.text = str(uuid.uuid4())
		pathXML = ET.SubElement(jobRecord, "path")
		pathXML.text = os.path.join(folderPath, job)
		descriptionXML = ET.SubElement(jobRecord, "description")
		accessXML = ET.SubElement(jobRecord, "access")
		curatorialEventsXML = ET.SubElement(jobRecord, "curatorialEvents")
		eventXML = ET.SubElement(curatorialEventsXML, "event")
		eventXML.set("timestamp", str(time.time()))
		eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
		eventXML.text = "Imaged from optical media with dd, carved from image with fiwalk and icat, converted all raw to jpg"

		#special fix for John Lewis photos
		if job == "20001244":
			eventXML = ET.SubElement(curatorialEventsXML, "event")
			eventXML.set("timestamp", str(time.time()))
			eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
			eventXML.text = "Original job number incorrect, changed 20000935 to 20001244"
		
		recordEventsXML = ET.SubElement(jobRecord, "recordEvents")
		
		
		#if old job number
		if job.isdigit() and job.startswith("200"):
				
			for order in OrderEntry:
				if order.tag == "OrderEntry":
					if order.find("Job_x0020_Number").text == job:
						match = order
						
			if match is None:
				for order in OrderEntry2:
					if order.tag == "OrderEntry":
						if order.find("Job_x0020_Number").text == job:
							match = order
			
			if match is None:
				print "NO MATCH FOR: " + str(job)
				sys.exit("NO MATCH FOR: " + str(job))
			else:
				description = match.find("Description").text.replace("\n", " ")
				description = " ".join(description.split())
				if "photo session:" in description:
					description = description.replace("photo session:", "").strip()
					
				elif "photo session" in description:
					description = description.replace("photo session", "").strip()
				if not match.find("Department") is None and match.find("Department").text:
					departCheck = True
					depart = match.find("Department").text
				else:
					departCheck = False
				
				if "****" in description:
					description = description.split("****")[0]
						
			if match.find("DateDue") is None:
				if match.find("Date") is None:
					print "DATE ERROR______________________________________________"
				else:
					dbDate = match.find("Date").text
			else:
				dbDate = match.find("DateDue").text
			
			jobRecord.set("name", job)
			if departCheck == True:
				descriptionXML.text = depart + ": " + description.strip()
			else:
				descriptionXML.text = description.strip()
			timestamp = ET.Element("timestamp")
			timestamp.text = dbDate.replace("T", " ")
			timestamp.set("timeType", "iso8601")
			timestamp.set("parser", "Database Entry")
			recordEventsXML.append(timestamp)			
			eventXML = ET.SubElement(curatorialEventsXML, "event")
			eventXML.set("timestamp", str(time.time()))
			eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
			eventXML.text = "description record extracted from photographer's Microsoft Access database by Job number"				
				
									
		else:
			try:
				jobDesc = os.listdir(jobDir)[0]
			except:
				print "no subpath for " + job
				jobDesc = job
			jobRecord.set("name", jobDesc)
			descriptionXML.text = jobDesc
			eventXML = ET.SubElement(curatorialEventsXML, "event")
			eventXML.set("timestamp", str(time.time()))
			eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
			eventXML.text = "description record used original folder name"

			for rootDir, directs, images in os.walk(jobDir):
				imageCount = 0
				for image in images:
					if image.lower().endswith(".jpg"):
						imageCount = imageCount + 1
						if imageCount == 2:
							imageFile = os.path.join(rootDir, image)
			try:
				exifDate = Image.open(imageFile)._getexif()[36867]
				timestamp = ET.Element("timestamp")
				timestamp.text = exifDate
				timestamp.set("timeType", "iso8601")
				timestamp.set("parser", "EXIF")
				recordEventsXML.append(timestamp)
			except:
				try:
					exifDate = Image.open(imageFile)._getexif()[306]
					timestamp = ET.Element("timestamp")
					timestamp.text = exifDate
					timestamp.set("timeType", "iso8601")
					timestamp.set("parser", "EXIF")
					recordEventsXML.append(timestamp)
				except:
					continue

		for root, dirs, files in os.walk(jobDir):
			for file in files:
				fileCheck = file.lower()
				if fileCheck == "thumbs.db" or fileCheck == "desktop.ini" or fileCheck == ".ds_store":
					pass
				else:
					filePath = os.path.join(root, file).decode(sys.getdefaultencoding())
					fileSize = os.path.getsize(filePath)
					if fileSize > 0:
						totalSize = totalSize + fileSize
						
						imageRecord = ET.Element("file")
						imageRecord.set("name", file)
						idXML = ET.SubElement(imageRecord, "id")
						idXML.text = str(uuid.uuid4())
						pathXML = ET.SubElement(imageRecord, "path")
						pathXML.text = filePath
						descriptionXML = ET.SubElement(imageRecord, "description")
						accessXML = ET.SubElement(imageRecord, "access")
						curatorialEventsXML = ET.SubElement(imageRecord, "curatorialEvents")
						eventXML = ET.SubElement(curatorialEventsXML, "event")
						eventXML.set("timestamp", str(time.time()))
						eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
						eventXML.text = "Imaged from optical media with dd, carved from image with fiwalk and icat, converted all raw to jpg"
						recordEventsXML = ET.SubElement(imageRecord, "recordEvents")

						try:
							exifImage = Image.open(filePath)
							exifDate = exifImage._getexif()[36867]
							timestamp = ET.Element("timestamp")
							timestamp.text = exifDate
							timestamp.set("timeType", "iso8601")
							timestamp.set("parser", "EXIF.DateTimeOriginal")
							recordEventsXML.append(timestamp)
						except:
							try:
								exifImage = Image.open(filePath)
								exifDate = exifImage._getexif()[306]
								timestamp = ET.Element("timestamp")
								timestamp.text = exifDate
								timestamp.set("timeType", "iso8601")
								timestamp.set("parser", "EXIF.DateTime")
								recordEventsXML.append(timestamp)
							except:
								noDateCount = noDateCount + 1
								pass
							
						jobRecord.append(imageRecord)
						
						if os.path.isfile(os.path.join(jobMove, file)):						
							def dupfileConflict(file, dupNumber, jobMove):
								fileRoot, fileExt = os.path.splitext(file)
								dupFile = fileRoot + "[" + str(dupNumber) + "]" + "." + fileExt
								if os.path.isfile(os.path.join(jobMove, dupFile)):
									dupNumber = dupNumber + 1
									print "<----------------- More than 2"
									dupNumber = dupfileConflict(file, dupNumber, jobMove)
								else:
									return dupNumber

							dupNumber = 2
							dupNumber = dupfileConflict(file, dupNumber, jobMove)
							fileRoot, fileExt = os.path.splitext(file)
							dupFile = fileRoot + "[" + str(dupNumber) + "]" + fileExt
							print dupFile
							try:
								jobMove = os.path.join(jobMove, dupFile)
							except:
								print jobMove
								print file
								print dupFile
								sys.exit("MOVE ERROR: \"" + jobMove + "\" --> \"" + dupFile + "\"")
							eventXML = ET.SubElement(curatorialEventsXML, "event")
							eventXML.set("timestamp", str(time.time()))
							eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
							eventXML.text = "File with same name already present, original files may have been in different directories. Renamed " + file + " to " + dupFile + "."
							
						if os.name == "nt":
							try:
								shutil.copy2(filePath, jobMove)
							except:
								sys.exit("shutil.copy2() ERROR: shutil.copy2(\"" + filePath + "\", \"" + jobMove + "\")")
						else:
							try:
								moveCmd = "cp -p \"" + filePath + "\" \"" + jobMove + "\""
								moveFile = Popen(moveCmd, shell=True, stdout=PIPE, stderr=PIPE)
								stdout, stderr = moveFile.communicate()
								if len(stderr) > 0:
									print stderr
									sys.exit("Unix cp -p error: " + stderr)
								if len(stdout) > 0:
									sys.exit("Unix cp -p output: " + stdout)
							except:
								sys.exit("cp COMMAND ERROR: " + moveCmd)

					else:
						print "NO FILE SIZE FOR " + filePath
						eventXML = ET.SubElement(curatorialEventsXML, "event")
						eventXML.set("timestamp", str(time.time()))
						eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
						eventXML.text = filePath + " may have been corrupted. icat resulted in file with no size, so file was ignored."
				
		sipRoot.append(jobRecord)

		metadataString = ET.tostring(sipRoot, pretty_print=True, xml_declaration=True, encoding="utf-8")
		metadataFile = open(os.path.join(accession, accessionNumber + ".xml"), "w")
		metadataFile.write(metadataString)
		metadataFile.close()				
	
	
	
	
	
	diskProcessTime = time.time() - diskStartTime
	totalTime = totalTime + diskProcessTime
	print "Process took " + str(diskProcessTime) + " seconds or " + str(diskProcessTime/60) + " minutes or " + str(diskProcessTime/3600) + " hours"
	avgTime = totalTime/folderCount
	print "Average is " + str(avgTime)
	remaning = folderTotal - folderCount
	print str(remaning) + " Remaining"
	estimateTime = avgTime*remaning
	print "Estimated time left: " + str(estimateTime) + " seconds or " + str(estimateTime/60) + " minutes or " + str(estimateTime/3600) + " hours"
	diskStartTime = time.time()
		
readableSize = humansize(totalSize)
sipRoot.find("profile/extent").set("unit", "bytes")
sipRoot.find("profile/extent").text = str(totalSize)
sipRoot.find("profile/extent").set("humanReadable", str(readableSize))
metadataString = ET.tostring(sipRoot, pretty_print=True, xml_declaration=True, encoding="utf-8")
metadataFile = open(os.path.join(accession, accessionNumber + ".xml"), "w")
metadataFile.write(metadataString)
metadataFile.close()
print str(noDateCount) + " unable to get dates"
		