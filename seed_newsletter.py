# seed_newsletter.py
from sqlmodel import Session
from database import engine
from models import NewsletterPost

sample_posts = [
    NewsletterPost(
        title="IS 16102 Amended for LED Lighting Products",
        category="Electronics",
        summary="BIS has amended IS 16102 to update safety and performance requirements for LED lighting products. Manufacturers should review compliance before their next certification renewal.",
    ),
    NewsletterPost(
        title="New QCO Notified for Textile Products",
        category="Textiles",
        summary="A new Quality Control Order has been notified for select textile products, mandating BIS certification before sale in the domestic market.",
    ),
    NewsletterPost(
        title="Food Safety Standards Update: Packaging Norms Revised",
        category="Food & Beverage",
        summary="BIS has revised packaging and labeling norms for packaged food products to align with updated FSSAI guidelines.",
    ),
    NewsletterPost(
        title="BIS Launches Simplified Certification Process for MSMEs",
        category="General",
        summary="BIS has introduced a simplified, fast-tracked certification pathway aimed at reducing compliance burden for micro, small, and medium enterprises.",
    ),
]

with Session(engine) as session:
    session.add_all(sample_posts)
    session.commit()
    print(f"Seeded {len(sample_posts)} newsletter posts.")
    