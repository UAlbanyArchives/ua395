import os
from lxml import etree as ET


if os.name == "nt":
	templateFile = "\\\\romeo\\wwwroot\\eresources\\digital_objects\\ua395\\template.html"
	eadFile = ""
	daoDir = ""
	metaDir = ""
else:
	templateFile = "/media/bcadmin/wwwroot/eresources/digital_objects/ua395/template.html"
	eadFile = "/media/bcadmin/Collect/spe/Tools/collections/ua395.xml"
	daoDir = "/media/bcadmin/wwwroot/eresources/digital_objects/ua395"
	metaDir = "/media/bcadmin/Lincoln/Special Collections/accessions/SIP"


parser = ET.XMLParser(remove_blank_text=True)
eadXML = ET.parse(eadFile, parser)
ead = eadXML.getroot()

				


for dao in ead.iterfind(".//dao"):
	cmpnt = dao.getparent().getparent()
	unitId = cmpnt.attrib["id"]

	for para in cmpnt.find("acqinfo"):
		if "Accession: " in para.find("date").tail:
			accessionNumber = para.find("date").tail.split("Accession: ")[1]

	sipDir = os.path.join(metaDir, accessionNumber)
	parser = ET.XMLParser(remove_blank_text=True)
	metadataFile = ET.parse(os.path.join(sipDir, accessionNumber + ".xml"), parser)
	metaRoot = metadataFile.getroot()
	for folder in metaRoot:
		if folder.tag == "folder":
			if folder.find("description").text == cmpnt.find("did/unittitle").text:
				metaRecord = folder

	folderSip = os.path.join(daoDir, cmpnt.attrib["id"].split("-")[1].split("_")[0])

	parser = ET.XMLParser(remove_blank_text=True)
	templateInput = ET.parse(templateFile, parser)
	template = templateInput.getroot()

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

	
	for root, dirs, files in os.walk(folderSip):
			for imageFile in files:
				if not imageFile.lower() == "thumbs.db":
					image = os.path.join(root, imageFile)


	for child in metaRecord:
			print child.attrib["name"]
			if not child.attrib["name"].lower() == "thumbs.db":
				if child.attrib["name"] == imageFile:
					print "found Match :)"
			
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


	htmlString = ET.tostring(template, pretty_print=True, method='html', xml_declaration=False, doctype="<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
	
	#htmlWrite = open(os.path.join(dipDir, cmpnt.attrib["id"] + ".html"), "w")
	htmlWrite = open(os.path.join("/home/bcadmin/Desktop/Processing/ua395/testDir", cmpnt.attrib["id"] + ".html"), "w")
	htmlWrite.write(htmlString)
	htmlWrite.close()
	"""

	f = open("testOut2.html", "wb")
	f.write(htmlString)
	f.close()
	"""