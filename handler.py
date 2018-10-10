import json
import logging
import time
import uuid

import sectoralarm
import os
import boto3

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def alarm_temp(event, context):
    logger.info("Getting temperatures")

    status_code = 200

    try:
        alarm = sectoralarm.Connect(os.environ['email'], os.environ['password'], os.environ['siteId'],
                                    os.environ['panelCode'])
    except:
        message = "Could log in to Alarm."
        logger.error(message, exc_info=True)
        status_code = 403
        body = {"message": message,
                "input": event}

        response = {
            "statusCode": status_code,
            "body": json.dumps(body)
        }
        return response
    try:
        temperatures = alarm.temp()
        body = {"temperatures": temperatures,
                "input": event}

    except:
        logger.error('Could not get status for annex.', exc_info=True)
        body = {"temperatures": "undefined",
                "input": event}
        status_code = 500

    timestamp = int(time.time() * 1000)
    table = dynamodb.Table(os.environ['TEMP_TABLE'])
    logger.info("Saving temperatures in " + os.environ['TEMP_TABLE'])
    for temp in temperatures:

        reading = {
            'id': str(uuid.uuid1()),
            'room': temp["Room"],
            'temperature': temp["Temperature"],
            'timestamp': timestamp
        }

        # write the temperature to the database
        table.put_item(Item=reading)

    logger.info("Alarm control ended.")
    response = {
        "statusCode": status_code,
        "body": json.dumps(body)}
    return response


def alarm_status(event, context):
    logger.info("Alarm status started.")

    status_code = 200

    try:
        alarm = sectoralarm.Connect(os.environ['email'], os.environ['password'], os.environ['siteId'],
                                    os.environ['panelCode'])
    except:
        message = "Could log in to Alarm."
        logger.error(message, exc_info=True)
        status_code = 403
        body = {"message": message,
                "input": event}

        response = {
            "statusCode": status_code,
            "body": json.dumps(body)
        }
        return response
    try:
        status = alarm.status()['AlarmStatus']
        body = {"armedStatus": status,
                "input": event}

    except:
        logger.error('Could not get status for annex.', exc_info=True)
        body = {"armedStatus": "undefined",
                "input": event}
        status_code = 500

    logger.info("Alarm control ended.")
    response = {
        "statusCode": status_code,
        "body": json.dumps(body)}
    return response


def annex_status(event, context):
    logger.info("Annex status started.")

    status_code = 200

    try:
        alarm = sectoralarm.Connect(os.environ['email'], os.environ['password'], os.environ['siteId'],
                                    os.environ['panelCode'])
    except:
        message = "Could log in to Alarm."
        logger.error(message, exc_info=True)
        status_code = 403
        body = {"message": message,
                "input": event}

        response = {
            "statusCode": status_code,
            "body": json.dumps(body)
        }
        return response
    try:
        status = alarm.status()['StatusAnnex']
        body = {"annexStatus": status,
                "input": event}

    except:
        logger.error('Could not get status for annex.', exc_info=True)
        body = {"annexStatus": "undefined",
                "input": event}
        status_code = 500

    logger.info("Alarm control ended.")
    response = {
        "statusCode": status_code,
        "body": json.dumps(body)}
    return response


def alarm_arm(event, context):
    """
    Arms the Annex. If notify is set it will send an e-mail on
    state change.
    """
    logger.info("Annex control started.")
    message = 'Arming the house.'
    status_code = 200
    alarm = None

    try:
        alarm = sectoralarm.Connect(os.environ['email'], os.environ['password'], os.environ['siteId'],
                                    os.environ['panelCode'])
    except:
        message = "Could log in to Alarm."
        logger.error(message, exc_info=True)
        status_code = 403
        body = {"message": message,
                "input": event}

        response = {
            "statusCode": status_code,
            "body": json.dumps(body)
        }
        return response

    try:
        alarm_status = alarm.status()
        message = 'Arming the house.'
        if alarm_status['Alarm Status'] != 'armed':
            logger.info(message)
            alarm.arm()
        else:
            message = 'House was already armed. Doing nothing.'
            logger.debug(message)


    except:
        message = "Could not arm house."
        logger.error(message, exc_info=True)
        status_code = 500

    body = {"message": message,
            "input": event}

    response = {
        "statusCode": status_code,
        "body": json.dumps(body)
    }
    return response


def annex_arm(event, context):
    """
    Arms the Annex. If notify is set it will send an e-mail on
    state change.
    """
    logger.info("Annex control started.")
    message = 'Arming the annex.'
    status_code = 200
    alarm = None

    try:
        alarm = sectoralarm.Connect(os.environ['email'], os.environ['password'], os.environ['siteId'],
                                    os.environ['panelCode'])
    except:
        message = "Could log in to Alarm."
        logger.error(message, exc_info=True)
        status_code = 403
        body = {"message": message,
                "input": event}

        response = {
            "statusCode": status_code,
            "body": json.dumps(body)
        }
        return response

    try:
        alarm_status = alarm.status()
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

    body = {"message": message,
            "input": event}

    response = {
        "statusCode": status_code,
        "body": json.dumps(body)
    }
    return response
