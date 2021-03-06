#!/usr/bin/python
#Copyright 2008-2009 InnomiNet
"""Handles submitting bug reports automatically"""

import os
import time

from common import Globals
from common.system import Files
from common.system import System
from common.utils.Basic import log_msg, log_ex, _ # pylint: disable-msg=W0611
from core import ClientUtil
from core import SendFileOverFTP
from gui import GUIController
import Applications.Tor
from Applications import CoreSettings

def check_previous_logs():
  try:
    #check to see if we closed cleanly before we start_logs!
    errorFile = os.path.join(Globals.LOG_FOLDER, 'errors.out')
    shutdownMarkerFileName = os.path.join(Globals.LOG_FOLDER, 'closedcleanly.txt')
    failedToCloseCleanlyLastTime = Files.file_exists(shutdownMarkerFileName)
    wasErrorLastTime = Files.file_exists(errorFile) and os.path.getsize(errorFile) != 0
    
    #submit error log
    if failedToCloseCleanlyLastTime or wasErrorLastTime:
      startTime = time.time()
      ClientUtil.create_error_archive("autogenerated")
      log_msg("Took %.2f seconds to zip error logs" % (time.time() - startTime), 2)
    #remove error log
    else:
      Files.delete_file(Globals.BUG_REPORT_NAME, True)
  except Exception, error:
    log_ex(error, "Failed to make error report!")
    
def create_marker_file():
  """Creating file to determine if we close cleanly"""
  shutdownMarkerFileName = os.path.join(Globals.LOG_FOLDER, 'closedcleanly.txt')
  shutdownMarkerFile = open(shutdownMarkerFileName, "wb")
  shutdownMarkerFile.write('creating file to determine if we close cleanly')
  shutdownMarkerFile.close()
  
def destroy_marker_file():
  fileName = os.path.join(Globals.LOG_FOLDER, 'closedcleanly.txt')
  encodedFileName = System.encode_for_filesystem(fileName)
  os.remove(encodedFileName)

def send_error_report():
  filename = str(Applications.Tor.get().settings.name)+'@'+Globals.VERSION+'@'+str(int(time.time()))
  return SendFileOverFTP.SendFileOverFTP(Globals.BUG_REPORT_NAME, filename)
  
def has_report_to_send():
  return Files.file_exists(Globals.BUG_REPORT_NAME)
  
def prompt_about_bug_report():
  coreSettings = CoreSettings.get()
  def response(dialog, response):
    if response == 0:
      coreSettings.sendBugReports = True
      send_error_report()
    else:
      coreSettings.sendBugReports = False
    coreSettings.save()
  if not coreSettings.askedAboutBugReports:
    GUIController.get().show_msgbox("BitBlinder had errors or crashed last time it was run.  Is it ok to send the anonymized error report to the developers?  If you dont, they will not be able to fix the errors!  :(", title="Please Send Us Your Errors!", cb=response, buttons=("Yes, send anonymous crash data", 0, "No", 1), width=400)
    coreSettings.askedAboutBugReports = True
    coreSettings.save()
  elif coreSettings.sendBugReports:
    send_error_report()
    
    
