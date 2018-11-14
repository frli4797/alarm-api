import json
import os
import logging
import time
import decimal
import urllib

import sectoralarm
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

available_sensors = {"F1 garage", "irnv over", "irnv vrum"}


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


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

    __write_temperatures(temperatures)

    logger.info("Alarm control ended.")
    response = {
        "statusCode": status_code,
        "body": json.dumps(body)}
    return response


def put_temperatures(event, context):
    """
    Cron job to recurring save temperatures.
    :param event:
    :param context:
    :return:
    """
    logger.info("Saving temperatures to database.")
    alarm = sectoralarm.Connect(os.environ['email'], os.environ['password'], os.environ['siteId'],
                                os.environ['panelCode'])
    temperatures = alarm.temp()
    __write_temperatures(temperatures)


def lasttemp(event, context):
    sensor: str = urllib.parse.unquote(str(event['pathParameters']['sensor']))
    logger.info("Getting temperature for " + sensor)
    try:
        body = __get_last_temperature(sensor)
        status = 200
    except IndexError:
        body = {"message" : "Sensor " + sensor + " not found"}
        status = 404

    response = {
        "statusCode": status,
        "body": json.dumps(body, cls=DecimalEncoder)}
    return response


def all_lasttemps(event, context):
    logger.info("Getting all the latest temperatures.")

    body = __get_last_temperatures(available_sensors)

    response = {
        "statusCode": 200,
        "body": json.dumps(body, cls=DecimalEncoder)}
    return response


def __write_temperatures(temperatures):
    timestamp = int(time.time() * 1000)
    table = dynamodb.Table(os.environ['TEMP_TABLE'])

    for temp in temperatures:
        logger.debug("Saving temperature " + temp["Temperature"]
                     + " for sensor " + temp["Room"]
                     + " in " + os.environ['TEMP_TABLE'])
        reading = {
            'sensor': temp["Room"],
            'temperature': temp["Temperature"],
            'timestamp': timestamp
        }

        # write the temperature to the database
        table.put_item(Item=reading)


def __get_last_temperatures(sensors):
    table = dynamodb.Table(os.environ['TEMP_TABLE'])
    body = []
    for sensor in sensors:
        sensor = urllib.parse.unquote(sensor)
        logger.debug("Getting temperature for sensor " + sensor)
        query_response = table.query(
            KeyConditionExpression=Key('sensor').eq(str(sensor)),
            Limit=1,
            ScanIndexForward=False
        )
        for i in query_response['Items']:
            body.append(i)
    return body


def __get_last_temperature(sensor):
    table = dynamodb.Table(os.environ['TEMP_TABLE'])

    logger.info("Getting temperature for sensor " + sensor)
    query_response = table.query(
        KeyConditionExpression=Key('sensor').eq(sensor),
        Limit=1,
        ScanIndexForward=False,
        ProjectionExpression="temperature"
    )

    return query_response['Items'][0]
