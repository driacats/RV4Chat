from aiohttp import web

async def handle_post(request):
	request = await request.json()
	print(request)
	return web.Response(status=200)

app = web.Application()
app.add_routes([web.post('/', handle_post)])
web.run_app(app, port=8888)
