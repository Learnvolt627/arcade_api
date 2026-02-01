import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from exceptions.custom import CardNotFoundError

RECORDS_FILE = "records.json"
AUDIT_FILE="audit_log.json"

logger=logging.getLogger(__name__)

def load_data():
    if not os.path.exists(RECORDS_FILE):
        return []
    try:
        with open(RECORDS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Failed to decode {RECORDS_FILE}. File may be corrupted")
        return []

def write_data(data):
    try:
        with open(RECORDS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"failed to write date to {RECORDS_FILE}: {e}")
        raise e


def log_audit(action:str , details:dict):

    #this will apppend log entry to audit json file

    entry={
        'timestamp': datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        'action': action,
        'details': details
    }

    if not os.path.exists(AUDIT_FILE):
        logs=[]
    else:
        try:
            with open(AUDIT_FILE, "r") as f:
                logs= json.load(f)
        except json.JSONDecodeError:
            logs = [] #so even if file is gets corrupted we start fresh
    logs.append(entry)

    with open(AUDIT_FILE, "w") as f:
        json.dump(logs, f , indent=4)


def find_card_index(cards: list, card_id:str) -> int:
    for index , card in enumerate(cards):
        if card["card_id"] == card_id:
            return index
        
    raise CardNotFoundError(f"Card with id {card_id} not found")