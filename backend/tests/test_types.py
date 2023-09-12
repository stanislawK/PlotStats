import pytest
from pydantic.error_wrappers import ValidationError

from api.models.category import Category
from api.types.category import CategoryType
from api.types.scan import AdhocScanInput, PydanticAdhocScanInput


def test_category_type() -> None:
    [name_field] = CategoryType._type_definition.fields  # type: ignore

    assert name_field.python_name == "name"

    instance = Category(name="Plot")
    data = CategoryType.from_pydantic(instance)
    assert data.name == "Plot"  # type: ignore


def test_adhoc_scan_input_type() -> None:
    [url_field] = AdhocScanInput._type_definition.fields  # type: ignore

    assert url_field.python_name == "url"
    with pytest.raises(
        ValidationError,
        match=("invalid or missing URL scheme"),
    ):
        PydanticAdhocScanInput(url="test")
    with pytest.raises(
        ValidationError,
        match=("url has to contain base url"),
    ):
        PydanticAdhocScanInput(url="https://test.com")
    instance = PydanticAdhocScanInput(url="https://www.test.io/query_params")
    data = AdhocScanInput.from_pydantic(instance)
    assert data.url == "https://www.test.io/query_params"  # type: ignore
