from unittest.mock import MagicMock

import pytest

from query_diet import context
from query_diet.middleware import TrackerMiddleware, post_track, pre_track

RESPONSE = object()


@pytest.fixture()
def middleware():
    get_response = MagicMock(return_value=RESPONSE)
    return TrackerMiddleware(get_response)


def test_middleware_response(middleware, request):
    response = middleware(request)

    middleware.get_response.assert_called_once_with(request)
    assert response is RESPONSE


def test_middleware_signals(middleware, request):
    pre_track_handler = MagicMock()
    pre_track.connect(pre_track_handler)

    post_track_handler = MagicMock()
    post_track.connect(post_track_handler)

    middleware(request)

    pre_track_handler.assert_called_once()
    post_track_handler.assert_called_once()


def test_middleware_reuses_existing_tracker(middleware, request):
    with context.tracker.scoped(value=MagicMock()) as tracker:
        post_track_handler = MagicMock()
        post_track.connect(post_track_handler)

        middleware(request)

        _, kwargs = post_track_handler.call_args
        assert kwargs["tracker"] is tracker


def test_middleware_creates_new_tracker(middleware, request):
    assert context.tracker() is None

    post_track_handler = MagicMock()
    post_track.connect(post_track_handler)

    middleware(request)

    _, kwargs = post_track_handler.call_args
    assert kwargs["tracker"] is not None
