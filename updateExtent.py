# coding: utf-8

import os
from lxml import etree as ET
import math


eadFile = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395\\ua395T.xml"

parser = ET.XMLParser(remove_blank_text=True)
eadInput = ET.parse(eadFile, parser)
ead = eadInput.getroot()

	

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

eadString = ET.tostring(ead, pretty_print=True, xml_declaration=True, encoding="utf-8")
eadOutput = open(eadFile, "w")
eadOutput.write(eadString)
eadOutput.close()