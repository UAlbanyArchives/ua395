# coding: utf-8

import os
from lxml import etree as ET
import time
import shortuuid
import uuid
import shutil
import sys
import traceback
import csv
import urllib
from subprocess import Popen, PIPE
from PIL import Image

from archives_tools import dacs


bagDir = os.path.dirname(os.path.realpath(__file__))
processingDir = os.path.dirname(os.path.realpath(__file__))
eadFile = os.path.join(processingDir, "ua395-frame.xml")

if os.name == "nt":
	templateFile = "\\\\romeo\\wwwroot\\eresources\\digital_objects\\ua395\\template.html"
	sipDir = "\\\\LINCOLN\\Masters\\Special Collections\\accessions\\SIP"
	dipDir = "\\\\romeo\\wwwroot\\eresources\\digital_objects\\ua395"
else:
	templateFile = "/media/bcadmin/wwwroot/eresources/digital_objects/ua395/template.html"
	sipDir = "/media/bcadmin/Lincoln/Special Collections/accessions/SIP"
	dipDir = "/media/bcadmin/wwwroot/eresources/digital_objects/ua395"
	
print sys.getfilesystemencoding()

startTime = time.time()
startTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
print "Start Time: " + startTimeReadable

#from http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
	for unit in ['','-K','-M','-G','-T','-P','-E','-Z']:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, 'Yi', suffix)
		
def makeNewCmpnt(newSeries, folder):
	#print folder.attrib["name"]
	firstDate = "3000-12-25"
	lastDate = "1900-01-01"
	did = newSeries.find("did")
	unittitle = did.find("unittitle")
	if not folder.find("description/unittitle") is None and folder.find("description/unittitle").text:
		unittitle.text = folder.find("description/unittitle").text
		if not folder.find("description/scopecontent") is None and folder.find("description/scopecontent").text:
			scopecontent = ET.SubElement(newSeries, "scopecontent")
			scopecontent.text = folder.find("description/scopecontent").text
	elif not folder.find("description/scopecontent") is None and folder.find("description/scopecontent").text:
		unittitle.text = folder.find("description/scopecontent").text
	else:
		unittitle.text = folder.attrib["name"].replace("-", " ")
	if not folder.find("description/controlaccess") is None and folder.find("description/controlaccess").text:
		controlaccess = ET.SubElement(newSeries, "controlaccess")
		for subjectHead in folder.find("description/controlaccess").text.split(";"):
			newSubject = ET.SubElement(controlaccess, "subject")
			newSubject.text = subjectHead.strip()
	if not folder.find("file/curatorialEvents/event") is None:
		acqinfo = ET.SubElement(newSeries, "acqinfo")
		for event in folder.find("file/curatorialEvents"):
			pElement = ET.SubElement(acqinfo, "p")
			if "T" in event.attrib["humanTime"]:
				eventTime = event.attrib["humanTime"].split("T")[0]
			else:
				eventTime = event.attrib["humanTime"].split(" ")[0]	
			dateElement = ET.SubElement(pElement, "date")
			dateElement.set("normal", eventTime)
			dateElement.text = dacs.iso2DACS(eventTime)
			dateElement.tail = event.text
	if len(folder.find("recordEvents").findall("timestamp")) > 0:
		for recordEvent in folder.find("recordEvents"):
			unitdate = ET.SubElement(did, "unitdate")
			if "T" in recordEvent.text:
				normalDate = recordEvent.text.split("T")[0]
			else:
				normalDate = recordEvent.text.split(" ")[0]
			unitdate.set("normal", normalDate)
			if recordEvent.attrib["parser"] == "SmugMug":
				unitdate.set("label", "SmugMug API last updated date")
			unitdate.text = dacs.iso2DACS(normalDate)
	else:
		dateCheck = False
		for timestamps in folder.xpath(".//timestamp"):
			if timestamps.text.startswith("0000"):
				pass
			else:
				dateCheck = True
				if "T" in timestamps.text:
					normalDate = timestamps.text.split("T")[0]
				else:
					normalDate = timestamps.text.split(" ")[0]
				normalDate = normalDate.replace(":", "-")
				if normalDate > lastDate:
					lastDate = normalDate
				if normalDate < firstDate:
					firstDate = normalDate
		if dateCheck == True:
			unitdate = ET.SubElement(did, "unitdate")
			unitdate.set("normal", firstDate + "/" + lastDate)
			unitdate.text = dacs.iso2DACS(firstDate + "/" + lastDate)
	fileCount = len(folder.findall("file"))
	if fileCount > 0:
		physdesc = ET.SubElement(did, "physdesc")
		dimensions = ET.SubElement(physdesc, "dimensions")
		dimensions.text = str(fileCount)
		dimensions.set("unit", "Digital Files")
	else:
		fileCount = len(folder.xpath(".//file"))
		if fileCount > 0:
			physdesc = ET.SubElement(did, "physdesc")
			dimensions = ET.SubElement(physdesc, "dimensions")
			dimensions.text = str(fileCount)
			dimensions.set("unit", "Digital Files")
	return newSeries
	
def getPath(folder, pathList):
	if folder.getparent().tag == "folder":
		if not folder.getparent().attrib["name"] == "ualbanyphotos":
			pathList.append(folder.getparent().attrib["name"].replace("-", " "))
		getPath(folder.getparent(), pathList)
	return pathList
	
def makeGallery(sipDir, dipDir, accessionNumber, metaRecord, unitId, cmpnt, templateFile, metaID):	
	reload(sys)
	sys.setdefaultencoding('mbcs')
	
	parser = ET.XMLParser(remove_blank_text=True)
	templateInput = ET.parse(templateFile, parser)
	template = templateInput.getroot()

	for dir in os.listdir(sipDir):
		if dir == accessionNumber:
			sip = dir
	if os.name == "nt":
		path = metaRecord.find("path").text.replace("/", "\\").replace("-\\", "\\")
	else:
		path = metaRecord.find("path").text.replace("-\\", "\\")
	if path.endswith("-"):
		path = path[:-1]
	pathSip = os.path.join(sipDir, sip, "data", "ualbanyphotos")
	folderSip = os.path.join(pathSip, path)
	folderThumbs = os.path.join(folderSip, "thumbs")
	dipId = unitId.split("-")[1].split("_")[0]
	folderDip = os.path.join(dipDir, dipId)
	if not os.path.isdir(folderDip):
		os.mkdir(folderDip)
	
	div = template.find(".//div[@id='dynamicContent']")
	for button in div.getparent().find("div/div"):
		if button.tag == "a":
			if button.attrib["id"] == "cmpntLink":
				button[1].text = " " + cmpnt.getparent().find("did/unittitle").text + " "
				oldLink = button.attrib["href"]
				newLink = "nam_" + unitId.split("_")[1]
				button.set("href", oldLink + newLink)
	try:
		if newLink.count('.') > 1:
			newLink = newLink.split(".")[0] + "." + newLink.split(".")[1]
		newLink = oldLink + newLink.replace(".", "-")
		subLink = template.find(".//li/a[@href='" + newLink + "']").getparent()
		subLink.set("class", "list-group-item active")
		topLink = subLink.getparent().getprevious()
		topLink.set("class", "list-group-item active")
	except:
		pass
	
	#previousarrow
	if not cmpnt.getprevious() is None:
		if cmpnt.getprevious().tag == cmpnt.tag:
			a = ET.SubElement(div, "a")
			a.set("class", "leftRight pull-left")
			a.set("href", cmpnt.getprevious().attrib["id"] + ".html")
			span = ET.SubElement(a, "span")
			span.set("class", "glyphicon glyphicon-arrow-left")
	#next arrow
	a = ET.SubElement(div, "a")
	a.set("class", "leftRight pull-right")
	nextID = "nam_" + cmpnt.attrib["id"].split("_")[1] + "_" + str(int(cmpnt.attrib["id"].split("_")[2]) + 1)
	a.set("href", nextID + ".html")
	span = ET.SubElement(a, "span")
	span.set("class", "glyphicon glyphicon-arrow-right")
	pageHeader = ET.SubElement(div, "div")
	pageHeader.set("class", "page-header text-center")
	h2 = ET.SubElement(pageHeader, "h2")
	h2.set("itemprop", "name")
	h2.text = cmpnt.find("did/unittitle").text
	
	colMd = ET.SubElement(div, "div")
	colMd.set("class", "col-md-12")
	colMd2 = ET.SubElement(colMd, "div")
	colMd2.set("class", "col-md-10")
	if not cmpnt.find("scopecontent") is None:
		if not cmpnt.find("scopecontent") is None:
			pElement = ET.SubElement(colMd2, "p")
			pElement.set("itemprop", "description")
			pElement.text = cmpnt.find("scopecontent").text
	if not cmpnt.find("acqinfo/p") is None:
		panel = ET.SubElement(colMd2, "div")
		panel.set("class", "panel panel-default")
		panelHeading = ET.SubElement(panel, "div")
		panelHeading.set("class", "panel-heading")
		panelHeading.set("data-toggle", "collapse")
		panelHeading.set("href", "#collapse1")
		h4 = ET.SubElement(panelHeading, "h4")
		h4.set("class", "panel-title")
		h4A = ET.SubElement(h4, "a")
		plusMinus = ET.SubElement(h4A, "span")
		plusMinus.set("class", "glyphicon glyphicon-plus")
		plusMinus.tail = " Processing Details"
		panelCollapse = ET.SubElement(panel, "div")
		panelCollapse.set("id", "collapse1")
		panelCollapse.set("class", "panel-collapse collapse")
		panelBody = ET.SubElement(panelCollapse, "div")
		panelBody.set("class", "panel-body")
		for processInfo in cmpnt.find("acqinfo"):
			pPanel = ET.SubElement(panelBody, "p")
			pPanel.text = processInfo.find("date").text + " - " + processInfo.find("date").tail

	colMd10 = ET.SubElement(colMd, "div")
	colMd10.set("class", "col-md-2")
	for date in cmpnt.find("did"):
		if date.tag == "unitdate":
			pDate = ET.SubElement(colMd10, "p")
			pDate.set("itemprop", "dateCreated")
			pDate.set("content", date.attrib["normal"])
			pDate.text = date.text
			if "label" in date.attrib:
				spanDate = ET.Element("span")
				spanDate.set("class", "glyphicon glyphicon-info-sign")
				spanDate.set("title", date.attrib["label"])
				spanDate.set("data-toggle", "tooltip")
				spanDate.set("data-placement", "top")
				pDate.append(spanDate)
	
	links = ET.SubElement(div, "div")
	links.set("id", "links")
	sequence = ET.SubElement(links, "div")
	sequence.set("class", "col-md-12 sequence")
	
	"""
	for child in cmpnt:
		if child.tag.startswith("c0"):
			aThumb = ET.SubElement(sequence, "a")
			aThumb.set("class", "thumbnail")
			aThumb.set("href", dipId + "/" + newFilename + ext)
			imageTitle = child.find("did/unittitle").text
			childDateText = ""
			for childDate in child.find("did"):
				if childDate.tag == "unitdate":
					childDateText = childDateText + ", " + childDate.text
					if "label" in childDate.attrib:
						childDateText = childDateText + " (" + childDate.attrib["label"] + ") "
			aThumb.set("title", childDateText)
			aThumb.set("data-gallery", "True")
			img = ET.SubElement(aThumb, "img")
			img.set("src", dipId + "/" + newFilename + "T" + ext)
			img.set("alt", childDateText)
	"""
	#limit for testing:
	#if 5 == 1:
	if 5 > 1:
		imageCount = 0
		validExt = [".jpg", ".jpeg", ".png"]
		for root, dirs, files in os.walk(imageDir):
			for imageFile in files:
				if not imageFile.lower() == "thumbs.db":
					image = os.path.join(root, imageFile)
					if os.path.isfile(image):
						if os.path.splitext(imageFile)[1].lower() in validExt:
							try:
								testImage = Image.open(image)
								fileSize = os.path.getsize(image)
								if fileSize > 0:
									imageCount = imageCount + 1
																		
									fileName = os.path.splitext(image)[0]
									ext = os.path.splitext(image)[1]
									fileExt = ext

									newFilename = unitId + "." + str(imageCount)
									if not os.path.isfile(os.path.join(folderDip, newFilename + ext)):
										shutil.copy2(image, os.path.join(folderDip, newFilename + ext))
									newThumbnail = os.path.join(folderDip, newFilename + "T" + ext)
									if not os.path.isfile(os.path.join(folderDip, newThumbnail)):
										shutil.copy2(image, newThumbnail)
										mogrifyCmd = "mogrify -resize 150x150 \"" + newThumbnail + "\""
										mogrify = Popen(mogrifyCmd, shell=True, stdout=PIPE, stderr=PIPE)
										stdout, stderr = mogrify.communicate()
										#if len(stderr) > 0:
											#print "thumbnail mogrify  error: " + stderr
											
									for child in metaRecord:
										if child.tag == "file":
											if not child.attrib["name"].lower() == "thumbs.db":
												if child.attrib["name"] == imageFile:
											
													#fileExt = ".jpg"
													aThumb = ET.SubElement(sequence, "a")
													aThumb.set("itemscope", "True")
													aThumb.set("itemprop", "associatedMedia")
													aThumb.set("itemtype", "http://schema.org/ImageObject")
													aThumb.set("class", "thumbnail")
													if os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + fileExt)):
														checkExt = fileExt
													elif os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + ".jpg")):
														checkExt = ".jpg"
													elif os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + ".JPG")):
														checkExt = ".JPG"
													elif os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + ".jpeg")):
														checkExt = ".jpeg"
													elif os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + ".JPEG")):
														checkExt = ".JPEG"
													elif os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + ".png")):
														checkExt = ".png"
													elif os.path.isfile(os.path.join(folderDip, unitId + "." + str(imageCount) + ".PNG")):
														checkExt = ".PNG"
													else:
														checkExt = fileExt
													aThumb.set("href", dipId + "/" + unitId + "." + str(imageCount) + checkExt)
													imageTitle = ""
													if not child.find("description/unittitle") is None and child.find("description/unittitle").text:
														imageTitle = child.find("description/unittitle").text
													elif not child.find("description/scopecontent") is None and child.find("description/scopecontent").text:
														imageTitle = child.find("description/scopecontent").text
													elif child.find("description").text:
														imageTitle = child.find("description").text
													else:
														imageTitle = child.attrib["name"]
													for childDate in child.find("recordEvents"):
														if childDate.tag == "timestamp":
															if not childDate.text.startswith("0000"):
																if "T" in childDate.text:
																	normalDate = childDate.text.split("T")[0].replace(":", "-")
																else:
																	normalDate = childDate.text.split(" ")[0].replace(":", "-")
																dacsDate = dacs.iso2DACS(normalDate)
																try:
																	imageTitle = imageTitle + ", " + dacsDate
																except:
																	print child.find("id").text
																	imageTitle = imageTitle + ", " + dacsDate
																if "source" in childDate.attrib:
																	imageTitle = imageTitle + " (" + childDate.attrib["source"] + ") "
																elif "parser" in childDate.attrib:
																	imageTitle = imageTitle + " (" + childDate.attrib["parser"] + ") "
													aThumb.set("title", imageTitle)
													aThumb.set("data-gallery", "True")
													img = ET.SubElement(aThumb, "img")
													img.set("src", dipId + "/" + unitId + "." + str(imageCount) + "T" + checkExt)
													img.set("alt", imageTitle)
											
							except:
								exceptMsg = "\n********************************************************************************************"
								exceptMsg = exceptMsg + "\nImage failed at " + str(time.strftime("%Y-%m-%d %H:%M:%S"))
								exceptMsg = exceptMsg + "\nID: " + metaID
								exceptMsg = exceptMsg + "\nID: " + unitId
								exceptMsg = exceptMsg + str(traceback.format_exc())
								updateLog = open(os.path.join(processingDir, "errorLogFlat.txt"), "a")
								updateLog.write(exceptMsg)
								updateLog.close()
	
			
	htmlString = ET.tostring(template, pretty_print=True, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
	htmlWrite = open(os.path.join(dipDir, cmpnt.attrib["id"] + ".html"), "w")
	htmlWrite.write(htmlString)
	htmlWrite.close()
	

reload(sys)
sys.setdefaultencoding('mbcs')
print sys.getdefaultencoding()

parser = ET.XMLParser(remove_blank_text=True)
eadInput = ET.parse(eadFile, parser)
ead = eadInput.getroot()

#csv.register_dialect('piper', delimiter='|', quoting=csv.QUOTE_NONE)
csvInput = os.path.join(processingDir, "arrangmentDraft2.csv")
csvFile = open(csvInput, "r")
csvList = csv.reader(csvFile, delimiter='|')
rowCount = 0
for albumRow in csvList:
	fileCount = albumRow[5]
	arrangement = albumRow[0]
	if len(arrangement) > 0 and not arrangement.lower() == "zero":
		if int(fileCount) > 0:
			rowCount = rowCount + 1
			metadataFilename = albumRow[8]
			imagesPath = albumRow[6]
			metaID = albumRow[7]
			title = albumRow[2]
			scope = albumRow[3]
			name = albumRow[1]
			arrangement = albumRow[0]
			
			print metaID
			processTime = time.time() - startTime
			print "Process took " + str(processTime) + " seconds or " + str(processTime/60) + " minutes or " + str(processTime/3600) + " hours"
			
			#track progress every 100
			if str(rowCount).endswith("00"):
				print rowCount
			
			for sip in os.listdir(sipDir):
				for sipFile in os.listdir(os.path.join(sipDir, sip)):
					if sipFile == metadataFilename:
						metadataFile = os.path.join(sipDir, sip, sipFile)
			metadataInput = ET.parse(metadataFile, parser)
			meta = metadataInput.getroot()
			accessionTime = meta["submitted"]
			for folder in meta.xpath(".//folder"):
				if folder.find("id").text == metaID:
					metaRecord = folder
			if metaRecord is None:
				print "META_ERROR: " + metaID
			arrangeList = arrangement.split("/")
			for series in ead.find("archdesc/dsc"):
				if series.tag == "c01":
					if series.find("did/unittitle").text == arrangeList[0]:
						seriesMatch = series
			if seriesMatch is None:
				print "ERROR: " + metaID
			for subseries in seriesMatch:
				if subseries.tag == "c02":
					if subseries.find("did/unittitle").text == arrangeList[1]:
						subseriesMatch = subseries
			if subseriesMatch is None:
				print "ERROR: " + metaID
			if not len(arrangeList) > 2:
				cmpntMatch = subseriesMatch
				cmpntTag = "c03"
			else:
				for subsubseries in subseriesMatch:
					if subsubseries.tag.startswith("c0"):
						if subsubseries.find("did/unittitle").text == arrangeList[1]:
							cmpntMatch = subsubseries
							cmpntTag ="c04"
				if cmpntMatch is None:
					print "ERROR: " + metaID
			if cmpntMatch is None:
				print "ERROR: " + metaID
			idCount = 1
			try:
				for existingFolder in cmpntMatch:
					if existingFolder.tag.startswith("c0"):
						idCount = idCount + 1
			except:
				print metaID
				for existingFolder in cmpntMatch:
					if existingFolder.tag.startswith("c0"):
						idCount = idCount + 1
			newId = cmpntMatch.attrib["id"] + "_" + str(idCount)
			newFolder = ET.SubElement(cmpntMatch, cmpntTag)
			newFolder.set("id", newId)
			did = ET.SubElement(newFolder, "did")
			unittitle = ET.SubElement(did, "unittitle")
			try:
				unittitle.text = title
			except:
				print metaID
				unittitle.text = title
			if len(scope) > 0:
				scopecontent = ET.SubElement(newFolder, "scopecontent")
				scopecontent.text = scopecontent
			for timestamp in metaRecord.find("recordEvents"):
				if "T" in timestamp.text:
					normalDate = timestamp.text.split("T")[0].replace(":", "-")
				else:
					normalDate = timestamp.text.split(" ")[0].replace(":", "-")
				unitdate = ET.SubElement(did, "unitdate")
				unitdate.set("normal", normalDate)
				unitdate.text = dacs.iso2DACS(normalDate)
				if "source" in timestamp.attrib:
					unitdate.set("label", timestamp.attrib["source"])
				elif "parser" in timestamp.attrib:
					unitdate.set("label", timestamp.attrib["parser"])
			if not metaRecord.find("curatorialEvents/event") is None:
				acqinfo = ET.SubElement(newFolder, "acqinfo")
				if not meta.find("profile/notes").text is None:
					pElement = ET.SubElement(acqinfo, "p")
					pElement.text = meta.find("profile/notes").text
				pElement = ET.SubElement(acqinfo, "p")
				dateElement = ET.SubElement(pElement, "date")
				dateElement.set("normal", accessionTime)
				dateElement.text = dacs.iso2DACS(accessionTime)
				dateElement.tail = "Accession: " + metadataFilename.split(".")[0]
				for event in metaRecord.find("curatorialEvents"):
					pElement = ET.SubElement(acqinfo, "p")
					if "timestampHuman" in event.attrib:
						human = "timestampHuman"
					elif "humanTime" in event.attrib:
						human = "humanTime"
					if "T" in event.attrib[human]:
						eventTime = event.attrib[human].split("T")[0]
					else:
						eventTime = event.attrib[human].split(" ")[0]	
					dateElement = ET.SubElement(pElement, "date")
					dateElement.set("normal", eventTime)
					dateElement.text = dacs.iso2DACS(eventTime)
					dateElement.tail = event.text
			imageFolder = imagesPath.split("\\")[-1]
			for sip in os.listdir(sipDir):
				if sip == metadataFilename.split(".xml")[0]:
					for sipfolder in os.listdir(os.path.join(sipDir, sip)):
						if sipfolder == "data":
							for accessionFolder in os.listdir(os.path.join(sipDir, sip, sipfolder)):
								correctPath = os.path.join(sipDir, sip, sipfolder, accessionFolder)
								for albumFolder in os.listdir(correctPath):
									#print albumFolder
									if albumFolder == imageFolder:
										correctPathMatch = correctPath
										matchfolder = albumFolder
			validExt = [".jpg", ".jpeg", ".png"]
			imageCount = 0
			sizeCount = 0
			imageDir = os.path.join(correctPathMatch, matchfolder)
			for root, dirs, files in os.walk(imageDir):
				for file in files:
					if not file.lower() == "thumbs.db":
						if os.path.splitext(file)[1].lower() in validExt:
							fileSize = os.path.getsize(os.path.join(root, file))
							if fileSize > 0:
								imageCount = imageCount + 1
								sizeCount = sizeCount + fileSize
			physdesc = ET.SubElement(did, "physdesc")
			folderSize = sizeof_fmt(sizeCount)
			extent = ET.SubElement(physdesc, "extent")
			extent.text = folderSize.split("-")[0]
			extent.set("unit", folderSize.split("-")[1])
			dimensions = ET.SubElement(physdesc, "dimensions")
			dimensions.text = str(imageCount)
			dimensions.set("unit", "Digital Files")
			
			dao = ET.Element("dao")
			dao.set("actuate", "onrequest")
			dao.set("linktype", "simple")
			dao.set("show", "new")
			dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + newId + ".html")
			did.append(dao)
			#makeGallery(sipDir, dipDir, metadataFilename.split(".xml")[0], metaRecord, newId, newFolder, templateFile, metaID)
			
			
			if str(rowCount).endswith("00"):
				eadString = ET.tostring(ead, pretty_print=True, xml_declaration=True, encoding="utf-8")
				eadWrite = open("ua395.xml", "w")
				eadWrite.write(eadString)
				eadWrite.close()
			
					
			
						
					
			
print rowCount
csvFile.close()
	
eadString = ET.tostring(ead, pretty_print=True, xml_declaration=True, encoding="utf-8")
eadWrite = open("ua395.xml", "w")
eadWrite.write(eadString)
eadWrite.close()