import os
import csv
import sys

processingDir = os.path.dirname(os.path.realpath(__file__))

if os.name == "nt":
	sipDir = "\\\\Lincoln\\Special Collections\\accessions\\SIP"
else:
	sipDir = "/media/bcadmin/Lincoln/Special Collections/accessions/SIP"

newInput = os.path.join(processingDir, "arrangmentDraft3.csv")
checkFile = open(newInput, "r")
checkList = csv.reader(checkFile, delimiter='|')
check = []
for row in checkList:
	check.append(row[6])
checkFile.close()

finalList = []

mainInput = os.path.join(processingDir, "arrangmentDraft2.csv")
mainFile = open(mainInput, "r")
mainList = csv.reader(mainFile, delimiter='|')

rowCount = 0
for albumRow in mainList:
	rowCount = rowCount + 1
	print "row " + str(rowCount)

	path = albumRow[6]
	folderDir = "disk" + path.split("\\disk")[1].replace("\\", "/")
	print "attempting to match: " + folderDir

	matchCount = False
	newCount = 0
	newFile = open(newInput, "r")
	newList = csv.reader(newFile, delimiter='|')
	for newRow in newList:
		newCount = newCount + 1
		if newCount == 1:
			pass
		else:
			newPath = newRow[6]
			pathMatch = "disk" + newPath.split("/disk")[1]
			if folderDir == pathMatch:
				print "match found"
				finalPath = os.path.join(sipDir, newRow[8].split(".")[0], "data", "data", pathMatch.split("/")[1])
				if os.path.isdir(finalPath):
					albumRow[5] = newRow[5]
					albumRow[6] = finalPath
					albumRow[7] = newRow[7]
					albumRow[8] = newRow[8]

					matchCount = True
					check.remove(newPath)
				else:
					print "PATH ERROR"
					print finalPath
					print path
					print pathMatch
					sys.exit()
	newFile.close()

	if matchCount == False:
		print "MATCH ERROR"
		print path
		print folderDir
		sys.exit()


	finalList.append(albumRow)

print check

with open(os.path.join(processingDir, "arrangmentDraftFinal.csv"), "wb") as f:
	writer = csv.writer(f, delimiter='|')
	writer.writerows(finalList)