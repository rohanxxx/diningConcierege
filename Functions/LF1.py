import json

import os
import time
import logging
import time
import boto3

import re

import dateutil.parser
import dateutil.utils
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --------------------------------SQS Fun-------------------------------------#


def push_to_sqs(event):
    #logger.debug(f'event: {event}')
    logger.debug("inside push_to_sqs")
    city = check_key_error(lambda: event['sessionState']['intent']['slots']['city']['value']['interpretedValue'])
    cuisine = check_key_error(lambda: event['sessionState']['intent']['slots']['cuisine']['value']['interpretedValue'])
    ParticipantCount = check_key_error(lambda: event['sessionState']['intent']['slots']['ParticipantCount']['value']['interpretedValue'])
    date = check_key_error(lambda: event['sessionState']['intent']['slots']['date']['value']['interpretedValue'])
    time = check_key_error(lambda: event['sessionState']['intent']['slots']['time']['value']['interpretedValue'])
    customerEmail = check_key_error(lambda: event['sessionState']['intent']['slots']['customerEmail']['value']['interpretedValue'])

    # Load confirmation history and track the current reservation.
    load_for_sqs = json.dumps({
        'City': city,
        'Cuisine': cuisine,
        'People': ParticipantCount,
        'Date': date,
        'Time': time,
        'Email': customerEmail
        
    })
    
    logger.debug(f'load_for_sqs: {load_for_sqs}')
    
    sqs = boto3.client('sqs')
    queue_url = "https://sqs.us-east-1.amazonaws.com/956075594925/message"
    response = sqs.send_message(
        QueueUrl = queue_url,
        MessageBody = load_for_sqs
        )

# -----------------------Validate Slots Helper Func---------------------------#

#validates the city information
def valid_city(city, resolvedValues):
    cityList = ["manhattan", "queens", "flushing", "nyc"]
    if city in cityList:
        return True
    return False

#checks the cusine data
def valid_cuisine(cuisine, resolvedValues):
    cuisineList = ["indian", "chinese", "thai", "italian", "japanese", "french", "mexican"]
    x = cuisine.lower()
    if x in cuisineList:
        logger.debug(f'line{44}')
        return True
    logger.debug(f'line{44}')
    return False

#check valid count
def valid_participant_count(ParticipantCount):
    try:
        count = int(ParticipantCount)
        if count > 0 and count < 13:
            return True
        else:
            return False
    except ValueError:
        return False

#checks for the valid date    
def valid_date(date):
    date = dateutil.parser.parse(date)
    if date < dateutil.utils.today():
        return False
    return True

#check for valid time
def valid_time(time, date):
    date = dateutil.parser.parse(date).date()
    time = dateutil.parser.parse(time).time()
    
    if datetime.combine(date, time) < datetime.now():
        return False
    return True

#checks for the valid email
def valid_email(customerEmail):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, customerEmail)):
        return True
    return False

# ----------------------Validate Slots----------------------------------------#
#checks for the key error
def check_key_error(func):
    try:
        return func()
    except TypeError:
        logger.debug("check_key_error return None")
        return None


#when valid is not right it asks for the slot value again
def ask_for_valid_slot(valid, slot, msg):
    response = {
        'valid': valid,
        'slot' : slot,
        'messages' : {
            'content': msg,
            'contentType': 'PlainText'
        }
    }
    logger.debug(f'response = {response}')
    return response

#validates the slots
def validate_slots(slots):
    city = check_key_error(lambda: slots['city']['value']['interpretedValue'])
    cuisine = check_key_error(lambda: slots['cuisine']['value']['interpretedValue'])
    ParticipantCount = check_key_error(lambda: slots['ParticipantCount']['value']['interpretedValue'])
    date = check_key_error(lambda: slots['date']['value']['interpretedValue'])
    time = check_key_error(lambda: slots['time']['value']['interpretedValue'])
    customerEmail = check_key_error(lambda: slots['customerEmail']['value']['interpretedValue'])
    
    if city:
        #logger.debug(f'line{110}')
        if valid_city(city, slots['city']['value']['resolvedValues']) == False:
            return ask_for_valid_slot(
                False, 
                'city', 
                'Your city area is not valid, can you please try again?'
                )
    
    if cuisine:
        if valid_cuisine(cuisine, slots['cuisine']['value']['resolvedValues']) == False:
            response = ask_for_valid_slot(
                False,
                'cuisine',
                'Your cusine choice is not found, can you please choose anoether one?'
                )
            #intent_request['messages'] = response["messages"]
            #logger.debug(f'intent_request[messages]: {response["messages"]}')
            return response
    
    if ParticipantCount:
        if not valid_participant_count(slots['ParticipantCount']['value']['interpretedValue']):
            return ask_for_valid_slot(
                False,
                'ParticipantCount',
                "Please enter valid participant number. (between 1 to 12)"
                )
    if date:
        if valid_date(slots['date']['value']['interpretedValue']) == False:
            return ask_for_valid_slot(
                False,
                'date',
                "Please enter a valid date. (e.g. mm/dd/yy)"
                )
                
    if date and time:
        if not valid_time(slots['time']['value']['interpretedValue'], slots['date']['value']['interpretedValue']):
            return ask_for_valid_slot(
                False,
                'time',
                "Please enter a valid time. (e.g. 7:00 PM)"
                )
    
    if customerEmail:
        if valid_email(slots['customerEmail']['value']['interpretedValue']) == False:
            return ask_for_valid_slot(
                False,
                'customerEmail',
                'Invalid email, please try again. (e.g. username@domain.com)'
                )
                
    response = {
        'valid': True
    }
                
    return response
# ----------------------------Delegate Actions--------------------------------#
'''
def dialogAction_delegate(intent_name, slots):
    response = {
        'sessionState': {
            'dialogAction':{
                'type': 'Delegate',
            },
            'intent':{
                'name': intent_name,
                'slots': slots,
                'state': 'ReadyForfillment'
            }
        }
    }
    
    return response
'''
def dialogAction_elicit_slot(intent_name, slots, slot_to_elicit, msg):
    return {
        'messages': [msg],
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': {
            'name': intent_name,
            'slots': slots,
            'state': 'Failed'
            }
        }
    }
'''
def dialogAction_close(intent_name, msg):
    return {
        'messages': [msg],
        'sessionState': {
            'dialogAction': {
                'type': 'Close',
            },
            'intent': {
                'name': intent_name,
                'state': 'Fulfilled'
            }
        }
    }
'''
# ----------------------------------------------------------------------------#
def restuarant_suggestions(intent_request):
    logger.debug("Inside restuarant_suggestions")
 
    city = check_key_error(
        lambda: intent_request['sessionState']['intent']['slots']['city']['value']['interpretedValue']
        )
    #logger.debug(f'city: {city}')
    cuisine = check_key_error(
        lambda: intent_request['sessionState']['intent']['slots']['cuisine']['value']['interpretedValue']
        )
    #logger.debug(f'cuisine: {cuisine}')
    ParticipantCount = check_key_error(
        lambda: intent_request['sessionState']['intent']['slots']['ParticipantCount']['value']['interpretedValue']
        )
    #logger.debug(f'ParticipantCount: {ParticipantCount}')
    date = check_key_error(
        lambda: intent_request['sessionState']['intent']['slots']['date']['value']['interpretedValue']
        )
    #logger.debug(f'date: {date}')
    time = check_key_error(
        lambda: intent_request['sessionState']['intent']['slots']['time']['value']['interpretedValue']
        )
    #logger.debug(f'time: {time}')
    customerEmail = check_key_error(
        lambda: intent_request['sessionState']['intent']['slots']['customerEmail']['value']['interpretedValue']
        )
    #logger.debug(f'customerEmail: {customerEmail}')

    
    if intent_request['invocationSource'] == 'DialogCodeHook':
        logger.debug("inside DialogCodeHook if statement")
        
        # Validate any slots which have been specified. If any are invalid, re-elicit for their value
        re_validated_slot = validate_slots(intent_request['sessionState']['intent']['slots'])
        if re_validated_slot['valid'] == False:
            logger.debug("inside of if re_validated_slot is false")
            slots = intent_request['sessionState']['intent']['slots']
            #logger.debug(f'slotToElicit:{slots}')
            #updates the slot
            slots[re_validated_slot['slot']] = None
 
            response = dialogAction_elicit_slot(
                intent_request['sessionState']['intent']['name'],
                slots,
                re_validated_slot['slot'],
                re_validated_slot['messages']
            )
            #logger.debug(f'dialogAction_elicit_slot = {response}')
            intent_request['messages'] = response['messages']
            intent_request["proposedNextState"]["dialogAction"] = response['sessionState']['dialogAction']
            #logger.debug(f'before response event: {intent_request}')
            return
        else:
            return

        
# ----------------------------------------------------------------------------#
def lambda_handler(event, context):
    logger.debug(f'inside lambda_handler')
    #logger.debug(f'event = {event}')
    
    # Check the Cloudwatch logs to understand data inside event and
    # parse it to handle logic to validate user input and send it to Lex
    # Lex called LF1 with the user message and previous related state so
    # you can verify the user input. Validate and let Lex know what to do next.
    
    resp = {"statusCode": 200, "sessionState": event["sessionState"]}
    # logger.debug(f'{resp}')
    # Lex will propose a next state if available but if user input is not valid,
    # you will modify it to tell Lex to ask the same question again (meaning ask
    # the current slot question again)

    #set's EST as default time zone of this program
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    if "proposedNextState" not in event:
        logger.debug("proposedNextState inside if")
        resp["sessionState"]["dialogAction"] = {"type": "Close"}
        push_to_sqs(event)
    else:
        logger.debug(f'proposedNextState inside else')
        restuarant_suggestions(event)
        logger.debug(f'event = {event}')
        resp["sessionState"]["dialogAction"] = event["proposedNextState"]["dialogAction"]
        
    return resp