from aiohttp import web, ClientSession
import aiohttp
import weakref
import aioredis
import asyncio


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
                    async with session.get('http://127.0.0.1:8000/post/') as resp:
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
    try:
        sub = await aioredis.create_redis(('localhost', 6379), loop=app.loop)
        ch, *_ = await sub.subscribe('new_post')
        async for msg in ch.iter(encoding='utf-8'):
            # Forward message to all connected websockets:
            for ws in app['websockets']:
                await ws.send_str('{}: {}'.format(ch.name, msg))
    except asyncio.CancelledError:
        pass
    finally:
        await sub.unsubscribe(ch.name)
        await sub.quit()


async def start_background_tasks(app):
    app['redis_listener'] = app.loop.create_task(listen_to_redis(app))


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
