import os
from imagemounter import ImageParser
from subprocess import Popen, PIPE
from lxml import etree as ET
from wand.image import Image

imageDir = "/home/bcadmin/Documents/ua395-1ea0335f-4759-4b1a-a7f7-ca15aac3ba19/data/ua395"
workingDir = "/home/bcadmin/Documents"

outputDir = "/home/bcadmin/Documents/fromDVDs"
if not os.path.isdir(outputDir):
	print "making outputDir"
	os.mkdir(outputDir)

count = 0
for diskImage in os.listdir(imageDir):
	#for limiting images for testing purposes
	count = count + 1
	if count == 2:
	#if diskImage == "disk6ba01c70-4900-4012-a393-8cc59c817b25.dd":
		print diskImage
		diskOutput = os.path.join(outputDir, diskImage)
		if not os.path.isdir(diskOutput):
			os.makedirs(diskOutput)
		outputXML = os.path.join(workingDir, diskImage + ".xml")
		fiwalk = Popen(["fiwalk", "-z", "-X", outputXML, os.path.join(imageDir, diskImage)], shell=False, stdout=PIPE, stderr=PIPE)
		stdout, stderr = fiwalk.communicate()

		fullNamesList = []
		fullNameSwitch = False
		"""for joliet extensions ISO9660 only, not udf
		isoinfo = Popen(["isoinfo", "-f", "-J", "-i", os.path.join(imageDir, diskImage)], shell=False, stdout=PIPE, stderr=PIPE)
		stdout, stderr = isoinfo.communicate()
		if len(stderr) > 1:
			print stderr
			fullNameSwitch = False
		if len(stdout) > 1:
			print stdout
			fullNameSwitch = True
			for line in stdout.split("\n"):
				fullNamesList.append(line.split(";")[0])
		"""

		"""for debugging
		fullNameOut = open("fullNameOut.txt", "w")
		for name in fullNamesList:
			fullNameOut.write("%s\n" % name)
		fullNameOut.close()
		"""

		parser = ET.XMLParser(remove_blank_text=True)
		fiwalkInput = ET.parse(outputXML, parser)
		fiwalkXML = fiwalkInput.getroot()
		ns = "{http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML}"
		fileList = []
		for volume in fiwalkXML:
			if volume.tag == ns + "volume":
				for fileobject in volume:
					if fileobject.tag == ns + "fileobject":
						filename = fileobject.find(ns + "filename").text
						if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
							if int(fileobject.find(ns + "filesize").text) > 2000000:
								fileList.append(os.path.splitext(filename.lower())[0])
								fileList.append(os.path.splitext(os.path.join(os.path.split(os.path.dirname(filename))[0], os.path.basename(filename)).lower())[0])
				fileCount = len(volume.findall(ns + "fileobject"))
				if fileCount == 0:
					print "ERROR: no file object in " + diskImage
					errorLog = open("errorLog.txt", "w")
					errorLog.write("\nERROR: no file objects found in " + diskImage)
					errotLog.close()
				for fileobject in volume:
					if fileobject.tag == ns + "fileobject":
						filename = fileobject.find(ns + "filename").text
						inode = fileobject.find(ns + "inode").text
						filePath = os.path.dirname(filename)
						#print filePath
						if fullNameSwitch == True:

							newPath = os.path.join(diskOutput, filePath)
						else:
							newPath = os.path.join(diskOutput, filePath)
						if not os.path.isdir(newPath):
							os.makedirs(newPath)
						extention = filename.lower()[-4:]
						extentionList = [".nef", ".crw", ".cr2", ".dng", ".raw", ".raf"]
						#get all jpgs or pngs
						if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg") or filename.lower().endswith(".png"):
							if int(fileobject.find(ns + "filesize").text) > 2000000:
								outfile = os.path.join(newPath, os.path.basename(filename))
								icatCmd = "icat -f iso9660 -i raw \"" + os.path.join(imageDir, diskImage) + "\" " + inode + " > \"" + outfile + "\""
								#print icatCmd
								icat = Popen(icatCmd, shell=True, stdout=PIPE, stderr=PIPE)
								stdout, stderr = icat.communicate()
								if len(stderr) > 0:
									print "icat JPEG error: " + stderr
						#get all raw images
						elif extention in extentionList:
							if os.path.splitext(filename)[0].lower() in fileList:
								print "jpg already created for " + os.path.basename(filename)
							elif os.path.splitext(os.path.join(os.path.split(os.path.dirname(filename))[0], os.path.basename(filename)))[0].lower() in fileList:
								print "jpg already created for " + os.path.basename(filename)
							else:
								outfile = os.path.join(newPath, os.path.basename(filename))
								icatCmd = "icat -f iso9660 -i raw \"" + os.path.join(imageDir, diskImage) + "\" " + inode + " > \"" + outfile + "\""
								#print icatCmd
								icat = Popen(icatCmd, shell=True, stdout=PIPE, stderr=PIPE)
								stdout, stderr = icat.communicate()
								if len(stderr) > 0:
									print "icat raw error: " + stderr
				
				#convert raw images
				for root, dirs, files in os.walk(newPath):
					for file in files:
						if os.path.getsize(os.path.join(root, file)) > 0:
							fileExt = os.path.splitext(file)[1]
							if fileExt.lower() in extentionList:
								print "converting " + file
								convertCmd = ["convert \"" + os.path.join(root, file) + "\" \"" + os.path.join(root, os.path.splitext(file)[0]) + ".JPG\""]
								convert = Popen(convertCmd, shell=True, stdout=PIPE, stderr=PIPE)
								stdout, stderr = convert.communicate()
								if len(stderr) > 0:
									print "JPEG error: " + stderr
								else:
									os.remove(os.path.join(root, file))


		os.remove(outputXML)
		#print diskImage