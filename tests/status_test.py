# import aiohttp
# import hackerpet as hp
# from aiohttp.test_utils import TestClient, TestServer
from aiohttp import web


async def local_api(_request: web.Request) -> web.Response:
    """example response from hackerpet"""
    example_response = (
        '{"timezone":"-5.000000",'
        '"dst_on":"1",'
        '"hub_mode":"1",'
        '"weekend_from":"09:00",'
        '"weekend_to":"16:00",'
        '"weekday_from":"09:00",'
        '"weekday_to":"16:00",'
        '"status":"Your hub is working.",'
        '"game_id_queued":"9",'
        '"game_id_playing":"9",'
        '"hub_state":"Active",'
        '"time":"Sat Jul 30 15:23:41 2022",'
        '"max_kibbles":"0",'
        '"kibbles_eaten_today":"0"}'
    )
    return web.Response(text=example_response)


# I am confused and don't know how to write tests


def test_example():
    """just an example"""
    assert 1 == 1
