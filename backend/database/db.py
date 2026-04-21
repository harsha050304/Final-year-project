from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client['trading_bot']
        
    def get_collection(self, name):
        return self.db[name]
    
    def save_prediction(self, ticker, current_price, predicted_price, confidence):
        predictions = self.get_collection('predictions')
        predictions.insert_one({
            'ticker': ticker,
            'timestamp': datetime.now(),
            'current_price': current_price,
            'predicted_price': predicted_price,
            'confidence': confidence
        })
    
    def save_trade(self, trade_data):
        trades = self.get_collection('trades')
        trades.insert_one(trade_data)
    
    def get_recent_predictions(self, limit=10):
        predictions = self.get_collection('predictions')
        return list(predictions.find().sort('timestamp', -1).limit(limit))
    
    def get_portfolio(self):
        portfolio = self.get_collection('portfolio')
        return portfolio.find_one() or {
            'cash': 100000,
            'holdings': {},
            'total_value': 100000,
            'returns': 0
        }
    
    def update_portfolio(self, data):
        portfolio = self.get_collection('portfolio')
        portfolio.replace_one({}, data, upsert=True)

# Test connection
if __name__ == "__main__":
    db = Database()
    print("✅ MongoDB Connected!")
    print(f"Portfolio: {db.get_portfolio()}")