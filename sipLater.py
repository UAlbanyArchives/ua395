import subprocess
import time

#time.sleep(8000)

#createSIP.py
print "bagging SIP"
rootDir = "\\\\romeo\\SPE\\Electronic_Records_Library\\ua395"

for xml in rootDir:
	if xml.endswith(".xml"):
		accesssionFile = os.path.join(rootDir, xml)
		
sipCmd = "python C:\\Projects\\createSIP\\createSIP.py -m " + accesssionFile + " -v " + os.path.join(rootDir, "fromDVDs4")
print sipCmd
createSIP = Popen(sipCmd, shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = createSIP.communicate()
if len(stderr) > 0:
	print stderr
if len(stdout) > 0:
	print stderr