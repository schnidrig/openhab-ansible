#!/usr/bin/python3

import websocket
from threading import Thread
import time
import sys
import requests
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)

##############################
# account specific values
USERNAME = '{{ vault_gardena_user }}'
PASSWORD = '{{ vault_gardena_password }}'
API_KEY = '{{ vault_gardena_api_key }}'

##############################
# other constants
AUTHENTICATION_HOST = 'https://api.authentication.husqvarnagroup.dev'
SMART_HOST = 'https://api.smart.gardena.dev'

dataFileName = "/etc/openhab2/automation/gardena/gardena.json"
logFileName = "/etc/openhab2/automation/gardena/gardena.json.log"

##############################
module_name = "monitor"
logger_name = "gardena." + module_name
# default logger
logger = logging.getLogger(logger_name)

##############################
class Client:

  def __init__(self, dataFile, logFile):
    self.dataFileName = dataFileName
    self.logFile = logFile
    self.logger = logging.getLogger(logger_name + '.Client')
    self.dataFile = None

  def on_message(self, message):
    if self.dataFile != None:
      self.dataFile.write(message)
      self.dataFile.write('\n')
      self.dataFile.flush()
    logFile.write(message)
    logFile.write('\n')
    logFile.flush()

  def on_error(self, error):
    self.logger.error(error)

  def on_close(self):
    self.live = False
    self.logger.info("### closed ###")
    self.dataFile.close()

  def on_open(self):
    self.logger.info("### connected ###")
    self.dataFile = open(dataFileName, "w")

    self.live = True

    def run(*args):
      while self.live:
        time.sleep(1)

    Thread(target=run).start()

    

##############################
if __name__ == "__main__":

  while True:

    try: 
      start = time.time()
      logger.info(datetime.datetime.now())
      logFile = open(logFileName, "a")

      payload = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD,
                'client_id': API_KEY}

      logger.debug("Logging into gardena system...")
      r = requests.post('{}/v1/oauth2/token'.format(AUTHENTICATION_HOST), data=payload)
      assert r.status_code == 200, r
      auth_token = r.json()["access_token"]
      logger.debug("Got token: {}".format(auth_token))

      headers = {
        "Content-Type": "application/vnd.api+json",
        "x-api-key": API_KEY,
        "Authorization-Provider": "husqvarna",
        "Authorization": "Bearer " + auth_token
      }

      r = requests.get('{}/v1/locations'.format(SMART_HOST), headers=headers)
      assert r.status_code == 200, r
      assert len(r.json()["data"]) > 0, 'location missing - user has not setup system'
      location_id = r.json()["data"][0]["id"]

      payload = {
        "data": {
          "type": "WEBSOCKET",
          "attributes": {
            "locationId": location_id
          },
          "id": "does-not-matter"
        }
      }
      logger.debug("Logged in (%s), getting WebSocket ID..." % auth_token)
      r = requests.post('{}/v1/websocket'.format(SMART_HOST), json=payload, headers=headers)

      assert r.status_code == 201, r
      logger.info("WebSocket ID obtained, connecting...")
      response = r.json()
      websocket_url = response["data"]["attributes"]["url"]

      # websocket.enableTrace(True)
      client = Client(dataFileName, logFile)
      ws = websocket.WebSocketApp(
        websocket_url,
        on_message=client.on_message,
        on_error=client.on_error,
        on_close=client.on_close)
      ws.on_open = client.on_open
      ws.run_forever(ping_interval=150, ping_timeout=1)

    except:
      delay = 15 * 60 - (time.time() - start)
      if (delay > 0):
        logger.info("Sleeping for: {} seconds before retrying.".format(delay))
        time.sleep(delay)
