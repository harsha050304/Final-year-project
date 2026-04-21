from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get connection string
mongo_uri = os.getenv('MONGODB_URI')

print("="*60)
print("🔍 MongoDB Connection Test")
print("="*60)

# Check if .env file is loaded
if mongo_uri is None:
    print("❌ ERROR: MONGODB_URI not found!")
    print("\n📋 Troubleshooting:")
    print("1. Check if .env file exists in backend/ folder")
    print("2. Check if .env has: MONGODB_URI=mongodb+srv://...")
    print("3. Make sure there's NO SPACE before or after '='")
    print("\n✅ Current directory:", os.getcwd())
    print("✅ .env file exists?", os.path.exists('.env'))
    exit(1)

print(f"✅ Connection string loaded: {mongo_uri[:50]}...")

try:
    print("\n⏳ Connecting to MongoDB Atlas...")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    
    # Force connection
    client.server_info()
    print("✅ MongoDB Connected Successfully!")
    
    # Test database operations
    db = client['tradewise']
    collection = db['test']
    
    print("\n⏳ Testing database write...")
    result = collection.insert_one({'test': 'data', 'timestamp': 'now', 'status': 'working'})
    print(f"✅ Write successful! ID: {result.inserted_id}")
    
    print("\n⏳ Testing database read...")
    data = collection.find_one({'test': 'data'})
    print(f"✅ Read successful! Data: {data}")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED! MongoDB is ready!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Connection Failed: {e}")
    print("\n📋 Common Issues:")
    print("1. Wrong password in connection string")
    print("2. Network Access not set to 0.0.0.0/0 in MongoDB Atlas")
    print("3. Wait 2-3 minutes after changing Network Access settings")
    exit(1)