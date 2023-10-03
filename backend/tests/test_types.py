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
    [url_field, schedule_field] = AdhocScanInput._type_definition.fields  # type: ignore

    assert url_field.python_name == "url"
    assert schedule_field.python_name == "schedule"
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
    with pytest.raises(
        ValidationError,
        match=(
            "day_of_week\\n  field required \(type=value_error\.missing\)\\nschedule -> minute\\n  field required \(type=value_error\.missing\)"  # noqa
        ),
    ):
        PydanticAdhocScanInput(
            url="https://www.test.io/query_params", schedule={"hour": 1}
        )
    instance = PydanticAdhocScanInput(
        url="https://www.test.io/query_params",
        schedule={"day_of_week": 0, "hour": 1, "minute": 2},
    )
    data = AdhocScanInput.from_pydantic(instance)
    assert data.url == "https://www.test.io/query_params"
    assert data.schedule.hour == 1  # type: ignore
    assert data.schedule.minute == 2  # type: ignore
    assert data.schedule.day_of_week == 0  # type: ignore
