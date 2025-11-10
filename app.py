from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import requests
import json
import logging

# Limits, do not spam this endpoint
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5000 per minute"]
)

# Turn off logging in output logs (no HTTP post prints)
log = logging.getLogger('abcd')
log.disabled = True

# Limiter 2, dictionary so that different servers can't spam the same endpoint
internalLimiter = {}

def removeFromLimiter(key):
    if key in internalLimiter:
        internalLimiter.pop(key)  # Remove debounce

# Webhook routing API
@app.route("/api/webhooks/<id>/<str>", methods=["POST"])
@limiter.limit("5000 per minute")
def proxy(id, str):
    if (id + "/" + str) in internalLimiter:
        return "Rate limit exceeded", 429
    
    internalLimiter[(id + "/" + str)] = True  # Debounce
    threading.Timer(2.0, removeFromLimiter, [(id + "/" + str)]).start()  # Function is called after 2 seconds asynchronously
    
    data = request.get_json(force=True)
    response = requests.post(f"https://discord.com/api/webhooks/{id}/{str}", json=data)
    return "", response.status_code

# Run application
if __name__ == "__main__":
    app.run()
