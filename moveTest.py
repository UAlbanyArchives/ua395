import os
import shutil
import smtplib

eadFile = "\\\\romeo\\Collect\\spe\\Greg\\Processing\\ua395\\ua395.xml"
zeta = "\\\\zeta\\xtf\\data"

shutil.copy2(eadFile, zeta)

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