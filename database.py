__all__ = ['create_connection', 'create_table', 'insert_response', 'get_average_response_time', 'get_fastest_response_time', 'get_slowest_response_time']

import sqlite3
from datetime import datetime

def create_connection():
    conn = sqlite3.connect('api_speed.db')
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_name TEXT NOT NULL,
        model_name TEXT NOT NULL,
        query TEXT NOT NULL,
        response_time REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

def insert_response(conn, api_name, model_name, query, response_time):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO api_responses (api_name, model_name, query, response_time)
    VALUES (?, ?, ?, ?)
    ''', (api_name, model_name, query, response_time))
    conn.commit()

def get_average_response_time(conn, api_name, model_name):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT AVG(response_time) FROM api_responses
    WHERE api_name = ? AND model_name = ?
    ''', (api_name, model_name))
    return cursor.fetchone()[0]

def get_fastest_response_time(conn, api_name, model_name):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT MIN(response_time) FROM api_responses
    WHERE api_name = ? AND model_name = ?
    ''', (api_name, model_name))
    return cursor.fetchone()[0]

def get_slowest_response_time(conn, api_name, model_name):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT MAX(response_time) FROM api_responses
    WHERE api_name = ? AND model_name = ?
    ''', (api_name, model_name))
    return cursor.fetchone()[0]

def initialize_database():
    conn = create_connection()
    create_table(conn)
    conn.close()

if __name__ == '__main__':
    initialize_database()