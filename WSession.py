import asyncio, aiohttp, ssl, json
#logger = logging.getLogger("WS")
WS_DEFAULT_TIMEOUT = 10

class WSRequests:
     
    def pingServer(timeout: int = WS_DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"POST",
            "url": f"/tickle",
            "params": "json=",
            "timeout": timeout
        }
    


WS_API_URI = r"wss://localhost:5000/v1/api/ws"

class WSSession:
    def __init__(self):
        self.ws = None
        self.session = None
        self.sslcontext = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=None,
            capath=None,
            cadata=None )
        self.reconnect_sleep_time = 10
        self.msg = ""

    async def websocketClientSession(self):
        #logger.info("Websocket try connecting..")

        while True:
            try:
                self.private_subscribed = False
                #timeout = aiohttp.ClientTimeout(total=60)
                #logger.info("New WS Session")
                async with aiohttp.ClientSession(
                    auto_decompress=False, json_serialize=False) as self.session:
                    try:
                        #logger.info("New WS Connection")
                        async with self.session.ws_connect(
                            WS_API_URI, ssl_context=self.sslcontext,
                            heartbeat=10
                        ) as self.ws:
                            await self.onConnect(self.ws)
                            while True:
                                async with asyncio.timeout(60):
                                    self.msg = await self.ws.receive()
                                await self.onMessage(self.ws, self.msg)
                                self.callback()
                                await self.onCallback()
                                await asyncio.sleep(0) #for other async processes

                    except aiohttp.ServerTimeoutError as e:
                        #logger.info(f"{e} ServerTimeout Error")
                        try:
                            pass
                        except:
                            break
            except WSServerException as e:
                msg = "Unknown"
                try:
                    msg = f"Unknown: {e}"
                    msg = aiohttp.WSMsgType(int(str(e))).name
                except:
                    pass
                #logger.info(f"WSSrvException: {msg}, Reconnecting..")
                await asyncio.sleep(0)
                continue
            except aiohttp.ServerDisconnectedError:
                await asyncio.sleep(self.reconnect_sleep_time)
                #logger.info(f"{e} WebSocket Try reconnecting.")
                continue
            except aiohttp.ClientConnectionError as e:
                await asyncio.sleep(self.reconnect_sleep_time)
                #logger.info(f"{e} WebSocket Try reconnecting..")
                continue
            except Exception as e:
                await asyncio.sleep(self.reconnect_sleep_time)
                #logger.info(f"{e} \nWS Reconnecting")
                continue  
            #await asyncio.sleep(0.5)

    async def onConnect(self, websocket):
        pass

    async def onMessage(self, websocket, message, **kwargs):
        pass

    async def onCallback(self):
        pass

    def callback(self):
        pass


class WSServerException(Exception):
    pass

