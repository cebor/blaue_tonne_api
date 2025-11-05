from io import BufferedReader, BytesIO

import httpx
import pdfplumber
from dateutil.parser import ParserError, parse

# Length of the date string in the format 'dd.mm.yy'
DATE_LENGTH = 8


class DistrictNotFoundException(Exception):
    pass


PDF_CACHE = {}


def _download_pdf(url: str) -> BufferedReader:
    if url in PDF_CACHE:
        pdf_data = PDF_CACHE[url]
        return pdf_data

    if not url.lower().endswith(".pdf"):
        raise ValueError("URL must point to a PDF file")

    response = httpx.get(url, follow_redirects=True)
    response.raise_for_status()
    if response.headers.get("content-type", "").lower() != "application/pdf":
        raise ValueError("URL does not point to a valid PDF file")

    # Read the PDF into memory and wrap it in a BufferedReader
    pdf_data = BytesIO(response.content)
    PDF_CACHE[url] = BufferedReader(pdf_data)
    return PDF_CACHE[url]


def _parse_dates(row):
    for col in row:
        try:
            if not isinstance(col, str) or len(col) < DATE_LENGTH:
                continue
            # rm preceding day names
            if len(col) > DATE_LENGTH:
                col = col[-DATE_LENGTH:]
            yield parse(col, dayfirst=True).isoformat()
        except ParserError:
            continue


def get_dates(url: str, pages: str, district):
    try:
        pdf_reader = _download_pdf(url)
        with pdfplumber.open(pdf_reader) as pdf:
            page_numbers = [int(p) for p in pages.split(",")]
            for page_num in page_numbers:
                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()

                for table in tables:
                    for row_idx, row in enumerate(table):
                        if district in (cell or "" for cell in row):
                            yield from _parse_dates(row)
                            yield from _parse_dates(table[row_idx + 1])
                            return  # Found our district, we're done

            # If we get here, district wasn't found
            raise DistrictNotFoundException

    except httpx.HTTPStatusError as err:
        if err.response.status_code == 404:
            return
        else:
            raise


if __name__ == "__main__":
    from pathlib import Path

    import yaml

    DISTRICT = "Aschau"
    yaml_path = Path(__file__).parent / "plans.yaml"
    try:
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)
            PLANS = config["plans"]
    except Exception:
        PLANS = []

    for plan in PLANS:
        dates = get_dates(plan["url"], plan["pages"], DISTRICT)
        for date in dates:
            print(date)
