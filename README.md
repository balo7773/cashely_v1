# Cashely v1

Cashely v1 is a Python-based financial wallet prototype that integrates with the **Monnify API**. It provides core fintech functionalities including user management, identity verification (KYC), wallet creation, and virtual account generation, backed by a local SQLite database.

## Features

- **User Management**: Register users with personal details.
- **Identity Verification**: Verify user identity using BVN (Bank Verification Number) and NIN (National Identity Number) via Monnify's Sandbox API.
- **Wallet System**: Create local wallets linked to users and track balances.
- **Virtual Accounts**: Generate reserved virtual bank accounts for users to receive funds.
- **Inventory Management**: Create and manage inventory items with multiple batches, tracking quantities and prices.
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

### 3. Example Workflow Script

Since `test_api.py` contains the class definitions, you can create a separate script (e.g., `main.py`) to execute the full user onboarding flow:

```python
from test_api import User

# 1. Register User (Sign Up)
print("Registering User...")
user_id = User.sign_up(
    full_name="Daniel Balo",
    email="daniel@example.com",
    mobile_no="08012345678",
    bvn="22222222222",
    nin="11111111111",
    dob="1995-05-12",
    password="securepassword123"
)

if user_id:
    print(f"User Registered with ID: {user_id}")

    # Instantiate User to access instance methods
    user = User("Daniel Balo", "daniel@example.com", "08012345678", "22222222222", "11111111111", "1995-05-12", "securepassword123")

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
        balance = user.get_wallet_balance(u_id)
        print(f"Current Wallet Balance: {balance}")
    else:
        print("Failed to create wallet.")
else:
    print("User registration failed (Email or BVN might already exist).")
```

### 4. Inventory Management

Cashely v1 includes basic inventory management functionality to track items and their batches. This allows you to create new inventory items and add additional batches to existing items.

#### Creating an Inventory Item

Use the `create_inventory` method to create a new inventory item with an initial batch:

```python
from test_api import User

# Instantiate a User (you can use any registered user or create a dummy one)
user = User("Dummy User", "dummy@example.com", "00000000000", "00000000000", "00000000000", "1990-01-01", "password123")

# Create a new inventory item
user.create_inventory(name="Laptop", quantity=10, price=50000.0)
```

This creates a new item named "Laptop" with an initial batch of 10 units at ₦50,000 each.

#### Adding a Batch to an Existing Item

To add more stock to an existing inventory item, use the `add_inventory_batch` method. You need the item's ID, which is generated when creating the item.

```python
# Assuming you have the item_id from create_inventory (e.g., from previous creation)
item_id = "some-uuid-here"  # Replace with actual UUID

# Add a new batch
user.add_inventory_batch(item_id=item_id, quantity=5, price=48000.0)
```

This adds a new batch of 5 units at ₦48,000 each to the existing item.

*Note: Inventory data is stored in the `inventory_items` and `inventory_batches` tables in `cashely.db`.*

## Project Structure

- **`test_api.py`**: Main application logic. Handles authentication, user creation, and API requests to Monnify.
- **`test_db.py`**: Database setup script. Defines the schema for users, wallets, and accounts.
- **`cashely.db`**: SQLite database file (generated after running `test_db.py`).