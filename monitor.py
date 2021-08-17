import json
import logging
import healthchecks
import statuspage_io

def main():
    
    #logging.basicConfig(filename='test.log', level=logging.DEBUG)

    f = open('monitor.config.json')
    configData = json.load(f)
    f.close()

    operator = statuspage_io.StatusPageOperator()

    for statusCheck in configData['statusChecks']:
        logging.info(str.format('Checking ', statusCheck['name'], '...'))
        statusResult = healthchecks.status_check(statusCheck['url'])
        if (statusResult.success):
            # Good Check
            logging.info("Status OK")
            if (statusCheck['statusPageComponentId'] != ''):
                operator.checkAndUpdateComponentStatus(statusCheck['statusPageComponentId'], "operational")

        else:
            # Bad check
            logging.warning(statusResult.message)
            if (statusCheck['statusPageComponentId'] != ''):
                incident = statuspage_io.Incident()
                incident.name = str.format("{0} is not responsive", statusCheck['name'])
                incident.description = str.format("{0} is not responsive", statusCheck['name'])
                operator.checkAndUpdateComponentStatus(statusCheck['statusPageComponentId'], "major_outage", incident)               
        

main()