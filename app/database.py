import os
import pymongo
import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://enquiry_db_user:uupZIRbERGIYnTVN@cluster0.r1sd5mu.mongodb.net/")

client = pymongo.MongoClient(MONGO_URI)
db = client.get_database("hr_operations_agent")

def serialize_doc(doc):
    if not doc:
        return None
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d["_id"])
        del d["_id"]
    return d

def serialize_list(docs):
    return [serialize_doc(d) for d in docs]

def seed_db():
    # If the old tenant acme exists, drop all collections to force re-seed
    if db.tenants.count_documents({"_id": "acme"}) > 0:
        print("[MONGO] Old tenant schema (acme) detected. Dropping collections for SEMCO Groups migration...")
        db.tenants.drop()
        db.employees.drop()
        db.payrolls.drop()
        db.quotes.drop()
        db.coupons.drop()
        db.clubs.drop()
        db.events.drop()
        db.assets.drop()
        db.document_requests.drop()
        db.survey_responses.drop()
        db.policies.drop()
        db.interviews.drop()

    if db.tenants.count_documents({}) > 0:
        return
        
    print("[MONGO SEEDER] Seeding database collections for SEMCO Groups...")
    
    # Tenants
    tenants = [
        {"_id": "semco", "name": "SEMCO Groups", "sso_domain": "semcogroups.com"}
    ]
    db.tenants.insert_many(tenants)
    
    # Employees
    pass
    
    # Empty structures
    
    print("[MONGO SEEDER] Seeding complete.")

