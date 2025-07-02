import sqlite3
from datetime import datetime

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS negotiations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item TEXT,
                  buyer_max REAL,
                  seller_min REAL,
                  final_price REAL,
                  conversation TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_negotiation(db_path, item, buyer_max, seller_min, final_price, conversation):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO negotiations 
                 (item, buyer_max, seller_min, final_price, conversation, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (item, buyer_max, seller_min, final_price, conversation, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_negotiation_history(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT id, item, buyer_max, seller_min, final_price, timestamp 
                 FROM negotiations ORDER BY timestamp DESC LIMIT 10''')
    history = []
    for row in c.fetchall():
        # Convert timestamp string back to datetime object
        timestamp_str = row[5]
        try:
            timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None
        except (ValueError, TypeError):
            # If conversion fails, keep as string
            timestamp = timestamp_str
        
        history.append({
            'id': row[0],
            'item': row[1],
            'buyer_max': row[2],
            'seller_min': row[3],
            'final_price': row[4],
            'timestamp': timestamp
        })
    conn.close()
    return history