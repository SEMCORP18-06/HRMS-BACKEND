import pymongo
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb+srv://enquiry_db_user:uupZIRbERGIYnTVN@cluster0.r1sd5mu.mongodb.net/"

def check_conn():
    print("[TEST] Attempting to connect to MongoDB Atlas cluster...")
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("[TEST SUCCESS] Successfully connected to MongoDB Atlas!")
        print("[TEST] Databases list: ", client.list_database_names())
    except ConnectionFailure as e:
        print(f"[TEST FAILED] Could not connect to server: {str(e)}")
    except Exception as e:
        print(f"[TEST ERROR] Connection error: {str(e)}")

if __name__ == "__main__":
    check_conn()
