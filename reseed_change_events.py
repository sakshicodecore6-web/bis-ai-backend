# reseed_change_events.py
from sqlmodel import Session, delete
from database import engine
from models import StandardChangeEvent

realistic_events = [
    StandardChangeEvent(
        standard_code="IS 16102",
        change_type="amended",
        description="IS 16102 has been amended to update safety and performance requirements for LED lighting products.",
        recommended_action="Review your product's compliance against the amended clauses and re-test if performance parameters changed.",
    ),
    StandardChangeEvent(
        standard_code="IS 10500",
        change_type="updated",
        description="IS 10500 (drinking water specification) has been updated with revised limits for certain trace contaminants.",
        recommended_action="Check your latest test report against the updated contaminant limits and retest if any parameter is close to the old threshold.",
    ),
    StandardChangeEvent(
        standard_code="IS 302",
        change_type="replaced",
        description="IS 302 (household electrical appliances - safety) has been replaced by an updated edition with revised insulation and grounding requirements.",
        recommended_action="Obtain the new edition of IS 302 and confirm your product design meets the revised safety clauses before your next renewal.",
    ),
    StandardChangeEvent(
        standard_code="IS 4905",
        change_type="withdrawn",
        description="IS 4905 (methods for random sampling) has been withdrawn and merged into a broader sampling standard.",
        recommended_action="Update your quality control documentation to reference the new consolidated sampling standard.",
    ),
]

with Session(engine) as session:
    # Clear all existing change events
    session.exec(delete(StandardChangeEvent))
    session.commit()

    # Insert clean realistic data
    session.add_all(realistic_events)
    session.commit()
    print(f"Reseeded {len(realistic_events)} realistic change events.")