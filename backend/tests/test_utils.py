import api.utils.fetching
from api.settings import settings
from api.utils.url_parsing import parse_url


def test_parsing_url() -> None:
    input_url = (
        f"{settings.base_url}pl/wyniki/sprzedaz/dzialka/wielkopolskie/"
        f"poznan/poznan/poznan?ownerTypeSingleSelect=ALL&distanceRadius=0"
        f"&priceMin=100000&priceMax=200000&viewType=listing"
    )
    output_url = parse_url(input_url)
    output_url = output_url.format(api_key="API_KEY")
    assert output_url == (
        f"{settings.base_url}_next/data/API_KEY/pl/wyniki/sprzedaz/dzialka/"
        f"wielkopolskie/poznan/poznan/poznan.json?ownerTypeSingleSelect=ALL&"
        f"distanceRadius=0&priceMin=100000&priceMax=200000&viewType=listing&"
        f"searchingCriteria=sprzedaz&searchingCriteria=dzialka&"
        f"searchingCriteria=wielkopolskie&searchingCriteria=poznan&"
        f"searchingCriteria=poznan&searchingCriteria=poznan"
    )


def test_extracting_token() -> None:
    with open("tests/example_files/404_resp.html", "r") as f:
        body = f.read()
    api.utils.fetching.extract_token(body)
    assert api.utils.fetching.TOKEN == "U-X80D14b5VUVY_qgIbBQ"
