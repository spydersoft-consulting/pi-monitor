import json
import logging
import healthchecks
import statuspage_io
import notifications

def main():
    
    #logging.basicConfig(filename='test.log', level=logging.DEBUG)

    f = open('monitor.config.json')
    configData = json.load(f)
    f.close()

    operator = statuspage_io.StatusPageOperator()

    for statusCheck in configData['statusChecks']:
        logging.info(str.format('Checking ', statusCheck['name'], '...'))
        statusResult = healthchecks.status_check(statusCheck['url'])
        incident = statuspage_io.Incident()
        newComponentStatus = "operational"

        sendNotification = False
        
        if (statusResult.success):
            # Good Check
            logging.info("Status OK")
            newComponentStatus = "operational"

        else:
            newComponentStatus = "major_outage"
            # Bad check
            logging.warning(statusResult.message)
            incident.name = str.format("{0} is not responsive", statusCheck['name'])
            incident.description = str.format("{0} is not responsive", statusCheck['name'])
            sendNotification = True
       

        if (statusCheck['statusPageComponentId'] != ''):
            statusIoResult = operator.checkAndUpdateComponentStatus(statusCheck['statusPageComponentId'], newComponentStatus, incident)   
            sendNotification = statusIoResult.incidentResult.incidentCreated

        if (sendNotification):              
            notifications.notify(incident.name, incident.description) 

main()