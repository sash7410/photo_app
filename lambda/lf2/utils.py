def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionState':{
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'sessionAttributes': session_attributes,
            'intent':{
                "name": intent_name,
                'slots': slots
            }
        },
        'messages': [message]
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'messages': message
        }
    }


def close(session_attributes, fulfillment_state, message, intent_name):
    response = {
        'sessionState':{
            'dialogAction':{
                'type': 'Close'
            },
            'sessionAttributes': session_attributes,
            'intent':{
                "name": intent_name,
                'state': fulfillment_state
            }
        },
        'messages': [message]
    }

    return response


def delegate(session_attributes, slots, intent_name):
    return {
        'sessionState':{
            'dialogAction': {
                'type': 'Delegate'
            },
            'sessionAttributes': session_attributes,
            'intent':{
                "name": intent_name,
                'slots': slots
            }
        }
    }
    
    
def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None