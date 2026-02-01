import logging
from fastapi import FastAPI , Request
from fastapi.responses import JSONResponse


from utils import load_data,write_data, log_audit,find_card_index
from schema.data_validation import Cards, ViewCardsDetails,Recharge,Refund

from exceptions.custom import CardNotFoundError, CardAlreadyExistsError , BalanceLimitExceededError


#logging library
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]

)

logger=logging.getLogger(__name__)
#Initializing FastAPI
app=FastAPI()

#Custom Exception Handlers


@app.exception_handler(CardNotFoundError)
def card_not_found_exception_handler(request: Request, exc: CardNotFoundError):
    logger.error(f"Card Not Found:{exc.card_id}")

    return JSONResponse(
        status_code=404,
        content={"message": f"Card with id {exc.card_id} not found."},
    )

@app.exception_handler(CardAlreadyExistsError)
def card_already_exists_exception_handler(request: Request, exc: CardAlreadyExistsError):
    logger.error(f"Card Already Exists:{exc.card_id}")

    return JSONResponse(
        status_code=400,
        content={"message": f"Card with id {exc.card_id} already exists."},
    )

@app.exception_handler(BalanceLimitExceededError)
def balance_limit_exceeded_exception_handler(request: Request, exc: BalanceLimitExceededError):
    logger.error(f"Balance Limit Exceeded: Current Balance {exc.current_amount}, Attempted Amount {exc.attempted_amount}, Limit {exc.limit}")

    return JSONResponse(
        status_code=400,
        content={"message": f"Balance limit exceeded. Current Balance: {exc.current_amount}, Attempted Amount: {exc.attempted_amount}, Limit: {exc.limit}."},
    )



#Home page
@app.get("/")
def home_page():
   return {'message':'Welcome to RFID API'}

#Creating new card
@app.post("/create")
def create(card: Cards):
    logger.info(f"Processing creation for: {card.card_id}")
    cards = load_data()

    # We manually check logic, then raise our custom error if needed
    for c in cards:
        if c["card_id"] == card.card_id:
            raise CardAlreadyExistsError(card.card_id) 

    cards.append(card.model_dump())
    write_data(cards)
    
    log_audit("create_card", {"card_id": card.card_id, "initial_balance": card.balance})
    logger.info(f"Success: Created card {card.card_id}")
    
    return {"message": "Card created successfully", "card": card}

#Viwing a existing card    
@app.get("/view_cards/{card_id}")
def view_card(card_id: str):
    cards = load_data()
    # If this fails, it raises CardNotFoundError. 
    # The handler above catches it automatically.
    index = find_card_index(cards, card_id) 
    return cards[index]
    
#recharge card
@app.put("/recharge/")
def recharge_card(data: Recharge):
    logger.info(f"Recharge request: {data.card_id} for {data.amount}")
    
    cards = load_data()
    index = find_card_index(cards, data.card_id)

    current_balance = cards[index]['balance']
    
    # Check Business Logic
    if current_balance + data.amount > 10000:
        raise BalanceLimitExceededError(current_balance, data.amount, 10000)

    cards[index]['balance'] += data.amount
    write_data(cards)

    log_audit("recharge_card", {
        "card_id": data.card_id, 
        "old": current_balance, 
        "new": cards[index]['balance']
    })
    
    return cards[index]


#refund card
@app.put("/refund")
def refund(data: Refund):
    logger.info(f"Refund request: {data.card_id}")
    cards = load_data()
    index = find_card_index(cards, data.card_id)

    refund_amount = cards[index]['balance']
    cards[index]['balance'] = 0.0
    write_data(cards)

    log_audit("refund_card", {"card_id": data.card_id, "refunded_amount": refund_amount})
    
    return {"message": f"Refunded {refund_amount}"}