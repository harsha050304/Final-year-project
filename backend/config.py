import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tradewise-secret-2025')
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # Trading settings
    INITIAL_CAPITAL = 100000
    SUPPORTED_TICKERS = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 
        'ICICIBANK.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS'
    ]
    
    # Gamification
    ACHIEVEMENT_LEVELS = {
        'Beginner': 0,
        'Trader': 5,
        'Pro': 20,
        'Expert': 50,
        'Master': 100
    }
    
    BADGES = {
        'first_trade': {'name': 'First Trade', 'icon': '🎯', 'points': 10},
        'profitable': {'name': 'Profitable', 'icon': '💰', 'points': 25},
        'streak_3': {'name': '3-Win Streak', 'icon': '🔥', 'points': 50},
        'sharpe_high': {'name': 'Risk Master', 'icon': '🛡️', 'points': 75},
        'diamond_hands': {'name': 'Diamond Hands', 'icon': '💎', 'points': 100}
    }