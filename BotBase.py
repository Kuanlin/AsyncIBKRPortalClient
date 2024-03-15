from RSession import *
from WSession import *

class BotBase():
    def __init__(self, rest:RESTRequestSession , ws:WSSession):
        self.init = asyncio.Event()
        self.rest = rest
        self.restReInit()

    def restReInit(self):
        self.init.clear()
        self.rest.aquireRequestList = self.restRequestList
        self.rest.onResponse = self.restOnResponse
        self.rest.onClientInit = self.restInit

    async def restInit(self):
        pass

    async def restRequestList(self) -> dict:
        return await restin.get()

    async def restOnResponse(self, response):
        name = response['name']
        content = response['content']
        #content = (await response.content.read()).decode('utf8')
        try:
            f = object.__getattribute__(self.__class__, f"on{name[0].upper()}{name[1:]}Resp")
            f(self, name, content)
        except (AttributeError, NameError) as e:
            print(e)
            #print(f"on{name[0].upper()}{name[1:]}Resp not found")

    def restResponse(func):
        def warp(self, name, content):
            #print("---restResponse")
            #print(f"------ response name :{name}")
            #print(f"------ response content: \r\n{content}")
            #print("restResponse---")
            func(self, name, content)
        return warp
        
    async def run(self):
        while True:
            try:
                while True:
                    await asyncio.sleep(0)
                    try:
                        await asyncio.sleep(0)
                        await self.mainloop()
                    except Exception as e:
                        await self.restReInit()
                        await asyncio.sleep(1)
                        next
            except Exception as e:
                await asyncio.sleep(1)
                next
        
    async def mainloop():
        await asyncio.sleep(0.5)
            