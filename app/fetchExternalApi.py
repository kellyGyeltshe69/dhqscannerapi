import httpx,os
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv, dotenv_values

dotenv_path = os.path.join(os.path.dirname(__file__),  '.env')
load_dotenv(dotenv_path)

router = APIRouter()

# Define the access token as a constant
EXTERNAL_API_TOKEN = os.getenv("EXTERNAL_API_TOKEN")

async def fetch_user_details(cid: str):
    url = f'https://auth.aws.desuung.org.bt/api/admin/profiles/cid-did?cid={cid}'
    headers = {
        'Authorization': f'Bearer {EXTERNAL_API_TOKEN}'  # Include the access token in the headers
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            user_details = response.json()
            return user_details
        else:
            # Handle errors or raise an exception if necessary
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch user details")


# Endpoint to fetch user details
@router.get('/user-details/{cid}')
async def get_user_details(cid: str):
    try:
        user_details = await fetch_user_details(cid)
        return user_details
    except HTTPException as e:
        return e


