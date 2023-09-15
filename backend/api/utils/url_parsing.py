from urllib.parse import urlparse

from api.settings import settings


def parse_url(url: str) -> str:
    deconstructed_url = urlparse(url)
    output_url = (
        settings.base_url
        + "_next/data/{api_key}"
        + deconstructed_url.path
        + ".json?"
        + deconstructed_url.query
    )
    searching_criteria = "&searchingCriteria=".join(
        ["", *deconstructed_url.path.split("/")[3:]]
    )
    output_url += searching_criteria
    return output_url
