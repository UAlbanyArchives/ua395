import os
from imagemounter import ImageParser
from subprocess import Popen, PIPE
from lxml import etree as ET
import time

imageDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/dvdImages"
workingDir = "/home/bcadmin/Documents"

outputDir = "/media/bcadmin/SPE/Electronic_Records_Library/ua395/fromDVDs2"

root = ET.Element("photosFromDVD")
errorRoot = ET.Element("errors")

def foundError(errorRoot, reason, imageFile, filename, inode, fileSize, outputPath):
	error = ET.SubElement(errorRoot, "error")
	error.set("reason", reason)
	image = ET.SubElement(error, "imageFile")
	image.text = imageFile
	file = ET.SubElement(error, "filename")
	file.text = filename
	inodeNumber = ET.SubElement(error, "inode")
	inodeNumber.text = inode
	size = ET.SubElement(error, "fileSize")
	size.text = fileSize
	output = ET.SubElement(error, "outputPath")
	output.text = outputPath
	return errorRoot

startTime = time.time()
startTimeReadable = str(time.strftime("%Y-%m-%d %H:%M:%S"))
print startTimeReadable

#remove tifs
"""
for rootDir, dirNames, allFiles in os.walk(outputDir):
	for tif in allFiles:
		if tif.lower().endswith(".tif") or tif.lower().endswith(".tiff"):
			print "removing " + str(tif)
			os.remove(os.path.join(rootDir, tif))
"""

photoCount = 0
count = 0
totalVerified = 0
extentionList = "jpg"
totalImageCount = len(os.listdir(imageDir))
diskStartTime = time.time()
for diskImage in os.listdir(imageDir):
	#for limiting images for testing purposes
	count = count + 1
	if count > 0:
		diskProcessTime = time.time() - diskStartTime
		diskStartTime = time.time()
		print "Process took " + str(diskProcessTime) + " seconds or " + str(diskProcessTime/60) + " minutes or " + str(diskProcessTime/3600) + " hours"
		print diskImage
		print str(count) + " of " + str(totalImageCount)
		imageFile = ET.SubElement(root, "imageFile")
		jpegList = []
		newJpegList = []
		diskOutput = os.path.join(outputDir, diskImage)
		if not os.path.isdir(diskOutput):
			outputDirCheck = ET.SubElement(imageFile, "outputDirCheck")
			outputDirCheck.text = "False"
		else:
			outputDirCheck = ET.SubElement(imageFile, "outputDirCheck")
			outputDirCheck.text = "True"
		fiwalkFile = os.path.join(workingDir, diskImage + ".xml")
		fiwalk = Popen(["fiwalk", "-z", "-X", fiwalkFile, os.path.join(imageDir, diskImage)], shell=False, stdout=PIPE, stderr=PIPE)
		stdout, stderr = fiwalk.communicate()
		if len(stdout) > 0:
			print stdout
			fiwalkOutput = ET.SubElement(imageFile, "fiwalkOutput")
			fiwalkOutput.text = stdout
		if len(stderr) > 0:
			print stderr
			fiwalkOutput = ET.SubElement(imageFile, "fiwalkOutput")
			fiwalkOutput.text = stderr
		
		parser = ET.XMLParser(remove_blank_text=True)
		fiwalkInput = ET.parse(fiwalkFile, parser)
		fiwalkXML = fiwalkInput.getroot()
		ns = "{http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML}"

		volumeCount = len(fiwalkXML.findall(ns + "volume"))
		imageFile.set("volumeCount", str(volumeCount))
		imageFile.set("imageName", str(diskImage))
		for volume in fiwalkXML:
			if volume.tag == ns + "volume":

				fileCount = len(volume.findall(ns + "fileobject"))
				imageFile.set("fileCount", str(fileCount))

				jpegCount = 0
				jpegOutfile = 0
				jpegVerified = 0

				knownRawCount = 0
				knownRawVerified = 0
				knownRawOutfile = 0
				knownRawConverted = 0
				knownRawConvertedVerified = 0

				otherRawCount = 0
				otherRawVerified = 0
				otherRawOutfile = 0
				otherRawConvertedOutfile = 0
				otherRawConvertedVerified = 0

				otherFiles = 0
				otherVerified = 0
				otherOutfile = 0
				otherOutfileConverted = 0
				otherOutfileConvertedVerified = 0
				#get all original JPEGS
				for fileobject in volume:
					if fileobject.tag == ns + "fileobject":
						filename = fileobject.find(ns + "filename").text
						if filename == "." or filename == "..":
							pass
						elif filename.lower().endswith("/.") or filename.lower().endswith("/.."):
							pass
						elif filename.lower().endswith(".db") or filename.lower().endswith(".xmp") or filename.lower().endswith(".htm") or filename.lower().endswith(".html") or filename.lower().endswith(".txt"):
							pass
						elif filename.lower().endswith(".bridgesort") or filename.lower().endswith(".ds_store"):
							pass
						elif filename.lower().endswith("$orphanfiles"):
							pass
						elif filename.lower().endswith(".doc") or filename.lower().endswith(".pdf") or filename.lower().endswith(".tmp"):
							pass
						elif filename.lower().endswith(".pe3") or filename.lower().endswith(".lnk") or filename.lower().endswith(".bib"):
							pass
						else:
							filePath = os.path.dirname(filename)
							outfile = os.path.join(diskOutput, filePath, os.path.basename(filename))
							if os.path.isdir(outfile):
								pass
							else:
								if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
									if int(fileobject.find(ns + "filesize").text) > 2000000:
										jpegList.append(os.path.splitext(os.path.basename(filename))[0])
									if int(fileobject.find(ns + "filesize").text) > 200000:
										newJpegList.append(os.path.splitext(os.path.basename(filename))[0])

				for fileobject in volume:
					if fileobject.tag == ns + "fileobject":


						filename = fileobject.find(ns + "filename").text
						if filename == "." or filename == "..":
							pass
						elif filename.lower().endswith("next.gif") or filename.lower().endswith("previous.gif") or filename.lower().endswith("home.gif"):
							pass
						elif filename.lower().endswith("/.") or filename.lower().endswith("/.."):
							pass
						elif filename.lower().endswith(".db") or filename.lower().endswith(".xmp") or filename.lower().endswith(".htm") or filename.lower().endswith(".html") or filename.lower().endswith(".txt"):
							pass
						elif filename.lower().endswith(".bridgesort") or filename.lower().endswith(".ds_store"):
							pass
						elif filename.lower().endswith("$orphanfiles"):
							pass
						elif filename.lower().endswith(".doc") or filename.lower().endswith(".pdf") or filename.lower().endswith(".tmp"):
							pass
						elif filename.lower().endswith(".pe3") or filename.lower().endswith(".lnk") or filename.lower().endswith(".bib"):
							pass
						else:


							extention = os.path.splitext(filename)[1]
							if not extention in extentionList:
								extentionList = extentionList + ", " + extention

							filePath = os.path.dirname(filename)
							outfile = os.path.join(diskOutput, filePath, os.path.basename(filename))
							if os.path.isdir(outfile):
								pass
							else:

								inode = fileobject.find(ns + "inode").text
								fileSize = fileobject.find(ns + "filesize").text

								if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
									if int(fileobject.find(ns + "filesize").text) <= 2000000:
										if int(fileobject.find(ns + "filesize").text) > 200000:
											#extract jpg
											icatCmd = "icat -f iso9660 -i raw \"" + os.path.join(imageDir, diskImage) + "\" " + inode + " > \"" + outfile + "\""
											print "extracting " + str(filename)
											icat = Popen(icatCmd, shell=True, stdout=PIPE, stderr=PIPE)
											stdout, stderr = icat.communicate()
											if len(stderr) > 0:
												print "icat raw error: " + stderr

									else:
										photoCount = photoCount + 1
								else:
									if not os.path.splitext(os.path.basename(filename))[0] in jpegList:
										photoCount = photoCount + 1

								if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
									if int(fileobject.find(ns + "filesize").text) > 2000000:
										jpegCount = jpegCount + 1
										
										if os.path.isfile(outfile):
											jpegOutfile = jpegOutfile + 1
											if os.path.getsize(outfile) > 0:
												jpegVerified = jpegVerified + 1
											else:
												errorRoot = foundError(errorRoot, "original JPG no size", diskImage, filename, inode, fileSize, outfile)
										else:
											errorRoot = foundError(errorRoot, "original JPG icat error", diskImage, filename, inode, fileSize, outfile)

									

								elif os.path.splitext(os.path.basename(filename))[0] in newJpegList:
									#remove converted JPG
									print "removing " + filename
									originalOutfile = outfile
									outfile = os.path.splitext(outfile)[0] + ".JPG"
									if os.path.isfile(outfile):
										os.remove(outfile)									


								elif filename.lower().endswith(".nef") or filename.lower().endswith(".cr2"):
									if os.path.splitext(os.path.basename(filename))[0] in jpegList:
										#Jpeg already verified
										pass
									else:
										knownRawCount = knownRawCount + 1
										if os.path.isfile(outfile):
											knownRawOutfile = knownRawOutfile + 1
											if os.path.getsize(outfile) > 0:
												knownRawVerified = knownRawVerified + 1
												errorRoot = foundError(errorRoot, "raw verified not converted", diskImage, filename, inode, fileSize, outfile)
											else:
												errorRoot = foundError(errorRoot, "raw not converted no size", diskImage, filename, inode, fileSize, outfile)
										else:
											originalOutfile = outfile
											outfile = os.path.splitext(outfile)[0] + ".JPG"

											if os.path.isfile(outfile):
												knownRawConverted = knownRawConverted + 1
												if os.path.getsize(outfile) > 0:
													knownRawConvertedVerified = knownRawConvertedVerified + 1
												else:
													errorRoot = foundError(errorRoot, "raw converted no size", diskImage, filename, inode, fileSize, outfile)
											else:
												errorRoot = foundError(errorRoot, "raw icat error", diskImage, filename, inode, fileSize, originalOutfile)
									

								elif filename.lower().endswith(".crw") or filename.lower().endswith(".dng") or filename.lower().endswith(".raw") or filename.lower().endswith(".raf"):
									if os.path.splitext(os.path.basename(filename))[0] in jpegList:
										#Jpeg already verified
										pass
									else:
										otherRawCount = otherRawCount + 1
										if os.path.isfile(outfile):
											otherRawOutfile = otherRawOutfile + 1
											if os.path.getsize(outfile) > 0:
												otherRawVerified = otherRawVerified + 1
												errorRoot = foundError(errorRoot, "other raw verified not converted", diskImage, filename, inode, fileSize, outfile)
											else:
												errorRoot = foundError(errorRoot, "other raw not converted no size", diskImage, filename, inode, fileSize, outfile)
										else:
											originalOutfile = outfile
											outfile = os.path.splitext(outfile)[0] + ".JPG"
											if os.path.isfile(outfile):
												otherRawConvertedOutfile = otherRawConvertedOutfile + 1
												if os.path.getsize(outfile) > 0:
													otherRawConvertedVerified = otherRawConvertedVerified + 1
											else:
												errorRoot = foundError(errorRoot, "other raw icat error", diskImage, filename, inode, fileSize, originalOutfile)
										

								else:
									if os.path.splitext(os.path.basename(filename))[0] in jpegList:
										#Jpeg already verified
										pass
									else:
										otherFiles = otherFiles + 1
										if os.path.isfile(outfile):
											otherOutfile = otherOutfile + 1
											if os.path.getsize(outfile) > 0:
												otherVerified = otherVerified + 1
												errorRoot = foundError(errorRoot, "other file verified not converted", diskImage, filename, inode, fileSize, outfile)
											else:
												errorRoot = foundError(errorRoot, "other file not converted no size", diskImage, filename, inode, fileSize, outfile)
										else:
											originalOutfile = outfile
											outfile = os.path.splitext(outfile)[0] + ".JPG"
											if os.path.isfile(outfile):
												otherOutfileConverted = otherOutfileConverted + 1
												if os.path.getsize(outfile) > 0:
													otherOutfileConvertedVerified = otherOutfileConvertedVerified + 1
											else:
												outExt = os.path.splitext(originalOutfile)[1].lower()
												if outExt == ".tif" or outExt == ".tiff" or outExt == ".psd":
													#print "extracting " + originalOutfile
													errorRoot = foundError(errorRoot, "other file icat error", diskImage, filename, inode, fileSize, originalOutfile)
													"""
													icatCmd = "icat -f iso9660 -i raw \"" + os.path.join(imageDir, diskImage) + "\" " + inode + " > \"" + originalOutfile + "\""
													#print icatCmd
													icat = Popen(icatCmd, shell=True, stdout=PIPE, stderr=PIPE)
													stdout, stderr = icat.communicate()
													if len(stderr) > 0:
														print "icat error for: " +filename + " " + stderr

													print "converting " + filename
													convertCmd = ["convert \"" + originalOutfile + "\" \"" + os.path.splitext(originalOutfile)[0] + ".JPG\""]
													convert = Popen(convertCmd, shell=True, stdout=PIPE, stderr=PIPE)
													stdout, stderr = convert.communicate()
													if len(stderr) > 0:
														print "Convert error for: " + originalOutfile + " " + stderr
													else:
														print "conversion successful"
														os.remove(originalOutfile)
													"""

				if jpegVerified == 0:
					jpegVerifiedPer = 0
				else:
					jpegVerifiedPer = 100 * float(jpegVerified)/float(jpegCount)
				if knownRawConvertedVerified == 0:
					rawVerifiedPer = 0
				else:
					rawVerifiedPer = 100 * float(knownRawConvertedVerified)/float(knownRawCount)
				if otherRawConvertedVerified == 0:
					otherRawVerifiedPer = 0
				else:
					otherRawVerifiedPer = 100 * float(otherRawConvertedVerified)/float(otherRawCount)
				if otherOutfileConvertedVerified == 0:
					otherVerifiedPer = 0
				else:
					otherVerifiedPer = 100 * float(otherOutfileConvertedVerified)/float(otherFiles)

				jpegElement = ET.SubElement(imageFile, "jpegCount")
				jpegElement.text = str(jpegCount)
				jpegElement.set("verifiedPer", str(jpegVerifiedPer))
				jpegElement.set("verified", str(jpegVerified))
				jpegElement.set("outfile", str(jpegOutfile))

				rawElement = ET.SubElement(imageFile, "knownRawCount")
				rawElement.text = str(knownRawCount)
				rawElement.set("verifiedPer", str(rawVerifiedPer))
				rawElement.set("verified", str(knownRawConvertedVerified))
				rawElement.set("outfile", str(knownRawConverted))
				rawElement.set("unconverted", str(knownRawOutfile))
				rawElement.set("unconvertedVertified", str(knownRawVerified))

				otherRawElement = ET.SubElement(imageFile, "otherRawCount")
				otherRawElement.text = str(otherRawCount)
				otherRawElement.set("verifiedPer", str(otherRawVerifiedPer))
				otherRawElement.set("verified", str(otherRawConvertedVerified))
				otherRawElement.set("outfile", str(otherRawConvertedOutfile))
				otherRawElement.set("unconverted", str(otherRawOutfile))
				otherRawElement.set("unconvertedVertified", str(otherRawVerified))

				otherFileElement = ET.SubElement(imageFile, "otherFiles")
				otherFileElement.text = str(otherFiles)
				otherFileElement.set("verifiedPer", str(otherVerifiedPer))
				otherFileElement.set("verified", str(otherOutfileConvertedVerified))
				otherFileElement.set("outfile", str(otherOutfileConverted))
				otherFileElement.set("unconverted", str(otherOutfile))
				otherFileElement.set("unconvertedVertified", str(otherVerified))

				totalVerified = totalVerified + jpegVerified + knownRawConvertedVerified + otherRawConvertedVerified + otherOutfileConvertedVerified
		os.remove(fiwalkFile)

if totalVerified == 0:
	totalVerifiedPer = 0
else:
	totalVerifiedPer = 100 * float(totalVerified)/float(photoCount)

totalUnconverted = knownRawOutfile + otherRawOutfile + otherOutfile
totalUnconvertedVerified = knownRawVerified + otherRawVerified + otherVerified



root.set("verifiedPer", str(totalVerifiedPer))
root.set("totalVerified", str(totalVerified))
root.set("totalPhotos", str(photoCount))
root.set("totalUnconverted", str(totalUnconverted))
root.set("totalUnconvertedVerified", str(totalUnconvertedVerified))
problemDisks = ET.Element("problemDisks")
errorList = []
for diskRecord in root:
	errorSwitch = False
	for photoType in diskRecord:
		if photoType.tag == "outputDirCheck":
			pass
		elif photoType.attrib["verifiedPer"] == "0" or photoType.attrib["verifiedPer"] == "100.0":
			pass
		else:
			errorSwitch = True
	if errorSwitch == True:
		errorList.append(diskRecord.attrib["imageName"])
for problem in errorList:
	problemElement = ET.SubElement(problemDisks, "problem")
	problemElement.text = str(problem)
extentionListElement = ET.Element("extentionList")
extentionListElement.text = str(extentionList)
root.insert(0, extentionListElement)
root.insert(0, problemDisks)

XMLString = ET.tostring(root, pretty_print=True)
file = open(os.path.join(workingDir, "verifyReport.xml"), "w")
file.write(XMLString)
file.close()

#make Human-readable
#from here: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
from math import log
unit_list = zip(['bytes', 'KB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def sizeof_fmt(num):
	"""Human friendly file size"""
	if num > 1:
		exponent = min(int(log(num, 1024)), len(unit_list) - 1)
		quotient = float(num) / 1024**exponent
		unit, num_decimals = unit_list[exponent]
		format_string = '{:.%sf} {}' % (num_decimals)
		return format_string.format(quotient, unit)
	if num == 0:
		return '0 bytes'
	if num == 1:
		return '1 byte'


errorCount = 0
errorSize = 0
extList = ".tif"
for errorFile in errorRoot:
	errorCount = errorCount + 1
	errorSize = errorSize + int(errorFile.find("fileSize").text.split(".")[0])
	ext = os.path.splitext(errorFile.find("filename").text)[1].lower()
	if not ext in extList:
		extList = extList + ", " + ext
avgSize = errorSize / errorCount
errorRoot.set("averageSizeHuman", str(sizeof_fmt(avgSize)))
errorRoot.set("averageSize", str(avgSize))
errorRoot.set("extensionList", str(extList))


errorString = ET.tostring(errorRoot, pretty_print=True)
file = open(os.path.join(workingDir, "errorFiles.xml"), "w")
file.write(errorString)
file.close()