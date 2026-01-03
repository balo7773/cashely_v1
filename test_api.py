#!/usr/bin/python3
from dotenv import load_dotenv, set_key, find_dotenv
import os
import requests
import base64
import uuid

# Load environment variables from .env file
dotenv_path = find_dotenv()
load_dotenv()
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
CONTRACT_CODE = os.getenv('CONTRACT_CODE')



# 1. Generate access token
def generate_access_token():
    credentials = f"{API_KEY}:{SECRET_KEY}"
    url = "https://sandbox.monnify.com/api/v1/auth/login"
    encoded_base64_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")
    headers = {
        "Authorization" : f"Basic {encoded_base64_credentials}"
    }
    response = requests.post(url, headers=headers)
    print(response.json())
    return response.json().get('responseBody', {}).get('accessToken')


set_key(dotenv_path, "JWT", generate_access_token()) # create or update JWT in .env file
JWT = os.getenv('JWT')
# Dont forget to set take note of expiry time of JWT
########


# 2. VERIFY BVN AND NIN
def verify_bvn(bvn, name, dob, mobile_no):
    
    url = "https://sandbox.monnify.com/api/v1/vas/bvn-details-match"
    headers = {
        "Authorization": f"Bearer {JWT}",
        "Content-Type": "application/json"
    }

    # handle parameters during signup stage to be sent as arguments here
    params = {
      "bvn": bvn,
      "name": name,
      "dateOfBirth": dob,
      "mobileNo": mobile_no
    }
    response = requests.post(url, headers=headers, json=params)
    message = response.json().get('responseMessage')
    if message != "success":
        return message

def verify_nin(nin):    
    url = "https://sandbox.monnify.com/api/v1/vas/nin-details"
    headers = {
        "Authorization": f"Bearer {JWT}",
        "Content-Type": "application/json"
    }

    # handle parameters during signup stage to be sent as arguments here
    params = {
        "nin": nin
        }
    response = requests.post(url, headers=headers, json=params)
    message = response.json().get('responseMessage')
    if message != "success":
        return message

# BVN and NIN verification can only be used in Live mode and has a cost attached to it
##########

# 3. Create Virtual Account
def create_virtual_account(account_name, customer_email):
    id = str(uuid.uuid4())
    url = "https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts"
    headers={
      "Authorization": f"Bearer {JWT}",
      "Content-Type": "application/json"
    }
    params = {
      "accountReference": f"{account_name}_{id}",
      "accountName": account_name,
      "currencyCode": "NGN",
      "contractCode": CONTRACT_CODE,
      "customerEmail": customer_email,
      "customerName": "John Doe",
      "bvn": "21212121212",
      "getAllAvailableBanks": "true",
      "preferredBanks": [
        "50515", "035"
      ]
    }
    
    response = requests.post(url, headers=headers, json=params)

    return response.json()
