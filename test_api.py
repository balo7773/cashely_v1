#!/usr/bin/python3
"""
Cashely API Test Module

This module handles user management, authentication with the Monnify API,
wallet creation, and virtual account generation using SQLite for persistence.
"""
from dotenv import load_dotenv, set_key, find_dotenv
import os
import requests
import base64
import uuid
import sqlite3
import test_db


# Load environment variables from .env file
dotenv_path = find_dotenv()
load_dotenv()
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
CONTRACT_CODE = os.getenv('CONTRACT_CODE')



# 1. Generate access token
def generate_access_token():
    """
    Authenticates with the Monnify API to retrieve a Bearer Token (JWT).
    
    Returns:
        str: The access token string required for subsequent API calls.
    """
    credentials = f"{API_KEY}:{SECRET_KEY}"
    url = "https://sandbox.monnify.com/api/v1/auth/login"
    encoded_base64_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")
    headers = {
        "Authorization" : f"Basic {encoded_base64_credentials}"
    }
    response = requests.post(url, headers=headers)
    print(response.json())
    return response.json().get('responseBody', {}).get('accessToken')

# Execute token generation immediately upon module load.
# Note: In a production app, this should likely be handled by a session manager
# or a scheduled task to handle token expiration/refreshing.
set_key(dotenv_path, "JWT", generate_access_token()) # create or update JWT in .env file
JWT = os.getenv('JWT')
# Dont forget to set take note of expiry time of JWT
########

class User:
    """
    Represents a user in the Cashely system.
    Provides methods for user registration, identity verification (BVN/NIN),
    wallet management, and virtual account creation.
    """

    def __init__(self, full_name, email, mobile_no, bvn, nin, dob, password_hash):
        """
        Initializes a new User instance.

        Args:
            full_name (str): User's full legal name.
            email (str): User's email address.
            mobile_no (str): User's phone number.
            bvn (str): Bank Verification Number.
            nin (str): National Identity Number.
            dob (str): Date of Birth (YYYY-MM-DD).
            password_hash (str): Securely hashed password.
        """
        self.full_name = full_name
        self.email = email
        self.mobile_no = mobile_no
        self.bvn = bvn
        self.nin = nin
        self.dob = dob
        self.password_hash = password_hash

    def store_user(self):
        """
        Persists the user instance into the local SQLite database.
        
        Returns:
            int: The auto-generated user ID if successful.
            None: If a database integrity error occurs (e.g., duplicate email/BVN).
        """
        conn = sqlite3.connect('cashely.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (full_name, email, mobile_no, bvn, nin, dob, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.full_name,
                self.email,
                self.mobile_no,
                self.bvn,
                self.nin,
                self.dob,
                self.password_hash
            ))
            conn.commit()
            user_id = cursor.lastrowid  # Get the auto-generated ID
            return user_id
        except sqlite3.IntegrityError as e:
            # Handle duplicate email, BVN, or NIN
            print(f"Error storing user: {e}")
            return None
        finally:
            conn.close()

    def verify_bvn(self, bvn, name, dob, mobile_no):
        """
        Verifies the provided BVN details against the Monnify API.

        Args:
            bvn (str): The BVN to verify.
            name (str): The name to match against the BVN record.
            dob (str): Date of birth to match.
            mobile_no (str): Mobile number to match.

        Returns:
            str: The error message if verification fails, otherwise None (implicitly success).
        """
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

    def verify_nin(self, nin):
        """
        Verifies the provided NIN details against the Monnify API.

        Args:
            nin (str): The National Identity Number to verify.

        Returns:
            str: The error message if verification fails, otherwise None.
        """
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

    def create_wallet(self, user_id):
        """
        Initializes a local wallet record for a specific user.
        
        1. Retrieves user details (Name, Email, BVN) from the DB.
        2. Generates a unique account reference.
        3. Inserts a new wallet record linked to the user.

        Args:
            user_id (int): The ID of the user to create a wallet for.

        Returns:
            tuple: (user_id, new_wallet_id, name, email, bvn, account_reference) on success.
            tuple: (None, None, None, None, None, None) on failure.
        """
        conn = sqlite3.connect('cashely.db')
        cursor = conn.cursor()

        try:
            # 1. Query the users table to get the user's details
            cursor.execute("SELECT full_name, email, bvn FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()

            # If no user is found with that ID, we can't proceed
            if not user_data:
                print(f"Error: No user found with ID {user_id}")
                return None, None, None, None # Return None for all values

            # Unpack the user data from the tuple
            name, email, bvn = user_data

            # 2. Create the unique account_reference
            account_reference = f"{name}_{user_id}"

            # 3. Insert the new record into the wallets table
            cursor.execute(
                "INSERT INTO wallets (user_id, account_reference) VALUES (?, ?)",
                (user_id, account_reference)
            )
            
            # 4. Get the ID of the wallet we just created
            # lastrowid is a special attribute on the cursor that gives you the ID of the last inserted row
            new_wallet_id = cursor.lastrowid
            
            # Commit the transaction to save the wallet
            conn.commit()

            print(f"Successfully created wallet with ID: {new_wallet_id} for user: {name}")
            
            # 5. Return all the necessary data for the next step
            return user_id, new_wallet_id, name, email, bvn, account_reference

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # If anything fails, return None
            return None, None, None, None, None, None
        finally:
            # Always close the connection
            conn.close()

        

    def create_virtual_account(self, user_id, wallet_id, name, email, bvn, account_ref):
        """
        Requests a reserved virtual account from Monnify and stores it in the database.

        Args:
            user_id (int): The ID of the user.
            wallet_id (int): The ID of the local wallet to link.
            name (str): Account holder name.
            email (str): Account holder email.
            bvn (str): Bank Verification Number.
            account_ref (str): Unique reference for the account.
        
        Note: This method prints the result to stdout rather than returning it.
        """
        url = "https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts"
        headers={
        "Authorization": f"Bearer {JWT}",
        "Content-Type": "application/json"
        }
        params = {
        "accountReference": account_ref,
        "accountName": name,
        "currencyCode": "NGN",
        "contractCode": CONTRACT_CODE,
        "customerEmail": email,
        "customerName": name,
        "bvn": bvn,
        "getAllAvailableBanks": "true",
        "preferredBanks": [
            "50515"
        ]
        }
        
        response = requests.post(url, headers=headers, json=params)
        if response.status_code == 200:
            response_body = response.json().get('responseBody', {})
            
            # 1. Seclude the keys from the response body
            monnify_reservation_id = response_body.get('reservationReference')
            source_created_at = response_body.get('createdOn')
            
            accounts = response_body.get('accounts', [])
            if not accounts:
                print("Error: API response did not contain account details.")
                return # Exit if no account info
                
            account_number = accounts[0].get('accountNumber')
            bank_name = accounts[0].get('bankName')
            bank_code = accounts[0].get('bankCode')

            # 2. Open the database connection
            conn = sqlite3.connect('cashely.db')
            cursor = conn.cursor()

            try:
                # 3. Prepare the SQL INSERT statement
                sql = '''
                    INSERT INTO virtual_accounts (
                        user_id, 
                        wallet_id, 
                        bank_name, 
                        bank_code, 
                        account_number, 
                        monnify_reservation_id, 
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                
                # 4. Execute the query with the data
                cursor.execute(sql, (
                    user_id,
                    wallet_id,
                    bank_name,
                    bank_code,
                    account_number,
                    monnify_reservation_id,
                    source_created_at  # Using the timestamp from Monnify's API
                ))
                
                # 6. Commit the changes to save them
                conn.commit()
                print("Successfully created and saved virtual account to the database.")

            except sqlite3.Error as e:
                print(f"Database error: {e}")
            finally:
                # 7. Close the connection
                conn.close()

        else:
            print(f"Failed to create virtual account. Status: {response.status_code}, Response: {response.text}")

            
    def get_wallet_balance(self, mobile_no):
        """
        Queries the database for the wallet balance associated with a mobile number.

        Args:
            mobile_no (str): The mobile number of the user.

        Returns:
            float: The wallet balance if found.
            None: If the user or wallet is not found.
        """
        conn = sqlite3.connect('cashely.db')
        cursor = conn.cursor()

        try:
            # 1. Get the user ID based on the mobile number
            cursor.execute("SELECT id FROM users WHERE mobile_no = ?", (mobile_no,))
            user_row = cursor.fetchone()

            if not user_row:
                print(f"No user found with mobile number: {mobile_no}")
                return None

            user_id = user_row[0]

            # 2. Get the wallet balance for the user
            cursor.execute("SELECT balance FROM wallets WHERE user_id = ?", (user_id,))
            wallet_row = cursor.fetchone()

            if not wallet_row:
                print(f"No wallet found for user ID: {user_id}")
                return None

            balance = wallet_row[0]
            return balance

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    
