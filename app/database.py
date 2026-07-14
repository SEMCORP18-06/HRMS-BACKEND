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
    today = datetime.date.today().isoformat()
    employees = [
        {
            "tenant_id": "semco",
            "emp_id": "SEMCO-001",
            "name": "John Doe",
            "email": "john@semcogroups.com",
            "password": "password123",
            "designation": "HR Operations Manager",
            "role": "Admin (HR)",
            "department": "People Ops",
            "dob": "1990-01-01",
            "doj": today,
            "personal_email": "john.personal@gmail.com",
            "current_address": "123 Main St, New York, NY",
            "office_contact": "+1-555-0199",
            "personal_contact": "+1-555-0100",
            "status": "ACTIVE",
            "system_access_revoked": 0
        }
    ]
    db.employees.insert_many(employees)
    
    # Empty structures
    
    print("[MONGO SEEDER] Seeding complete.")

