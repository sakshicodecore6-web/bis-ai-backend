# seed_labs.py
from sqlmodel import Session
from database import engine
from models import Laboratory

sample_labs = [
    Laboratory(
        name="Central Testing Labs",
        category="Electronics",
        location="Mumbai",
        capability="EMI/EMC testing, safety compliance for consumer electronics",
        contact_email="contact@centraltesting.example",
        contact_phone="022-12345678",
    ),
    Laboratory(
        name="National Textile Testing Institute",
        category="Textiles",
        location="Surat",
        capability="Fabric strength, colorfastness, flammability testing",
        contact_email="info@ntti.example",
        contact_phone="0261-9988776",
    ),
    Laboratory(
        name="FoodSafe Analytical Labs",
        category="Food & Beverage",
        location="Delhi",
        capability="Microbiological testing, nutritional analysis, packaging compliance",
        contact_email="hello@foodsafe.example",
        contact_phone="011-4455667",
    ),
    Laboratory(
        name="Precision Electronics Lab",
        category="Electronics",
        location="Bengaluru",
        capability="PCB testing, battery safety, IoT device certification",
        contact_email="support@precisionlabs.example",
        contact_phone="080-2233445",
    ),
]

with Session(engine) as session:
    session.add_all(sample_labs)
    session.commit()
    print(f"Seeded {len(sample_labs)} labs.")