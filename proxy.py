# Libraries / Modules
from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import requests
import json
import logging
import time

# Limits, do no spam this endpoint
app = Flask(__name__)
limiter = Limiter(
  app,
  key_func=get_remote_address,
  default_limits=["5000 per 1 minute"]
)

# turn off logging in output logs (no http post prints)
log = logging.getLogger('abcd')
log.disabled = True

# limiter 2, dictionary so that different servers can't spam the same endpoint
internalLimiter = {}
def removeFromLimiter(key):
  if key in internalLimiter.keys():
    internalLimiter.pop(key) # Remove debounce

# Webhook routing api
@app.route("/api/webhooks/<id>/<str>", methods = ["POST"])
def proxy(id, str):
  if (id + "/" + str) in internalLimiter.keys():
    return "Rate limit exceeded", 429
  
  internalLimiter[(id + "/" + str)] = True #debounce
  threading.Timer(2.0, removeFromLimiter, [(id + "/" + str)]).start() # function is called after 2 asynchronously
  
  data = request.get_json(force = True)
  response = requests.post("https://discord.com/api/webhooks/"+id+"/"+str, json = data)
  return "", int(response.status_code)

# Run application
if __name__ == "__main__":
  app.run()