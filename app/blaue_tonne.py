import camelot
from dateutil.parser import ParserError, parse


def __parse_dates(df):
    for col in df:
        try:
            value = df[col].values[0]
            yield parse(value[3:], dayfirst=True).isoformat(timespec='microseconds')
        except ParserError:
            pass


def get_dates(url: str, pages: str, district):
    tables = camelot.read_pdf(url, flavor="stream", pages=pages)

    for n in range(tables.n):
        index = tables[n].df.loc[tables[n].df[0] == district].index
        if not index.empty:
            yield from __parse_dates(tables[n].df.loc[index - 1])
            yield from __parse_dates(tables[n].df.loc[index + 1])
            break


if __name__ == "__main__":
    URL = "https://chiemgau-recycling.de/wp-content/uploads/2022/11/Abfuhrplan_LK_Rosenheim_2023.pdf"
    PAGES = "1,2"
    DISTRICT = "Bruckmühl 1"

    dates = get_dates(URL, PAGES, DISTRICT)

    for date in dates:
        print(date)
