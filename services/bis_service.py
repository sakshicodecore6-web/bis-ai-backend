import re
from html.parser import HTMLParser
from urllib.parse import quote

import httpx


BIS_LIMS_SEARCH_URL = (
    "https://lims.bis.gov.in/home/search_is_number/"
)


class BISSearchParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.table_depth = 0
        self.current_row = None
        self.current_cell = None
        self.top_level_rows = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table_depth += 1
            return

        # Only read rows from top-level tables.
        # BIS has nested tables inside lab records for testing charges.
        if (
            tag == "tr"
            and self.table_depth == 1
        ):
            self.current_row = []

        elif (
            tag in ("td", "th")
            and self.table_depth == 1
            and self.current_row is not None
        ):
            self.current_cell = []

    def handle_data(self, data):
        if (
            self.table_depth == 1
            and self.current_cell is not None
        ):
            text = " ".join(data.split())

            if text:
                self.current_cell.append(text)

    def handle_endtag(self, tag):
        if (
            tag in ("td", "th")
            and self.table_depth == 1
            and self.current_row is not None
            and self.current_cell is not None
        ):
            value = " ".join(self.current_cell).strip()
            self.current_row.append(value)
            self.current_cell = None

        elif (
            tag == "tr"
            and self.table_depth == 1
            and self.current_row is not None
        ):
            if self.current_row:
                self.top_level_rows.append(self.current_row)

            self.current_row = None

        elif tag == "table":
            self.table_depth -= 1


def extract_is_number(standard_code: str) -> str:
    match = re.search(r"\b(\d{3,6})\b", standard_code)

    if not match:
        raise ValueError(
            "Could not identify an IS number from the supplied standard code."
        )

    return match.group(1)


def search_bis_lims(standard_code: str) -> list[dict]:
    is_number = extract_is_number(standard_code)

    url = (
        f"{BIS_LIMS_SEARCH_URL}"
        f"?is_number__doc_no={quote(is_number)}&page=1"
    )

    response = httpx.get(
        url,
        timeout=20.0,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    response.raise_for_status()

    parser = BISSearchParser()
    parser.feed(response.text)

    results = []

    for row in parser.top_level_rows:

        # We need at least the main BIS table columns.
        if len(row) < 8:
            continue

        # Skip the header row.
        if row[0].lower() == "s.no.":
            continue

        indian_standard = row[3]

        if is_number not in indian_standard:
            continue

        results.append(
            {
                "lab_name": row[1],
                "indian_standard": indian_standard,
                "product": row[4],
                "grade_type_size": row[5],
                "testing_charge": row[6],
                "validity_date": row[7],
                "remark": row[8] if len(row) > 8 else None,
                "source_url": url,
            }
        )

    return results


def debug_bis_response(standard_code: str) -> dict:
    is_number = extract_is_number(standard_code)

    url = (
        f"{BIS_LIMS_SEARCH_URL}"
        f"?is_number__doc_no={quote(is_number)}&page=1"
    )

    response = httpx.get(
        url,
        timeout=20.0,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    html = response.text

    return {
        "status_code": response.status_code,
        "content_length": len(html),
        "contains_16102": "16102" in html,
        "table_count": html.lower().count("<table"),
        "row_count": html.lower().count("<tr"),
        "first_1000_chars": html[:1000],
    }

def get_bis_standard_context(standard_code: str) -> dict:
    results = search_bis_lims(standard_code)

    if not results:
        raise ValueError(
            f"No BIS LIMS records found for IS {standard_code}"
        )

    first_result = results[0]

    indian_standard = first_result.get("indian_standard", "")

    return {
        "is_number": extract_is_number(standard_code),
        "is_title": first_result.get("product"),
        "is_year": None,
        "superseding_standard": None,
        "bis_scheme": None,
        "regulatory_status": None,
        "source_url": first_result.get("source_url"),
    }