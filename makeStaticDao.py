import os
from lxml import etree as ET


if os.name == "nt":
	templateFile = "\\\\romeo\\wwwroot\\eresources\\digital_objects\\ua395\\template.html"
else:
	templateFile = "/media/bcadmin/wwwroot/eresources/digital_objects/ua395/template.html"


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