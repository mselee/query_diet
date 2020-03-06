from unittest.mock import MagicMock

import pytest

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
