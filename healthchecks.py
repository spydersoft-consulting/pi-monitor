import sys
import requests

class StatusResult:
    success = True
    message = ''

    def __init__(self, success):
        self.success = success

def status_check(url):

    try:
        r = requests.get(url)
        result = StatusResult(r.status_code == 200)
        if (not result.success):
            result.message = r.status_code + " " + r.text
    except:
        result = StatusResult(False)
        result.message = "Unknown status failure"
    
    return result
