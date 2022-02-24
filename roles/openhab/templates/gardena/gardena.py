# Copyright (c) 2019 by Christian Schnidrig.

# https://github.com/TooTallNate/Java-WebSocket

# jython imports
from org.slf4j import LoggerFactory
import uuid
import math
import sys
import traceback
import time
import json
import jsonmerge

# java imports
#from org.eclipse.smarthome.core.scheduler import CronExpression
import profile
from org.yaml.snakeyaml import Yaml
from java.nio.file.StandardWatchEventKinds import ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY
try:
    from org.openhab.core.service import AbstractWatchService
except:
    from org.eclipse.smarthome.core.service import AbstractWatchService

#######################################################
#######################################################
#######################################################
# constants

module_name = "gardena"
logger_name = "jython." + module_name
module_prefix = module_name + "_"

# location of script
openhab_base_dir = '/etc/openhab2'
automationDir = openhab_base_dir + '/automation'
gardenaDir = automationDir + '/gardena'
gardena_config_file_name = 'gardena.yml'
gardena_config_file = gardenaDir + '/' + gardena_config_file_name
gardena_data_file_name = 'gardena.json'
gardena_data_file = gardenaDir + '/' + gardena_data_file_name

#######################################################
# some globals
config = None
data = None

# default logger
logger = LoggerFactory.getLogger(logger_name)

#######################################################
#######################################################
#######################################################
# config
class Config():
  def __init__(self):
    self.logger = LoggerFactory.getLogger(logger_name + ".Config")
    self.gardenaConfig = Yaml().load(open(gardena_config_file))
    self.logger.info("Config loaded")

  def getDeviceMapping(self):
    return self.gardenaConfig['device_mapping']

  def getItemNamePrefix(self):
    return self.gardenaConfig['item_name_prefix']

  def getValueMapping(self):
    return self.gardenaConfig['value_mapping']

#######################################################
#######################################################
#######################################################
# gardena monitor

def gardena_monitor():
  logger = LoggerFactory.getLogger(logger_name + ".gardena_monitor")
  config = Config()

  device_mapping = config.getDeviceMapping()

  data = {}

  with open (gardena_data_file, "r") as data_file:
    lines=data_file.readlines()
    for line in lines:
      json_line = json.loads(line)
      if 'attributes' in json_line.keys():
        data = jsonmerge.merge(data, {json_line['type']: { json_line['id']: json_line['attributes'] }})
  
  logger.debug(json.dumps(data, indent=4))
  value_mapping = config.getValueMapping()
  prefix = config.getItemNamePrefix()
  for type in value_mapping:
    for value_set in data[type]:
      valve_number = None
      id = value_set
      if type == "VALVE":
        id, valve_number = id.split(':')
      if id in device_mapping:
        device_name = device_mapping[id]
        if type == "VALVE":
          device_name = device_name + "_" + str(valve_number)
        logger.debug("Found device: " + device_name + " of type: " + type)
        for value_name in value_mapping[type]:
          if not value_name.endswith('_map'):
            if value_name in data[type][value_set]:
              item_suffix = value_mapping[type][value_name]
              item_name = prefix + "_" + device_name + "_" + item_suffix
              item = ir.get(item_name)
              if item == None:
                logger.info("Item not found: " + item_name)
              else:
                  value = str(data[type][value_set][value_name]['value'])
                  if value_name + '_map' in value_mapping[type]:
                    value = str(value_mapping[type][value_name + '_map'][value])
                  logger.info("Set item " + item_name + " = " + value)
                  events.postUpdate(item_name, value)

#######################################################
#######################################################
#######################################################
# fileWatcher

class FileWatcher(AbstractWatchService):
  def __init__(self, path, event_kinds=[ENTRY_CREATE, ENTRY_DELETE, ENTRY_MODIFY], watch_subdirectories=False):
    AbstractWatchService.__init__(self, path)
    self.logger = LoggerFactory.getLogger(logger_name + ".FileWatcher")
    self.event_kinds = event_kinds
    self.watch_subdirectories = watch_subdirectories
    self.logger.debug("new fileWatcher for " + str(path) + " created.")

  def getWatchEventKinds(self, path):
    return self.event_kinds

  def watchSubDirectories(self):
    return self.watch_subdirectories

  def processWatchEvent(self, event, kind, path):
    try: 
      self.logger.debug(event.toString())
      self.logger.debug(kind.toString())
      self.logger.debug(path.toString())
      if str(path.toString()) == gardena_config_file or str(path.toString()) == gardena_data_file:
        logger.info("File " + str(path.toString()) + " changed. Reloading.")
        try:
          gardena_monitor()
        except:
          logger.error("gardena_monitor failed.")
          logger.error(traceback.format_exc())
    except:
      self.logger.error("processWatchEvent callback failed.")
      self.logger.error(traceback.format_exc())
    self.deactivate()
    self.activate()

#######################################################
#######################################################
#######################################################
# __main__

fileWatcherGardena = None

#######################################################
# script load/unload hooks
def scriptLoaded(id):
  try:
    logger.info("scriptLoaded()")
    fileWatcherGardena = FileWatcher(gardenaDir)
    fileWatcherGardena.activate()
    gardena_monitor()
  except:
    logger.error(traceback.format_exc())
    if fileWatcherGardena is not None:
      fileWatcherGardena.deactivate()

def scriptUnloaded():
  logger.info("scriptUnloaded()")
  if fileWatcherGardena is not None:
    fileWatcherGardena.deactivate()

