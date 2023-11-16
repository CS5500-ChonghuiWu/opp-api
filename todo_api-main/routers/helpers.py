from starlette.exceptions import HTTPException

import httpx

async def validate_card(card_number: str) -> dict:
    url = "https://c3jkkrjnzlvl5lxof74vldwug40pxsqo.lambda-url.us-west-2.on.aws"
    data = {"card_number": card_number}
    headers = {"content-type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    return response.json()

async def check_funds_and_fraud(card_number: str, amount: float) -> dict:
    url = "https://223didiouo3hh4krxhm4n4gv7y0pfzxk.lambda-url.us-west-2.on.aws"
    data = {"card_number": card_number, "amt": amount}
    headers = {"content-type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    return response.json()

def check_user_authentication(user):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
