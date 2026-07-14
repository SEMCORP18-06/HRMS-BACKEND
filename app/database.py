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
            "role": "HR Operations Manager",
            "department": "People Ops",
            "dob": "1990-01-01",
            "doj": today,
            "personal_email": "john.personal@gmail.com",
            "current_address": "123 Main St, New York, NY",
            "office_contact": "+1-555-0199",
            "personal_contact": "+1-555-0100",
            "status": "ACTIVE",
            "system_access_revoked": 0
        },
        {
            "tenant_id": "semco",
            "emp_id": "SEMCO-002",
            "name": "Alice Smith",
            "email": "alice@semcogroups.com",
            "password": "password123",
            "designation": "Lead Software Engineer",
            "role": "Lead Software Engineer",
            "department": "Engineering",
            "dob": "1995-06-12",
            "doj": "2022-10-01",
            "personal_email": "alice.smith@gmail.com",
            "current_address": "456 Tech Lane, San Francisco, CA",
            "office_contact": "+1-555-0211",
            "personal_contact": "+1-555-0200",
            "status": "ACTIVE",
            "system_access_revoked": 0
        },
        {
            "tenant_id": "semco",
            "emp_id": "SEMCO-003",
            "name": "Bob Johnson",
            "email": "bob@semcogroups.com",
            "password": "password123",
            "designation": "Senior Product Designer",
            "role": "Senior Product Designer",
            "department": "Design",
            "dob": "1991-12-25",
            "doj": "2021-02-15",
            "personal_email": "bob.design@gmail.com",
            "current_address": "789 Art Way, Brooklyn, NY",
            "office_contact": "+1-555-0322",
            "personal_contact": "+1-555-0300",
            "status": "ACTIVE",
            "system_access_revoked": 0
        }
    ]
    db.employees.insert_many(employees)
    
    # Quotes
    quotes = [
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
        {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
        {"text": "Act as if what you do makes a difference. It does.", "author": "William James"}
    ]
    db.quotes.insert_many(quotes)
    
    # Assets
    assets = [
        {"tenant_id": "semco", "hardware_name": "MacBook Pro M3", "serial_number": "SN-MBPM3-9081", "status": "AVAILABLE", "assigned_to": None, "checkout_date": None, "due_date": None},
        {"tenant_id": "semco", "hardware_name": "ThinkPad T14 Gen 4", "serial_number": "SN-TPT14-2201", "status": "AVAILABLE", "assigned_to": None, "checkout_date": None, "due_date": None},
        {"tenant_id": "semco", "hardware_name": "Dell UltraSharp 32 4K Monitor", "serial_number": "SN-DEL32-4410", "status": "AVAILABLE", "assigned_to": None, "checkout_date": None, "due_date": None}
    ]
    db.assets.insert_many(assets)
    
    # Policies
    policies = [
        {"tenant_id": "semco", "category": "WFH", "title": "Work From Home SOP", "content": "Employees can work remotely up to 3 days a week. Core collaborating hours are 10:00 AM to 4:00 PM IST. Stipends of ₹4,000/month are provided for internet expenses."},
        {"tenant_id": "semco", "category": "Leaves", "title": "Unlimited PTO Policy", "content": "SEMCO offers flexible paid time off. Minimum recommended guidelines are 15 days per calendar year. Approvals are coordinated via department leads with at least 2 weeks notice."},
        {"tenant_id": "semco", "category": "Travel", "title": "Business Travel Expenses SOP", "content": "Standard airfare and high-speed rail expenses are fully reimbursable. Daily meal allowance cap is ₹6,000. Hotel stays are capped at ₹16,000 per night unless pre-authorized."}
    ]
    db.policies.insert_many(policies)
    
    # Coupons
    coupons = [
        {"tenant_id": "semco", "code": "AMZN-HR2000-XYZ", "amount": 2000.0, "brand": "Amazon Gift Card", "assigned_to_email": None, "is_redeemed": False},
        {"tenant_id": "semco", "code": "SBUX-COFFEE-500", "amount": 500.0, "brand": "Starbucks Coffee Coupon", "assigned_to_email": None, "is_redeemed": False}
    ]
    db.coupons.insert_many(coupons)
    
    # Clubs
    clubs = [
        {"tenant_id": "semco", "name": "Coding Club", "description": "A forum for tech enthusiasts to discuss algorithms and systems.", "members": []},
        {"tenant_id": "semco", "name": "Design Circle", "description": "Fostering creative designs and review sessions.", "members": []}
    ]
    db.clubs.insert_many(clubs)
    
    print("[MONGO SEEDER] Seeding complete.")
