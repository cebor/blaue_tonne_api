from urllib.error import HTTPError

from camelot import read_pdf
from dateutil.parser import ParserError, parse

# Length of the date string in the format 'dd.mm.yy'
DATE_LENGTH = 8


class DistrictNotFoundException(Exception):
    pass


def _parse_dates(df):
    for col in df:
        try:
            value = df[col].values[0]
            if not isinstance(value, str) or len(value) < DATE_LENGTH:
                continue
            # rm preceding day names
            if len(value) > DATE_LENGTH:
                value = value[-DATE_LENGTH:]
            yield parse(value, dayfirst=True).isoformat()
        except ParserError:
            pass


def get_dates(url: str, pages: str, district):
    try:
        tables = read_pdf(url, flavor="stream", pages=pages)
    except HTTPError as err:
        if err.code == 404:
            return
        else:
            raise

    for n in range(tables.n):
        index = tables[n].df.loc[tables[n].df[0] == district].index
        if not index.empty:
            yield from _parse_dates(tables[n].df.loc[index - 1])
            yield from _parse_dates(tables[n].df.loc[index + 1])
            break
    else:
        raise DistrictNotFoundException


if __name__ == "__main__":
    PLANS = [
        # {"url": "https://chiemgau-recycling.de/wp-content/uploads/2022/11/Abfuhrplan_LK_Rosenheim_2023.pdf", "pages": "1,2"},
        # {"url": "https://chiemgau-recycling.de/wp-content/uploads/2023/11/Abfuhrplan_LK_Rosenheim_2024.pdf", "pages": "1,2"},
        {"url": "https://chiemgau-recycling.de/wp-content/uploads/2025/01/Abfuhrplan_LK_Rosenheim_2025.pdf", "pages": "1,2"},
    ]
    DISTRICT = "Bruckmühl 2"

    for plan in PLANS:
        dates = get_dates(plan["url"], plan["pages"], DISTRICT)
        for date in dates:
            print(date)
