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
import smtplib


if os.name == "nt":
	bagDir = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395"
	processingDir = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395"
	eadFile = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395\ua395.xml"
	templateFile = "\\\\romeo\\wwwroot\\eresources\\digital_objects\\ua395\\template.html"
	sipDir = "\\\\LINCOLN\\Masters\\Special Collections\\accessions\\SIP"
	dipDir = "\\\\romeo\\wwwroot\\eresources\\digital_objects\\ua395"
else:
	bagDir = ""
	processingDir = ""
	
print sys.getfilesystemencoding()

startTime = time.time()
startTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
print "Start Time: " + startTimeReadable

seriesList = []

def dacsFromNormal(normalDate):
	calendar = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
	if len(normalDate) < 1:
		displayDate = normalDate
	if "/" in normalDate:
		startDate = normalDate.split('/')[0]
		endDate = normalDate.split('/')[1]
		if "-" in startDate:
			if startDate.count('-') == 1:
				startYear = startDate.split("-")[0]
				startMonth = startDate.split("-")[1]
				displayStart = startYear + " " + calendar[startMonth]
			else:
				startYear = startDate.split("-")[0]
				startMonth = startDate.split("-")[1]
				startDay = startDate.split("-")[2]
				if startDay.startswith("0"):
					displayStartDay = startDay[1:]
				else:
					displayStartDay = startDay
				displayStart = startYear + " " + calendar[startMonth] + " " + displayStartDay
		else:
			displayStart = startDate
		if "-" in endDate:
			if endDate.count('-') == 1:
				endYear = endDate.split("-")[0]
				endMonth = endDate.split("-")[1]
				displayEnd = endYear + " " + calendar[endMonth]
			else:
				endYear = endDate.split("-")[0]
				endMonth = endDate.split("-")[1]
				endDay = endDate.split("-")[2]
				if endDay.startswith("0"):
					displayEndDay = endDay[1:]
				else:
					displayEndDay = endDay
				displayEnd = endYear + " " + calendar[endMonth] + " " + displayEndDay
		else:
			displayEnd = endDate
		displayDate = displayStart + "-" + displayEnd
	else:
		if "-" in normalDate:
			if normalDate.count('-') == 1:
				year = normalDate.split("-")[0]
				month = normalDate.split("-")[1]
				displayDate = year + " " + calendar[month]
			else:
				year = normalDate.split("-")[0]
				month = normalDate.split("-")[1]
				day = normalDate.split("-")[2]
				if day.startswith("0"):
					displayDay = day[1:]
				else:
					displayDay = day
				displayDate = year + " " + calendar[month] + " " + displayDay
		else:
			displayDate = normalDate
	return displayDate
	
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
			dateElement.text = dacsFromNormal(eventTime)
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
			unitdate.text = dacsFromNormal(normalDate)
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
			unitdate.text = dacsFromNormal(firstDate + "/" + lastDate)
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
	
def makeGallery(sipDir, dipDir, accessionNumber, metaRecord, unitId, cmpnt, templateFile):	
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
	#limit for testing:
	#if metaRecord.attrib["name"] == "Academic-Partnerships":
	#ings
	extList = []
	if 5 > 1:
		imageCount = 0
		for imageFile in os.listdir(folderSip):
			if not imageFile.lower() == "thumbs.db":
				image = os.path.join(folderSip, imageFile)
				fileName = os.path.splitext(image)[0]
				ext = os.path.splitext(image)[1]
				extList.append(ext)
				try:
					#print os.path.basename(fileName).encode(sys.getdefaultencoding())
					thumbFile =  urllib.quote(os.path.basename(fileName), safe='') + "-Th" + ext
				except:
					thumbFile =  os.path.basename(fileName).replace(" ", "%20").replace("(", "%28").replace(")", "%29") + "-Th" + ext
				thumbnail = os.path.join(folderThumbs, thumbFile)
				if os.path.isfile(image):
					imageCount = imageCount + 1
					newFilename = unitId + "." + str(imageCount)
					if not os.path.isfile(os.path.join(folderDip, newFilename + ext)):
						shutil.copy2(image, os.path.join(folderDip, newFilename + ext))
					newThumbnail = os.path.join(folderDip, newFilename + "T" + ext)
					if os.path.isfile(thumbnail):
						if not os.path.isfile(newThumbnail):
							shutil.copy2(thumbnail, newThumbnail)
					else:
						shutil.copy2(image, newThumbnail)
						mogrifyCmd = ["mogrify -resize 300x300\"" + newThumbnail + "\""]
						mogrify = Popen(mogrifyCmd, shell=True, stdout=PIPE, stderr=PIPE)
						stdout, stderr = mogrify.communicate()
						if len(stderr) > 0:
							print "thumbnail mogrify  error: " + stderr
	div = template.find(".//div[@id='dynamicContent']")
	
	#hope this part works
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
	
	if not cmpnt.getprevious() is None:
		if cmpnt.getprevious().tag == cmpnt.tag:
			a = ET.SubElement(div, "a")
			a.set("class", "leftRight pull-left")
			a.set("href", cmpnt.getprevious().attrib["id"] + ".html")
			span = ET.SubElement(a, "span")
			span.set("class", "glyphicon glyphicon-arrow-left")
	if not metaRecord.getnext() is None:
		if metaRecord.getnext().tag == metaRecord.tag:
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
	imageCount = 0
	for child in metaRecord:
		if child.tag == "file":
			if not child.attrib["name"].lower() == "thumbs.db":
				fileExt = extList[imageCount]
				imageCount = imageCount + 1
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
							dacsDate = dacsFromNormal(normalDate)
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
arrangementList = []
for metadataFile in os.listdir(bagDir):
	if metadataFile.endswith("Nqe.xml"):
		metadataInput = ET.parse(os.path.join(bagDir, metadataFile), parser)
		metadata = metadataInput.getroot()
		accessionNumber = metadata.attrib["number"]


		#find all top-level albums
		for folder1 in metadata.find("folder").findall("folder"):
			#if contain files:
			if not folder1.find("file") is None:
				if folder1.attrib["name"] == "First-Tuesday-at-Museum":
					FirstTuesday = folder1

				
		#find all folder-level objects
		for folder1 in metadata.find("folder").findall("folder"):

			#if contain files:
			if not folder1.find("file") is None:
				if folder1.attrib["name"] == "First-Tuesday-at-Museum":
					FirstTuesday = folder1
				else:
					print "ERROR: Unexpected Folder " + folder1.attrib["name"]
				
			else:
						
				originalName = folder1.attrib["name"]
				name = folder1.attrib["name"].replace("-", " ")
				parentName = name
				seriesName1 = name
				#eliminate thumbnail directories
				if not name.lower() == "thumbs":
				
					
					matchCheck = False
					lastId = "0"
					for cmpntCheck in ead.find("archdesc/dsc"):
						lastId = cmpntCheck.attrib["id"].split("-")[1]
						if cmpntCheck.find("did/unittitle").text == name:
							matchCheck = True
							series = cmpntCheck
							
					
					if matchCheck == False:
						#make new series
						newSeries = ET.SubElement(ead.find("archdesc/dsc"), "c01")
						newSeriesId = int(lastId) + 1
						newSeries.set("id", "nam_ua395-" + str(newSeriesId))
						newSeries.set("level", "series")
						did = ET.SubElement(newSeries, "did")
						unitid = ET.SubElement(did, "unitid")
						unitid.text = str(newSeriesId)
						unittitle = ET.SubElement(did, "unittitle")
						unittitle.set("label", "Series")
						newSeries = makeNewCmpnt(newSeries, folder1)
						series = newSeries
					
					matchCheck = False
					lastId = "0"
					for folder2 in folder1:
						if folder2.tag == "folder":
							originalName = folder2.attrib["name"]
							name = folder2.attrib["name"].replace("-", " ")
							parentName2 = name
							seriesName2 = name
							#eliminate thumbnail directories
							if not name.lower() == "thumbs":
								#if files present (folder-level)
								if not folder2.find("file") is None:
									if not seriesName1 + "/" + seriesName1 in seriesList:
										seriesList.append(seriesName1 + "/" + seriesName1)
									
									lastId = "0"
									for cmpntCheck in series:
										if cmpntCheck.tag == "c02":
											lastId = cmpntCheck.attrib["id"].split(".")[1]
											if cmpntCheck.find("did/unittitle").text == parentName:
												matchCheck = True
												subseries = cmpntCheck
												
												matchCheck2 = False
												lastId = "0"
												for cmpntCheck in subseries:
													if cmpntCheck.tag == "c03":
														lastId = cmpntCheck.attrib["id"].split("_")[2]
														if cmpntCheck.find("did/unittitle").text == name:
															matchCheck2 = True
															folderLevel = cmpntCheck
												if matchCheck2 == False:
													#make new folder
													newSeries = ET.SubElement(subseries, "c03")
													newSeriesId = int(lastId) + 1
													newSeries.set("id", subseries.attrib["id"] + "_" + str(newSeriesId))
													did = ET.SubElement(newSeries, "did")
													unittitle = ET.SubElement(did, "unittitle")
													newSeries = makeNewCmpnt(newSeries, folder2)
													folderLevel = newSeries		
												#FOLDER HERE
												dao = ET.Element("dao")
												dao.set("actuate", "onrequest")
												dao.set("linktype", "simple")
												dao.set("show", "new")
												dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
												folderLevel.find("did").append(dao)
												makeGallery(sipDir, dipDir, accessionNumber, folder2, folderLevel.attrib["id"], folderLevel, templateFile)
												

												
									if matchCheck == False:
										#make new series
										newSeries = ET.SubElement(series, "c02")
										newSeriesId = int(lastId) + 1
										newSeries.set("id", series.attrib["id"] + "." + str(newSeriesId))
										newSeries.set("level", "subseries")
										did = ET.SubElement(newSeries, "did")
										unitid = ET.SubElement(did, "unitid")
										unitid.text = str(newSeries.attrib["id"].split("-")[1])
										unittitle = ET.SubElement(did, "unittitle")
										unittitle.set("label", "Subseries")
										newSeries = makeNewCmpnt(newSeries, folder1)
										subseries = newSeries
										
										newSeries = ET.SubElement(subseries, "c03")
										newSeries.set("id", subseries.attrib["id"] + "_1" )
										did = ET.SubElement(newSeries, "did")
										unittitle = ET.SubElement(did, "unittitle")
										newSeries = makeNewCmpnt(newSeries, folder2)
										folderLevel = newSeries
										#FOLDER HERE
										dao = ET.Element("dao")
										dao.set("actuate", "onrequest")
										dao.set("linktype", "simple")
										dao.set("show", "new")
										dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
										folderLevel.find("did").append(dao)
										makeGallery(sipDir, dipDir, accessionNumber, folder2, folderLevel.attrib["id"], folderLevel, templateFile)
										
										
								else:
									#print "series"
									#series, like College of Arts and Sciences
									
									matchCheck = False
									lastId = "0"
									for cmpntCheck in series:
										if cmpntCheck.tag == "c02":
											lastId = cmpntCheck.attrib["id"].split(".")[1]
											if cmpntCheck.find("did/unittitle").text == name:
												matchCheck = True
												subseries = cmpntCheck
									if matchCheck == False:
										#make new series
										newSeries = ET.SubElement(series, "c02")
										newSeriesId = int(lastId) + 1
										newSeries.set("id", series.attrib["id"] + "." + str(newSeriesId))
										newSeries.set("level", "subseries")
										did = ET.SubElement(newSeries, "did")
										unitid = ET.SubElement(did, "unitid")
										unitid.text = str(newSeries.attrib["id"].split("-")[1])
										unittitle = ET.SubElement(did, "unittitle")
										unittitle.set("label", "Subseries")
										newSeries = makeNewCmpnt(newSeries, folder2)
										subseries = newSeries
										
										#for First-Tuesday-at-Museum
										if folder2.attrib["name"] == "University-Art-Museum":
											newSeries = ET.SubElement(subseries, "c03")
											newSeries.set("id", subseries.attrib["id"] + "_1")
											did = ET.SubElement(newSeries, "did")
											unittitle = ET.SubElement(did, "unittitle")
											newSeries = makeNewCmpnt(newSeries, FirstTuesday)
											folderLevel = newSeries
											#FOLDER HERE
											dao = ET.Element("dao")
											dao.set("actuate", "onrequest")
											dao.set("linktype", "simple")
											dao.set("show", "new")
											dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
											newSeries.find("did").append(dao)
											makeGallery(sipDir, dipDir, accessionNumber, FirstTuesday, folderLevel.attrib["id"], folderLevel, templateFile)
											print "first Tuesday"
										
										
									matchCheck = False
									lastId = "0"
									folderSwitch = False
									for folder3 in folder2:
										if folder3.tag == "folder":
											originalName = folder3.attrib["name"]
											name = folder3.attrib["name"].replace("-", " ")
											#eliminate thumbnail directories
											if not name.lower() == "thumbs":
												#check for more series
												#print folder3.attrib["name"]
												if folder3.find("file") is None:
													folderSwitch = True
									for folder3 in folder2:
										if folder3.tag == "folder":
											originalName = folder3.attrib["name"]
											name = folder3.attrib["name"].replace("-", " ")
											#eliminate thumbnail directories
											if not name.lower() == "thumbs":
											
												if not folder3.find("file") is None:
													
													if folderSwitch == True:
														
														#make another duplicate subseries
														#folder 3 is a subsubseries
														matchCheck2 = False
														lastId = "0"
														for cmpntCheck in subseries:
															if cmpntCheck.tag == "c03":
																lastId = int(cmpntCheck.attrib["id"].split(".")[-1]) + 1
																if cmpntCheck.find("did/unittitle").text == parentName2:
																	matchCheck2 = True
																	subsubseries = cmpntCheck
																	
														if matchCheck2 == False:
															#make new subseries
															newSeries = ET.SubElement(subseries, "c03")
															newSeriesId = int(lastId) + 1
															newSeries.set("id", subseries.attrib["id"] + "." + str(newSeriesId))
															#newSeries.set("level", "subseries")
															did = ET.SubElement(newSeries, "did")
															unitid = ET.SubElement(did, "unitid")
															unitid.text = str(newSeries.attrib["id"].split("-")[1])
															unittitle = ET.SubElement(did, "unittitle")
															unittitle.set("label", "Subseries")
															newSeries = makeNewCmpnt(newSeries, folder2)
															subsubseries = newSeries
															
															newSeries = ET.SubElement(newSeries, "c04")
															newSeries.set("id", subsubseries.attrib["id"] + "_1")
															did = ET.SubElement(newSeries, "did")
															unittitle = ET.SubElement(did, "unittitle")
															newSeries = makeNewCmpnt(newSeries, folder3)
															folderLevel = newSeries
															#FOLDER HERE
															dao = ET.Element("dao")
															dao.set("actuate", "onrequest")
															dao.set("linktype", "simple")
															dao.set("show", "new")
															dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
															folderLevel.find("did").append(dao)
															makeGallery(sipDir, dipDir, accessionNumber, folder3, folderLevel.attrib["id"], folderLevel, templateFile)
															
														else:
															matchCheck3 = False
															
															lastId = "0"
															for cmpntCheck in subsubseries:
																if cmpntCheck.tag == "c04":
																	lastId = int(cmpntCheck.attrib["id"].split("_")[2]) + 1
																	if cmpntCheck.find("did/unittitle").text == name:
																		matchCheck3 = True
																		folderLevel = cmpntCheck
																		
															if matchCheck3 == False:
																newSeries = ET.SubElement(subsubseries, "c04")
																newSeries.set("id", subsubseries.attrib["id"] + "_" + str(lastId))
																did = ET.SubElement(newSeries, "did")
																unittitle = ET.SubElement(did, "unittitle")
																newSeries = makeNewCmpnt(newSeries, folder3)
															folderLevel = newSeries
															#FOLDER HERE
															dao = ET.Element("dao")
															dao.set("actuate", "onrequest")
															dao.set("linktype", "simple")
															dao.set("show", "new")
															dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
															folderLevel.find("did").append(dao)
															makeGallery(sipDir, dipDir, accessionNumber, folder3, folderLevel.attrib["id"], folderLevel, templateFile)
															
															
													else:
														#folder 3 is just a folder in a subseries
														matchCheck = False
														
														lastId = "0"
														for cmpntCheck in subseries:
															if cmpntCheck.tag == "c03":
																lastId = cmpntCheck.attrib["id"].split("_")[2]
																if cmpntCheck.find("did/unittitle").text == name:
																	matchCheck = True
																	folderLevel = cmpntCheck
														if matchCheck == False:
															#make new series
															newSeries = ET.SubElement(subseries, "c03")
															newSeriesId = int(lastId) + 1
															newSeries.set("id", subseries.attrib["id"] + "_" + str(newSeriesId))
															did = ET.SubElement(newSeries, "did")
															unittitle = ET.SubElement(did, "unittitle")
															newSeries = makeNewCmpnt(newSeries, folder3)
															folderLevel = newSeries	
														#FOLDER HERE
														dao = ET.Element("dao")
														dao.set("actuate", "onrequest")
														dao.set("linktype", "simple")
														dao.set("show", "new")
														dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
														folderLevel.find("did").append(dao)
														makeGallery(sipDir, dipDir, accessionNumber, folder3, folderLevel.attrib["id"], folderLevel, templateFile)
														

												else:													
													#series, like Academics/College of Arts and Sciences/Geography and Planning
													matchCheck2 = False
													lastId = "0"
													for cmpntCheck in subseries:
														if cmpntCheck.tag == "c03":
															lastId = cmpntCheck.attrib["id"].split(".")[-1]
															if cmpntCheck.find("did/unittitle").text == name:
																matchCheck2 = True
																subsubseries = cmpntCheck
													if matchCheck2 == False:
														#make new subseries
														newSeries = ET.SubElement(subseries, "c03")
														newSeriesId = int(lastId) + 1
														newSeries.set("id", subseries.attrib["id"] + "." + str(newSeriesId))
														#newSeries.set("level", "subseries")
														did = ET.SubElement(newSeries, "did")
														unitid = ET.SubElement(did, "unitid")
														unitid.text = str(newSeries.attrib["id"].split("-")[1])
														unittitle = ET.SubElement(did, "unittitle")
														unittitle.set("label", "Subseries")
														newSeries = makeNewCmpnt(newSeries, folder3)
														subsubseries = newSeries
														
													for folder4 in folder3:
														if folder4.tag == "folder":
															originalName = folder4.attrib["name"]
															name = folder4.attrib["name"].replace("-", " ")
															#eliminate thumbnail directories
															if not name.lower() == "thumbs":
															
																if not folder4.find("file") is None:
																	matchCheck2 = False
																	
																	for cmpntCheck in subsubseries:
																		if cmpntCheck.tag == "c04":
																			lastId = cmpntCheck.attrib["id"].split("_")[2]
																			if cmpntCheck.find("did/unittitle").text == name:
																				matchCheck2 = True
																				folderLevel = cmpntCheck
																	if matchCheck2 == False:
																		#make new subseries
																		newSeries = ET.SubElement(subsubseries, "c04")
																		newSeriesId = int(lastId) + 1
																		newSeries.set("id", subsubseries.attrib["id"] + "_" + str(newSeriesId))
																		did = ET.SubElement(newSeries, "did")
																		unittitle = ET.SubElement(did, "unittitle")
																		newSeries = makeNewCmpnt(newSeries, folder4)
																		folderLevel = newSeries
																	#FOLDER HERE
																	dao = ET.Element("dao")
																	dao.set("actuate", "onrequest")
																	dao.set("linktype", "simple")
																	dao.set("show", "new")
																	dao.set("href", "http://library.albany.edu/speccoll/findaids/eresources/digital_objects/ua395/" + folderLevel.attrib["id"] + ".html")
																	folderLevel.find("did").append(dao)
																	makeGallery(sipDir, dipDir, accessionNumber, folder4, folderLevel.attrib["id"], folderLevel, templateFile)
																	
																		
																	
							
try:
	for c01 in ead.find("archdesc/dsc"):
		if c01.tag == "c01":
			for c02 in c01:
				if c02.tag == "c02":
					for c03 in c02:
						if c03.tag == "c03":
							if "label" in c03.find("did/unittitle").attrib:
								files = 0
								sizeMB = 0
								physdesc = c03.find("did/physdesc")
								for child in c03:
									if child.tag == "c04":
										if child.find("did/physdesc/dimensions") is None:
											pass
										else:
											files = files + int(child.find("did/physdesc/dimensions").text)
										if child.find("did/physdesc/extent") is None:
											pass
										elif child.find("did/physdesc/extent").attrib["unit"] == "MB":
											sizeMB = sizeMB + float(child.find("did/physdesc/extent").text)
										elif child.find("did/physdesc/extent").attrib["unit"] == "GB":
											cmpntMB = float(child.find("did/physdesc/extent").text) * 1024
											sizeMB = sizeMB + cmpntMB
								if physdesc.find("extent") is None:
									extent = ET.Element("extent")
									if sizeMB > 1023:
										sizeGB = sizeMB / 1024
										extent.text = str(math.ceil(sizeGB*100)/100) 
										extent.set("unit", "GB")
									else:
										extent.text = str(sizeMB)
										extent.set("unit", "MB")
									physdesc.insert(0, extent)
								else:
									if sizeMB > 1023:
										sizeGB = sizeMB / 1024
										physdesc.find("extent").text = str(math.ceil(sizeGB*100)/100) 
										physdesc.find("extent").set("unit", "GB")
									else:
										physdesc.find("extent").text = str(sizeMB)
										physdesc.find("extent").set("unit", "MB")
								if physdesc.find("dimensions") is None:
									dimensions = ET.SubElement(physdesc, "dimensions")
									dimensions.text = str(files)
									dimensions.set("unit", "Digital Files")
								else:
									physdesc.find("dimensions").text = str(files)
									physdesc.find("dimensions").set("unit", "Digital Files")
			
			
	for c01 in ead.find("archdesc/dsc"):
		if c01.tag == "c01":
			for c02 in c01:
				if c02.tag == "c02":
					if "label" in c02.find("did/unittitle").attrib:
						files = 0
						sizeMB = 0
						physdesc = c02.find("did/physdesc")
						for child in c02:
							if child.tag == "c03":
								if child.find("did/physdesc/dimensions") is None:
									pass
								else:
									files = files + int(child.find("did/physdesc/dimensions").text)
								if child.find("did/physdesc/extent") is None:
									pass
								elif child.find("did/physdesc/extent").attrib["unit"] == "MB":
									sizeMB = sizeMB + float(child.find("did/physdesc/extent").text)
								elif child.find("did/physdesc/extent").attrib["unit"] == "GB":
									cmpntMB = float(child.find("did/physdesc/extent").text) * 1024
									sizeMB = sizeMB + cmpntMB
						if physdesc.find("extent") is None:
							extent = ET.Element("extent")
							if sizeMB > 1023:
								sizeGB = sizeMB / 1024
								extent.text = str(math.ceil(sizeGB*100)/100) 
								extent.set("unit", "GB")
							else:
								extent.text = str(sizeMB)
								extent.set("unit", "MB")
							physdesc.insert(0, extent)
						else:
							if sizeMB > 1023:
								sizeGB = sizeMB / 1024
								physdesc.find("extent").text = str(math.ceil(sizeGB*100)/100) 
								physdesc.find("extent").set("unit", "GB")
							else:
								physdesc.find("extent").text = str(sizeMB)
								physdesc.find("extent").set("unit", "MB")
						if physdesc.find("dimensions") is None:
							dimensions = ET.SubElement(physdesc, "dimensions")
							dimensions.text = str(files)
							dimensions.set("unit", "Digital Files")
						else:
							physdesc.find("dimensions").text = str(files)
							physdesc.find("dimensions").set("unit", "Digital Files")
						
	for c01 in ead.find("archdesc/dsc"):
		if c01.tag == "c01":
			if "label" in c01.find("did/unittitle").attrib:
				files = 0
				sizeMB = 0
				physdesc = c01.find("did/physdesc")
				for child in c01:
					if child.tag == "c02":
						if child.find("did/physdesc/dimensions") is None:
							pass
						else:
							files = files + int(child.find("did/physdesc/dimensions").text)
						if child.find("did/physdesc/extent") is None:
							pass
						elif child.find("did/physdesc/extent").attrib["unit"] == "MB":
							sizeMB = sizeMB + float(child.find("did/physdesc/extent").text)
						elif child.find("did/physdesc/extent").attrib["unit"] == "GB":
							cmpntMB = float(child.find("did/physdesc/extent").text) * 1024
							sizeMB = sizeMB + cmpntMB
				if physdesc.find("extent") is None:
					extent = ET.Element("extent")
					if sizeMB > 1023:
						sizeGB = sizeMB / 1024
						extent.text = str(math.ceil(sizeGB*100)/100) 
						extent.set("unit", "GB")
					else:
						extent.text = str(sizeMB)
						extent.set("unit", "MB")
					physdesc.insert(0, extent)
				else:
					if sizeMB > 1023:
						sizeGB = sizeMB / 1024
						physdesc.find("extent").text = str(math.ceil(sizeGB*100)/100) 
						physdesc.find("extent").set("unit", "GB")
					else:
						physdesc.find("extent").text = str(sizeMB)
						physdesc.find("extent").set("unit", "MB")
				if physdesc.find("dimensions") is None:
					dimensions = ET.SubElement(physdesc, "dimensions")
					dimensions.text = str(files)
					dimensions.set("unit", "Digital Files")
				else:
					physdesc.find("dimensions").text = str(files)
					physdesc.find("dimensions").set("unit", "Digital Files")
				
	files = 0
	sizeMB = 0
	physdesc = ead.find("archdesc/did/physdesc")
	for child in ead.find("archdesc/dsc"):
		if child.tag == "c01":
			if child.find("did/physdesc/dimensions") is None:
				pass
			else:
				files = files + int(child.find("did/physdesc/dimensions").text)
			if child.find("did/physdesc/extent") is None:
				pass
			elif child.find("did/physdesc/extent").attrib["unit"] == "MB":
				sizeMB = sizeMB + float(child.find("did/physdesc/extent").text)
			elif child.find("did/physdesc/extent").attrib["unit"] == "GB":
				cmpntMB = float(child.find("did/physdesc/extent").text) * 1024
				sizeMB = sizeMB + cmpntMB
	if physdesc.find("extent") is None:
		extent = ET.Element("extent")
		if sizeMB > 1023:
			sizeGB = sizeMB / 1024
			extent.text = str(math.ceil(sizeGB*100)/100) 
			extent.set("unit", "GB")
		else:
			extent.text = str(sizeMB)
			extent.set("unit", "MB")
		physdesc.insert(0, extent)
	else:
		if sizeMB > 1023:
			sizeGB = sizeMB / 1024
			physdesc.find("extent").text = str(math.ceil(sizeGB*100)/100) 
			physdesc.find("extent").set("unit", "GB")
		else:
			physdesc.find("extent").text = str(sizeMB)
			physdesc.find("extent").set("unit", "MB")
	if physdesc.find("dimensions") is None:
		dimensions = ET.SubElement(physdesc, "dimensions")
		dimensions.text = str(files)
		dimensions.set("unit", "Digital Files")
	else:
		physdesc.find("dimensions").text = str(files)
		physdesc.find("dimensions").set("unit", "Digital Files")
except:
	pass
				
eadString = ET.tostring(ead, pretty_print=True, xml_declaration=True, encoding="utf-8")
eadWrite = open(eadFile, "w")
eadWrite.write(eadString)
eadWrite.close()

zeta = "\\\\zeta\\xtf\\data"

shutil.copy2(eadFile, zeta)

sender = 'UAlbanyArchivesNotify@gmail.com'
receivers = ['acybulski@albany.edu']
subject = "Script is finished"

body = "Script completed and copied ua395.xml to the data folder.\n\n Can you please move this file to production and run the indexer?\n\nThanks,\nGreg"
message = 'Subject: %s\n\n%s' % (subject, body)
smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.ehlo()
emailPW = "notifySL356"
smtpObj.login('UAlbanyArchivesNotify', emailPW)
smtpObj.sendmail(sender, receivers, message)
smtpObj.quit()

sender = 'UAlbanyArchivesNotify@gmail.com'
receivers = ['gwiedeman@albany.edu']
subject = "Script is finished"

body = "Script completed and copied ua395.xml to the data folder.\n\n Can you please move this file to production and run the indexer?\n\nThanks,\nGreg"
message = 'Subject: %s\n\n%s' % (subject, body)
smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.ehlo()
emailPW = "notifySL356"
smtpObj.login('UAlbanyArchivesNotify', emailPW)
smtpObj.sendmail(sender, receivers, message)
smtpObj.quit()
