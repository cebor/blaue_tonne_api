from sys import stderr
from urllib.error import HTTPError

from camelot.io import read_pdf
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
            print(f"Could not parse date: {value}", file=stderr)
            continue


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
    from pathlib import Path
    import yaml

    DISTRICT = "Bruckmühl 2"
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
