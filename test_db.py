#!/usr/bin/python3
import sqlite3

def init_db():
    # This creates the file 'cashely.db' if it doesn't exist
    conn = sqlite3.connect('cashely.db')
    cursor = conn.cursor()

    # 1. Users Table (Owners)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile_no TEXT,
            bvn TEXT UNIQUE,
            nin TEXT UNIQUE,
            dob TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
    ''')

    # 2. Wallets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_reference TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # 3. Virtual Accounts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS virtual_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            wallet_id INTEGER NOT NULL,
            bank_name TEXT NOT NULL,
            bank_code TEXT NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            monnify_reservation_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(wallet_id) REFERENCES wallets(id)
        )
    ''')

    # 4. Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'credit' or 'debit'
            amount REAL NOT NULL,
            settlement_amount REAL,
            bank_name TEXT, -- Which bank did they use?
            monnify_tran_ref TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(wallet_id) REFERENCES wallets(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()


