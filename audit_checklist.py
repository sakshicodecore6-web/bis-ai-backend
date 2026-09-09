# audit_checklist.py
# Simple rule-based checklist: each item looks for keywords in the
# extracted document text. This will later be replaced/augmented by
# an AI-powered analyzer.

CHECKLIST = [
    {
        "id": "application_form",
        "label": "Application documents",
        "keywords": ["application", "applicant", "form"],
    },
    {
        "id": "manufacturer_details",
        "label": "Manufacturer details",
        "keywords": ["manufacturer", "manufacturing unit", "factory address"],
    },
    {
        "id": "lab_test_report",
        "label": "Laboratory test report",
        "keywords": ["test report", "laboratory", "test result"],
    },
    {
        "id": "product_specification",
        "label": "Product specification sheet",
        "keywords": ["specification", "technical parameters", "product spec"],
    },
    {
        "id": "standard_reference",
        "label": "BIS standard reference (IS number)",
        "keywords": ["bis", "indian standard"],
        "regex": r"\bIS[\s:-]?\d{3,6}\b",
    },
]