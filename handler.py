import json
import logging
import sectoralarm
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def annex_status(event, context):
    logger.info("Annex status started.")

    message = ""
    status_code = 200
    logger.debug("Email: " + os.environ['email'])

    alarm = sectoralarm.connect(os.environ['email'], os.environ['password'], os.environ['siteId'], os.environ['panelCode'])

    try:
        status = alarm.status()['StatusAnnex']
        body = { "annexStatus": status,
            "input": event}

    except:
        logger.error('Could not get status for annex.', exc_info=True)
        body = { "annexStatus": status,
            "input": event}
        status_code = 500


    logger.info("Alarm control ended.")
    response = {
        "statusCode": status_code,
        "body": json.dumps(body)}
    return response

def annex_arm(event, context):
    '''
    Arms the Annex. If notify is set it will send an e-mail on
    state change.
    '''
    logger.info("Annex control started.")
    message = 'Arming the annex.'
    status_code = 200

    alarm = sectoralarm.connect(os.environ['email'], os.environ['password'], os.environ['siteId'], os.environ['panelCode'])
        
    try:
        alarm_status= alarm.status()
        message = 'Arming the annex.'
        if alarm_status['StatusAnnex'] != 'armed':
            logger.info(message)
            alarm.arm_annex()
        else:
            message = 'Annex was already armed. Doing nothing.'
            logger.debug(message)


    except:
        message = "Could not arm annex."
        logger.error(message, exc_info=True)
        status_code = 500


    body = { "message": message,
        "input": event}

    response = {
        "statusCode": status_code,
        "body": json.dumps(body)
    }
    return response