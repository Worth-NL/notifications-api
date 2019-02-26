from datetime import datetime
from itertools import product

from freezegun import freeze_time

from app.dao.inbound_sms_dao import (
    dao_get_inbound_sms_for_service,
    dao_count_inbound_sms_for_service,
    delete_inbound_sms_older_than_retention,
    dao_get_inbound_sms_by_id,
    dao_get_paginated_inbound_sms_for_service_for_public_api,
    dao_get_paginated_most_recent_inbound_sms_by_user_number_for_service
)
from tests.conftest import set_config
from tests.app.db import create_inbound_sms, create_service, create_service_data_retention


def test_get_all_inbound_sms(sample_service):
    inbound = create_inbound_sms(sample_service)

    res = dao_get_inbound_sms_for_service(sample_service.id)
    assert len(res) == 1
    assert res[0] == inbound


def test_get_all_inbound_sms_when_none_exist(sample_service):
    res = dao_get_inbound_sms_for_service(sample_service.id)
    assert len(res) == 0


def test_get_all_inbound_sms_limits_and_orders(sample_service):
    with freeze_time('2017-01-01'):
        create_inbound_sms(sample_service)
    with freeze_time('2017-01-03'):
        three = create_inbound_sms(sample_service)
    with freeze_time('2017-01-02'):
        two = create_inbound_sms(sample_service)

        res = dao_get_inbound_sms_for_service(sample_service.id, limit=2)

    assert len(res) == 2
    assert res[0] == three
    assert res[0].created_at == datetime(2017, 1, 3)
    assert res[1] == two
    assert res[1].created_at == datetime(2017, 1, 2)


def test_get_all_inbound_sms_filters_on_service(notify_db_session):
    service_one = create_service(service_name='one')
    service_two = create_service(service_name='two')

    sms_one = create_inbound_sms(service_one)
    create_inbound_sms(service_two)

    res = dao_get_inbound_sms_for_service(service_one.id)
    assert len(res) == 1
    assert res[0] == sms_one


def test_get_all_inbound_sms_filters_on_time(sample_service, notify_db_session):
    create_inbound_sms(sample_service, user_number='447700900111', content='111 1', created_at=datetime(2017, 1, 2))
    sms_two = create_inbound_sms(
        sample_service,
        user_number='447700900111',
        content='111 2',
        created_at=datetime(2017, 1, 3)
    )

    with freeze_time('2017-01-09'):
        res = dao_get_inbound_sms_for_service(sample_service.id)

    assert len(res) == 1
    assert res[0] == sms_two


def test_count_inbound_sms_for_service(notify_db_session):
    service_one = create_service(service_name='one')
    service_two = create_service(service_name='two')

    create_inbound_sms(service_one)
    create_inbound_sms(service_one)
    create_inbound_sms(service_two)

    assert dao_count_inbound_sms_for_service(service_one.id) == 2


def test_count_inbound_sms_for_service_filters_messages_older_than_seven_days(sample_service, notify_db_session):
    create_inbound_sms(sample_service, user_number='447700900111', content='111 2', created_at=datetime(2017, 1, 2))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 2', created_at=datetime(2017, 1, 3))

    with freeze_time('2017-01-09'):
        assert dao_count_inbound_sms_for_service(sample_service.id) == 1


@freeze_time("2017-06-08 12:00:00")
def test_should_delete_inbound_sms_according_to_data_retention(notify_db_session):
    service_without_retention = create_service(service_name='without retention')
    service_with_three_day_retention = create_service(service_name='three days')
    service_with_month_retention = create_service(service_name='thirty days')

    services = [service_with_three_day_retention, service_without_retention, service_with_month_retention]

    create_service_data_retention(service_with_month_retention.id, notification_type='sms', days_of_retention=30)
    create_service_data_retention(service_with_three_day_retention.id, notification_type='sms', days_of_retention=3)
    # email retention doesn't affect anything
    create_service_data_retention(service_with_three_day_retention.id, notification_type='email', days_of_retention=4)

    dates = [
        datetime(2017, 6, 4, 23, 00),  # just before three days
        datetime(2017, 6, 4, 22, 59),  # older than three days
        datetime(2017, 5, 31, 23, 00),  # just before seven days
        datetime(2017, 5, 31, 22, 59),  # older than seven days
        datetime(2017, 5, 7, 22, 59),  # older than thirty days
    ]

    for date, service in product(dates, services):
        create_inbound_sms(service, created_at=date)

    deleted_count = delete_inbound_sms_older_than_retention()

    # four deleted for the 3-day service, two for the default seven days one, one for the 30 day
    assert deleted_count == 7
    assert dao_count_inbound_sms_for_service(service_without_retention.id) == 3
    assert dao_count_inbound_sms_for_service(service_with_three_day_retention.id) == 1
    assert dao_count_inbound_sms_for_service(service_with_month_retention.id) == 4


def test_get_inbound_sms_by_id_returns(sample_service):
    inbound_sms = create_inbound_sms(service=sample_service)
    inbound_from_db = dao_get_inbound_sms_by_id(inbound_sms.service.id, inbound_sms.id)

    assert inbound_sms == inbound_from_db


def test_dao_get_paginated_inbound_sms_for_service_for_public_api(sample_service):
    inbound_sms = create_inbound_sms(service=sample_service)
    inbound_from_db = dao_get_paginated_inbound_sms_for_service_for_public_api(inbound_sms.service.id)

    assert inbound_sms == inbound_from_db[0]


def test_dao_get_paginated_inbound_sms_for_service_for_public_api_return_only_for_service(sample_service):
    inbound_sms = create_inbound_sms(service=sample_service)
    another_service = create_service(service_name='another service')
    another_inbound_sms = create_inbound_sms(another_service)

    inbound_from_db = dao_get_paginated_inbound_sms_for_service_for_public_api(inbound_sms.service.id)

    assert inbound_sms in inbound_from_db
    assert another_inbound_sms not in inbound_from_db


def test_dao_get_paginated_inbound_sms_for_service_for_public_api_no_inbound_sms_returns_empty_list(sample_service):
    inbound_from_db = dao_get_paginated_inbound_sms_for_service_for_public_api(sample_service.id)

    assert inbound_from_db == []


def test_dao_get_paginated_inbound_sms_for_service_for_public_api_page_size_returns_correct_size(sample_service):
    inbound_sms_list = [
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
    ]
    reversed_inbound_sms = sorted(inbound_sms_list, key=lambda sms: sms.created_at, reverse=True)

    inbound_from_db = dao_get_paginated_inbound_sms_for_service_for_public_api(
        sample_service.id,
        older_than=reversed_inbound_sms[1].id,
        page_size=2
    )

    assert len(inbound_from_db) == 2


def test_dao_get_paginated_inbound_sms_for_service_for_public_api_older_than_returns_correct_list(sample_service):
    inbound_sms_list = [
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
    ]
    reversed_inbound_sms = sorted(inbound_sms_list, key=lambda sms: sms.created_at, reverse=True)

    inbound_from_db = dao_get_paginated_inbound_sms_for_service_for_public_api(
        sample_service.id,
        older_than=reversed_inbound_sms[1].id,
        page_size=2
    )

    expected_inbound_sms = reversed_inbound_sms[2:]

    assert expected_inbound_sms == inbound_from_db


def test_dao_get_paginated_inbound_sms_for_service_for_public_api_older_than_end_returns_empty_list(sample_service):
    inbound_sms_list = [
        create_inbound_sms(sample_service),
        create_inbound_sms(sample_service),
    ]
    reversed_inbound_sms = sorted(inbound_sms_list, key=lambda sms: sms.created_at, reverse=True)

    inbound_from_db = dao_get_paginated_inbound_sms_for_service_for_public_api(
        sample_service.id,
        older_than=reversed_inbound_sms[1].id,
        page_size=2
    )

    assert inbound_from_db == []


def test_most_recent_inbound_sms_only_returns_most_recent_for_each_number(notify_api, sample_service):
    create_inbound_sms(sample_service, user_number='447700900111', content='111 1', created_at=datetime(2017, 1, 1))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 2', created_at=datetime(2017, 1, 2))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 3', created_at=datetime(2017, 1, 3))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 4', created_at=datetime(2017, 1, 4))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 5', created_at=datetime(2017, 1, 5))
    create_inbound_sms(sample_service, user_number='447700900222', content='222 1', created_at=datetime(2017, 1, 1))
    create_inbound_sms(sample_service, user_number='447700900222', content='222 2', created_at=datetime(2017, 1, 2))

    with set_config(notify_api, 'PAGE_SIZE', 3):
        with freeze_time('2017-01-02'):
            res = dao_get_paginated_most_recent_inbound_sms_by_user_number_for_service(sample_service.id, page=1)

    assert len(res.items) == 2
    assert res.has_next is False
    assert res.per_page == 3
    assert res.items[0].content == '111 5'
    assert res.items[1].content == '222 2'


def test_most_recent_inbound_sms_paginates_properly(notify_api, sample_service):
    create_inbound_sms(sample_service, user_number='447700900111', content='111 1', created_at=datetime(2017, 1, 1))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 2', created_at=datetime(2017, 1, 2))
    create_inbound_sms(sample_service, user_number='447700900222', content='222 1', created_at=datetime(2017, 1, 3))
    create_inbound_sms(sample_service, user_number='447700900222', content='222 2', created_at=datetime(2017, 1, 4))
    create_inbound_sms(sample_service, user_number='447700900333', content='333 1', created_at=datetime(2017, 1, 5))
    create_inbound_sms(sample_service, user_number='447700900333', content='333 2', created_at=datetime(2017, 1, 6))
    create_inbound_sms(sample_service, user_number='447700900444', content='444 1', created_at=datetime(2017, 1, 7))
    create_inbound_sms(sample_service, user_number='447700900444', content='444 2', created_at=datetime(2017, 1, 8))

    with set_config(notify_api, 'PAGE_SIZE', 2):
        with freeze_time('2017-01-02'):
            # first page has most recent 444 and 333
            res = dao_get_paginated_most_recent_inbound_sms_by_user_number_for_service(sample_service.id, page=1)
            assert len(res.items) == 2
            assert res.has_next is True
            assert res.per_page == 2
            assert res.items[0].content == '444 2'
            assert res.items[1].content == '333 2'

            # second page has no 444 or 333 - just most recent 222 and 111
            res = dao_get_paginated_most_recent_inbound_sms_by_user_number_for_service(sample_service.id, page=2)
            assert len(res.items) == 2
            assert res.has_next is False
            assert res.items[0].content == '222 2'
            assert res.items[1].content == '111 2'


def test_most_recent_inbound_sms_only_returns_values_within_7_days(notify_api, sample_service):
    create_inbound_sms(sample_service, user_number='447700900111', content='111 1', created_at=datetime(2017, 4, 1))
    create_inbound_sms(sample_service, user_number='447700900111', content='111 2', created_at=datetime(2017, 4, 1))
    create_inbound_sms(sample_service, user_number='447700900222', content='222 1', created_at=datetime(2017, 4, 1))
    create_inbound_sms(sample_service, user_number='447700900222', content='222 2', created_at=datetime(2017, 4, 1))
    create_inbound_sms(sample_service, user_number='447700900333', content='333 1', created_at=datetime(2017, 4, 2))
    create_inbound_sms(sample_service, user_number='447700900333', content='333 2', created_at=datetime(2017, 4, 3))
    create_inbound_sms(sample_service, user_number='447700900444', content='444 1', created_at=datetime(2017, 4, 4))
    create_inbound_sms(sample_service, user_number='447700900444', content='444 2', created_at=datetime(2017, 4, 5))

    # 7 days ago BST midnight
    create_inbound_sms(sample_service, user_number='447700900666', content='666 1', created_at='2017-04-02T23:00:00')

    with freeze_time('2017-04-09T12:00:00'):
        res = dao_get_paginated_most_recent_inbound_sms_by_user_number_for_service(sample_service.id, page=1)

    assert len(res.items) == 3
    assert res.items[0].content == '444 2'
    assert res.items[1].content == '333 2'
    assert res.items[2].content == '666 1'
