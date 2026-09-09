# roadmap_data.py
# Generalized 12-step BIS compliance roadmap — mirrors the frontend's
# src/data/roadmapSteps.js. Step IDs must match exactly, since the
# frontend keeps checked-state keyed by these same IDs.

ROADMAP_STEPS = [
    {
        "id": "step-01",
        "title": "Identify the applicable Indian Standard",
        "description": "Determine which IS number governs your product category before doing anything else.",
    },
    {
        "id": "step-02",
        "title": "Check if certification is mandatory or voluntary",
        "description": "Some product categories fall under mandatory BIS certification (CRS/ISI); others are voluntary.",
    },
    {
        "id": "step-03",
        "title": "Prepare your product documentation",
        "description": "Gather technical specifications, manufacturing process details, and raw material sourcing info.",
    },
    {
        "id": "step-04",
        "title": "Select an accredited testing laboratory",
        "description": "Choose a BIS-recognized lab that tests for your specific standard.",
    },
    {
        "id": "step-05",
        "title": "Submit samples for testing",
        "description": "Send representative product samples to the lab along with required forms.",
    },
    {
        "id": "step-06",
        "title": "Review the test report",
        "description": "Check whether your product meets every parameter specified in the standard.",
    },
    {
        "id": "step-07",
        "title": "Address any failed parameters",
        "description": "If a parameter fails, adjust your product or process and retest before proceeding.",
    },
    {
        "id": "step-08",
        "title": "Apply for a BIS license on the eBIS portal",
        "description": "Submit your application along with the test report and supporting documents.",
    },
    {
        "id": "step-09",
        "title": "Factory inspection (if applicable)",
        "description": "A BIS officer may visit your manufacturing unit to verify production conditions.",
    },
    {
        "id": "step-10",
        "title": "Pay the applicable licensing fees",
        "description": "Fees vary based on product category and license type.",
    },
    {
        "id": "step-11",
        "title": "Receive your BIS license / ISI mark approval",
        "description": "Once approved, you can legally use the ISI mark on your product.",
    },
    {
        "id": "step-12",
        "title": "Track renewal and compliance alerts",
        "description": "BIS licenses need periodic renewal — keep track of upcoming standard revisions too.",
    },
]