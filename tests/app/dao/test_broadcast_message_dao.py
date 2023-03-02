from datetime import datetime

from app.constants import BROADCAST_TYPE
from app.dao.broadcast_message_dao import (
    create_broadcast_provider_message,
    dao_get_all_broadcast_messages,
    get_earlier_events_for_broadcast_event,
)
from app.dao.broadcast_service_dao import (
    insert_or_update_service_broadcast_settings,
)
from app.models import BroadcastEventMessageType
from tests.app.db import (
    create_broadcast_event,
    create_broadcast_message,
    create_service,
    create_template,
)


def test_get_earlier_events_for_broadcast_event(sample_service):
    t = create_template(sample_service, BROADCAST_TYPE)
    bm = create_broadcast_message(t)

    events = [
        create_broadcast_event(
            bm,
            sent_at=datetime(2020, 1, 1, 12, 0, 0),
            message_type=BroadcastEventMessageType.ALERT,
            transmitted_content={"body": "Initial content"},
        ),
        create_broadcast_event(
            bm,
            sent_at=datetime(2020, 1, 1, 13, 0, 0),
            message_type=BroadcastEventMessageType.UPDATE,
            transmitted_content={"body": "Updated content"},
        ),
        create_broadcast_event(
            bm,
            sent_at=datetime(2020, 1, 1, 14, 0, 0),
            message_type=BroadcastEventMessageType.UPDATE,
            transmitted_content={"body": "Updated content"},
            transmitted_areas=["wales"],
        ),
        create_broadcast_event(
            bm,
            sent_at=datetime(2020, 1, 1, 15, 0, 0),
            message_type=BroadcastEventMessageType.CANCEL,
            transmitted_finishes_at=datetime(2020, 1, 1, 15, 0, 0),
        ),
    ]

    # only fetches earlier events, and they're in time order
    earlier_events = get_earlier_events_for_broadcast_event(events[2].id)
    assert earlier_events == [events[0], events[1]]


def test_create_broadcast_provider_message_creates_in_correct_state(sample_broadcast_service):
    t = create_template(sample_broadcast_service, BROADCAST_TYPE)
    broadcast_message = create_broadcast_message(t)
    broadcast_event = create_broadcast_event(
        broadcast_message,
        sent_at=datetime(2020, 1, 1, 12, 0, 0),
        message_type=BroadcastEventMessageType.ALERT,
        transmitted_content={"body": "Initial content"},
    )

    broadcast_provider_message = create_broadcast_provider_message(broadcast_event, "fake-provider")

    assert broadcast_provider_message.status == "sending"
    assert broadcast_provider_message.broadcast_event_id == broadcast_event.id
    assert broadcast_provider_message.created_at is not None
    assert broadcast_provider_message.updated_at is None


def test_dao_get_all_broadcast_messages(sample_broadcast_service):
    template_1 = create_template(sample_broadcast_service, BROADCAST_TYPE)
    # older message, should appear second in list
    broadcast_message_1 = create_broadcast_message(
        template_1, starts_at=datetime(2021, 6, 15, 12, 0, 0), status="cancelled"
    )

    service_2 = create_service(service_name="broadcast service 2", service_permissions=[BROADCAST_TYPE])
    insert_or_update_service_broadcast_settings(service_2, channel="severe")

    template_2 = create_template(service_2, BROADCAST_TYPE)
    # newer message, should appear first in list
    broadcast_message_2 = create_broadcast_message(
        template_2,
        stubbed=False,
        status="broadcasting",
        starts_at=datetime(2021, 6, 20, 12, 0, 0),
    )

    # broadcast_message_stubbed
    create_broadcast_message(
        template_2,
        stubbed=True,
        status="broadcasting",
        starts_at=datetime(2021, 6, 15, 12, 0, 0),
    )
    # broadcast_message_old
    create_broadcast_message(
        template_2,
        stubbed=False,
        status="completed",
        starts_at=datetime(2021, 5, 20, 12, 0, 0),
    )
    # broadcast_message_rejected
    create_broadcast_message(
        template_2,
        stubbed=False,
        status="rejected",
        starts_at=datetime(2021, 6, 15, 12, 0, 0),
    )

    broadcast_messages = dao_get_all_broadcast_messages()
    assert len(broadcast_messages) == 2
    assert broadcast_messages == [
        (
            broadcast_message_2.id,
            None,
            "severe",
            "Dear Sir/Madam, Hello. Yours Truly, The Government.",
            {"ids": [], "simple_polygons": []},
            "broadcasting",
            datetime(2021, 6, 20, 12, 0),
            None,
            None,
            None,
        ),
        (
            broadcast_message_1.id,
            None,
            "severe",
            "Dear Sir/Madam, Hello. Yours Truly, The Government.",
            {"ids": [], "simple_polygons": []},
            "cancelled",
            datetime(2021, 6, 15, 12, 0),
            None,
            None,
            None,
        ),
    ]
