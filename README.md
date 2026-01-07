# Cashely v1

Cashely v1 is a Python-based financial wallet prototype that integrates with the **Monnify API**. It provides core fintech functionalities including user management, identity verification (KYC), wallet creation, and virtual account generation, backed by a local SQLite database.

## Features

- **User Management**: Register users with personal details.
- **Identity Verification**: Verify user identity using BVN (Bank Verification Number) and NIN (National Identity Number) via Monnify's Sandbox API.
- **Wallet System**: Create local wallets linked to users and track balances.
- **Virtual Accounts**: Generate reserved virtual bank accounts for users to receive funds.
- **Persistence**: Uses SQLite (`cashely.db`) to store user, wallet, and transaction data.

## Prerequisites

- Python 3.x
- Monnify Sandbox Account (for API keys)

## Installation

1. **Navigate to the project directory**.

2. **Install dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

3. **Environment Configuration**:
   Create a `.env` file in the root directory and add your Monnify credentials:
   ```ini
   API_KEY=your_monnify_api_key
   SECRET_KEY=your_monnify_secret_key
   CONTRACT_CODE=your_monnify_contract_code
   ```

## Usage

### 1. Initialize the Database
Before running the application logic, initialize the SQLite database tables.

```bash
python3 test_db.py
```
This creates `cashely.db` with tables for `users`, `wallets`, `virtual_accounts`, and `transactions`.

### 2. Run the API Logic
The core logic resides in `test_api.py`. Currently, this script contains the `User` class and methods to interact with the API.

```bash
python3 test_api.py
```

*Note: The script automatically generates an access token and updates the `.env` file upon execution.*

# Create the object
new_user = User("John Doe", "john@example.com", "08012345678", "12345678901", "11111111111", "1990-01-01", "hashed_password")

# Save to DB
user_id = new_user.store_user()
# Create the object
new_user = User("John Doe", "john@example.com", "08012345678", "12345678901", "11111111111", "1990-01-01", "hashed_password")

# Save to DB
user_id = new_user.store_user()
### 3. Example Workflow Script

Since `test_api.py` contains the class definitions, you can create a separate script (e.g., `main.py`) to execute the full user onboarding flow:

```python
from test_api import User

# 1. Define User Details
user = User(
    full_name="Daniel Balo",
    email="daniel@example.com",
    mobile_no="08012345678",
    bvn="22222222222",
    nin="11111111111",
    dob="1995-05-12",
    password_hash="securehash123"
)

# 2. Store User in DB
print("Registering User...")
user_id = user.store_user()

if user_id:
    print(f"User Registered with ID: {user_id}")

    # 3. Create Wallet
    # This returns the data needed to create the virtual account
    user_data = user.create_wallet(user_id)
    
    # Check if wallet creation was successful (it returns a tuple of 6 items)
    if user_data[0] is not None:
        u_id, w_id, name, email, bvn, ref = user_data
        
        # 4. Create Virtual Account
        print("Requesting Virtual Account from Monnify...")
        user.create_virtual_account(u_id, w_id, name, email, bvn, ref)
        
        # 5. Check Balance
        balance = user.get_wallet_balance("08012345678")
        print(f"Current Wallet Balance: {balance}")
    else:
        print("Failed to create wallet.")
else:
    print("User registration failed (Email or BVN might already exist).")
```

## Project Structure

- **`test_api.py`**: Main application logic. Handles authentication, user creation, and API requests to Monnify.
- **`test_db.py`**: Database setup script. Defines the schema for users, wallets, and accounts.
- **`cashely.db`**: SQLite database file (generated after running `test_db.py`).