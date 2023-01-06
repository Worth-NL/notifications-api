import json
import uuid

import pytest

from app.models import LetterBranding
from tests import create_admin_authorization_header
from tests.app.db import create_letter_branding


def test_get_all_letter_brands(client, notify_db_session):
    hm_gov = create_letter_branding()
    test_branding = create_letter_branding(
        name="test branding",
        filename="test-branding",
    )
    response = client.get("/letter-branding", headers=[create_admin_authorization_header()])
    assert response.status_code == 200
    json_response = json.loads(response.get_data(as_text=True))
    assert len(json_response) == 2
    for brand in json_response:
        if brand["id"] == str(hm_gov.id):
            assert hm_gov.serialize() == brand
        elif brand["id"] == str(test_branding.id):
            assert test_branding.serialize() == brand
        else:
            raise AssertionError()


def test_get_letter_branding_by_id(client, notify_db_session):
    hm_gov = create_letter_branding()
    create_letter_branding(name="test domain", filename="test-domain")
    response = client.get("/letter-branding/{}".format(hm_gov.id), headers=[create_admin_authorization_header()])

    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == hm_gov.serialize()


def test_get_letter_branding_by_id_returns_404_if_does_not_exist(client, notify_db_session):
    response = client.get("/letter-branding/{}".format(uuid.uuid4()), headers=[create_admin_authorization_header()])
    assert response.status_code == 404


def test_create_letter_branding_when_user_is_provided(admin_request, sample_user):
    form = {"name": "super brand", "filename": "super-brand", "created_by_id": str(sample_user.id)}

    response = admin_request.post(
        "letter_branding.create_letter_brand",
        _data=form,
        _expected_status=201,
    )

    letter_brand = LetterBranding.query.get(response["id"])
    assert letter_brand.name == form["name"]
    assert letter_brand.filename == form["filename"]
    assert letter_brand.created_at
    assert letter_brand.updated_at is None
    assert letter_brand.created_by_id == sample_user.id


def test_create_letter_branding_when_user_is_not_provided(admin_request, notify_db_session):
    form = {"name": "super brand", "filename": "super-brand"}

    response = admin_request.post(
        "letter_branding.create_letter_brand",
        _data=form,
        _expected_status=201,
    )

    letter_brand = LetterBranding.query.get(response["id"])
    assert letter_brand.name == form["name"]
    assert letter_brand.filename == form["filename"]
    assert letter_brand.created_at
    assert letter_brand.updated_at is None
    assert letter_brand.created_by_id is None


def test_update_letter_branding_when_updated_by_user_is_provided(admin_request, sample_user):
    existing_brand = create_letter_branding()

    form = {"name": "new name", "filename": "new filename", "updated_by_id": str(sample_user.id)}

    response = admin_request.post(
        "letter_branding.update_letter_branding",
        letter_branding_id=existing_brand.id,
        _data=form,
        _expected_status=201,
    )

    letter_brand = LetterBranding.query.get(response["id"])
    assert letter_brand.name == form["name"]
    assert letter_brand.filename == form["filename"]
    assert letter_brand.updated_by_id == sample_user.id
    assert letter_brand.updated_at


def test_update_letter_branding_when_updated_by_user_is_not_provided(admin_request, notify_db_session):
    existing_brand = create_letter_branding()

    form = {"name": "new name", "filename": "new filename"}

    response = admin_request.post(
        "letter_branding.update_letter_branding",
        letter_branding_id=existing_brand.id,
        _data=form,
        _expected_status=201,
    )

    letter_brand = LetterBranding.query.get(response["id"])
    assert letter_brand.name == form["name"]
    assert letter_brand.filename == form["filename"]
    assert letter_brand.updated_by_id is None
    assert letter_brand.updated_at


def test_update_letter_branding_returns_400_when_integrity_error_is_thrown(client, notify_db_session):
    create_letter_branding(name="duplicate", filename="duplicate")
    brand_to_update = create_letter_branding(name="super brand", filename="super brand")
    form = {
        "name": "duplicate",
        "filename": "super-brand",
    }

    response = client.post(
        "/letter-branding/{}".format(brand_to_update.id),
        headers=[("Content-Type", "application/json"), create_admin_authorization_header()],
        data=json.dumps(form),
    )

    assert response.status_code == 400
    json_resp = json.loads(response.get_data(as_text=True))
    assert json_resp["message"] == {"name": ["Name already in use"]}


def test_get_letter_branding_unique_name_returns_name_if_nothing_in_db_with_that_name(
    admin_request,
    notify_db_session,
):
    create_letter_branding(name="Other Department")

    response = admin_request.post("letter_branding.get_letter_branding_unique_name", _data={"name": "Department Name"})
    assert response == {"name": "Department Name"}


def test_get_letter_branding_unique_name_returns_alternate_option_if_name_already_used(
    admin_request,
    notify_db_session,
):
    create_letter_branding(name="DEPARTMENT name")

    response = admin_request.post("letter_branding.get_letter_branding_unique_name", _data={"name": "Department Name"})
    assert response == {"name": "Department Name (alternate 1)"}


def test_get_letter_branding_unique_name_returns_first_available_alternate_option(
    admin_request,
    notify_db_session,
):
    create_letter_branding(name="Department Name", filename="1")
    create_letter_branding(name="Department Name (alternate 1)", filename="2")
    create_letter_branding(name="Department Name (alternate 2)", filename="3")
    create_letter_branding(name="Department Name (alternate 4)", filename="4")
    # we've already renamed one of the options
    create_letter_branding(name="Department Name (blue banner)", filename="5")

    response = admin_request.post("letter_branding.get_letter_branding_unique_name", _data={"name": "Department Name"})
    assert response == {"name": "Department Name (alternate 3)"}


def test_get_letter_branding_unique_name_gives_up_if_100_options_assigned(
    admin_request,
    notify_db_session,
):
    create_letter_branding(name="Department Name", filename="first")
    for x in range(1, 100):
        create_letter_branding(name=f"Department Name (alternate {x})", filename=str(x))

    with pytest.raises(ValueError) as exc:
        admin_request.post("letter_branding.get_letter_branding_unique_name", _data={"name": "Department Name"})
    assert "Couldnt assign a unique name for Department Name" in str(exc.value)
