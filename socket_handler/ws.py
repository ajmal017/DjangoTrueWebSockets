import asyncio
import os
import weakref

import aiohttp
import aioredis
import srvlookup
from aiohttp import web, ClientSession

REDIS_HOST = os.environ['REDIS_HOST']
try:
    results = srvlookup.lookup('http', 'tcp', 'django')
    DJANGO_HOST = results[0].host
    DJANGO_PORT = results[0].port
except srvlookup.SRVQueryFailure:
    DJANGO_HOST = os.environ['DJANGO_HOST']
    DJANGO_PORT = os.environ['DJANGO_PORT']


routes = web.RouteTableDef()


@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    session = ClientSession()

    request.app['websockets'].add(ws)
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                elif msg.data == 'posts':
                    async with session.get(f'http://{DJANGO_HOST}:{DJANGO_PORT}/post/') as resp:  # TODO: settings
                        await ws.send_json(await resp.json())
                else:
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())
    finally:
        request.app['websockets'].discard(ws)
    
    await session.close()

    print('websocket connection closed')
    return ws


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY,
                       message='Server shutdown')


async def listen_to_redis(app):
    sub = None
    chanel_name = 'new_post'
    try:
        sub = await aioredis.create_redis((REDIS_HOST, 6379), timeout=2)  # loop=app.loop
        ch, *_ = await sub.subscribe(chanel_name)
        async for msg in ch.iter(encoding='utf-8'):
            # Forward message to all connected websockets:
            for ws in app['websockets']:
                await ws.send_str('{}: {}'.format(ch.name, msg))
    except asyncio.CancelledError:
        pass
    except ConnectionRefusedError:
        print('Redis conn refused')
    except Exception:
        print('EXCEPTION')
        raise
    finally:
        if sub:
            await sub.unsubscribe(chanel_name)
            await sub.quit()


async def start_background_tasks(app):
    loop = asyncio.get_event_loop()
    task = loop.create_task(listen_to_redis(app))
    app['redis_listener'] = task  # asyncio.create_task()


async def cleanup_background_tasks(app):
    app['redis_listener'].cancel()
    await app['redis_listener']


app = web.Application()
app.add_routes(routes)
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)
app.on_shutdown.append(on_shutdown)
app['websockets'] = weakref.WeakSet()

if __name__ == '__main__':
    web.run_app(app)
