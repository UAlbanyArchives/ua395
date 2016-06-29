import requests
import json
from lxml import etree as ET
import time
import urllib
import os
import uuid
import hashlib
import simplejson
import shutil
import traceback
import datetime
import exifread

startTime = time.time()
startTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
print startTimeReadable

#start log
startLog = open("log.txt", "a")
logText = "\n****************************************************************************************************************\n"
logText = logText + "Crawl started " + startTimeReadable
startLog.write(logText)
startLog.close()

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


if os.name == "nt":
	basePath = "\\Processing\\ua395"
	stagingPath = "\\Processing\\ua395\\stagingUA395"
else:
	basePath = "/home/bcadmin/Desktop/Processing/ua395"
	stagingPath = "/home/bcadmin/Desktop/Processing/ua395/stagingUA395"

try:
	def readField(JSON, parent, fieldString):
		try:
			newElement = ET.SubElement(parent, fieldString.lower())
			newElement.text = JSON[fieldString].replace(u"\u2018", "'").replace(u"\u2019", "'").strip()
		except:
			print "Could not read " + fieldString + " from " + JSON["Uri"]

	def md5(fname):
		hash_md5 = hashlib.md5()
		with open(fname, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
		return hash_md5.hexdigest()

	#url = "http://www.smugmug.com/api/v2/user/ualbanyphotos"
	#url = "http://www.smugmug.com/api/v2/user/ualbanyphotos?APIKey=yOoGBuxh2vLhQzmESiDk1qrqVsVBICUZ"
	#url = "http://www.smugmug.com/api/v2/user/ualbanyphotos!albums?start=1&count=99999999?APIKey=yOoGBuxh2vLhQzmESiDk1qrqVsVBICUZ"
	url = "http://www.smugmug.com/api/v2/user/ualbanyphotos!albums?start=1&count=99999&APIKey=yOoGBuxh2vLhQzmESiDk1qrqVsVBICUZ"
	parser = ET.XMLParser(remove_blank_text=True)

	headers = {
		'Accept': 'application/json',
	}

	r = requests.get(url, headers=headers)
	print r.status_code

	#print r.json()
	blockedCount = 0
	passwordCount = 0

	passwordText = ""
	blockedText = ""
	
	if os.path.isfile(os.path.join(basePath, "albums.xml")):
		albumsInput = ET.parse(os.path.join(basePath, "albums.xml"), parser)
		albumsXML = albumsInput.getroot()
	else:
		print "Error: existing Album records not found."
		finalTime = time.time() - startTime
		print "Total Time: " + str(finalTime) + " seconds, " + str(finalTime/60) + " minutes, " + str(finalTime/3600) + " hours"
		errorLog = open("errorLog.txt", "a")
		errorText = "***********************************************************************************\n" + str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n" + str(finalTime) + " seconds\n" + str(finalTime/60) + " minutes\n" + str(finalTime/3600) + " hours" + "\nTraceback:\n" + "Error: existing Album records not found."
		errorLog.write(errorText)
		errorLog.close()
		albumsXML = ET.Element("albums")

	for album in r.json()["Response"]["Album"]:
		
		if album["ResponseLevel"] != "Public":
			passwordCount = passwordCount + 1
			passwordText = passwordText + "\n" + album["WebUri"]# + " (" + album["Name"] + ")"
		
		elif album["AllowDownloads"] != True:
			blockedCount = blockedCount + 1
			blockedText = blockedText + "\n" + album["WebUri"]# + " (" + album["Name"] + ")"
			
		else:
			#no permissions issues
			
			#check if album has already been downloaded and all content is the same
			try:
				albumURI = albumsXML.xpath("//uri[text()='" + album["Uri"] + "']")[0]
				albumXML = albumURI.getparent()

				if albumXML.find("urlpath").text == album["UrlPath"] and albumXML.find("name").text == album["Name"] and albumXML.find("nicename").text == album["NiceName"] and albumXML.find("imagesURI").text == album["Uris"]["AlbumImages"]["Uri"]:
					#updated album record
					ImagesLastUpdatedMatch = 0
					DescriptionMatch = 0
					KeywordsMatch = 0
					for albumField in albumXML:
						if albumField.tag == "imageslastupdated" and albumField.text == album["ImagesLastUpdated"]:
							ImagesLastUpdatedMatch = ImagesLastUpdatedMatch + 1
						if albumField.tag == "description" and albumField.text == album["Description"]:
							DescriptionMatch = DescriptionMatch + 1
						if albumField.tag == "keywords" and albumField.text == album["Keywords"]:
							KeywordsMatch = KeywordsMatch + 1
							
					if ImagesLastUpdatedMatch == 0:
						readField(album, albumXML, "ImagesLastUpdated")
					if DescriptionMatch == 0:
						readField(album, albumXML, "Description")
					if KeywordsMatch == 0:
						readField(album, albumXML, "Keywords")
				
				else:
					#conflict with old record
					conflictXML = ET.SubElement(albumXML, "conflict")
					conflictXML.set("conflictDiscovered",str(time.time()))
					newAlbumXML = ET.SubElement(conflictXML, "album")
					readField(album, newAlbumXML, "Uri")
					readField(album, newAlbumXML, "UrlPath")
					readField(album, newAlbumXML, "Name")
					readField(album, newAlbumXML, "NiceName")
					readField(album, newAlbumXML, "ImagesLastUpdated")
					readField(album, newAlbumXML, "Description")
					if album["Title"] != album["Name"]:
						print "Title is different for " + album["Name"]
						readField(album, newAlbumXML, "Title")
					readField(album, newAlbumXML, "Keywords")
					imagesURI = ET.SubElement(newAlbumXML, "imagesURI")
					imagesURI.text = album["Uris"]["AlbumImages"]["Uri"]
					
			except:
				albumXML = ET.SubElement(albumsXML, "album")
				readField(album, albumXML, "Uri")
				readField(album, albumXML, "UrlPath")
				readField(album, albumXML, "Name")
				readField(album, albumXML, "NiceName")
				readField(album, albumXML, "ImagesLastUpdated")
				readField(album, albumXML, "Description")
				if album["Title"] != album["Name"]:
					print "Title is different for " + album["Name"]
					readField(album, albumXML, "Title")
				readField(album, albumXML, "Keywords")
				imagesURI = ET.SubElement(albumXML, "imagesURI")
				imagesURI.text = album["Uris"]["AlbumImages"]["Uri"]
				

	passwordFile = open("password.txt", "w")
	passwordFile.write(passwordText)
	passwordFile.close()

	blockedFile = open("blocked.txt", "w")
	blockedFile.write(blockedText)
	blockedFile.close()
			
	print str(passwordCount) + " albums require a password"
	print str(blockedCount) + " albums cannot be completely downloaded"

	albumString = ET.tostring(albumsXML, pretty_print=True, xml_declaration=True, encoding="utf-8")
	albumFile = open("albums.xml", "w")
	albumFile.write(albumString)
	albumFile.close()
	
	with open('hashIndex.json', 'r') as fp:
		hashIndex = simplejson.loads(fp.read())
		
	if os.path.isfile(os.path.join(basePath, "images.xml")):
		#imageInput = ET.parse(os.path.join(basePath, "images.xml"), parser)
		imagesXML = ET.Element("albums")
	else:
		imagesXML = ET.Element("albums")

	runningFileSize = 0
	for folder in albumsXML:

		try: 
			folderXML = imagesXML.xpath("//album[@uri='" + folder.find("uri").text + "']")[0]
		except:
			folderXML = ET.SubElement(imagesXML, "album")
			folderXML.set("name", folder.find("name").text)
			folderXML.set("uri", folder.find("uri").text)

		#url for api request for each album to list images
		keyFile = blockedFile = open("key.txt", "r")
		line1 = keyFile.readline().split("\n")[0]
		keyString = line1.split("Key: ")[1].strip()
		keyFile.close()
		url = "http://www.smugmug.com" + folder.find("imagesURI").text + "?APIKey=" + keyString
		r = requests.get(url, headers=headers)
		#print status code if not successful
		if str(r.status_code) != "200":
			print r.status_code
		
		for image in r.json()["Response"]["AlbumImage"]:
			#check against json hash index
			try:
				metaHash = image["ArchivedMD5"]
				if len(metaHash) < 1:
					raise ValueError("no hash in API data")
			except:
				metaHash = "'''''"
				
			if metaHash in hashIndex.values():
				#image already downloaded
				pass
			else:
		
				imageXML = ET.SubElement(folderXML, "image")
				readField(image, imageXML, "Uri")
				readField(image, imageXML, "FileName")
				readField(image, imageXML, "Date")
				readField(image, imageXML, "WebUri")
				readField(image, imageXML, "LastUpdated")
				readField(image, imageXML, "ArchivedMD5")
				readField(image, imageXML, "ThumbnailUrl")
				readField(image, imageXML, "Caption")
				readField(image, imageXML, "Keywords")
				
				imageURL = ET.SubElement(imageXML, "ArchivedUri".lower())
				try:
					imageURL.text = image["ArchivedUri"].replace(u"\u2018", "'").replace(u"\u2019", "'").strip()
				except:
					imageURL.text = image["WebUri"] + "/0/O/" + image["FileName"].replace(" ", "%20")
				
				try:
					runningFileSize = runningFileSize + int(image["ArchivedSize"])
				except:
					pass

	
	imageString = ET.tostring(imagesXML, pretty_print=True, xml_declaration=True, encoding="utf-8")
	imagesFile = open("images.xml", "w")
	imagesFile.write(imageString)
	imagesFile.close()

	#for debugging
	"""
	imagesFile2 = open("imagesTest.xml", "w")
	imagesFile2.write(imageString)
	imagesFile2.close()
	"""
		
			
	metaTime = time.time() - startTime
	print "Total File Size: " + str(runningFileSize)
	print "Total Time to get metadata: " + str(metaTime)

	input = ET.parse(os.path.join(basePath, "images.xml"), parser)
	imagesXML = input.getroot()
	
	if not os.path.isdir(os.path.join(stagingPath, "ualbanyphotos")):
		os.makedirs(os.path.join(stagingPath, "ualbanyphotos"))


	for group in imagesXML:
		if group.find("image") is None:
			pass
		else:
			#print "examining " + group.attrib["uri"]
			
			for file in group:
				with open('hashIndex.json', 'r') as fp:
					hashIndex = simplejson.loads(fp.read())
				if file.find("archivedmd5").text is None:
					metaHash = "'''''"
				else:
					metaHash = file.find("archivedmd5").text
				if metaHash in hashIndex.values():
					#print "hash found for " + makeFile
					#print "removing " + file.find("uri").text + " from " + group.attrib["uri"]
					group.remove(file)
				else:
					#print "downloading " + file.find("uri").text
					filename = file.find("filename").text
					path = file.find("weburi").text
					path = path.split("//")[1]
					path = path.replace("-/", "/")
					path = os.path.dirname(path)
					path = path.replace("www.ualbanyphotos.com/", "").replace("photos.smugmug.com/", "")
					path = path.replace("-", " ")
					#Only for Windows paths:
					if os.name =="nt":				
						path = path.replace("/", "\\")
					destination = os.path.join(os.path.join(stagingPath, "ualbanyphotos"), path)
					#print destination
					if not os.path.isdir(destination):
						os.makedirs(destination)
					makeFile = os.path.join(destination, filename)
					href = file.find("archiveduri").text
					thumb = file.find("thumbnailurl").text
					#print href
					#download file
					
					try:
						urllib.urlretrieve(href, makeFile)
					except:
						try:
							print "failed first attempt to retrieve " + file.find("uri").text
							with open(makeFile, 'wb') as handle:
								response = requests.get(href, stream=True)
								for block in response.iter_content(1024):
									handle.write(block)
						except:
							try:
								print "failed second attempt to retrieve " + file.find("uri").text
								href = href.replace("https://", "http://")
								with open(makeFile, 'wb') as handle:
									response = requests.get(href, stream=True)
									for block in response.iter_content(1024):
										handle.write(block)
							except:
								print "failed final attempt to retrieve " + file.find("uri").text
								exceptMsg = str(traceback.format_exc())
								finalTime = time.time() - startTime
								print "Total Time: " + str(finalTime) + " seconds, " + str(finalTime/60) + " minutes, " + str(finalTime/3600) + " hours"
								print exceptMsg
								errorLog = open("errorLog.txt", "a")
								errorText = "***********************************************************************************\n" + str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n" + str(finalTime) + " seconds\n" + str(finalTime/60) + " minutes\n" + str(finalTime/3600) + " hours" + "\nTraceback:\n" + exceptMsg
								errorLog.write(errorText)
								errorLog.close()
								
					thumbDir = os.path.join(destination, "thumbs")
					if not os.path.isdir(thumbDir):
						os.makedirs(thumbDir)
					thumbName = os.path.basename(thumb)
					thumbFile = os.path.join(thumbDir, thumbName)
					try:
						urllib.urlretrieve(thumb, thumbFile)
					except:
						try:
							print "failed first attempt to retrieve thumbnail for " + file.find("uri").text
							with open(thumbFile, 'wb') as handle:
								response = requests.get(thumb, stream=True)
								for block in response.iter_content(1024):
									handle.write(block)
						except:
							try:
								print "failed second attempt to retrieve thumbnail for " + file.find("uri").text
								thumb = thumb.replace("https://", "http://")
								with open(thumbFile, 'wb') as handle:
									response = requests.get(thumb, stream=True)
									for block in response.iter_content(1024):
										handle.write(block)
							except:
								print "failed final attempt to retrieve thumbnail for " + file.find("uri").text
								exceptMsg = str(traceback.format_exc())
								finalTime = time.time() - startTime
								print "Total Time: " + str(finalTime) + " seconds, " + str(finalTime/60) + " minutes, " + str(finalTime/3600) + " hours"
								print exceptMsg
								errorLog = open("errorLog.txt", "a")
								errorText = "***********************************************************************************\n" + str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n" + str(finalTime) + " seconds\n" + str(finalTime/60) + " minutes\n" + str(finalTime/3600) + " hours" + "\nTraceback:\n" + exceptMsg
								errorLog.write(errorText)
								errorLog.close()

					if file.find("downloadTime") is None:
						downloadXML = ET.SubElement(file, "downloadTime")
						downloadXML.set("type", "posix")
						downloadXML.text = str(time.time())
					else:
						file.find("downloadTime").set("type", "posix")
						file.find("downloadTime").text = str(time.time())
					fileHash = str(md5(makeFile))
					if metaHash == "'''''":
						if fileHash in hashIndex.values():
							#issue here
							#print "hash found for " + makeFile
							#print "removing " + str(file.find("uri").text) + " from " + str(group.attrib["uri"])
							group.remove(file)
							os.remove(thumbFile)
							os.remove(makeFile)
						else:
							print makeFile + " is new"
							hashIndex.update({file.find("uri").text: fileHash})
					else:
						if file.find("archivedmd5").text == fileHash:
							hashXML = ET.SubElement(file, "hash")
							hashXML.set("type", "md5")
							hashXML.text = "success"
						else:
							hashXML = ET.SubElement(file, "hash")
							hashXML.set("type", "md5")
							hashXML.text = "failed"
						hashIndex[file.find("uri").text] = fileHash
						
							
					with open('hashIndex.json', 'w') as fp:
						simplejson.dump(hashIndex, fp)
					
			

	#count new albums and remove empty albums from images.xml
	newAlbumCount = 0
	for albumElement in imagesXML:
		#print "looking at " + str(albumElement.attrib["uri"])
		#print "count is " + str(len(albumElement.findall("image")))
		if len(albumElement.findall("image")) == 0:
			imagesXML.remove(albumElement)
		else:
			newAlbumCount = newAlbumCount + 1

	imageString = ET.tostring(imagesXML, pretty_print=True, xml_declaration=True, encoding="utf-8")
	imagesFile = open("images.xml", "w")
	imagesFile.write(imageString)
	imagesFile.close()
			

	#count files and data
	fileCount = 0
	totalSize = 0
	for root, dirs, files in os.walk(os.path.join(stagingPath, "ualbanyphotos")):
		fileCount += len(files)
		for f in files:
			fp = os.path.join(root, f)
			totalSize += os.path.getsize(fp)
	readableSize = humansize(totalSize)


	#remove empty directories
	for root, dirs, files in os.walk(os.path.join(stagingPath, "ualbanyphotos"), topdown=False):
		for folder in dirs:
			if len(os.listdir(os.path.join(root, folder))) == 0:
				print "removing " + folder
				os.rmdir(os.path.join(root, folder))
	for root, dirs, files in os.walk(os.path.join(stagingPath, "ualbanyphotos"), topdown=True):
		for folder in reversed(dirs):
			if len(os.listdir(os.path.join(root, folder))) == 0:
				print "removing " + folder
				os.rmdir(os.path.join(root, folder))

	
	#log albums and images files for crawl
	startTimeFilename = startTimeReadable.replace(":", "-").replace(" ", "_")
	shutil.copy2("images.xml", os.path.join(basePath, "arrangement"))
	#print os.path.join(basePath, "arrangement", "images.xml")
	os.rename(os.path.join(basePath, "arrangement", "images.xml"), os.path.join(basePath, "arrangement", startTimeFilename + "images.xml"))
	shutil.copy2("albums.xml", os.path.join(basePath, "arrangement"))
	os.rename(os.path.join(basePath, "arrangement", "albums.xml"), os.path.join(basePath, "arrangement", startTimeFilename + "albums.xml"))

	#make SIP metadata file
	if newAlbumCount > 0:
		collectionID = "ua395"
		accessionNumber = collectionID + "-" + str(uuid.uuid4())
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
		methodXML.text = "Crawled from Smug Mug API using ua395.py (https://github.com/UAlbanyArchives/ua395/blob/master/ua395.py)"
		locationXML = ET.SubElement(profileXML, "location")
		locationXML.text = basePath
		extentXML = ET.SubElement(profileXML, "extent")
		extentXML.set("unit", "bytes")
		extentXML.text = str(totalSize)
		extentXML.set("humanReadable", str(readableSize))


		inputImages = ET.parse(os.path.join(basePath, "images.xml"), parser)
		imagesXML = inputImages.getroot()
		inputAlbums = ET.parse(os.path.join(basePath, "albums.xml"), parser)
		albumsXML = inputAlbums.getroot()
		def makeRecord(path):
			if os.path.isdir(path):
				record = ET.Element("folder")
			else:
				record = ET.Element("file")
			record.set("name", os.path.basename(path))
			idXML = ET.SubElement(record, "id")
			idXML.text = str(uuid.uuid4())
			pathXML = ET.SubElement(record, "path")
			descriptionXML = ET.SubElement(record, "description")
			accessXML = ET.SubElement(record, "access")
			curatorialEventsXML = ET.SubElement(record, "curatorialEvents")
			recordEventsXML = ET.SubElement(record, "recordEvents")
			return record
		#loop thorugh directory and create records
		def loopAccession(path, root):
			if os.path.isdir(path):
				record = makeRecord(path)
				root.append(record)
				for item in os.listdir(path):
					root = loopAccession(os.path.join(path, item), record)
			else:
				root.append(makeRecord(path))
			return root
		sipRoot.append(loopAccession(os.path.join(stagingPath, "ualbanyphotos"), sipRoot))
		for album in imagesXML:
			albumUri = albumPath.attrib["uri"]
			for albumListing in albumsXML:
				if albumListing.find("uri").text == albumUri:
					albumRecord = albumListing

			albumPath = albumRecord.find("urlpath").text
			if albumPath.startswith("/"):
				albumPath = albumPath[1:]
			query = "/"
			for level in albumPath.split("/"):
				query = query + "/folder[@name='" + level + "']"
			albumNode = sipRoot.xpath(query)
			albumNode.find("path").text = albumPath
			unittitle = ET.Element("unittitle")
			unittitle.text = albumRecord.find("name").text
			scopecontent = ET.Element("scopecontent")
			scopecontent.text = albumRecord.find("description").text
			controlaccess = ET.Element("controlaccess")
			controlaccess.text = albumRecord.find("keywords").text
			albumNode.find("description").append(unittitle)
			albumNode.find("description").append(scopecontent)
			albumNode.find("description").append(controlaccess)
			timestamp = ET.Element("timestamp")
			timestamp.text = albumRecord.find("imageslastupdated").text
			timestamp.set("timeType", "iso8601")
			timestamp.set("parser", "SmugMug")
			albumNode.find("recordEvents").append(timestamp)

			for image in album:
				weburi = image.find("weburi").text.split("http://www.ualbanyphotos.com/")[1]
				imagePath = os.path.basename(weburi)
				if imagePath.startswith("/"):
					imagePath = imagePath[1:]
				query = "/"
				for level in imagePath.split("/"):
					query = query + "/folder[@name='" + level + "']"
				imageNode = sipRoot.xpath(query)

				imageNode.find("path").text = imagePath
				unittitle = ET.Element("unittitle")
				unittitle.text = image.find("caption").text
				controlaccess = ET.Element("controlaccess")
				controlaccess.text = image.find("keywords").text
				imageNode.find("description").append(unittitle)
				imageNode.find("description").append(controlaccess)
				event1 = ET.SubElement(imageNode.find("curatorialEvents"), "event")
				event1.text = "downloaded from SmugMug API"
				downloadTime = imageNode.find("downloadTime").text
				event1.set("timestamp", downloadTime)
				event1.set("humanTime", datetime.datetime.fromtimestamp(int(downloadTime)).strftime('%Y-%m-%d %H:%M:%S'))
				if imageNode.find("hash").text.lower() == "success":
					event2 = ET.SubElement(imageNode.find("curatorialEvents"), "event")
					event2.text = "MD5 hash matched SmugMug hash"
					event2.set("timestamp", downloadTime)
					event2.set("humanTime", datetime.datetime.fromtimestamp(int(downloadTime)).strftime('%Y-%m-%d %H:%M:%S'))
				timestamp = ET.Element("timestamp")
				timestamp.text = image.find("date").text
				timestamp.set("timeType", "iso8601")
				timestamp.set("parser", "SmugMug")
				imageNode.find("recordEvents").append(timestamp)
				#exif date
				try:
					imageFile = os.path.join(stagingPath, "ualbanyphotos", imagePath, imageNode.find("filename").text)
					with open(imagefile, "r") as img:
						tags = exifread.process_file(img, stop_tag='DateTimeOriginal')
						exifDate = tags.get("DateTimeOriginal")
						img.close()
					timestamp = ET.Element("timestamp")
					timestamp.text = exifDate
					timestamp.set("timeType", "iso8601")
					timestamp.set("parser", "exifread")
					timestamp.set("label", "DateTimeOriginal")
					imageNode.find("recordEvents").append(timestamp)

				except:
					exceptMsg = str(traceback.format_exc())
					print exceptMsg

		metadataString = ET.tostring(sipRoot, pretty_print=True, xml_declaration=True, encoding="utf-8")
		metadataFile = open(os.path.join(stagingPath), accessionNumber + ".xml", "w")
		metadataFile.write(metadataString)
		metadataFile.close()
		
		#createSIP.py


	else:
		os.remove(os.path.join(stagingPath, "ualbanyphotos"))


	#update log.txt
	finalTime = time.time() - startTime
	print "Total Time: " + str(finalTime) + " seconds, " + str(finalTime/60) + " minutes, " + str(finalTime/3600) + " hours"
	finalTimeFile = open("log.txt", "a")
	logText = "\nSuccessful Crawl ran " + str(time.strftime("%Y-%m-%d %H:%M:%S"))
	logText = logText + "\nProcess took " + str(finalTime) + " seconds or " + str(finalTime/60) + " minutes or " + str(finalTime/3600) + " hours"
	logText = logText + "\n" + str(newAlbumCount) + " new albums found"
	logText = logText + "\n" + str(fileCount) + " files downloaded"
	logText = logText + "\n" + str(totalSize) + " bytes or " + str(readableSize) + " downloaded"
	finalTimeFile.write(logText)
	finalTimeFile.close()

	
except:
	exceptMsg = str(traceback.format_exc())

	updateLog = open("log.txt", "a")
	logText = "\nCrawl failed at " + str(time.strftime("%Y-%m-%d %H:%M:%S"))
	updateLog.write(logText)
	updateLog.close()

	finalTime = time.time() - startTime
	print "Total Time: " + str(finalTime) + " seconds, " + str(finalTime/60) + " minutes, " + str(finalTime/3600) + " hours"
	print exceptMsg
	errorLog = open("errorLog.txt", "a")
	errorText = "***********************************************************************************\n" + str(time.strftime("%Y-%m-%d %H:%M:%S")) + "\n" + str(finalTime) + " seconds\n" + str(finalTime/60) + " minutes\n" + str(finalTime/3600) + " hours" + "\nTraceback:\n" + exceptMsg
	errorLog.write(errorText)
	errorLog.close()


	#needs:
	#Remove empty folders
	#create metadata file for SIP