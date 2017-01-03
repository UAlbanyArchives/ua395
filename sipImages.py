# coding: utf-8

import os
from lxml import etree as ET
import time
import shortuuid
import uuid
from PIL import Image
import shutil
import sys
import traceback

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

if os.name == "nt":
	#imageDir = "C:\\Projects\\sipImages"
	imageDir = "\\\\romeo\\SPE\\Electronic_Records_Library\\ua395\\fromDVDs4"
	#baseDir = "C:\\Projects\\sipImages"
	baseDir = "\\\\romeo\\SPE\\Electronic_Records_Library\\ua395"
	descDir = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395"
else:
	imageDir = ""
	baseDir = ""
	

startTime = time.time()
startTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
print "Start Time: " + startTimeReadable


count = 0
totalVerified = 0
totalImageCount = len(os.listdir(imageDir))
diskStartTime = time.time()
totalTime = 0

parser = ET.XMLParser(remove_blank_text=True)
Order1Input = ET.parse(os.path.join(descDir, "OrderEntry.xml"), parser)
Order2Input = ET.parse(os.path.join(descDir, "OrderEntry2.xml"), parser)
OrderEntry = Order1Input.getroot()
OrderEntry2 = Order2Input.getroot()

workingDir = os.path.join(baseDir, "dvd_batch4")
if not os.path.isdir(workingDir):
	os.mkdir(workingDir)
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
methodXML.text = "Imaged from DVD and CD-R and extracted from raw files into JPGs (https://github.com/UAlbanyArchives/ua395)"
locationXML = ET.SubElement(profileXML, "location")
locationXML.text = baseDir
extentXML = ET.SubElement(profileXML, "extent")




totalSize = 0
for diskImage in os.listdir(imageDir):
	#for limiting images for testing purposes
	count = count + 1
	#if count > 0:
	if not os.path.isdir(os.path.join(imageDir, diskImage)):
		pass
	elif diskImage == "dvd_batch4":
		pass
	else:
		print "reading " + diskImage
		print str(count) + " of " + str(totalImageCount)
		
		for job in os.listdir(os.path.join(imageDir, diskImage)):
			jobDir = os.path.join(workingDir, job)
			if not os.path.isdir(jobDir):
				os.mkdir(jobDir)
			
			jobRecord = ET.Element("folder")
			idXML = ET.SubElement(jobRecord, "id")
			idXML.text = str(uuid.uuid4())
			pathXML = ET.SubElement(jobRecord, "path")
			pathXML.text = os.path.join(imageDir, diskImage, job)
			descriptionXML = ET.SubElement(jobRecord, "description")
			accessXML = ET.SubElement(jobRecord, "access")
			curatorialEventsXML = ET.SubElement(jobRecord, "curatorialEvents")
			eventXML = ET.SubElement(curatorialEventsXML, "event")
			eventXML.set("timestamp", str(time.time()))
			eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
			eventXML.text = "Imaged from optical media with dd, carved from image with fiwalk and icat, converted all raw to jpg"
			recordEventsXML = ET.SubElement(jobRecord, "recordEvents")
			
			
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
				"""
				print "Job error: " + str(job)
				with open("jobError.txt", "a") as f:
					f.write( "\n\n*******************************\nJob error: " + str(job) + "\nDisk: " + diskImage)
					f.close()
				"""
				try:
					jobDesc = os.listdir(os.path.join(imageDir, diskImage, job))[0]
				except:
					print "no subpath for " + job
					jobDesc = job
				jobRecord.set("name", jobDesc)
				descriptionXML.text = jobDesc
				eventXML = ET.SubElement(curatorialEventsXML, "event")
				eventXML.set("timestamp", str(time.time()))
				eventXML.set("timestampHuman", str(time.strftime("%Y-%m-%d %H:%M:%S")))
				eventXML.text = "description record used original folder name"
				jobDirect = os.path.join(imageDir, diskImage, job)
				for rootDir, directs, images in os.walk(jobDirect):
					imageCount =0
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
					
			for root, dirs, files in os.walk(os.path.join(imageDir, diskImage, job)):
				for file in files:
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
						except:
							print "open fail"
						try:
							exifDate = exifImage._getexif()[36867]
							timestamp = ET.Element("timestamp")
							timestamp.text = exifDate
							timestamp.set("timeType", "iso8601")
							timestamp.set("parser", "EXIF.DateTimeOriginal")
							recordEventsXML.append(timestamp)
						except:
							try:
								exifDate = exifImage._getexif()[306]
								timestamp = ET.Element("timestamp")
								timestamp.text = exifDate
								timestamp.set("timeType", "iso8601")
								timestamp.set("parser", "EXIF.DateTime")
								recordEventsXML.append(timestamp)
							except:
								noDateCount = noDateCount + 1
								continue
								
							
						jobRecord.append(imageRecord)
						
						if os.path.isfile(os.path.join(jobDir, file)):
							pass
						else:
							shutil.copy2(os.path.join(root, file), jobDir)
					
			sipRoot.append(jobRecord)

				
		
		
		
		
		
		diskProcessTime = time.time() - diskStartTime
		totalTime = totalTime + diskProcessTime
		print "Process took " + str(diskProcessTime) + " seconds or " + str(diskProcessTime/60) + " minutes or " + str(diskProcessTime/3600) + " hours"
		avgTime = totalTime/count
		print "Average is " + str(avgTime)
		remaning = totalImageCount-count
		print str(remaning) + " Remaining"
		estimateTime = avgTime*remaning
		print "Estimated time left: " + str(estimateTime) + " seconds or " + str(estimateTime/60) + " minutes or " + str(estimateTime/3600) + " hours"
		diskStartTime = time.time()
		
readableSize = humansize(totalSize)
sipRoot.find("profile/extent").set("unit", "bytes")
sipRoot.find("profile/extent").text = str(totalSize)
sipRoot.find("profile/extent").set("humanReadable", str(readableSize))
metadataString = ET.tostring(sipRoot, pretty_print=True, xml_declaration=True, encoding="utf-8")
metadataFile = open(os.path.join(baseDir, accessionNumber + ".xml"), "w")
metadataFile.write(metadataString)
metadataFile.close()
print noDateCount
		