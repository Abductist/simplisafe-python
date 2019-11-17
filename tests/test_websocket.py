"""Define tests for the Websocket API."""
import aiohttp
import pytest
from unittest.mock import patch, MagicMock
from urllib.parse import urlencode

from socketio.exceptions import SocketIOError

from simplipy import API
from simplipy.errors import WebsocketError

from .const import TEST_ACCESS_TOKEN, TEST_EMAIL, TEST_PASSWORD, TEST_USER_ID
from .fixtures import *  # noqa
from .fixtures.v3 import *  # noqa


def async_mock(*args, **kwargs):
    """Return a mock asynchronous function."""
    m = MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


@pytest.mark.asyncio
async def test_connect_async_success(event_loop, v3_server):
    """Test triggering an async handler upon connection to the websocket."""
    async with v3_server:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            api = await API.login_via_credentials(TEST_EMAIL, TEST_PASSWORD, websession)
            api.websocket._sio.eio._trigger_event = async_mock()
            api.websocket._sio.eio.connect = async_mock()

            on_connect = async_mock()
            api.websocket.async_on_connect(on_connect)

            connect_params = {
                "ns": f"/v1/user/{TEST_USER_ID}",
                "accessToken": TEST_ACCESS_TOKEN,
            }

            await api.websocket.async_connect()
            api.websocket._sio.eio.connect.mock.assert_called_once_with(
                f"wss://api.simplisafe.com/socket.io?{urlencode(connect_params)}",
                engineio_path="socket.io",
                headers={},
                transports=["websocket"],
            )

            await api.websocket._sio._trigger_event("connect", namespace="/")
            on_connect.mock.assert_called_once()


@pytest.mark.asyncio
async def test_connect_sync_success(event_loop, v3_server):
    """Test triggering a synchronous handler upon connection to the websocket."""
    async with v3_server:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            api = await API.login_via_credentials(TEST_EMAIL, TEST_PASSWORD, websession)
            api.websocket._sio.eio._trigger_event = async_mock()
            api.websocket._sio.eio.connect = async_mock()

            on_connect = MagicMock()
            api.websocket.on_connect(on_connect)

            connect_params = {
                "ns": f"/v1/user/{TEST_USER_ID}",
                "accessToken": TEST_ACCESS_TOKEN,
            }

            await api.websocket.async_connect()
            api.websocket._sio.eio.connect.mock.assert_called_once_with(
                f"wss://api.simplisafe.com/socket.io?{urlencode(connect_params)}",
                engineio_path="socket.io",
                headers={},
                transports=["websocket"],
            )

            await api.websocket._sio._trigger_event("connect", namespace="/")
            on_connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_failure(event_loop, v3_server):
    """Test connecting to the socket and an exception occurring."""
    async with v3_server:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            api = await API.login_via_credentials(TEST_EMAIL, TEST_PASSWORD, websession)
            api.websocket._sio.eio.connect = async_mock(side_effect=SocketIOError())

        with pytest.raises(WebsocketError):
            await api.websocket.async_connect()


@pytest.mark.asyncio
async def test_async_events(event_loop, v3_server):
    """Test events with async handlers."""
    async with v3_server:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            api = await API.login_via_credentials(TEST_EMAIL, TEST_PASSWORD, websession)
            api.websocket._sio.eio._trigger_event = async_mock()
            api.websocket._sio.eio.connect = async_mock()
            api.websocket._sio.eio.disconnect = async_mock()

            on_connect = async_mock()
            on_disconnect = async_mock()
            on_event = async_mock()

            api.websocket.async_on_connect(on_connect)
            api.websocket.async_on_disconnect(on_disconnect)
            api.websocket.async_on_event(on_event)

            connect_params = {
                "ns": f"/v1/user/{TEST_USER_ID}",
                "accessToken": TEST_ACCESS_TOKEN,
            }

            await api.websocket.async_connect()
            api.websocket._sio.eio.connect.mock.assert_called_once_with(
                f"wss://api.simplisafe.com/socket.io?{urlencode(connect_params)}",
                engineio_path="socket.io",
                headers={},
                transports=["websocket"],
            )

            await api.websocket._sio._trigger_event("connect", namespace="/")
            on_connect.mock.assert_called_once()

            await api.websocket._sio._trigger_event(
                "event", namespace=f"/v1/user/{TEST_USER_ID}"
            )
            on_event.mock.assert_called_once()

            await api.websocket.async_disconnect()
            await api.websocket._sio._trigger_event("disconnect", namespace="/")
            api.websocket._sio.eio.disconnect.mock.assert_called_once_with(abort=True)
            on_disconnect.mock.assert_called_once()


@pytest.mark.asyncio
async def test_sync_events(event_loop, v3_server):
    """Test events with synchronous handlers."""
    async with v3_server:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            api = await API.login_via_credentials(TEST_EMAIL, TEST_PASSWORD, websession)
            api.websocket._sio.eio._trigger_event = async_mock()
            api.websocket._sio.eio.connect = async_mock()
            api.websocket._sio.eio.disconnect = async_mock()

            on_connect = MagicMock()
            on_disconnect = MagicMock()
            on_event = MagicMock()

            api.websocket.on_connect(on_connect)
            api.websocket.on_disconnect(on_disconnect)
            api.websocket.on_event(on_event)

            connect_params = {
                "ns": f"/v1/user/{TEST_USER_ID}",
                "accessToken": TEST_ACCESS_TOKEN,
            }

            await api.websocket.async_connect()
            api.websocket._sio.eio.connect.mock.assert_called_once_with(
                f"wss://api.simplisafe.com/socket.io?{urlencode(connect_params)}",
                engineio_path="socket.io",
                headers={},
                transports=["websocket"],
            )

            await api.websocket._sio._trigger_event("connect", namespace="/")
            on_connect.assert_called_once()

            await api.websocket._sio._trigger_event(
                "event", namespace=f"/v1/user/{TEST_USER_ID}"
            )
            on_event.assert_called_once()

            await api.websocket.async_disconnect()
            await api.websocket._sio._trigger_event("disconnect", namespace="/")
            api.websocket._sio.eio.disconnect.mock.assert_called_once_with(abort=True)
            on_disconnect.assert_called_once()