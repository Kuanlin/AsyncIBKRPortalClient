import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from BotBase import BotBase
from RSession import *
from WSession import *
from pprint import pprint as pp

jf = open("config.json","r")
acctId = "U"+json.load(jf)["id"]



class Bot(BotBase):

    async def restInit(self):
        print("---restInit")
        self.balance = False
        self.orderSubmitted = False
        self.orderApproveReplied = True
        self.test = False
        self.myPositions = {}
        self.myLiveOrders = {}
        #await restin.put ([
        #    RESTRequests.transactionHistory(
        #        accountIds = ["ABC", "DEF"], conids = [123, 456] ) ])
        '''
        await restin.put ([
            RESTRequests.placeOrders( 
                orders = [ Order(acctId = acctId,conid=6223250, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=120, quantity=1, tif=OrderTIF.DAY)],
                accountId = str(acctId)
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(acctId = acctId,conid=6223250, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=120, quantity=1, tif=OrderTIF.DAY)],
                accountId = str(acctId)
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(acctId = acctId,conid=6223250, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=120, quantity=1, tif=OrderTIF.DAY)],
                accountId = str(acctId)
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(acctId = acctId,conid=6223250, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=120, quantity=1, tif=OrderTIF.DAY)],
                accountId = str(acctId)
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(acctId = acctId,conid=6223250, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=120, quantity=1, tif=OrderTIF.DAY)],
                accountId = str(acctId)
            ),
        ])'''

        await restin.put([
            RESTRequests.modifyOrder(orderId = "2096356379", acctId=acctId, conid=6223250, price = 119, quantity = 1)
        ])

    @BotBase.restResponse
    def onPlaceOrdersResp(self, name, content):
        self.orderApproveReplied = False
        print(f"##{name} : {content}")

    @BotBase.restResponse
    def onRespondChain_OrdersApprovResp(self, name, content):
        self.orderApproveReplied = True
        print(f"##{name} : {content}")

    @BotBase.restResponse
    def onTransactionHistoryResp(self, name, content):
        print("---onTransactionHistoryResp")

    @BotBase.restResponse
    def onLiveOrdersResp(self, name, content):
        #print(f"##{name} : {content}")
        jc = json.loads(content)
        self.myLiveOrders = jc.get('orders')
        print(f"liveOrders: {self.myLiveOrders} {type(self.myLiveOrders)}")
        #pp(jc)

    @BotBase.restResponse
    def onPositionsAllResp(self, name, content):
        #print(f"##{name} : {content}")
        #print(f"##{name} : ", end="")
        jc = json.loads(content)
        self.myPositions = { p.get('contractDesc'):p for p in jc }
        #pp(self.myPositions)
        #myPositions = pos
        #for p in pos:
        #    print(f"DESC:{p.get('contractDesc')}\nPOS:{p.get('position')}\nMKP:{p.get('mktPrice')}")

    @BotBase.restResponse
    def onRespondChain_PositionNextPageResp(self, name, content):
        #print(f"##{name} : {content}")
        #print()
        pass

    @BotBase.restResponse
    def onSecurityStocksBySymbolsResp(self, name, content):
        #print(f"##{name} : ", end="")
        #pp(json.loads(content))
        jc = json.loads(content)
        #pp([ (c, jc.get(c)[0].get("contracts")[0].get("conid")) for c in jc.keys() ])
        #print()

    async def mainloop(self):
        await asyncio.sleep(0.5)
        #calculate all
        '''
        if not self.balance and self.orderApproveReplied:
            await restin.put([
                RESTRequests.placeOrders([
                    Order(conid=1234, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=3.1415, quantity=10000.333445, tif=OrderTIF.DAY),
                    Order(conid=5678, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=3.1415, quantity=9999, tif=OrderTIF.DAY),
                    Order(conid=9101, side=OrderSide.BUY, orderType=OrderType.MARKET, price=550, quantity=10000.333445, tif=OrderTIF.DAY) ]) ])
            self.balance = True
        '''
        if not self.balance:
            pageId = 0
            #print(acctId)
            await restin.put([
                RESTRequests.positionsAll(pageId = 0, accountId = acctId),    
                #RESTRequests.securityStocksBySymbols(["TSM", "MSFT", "AAPL", "TSLA"]),
                RESTRequests.liveOrders(),
            ])
        tsm=self.myPositions.get('TSM')
        msft=self.myPositions.get('MSFT')
        #pp(tsm)
        '''
        if tsm != None and len(self.myLiveOrders)==0 and self.test == False:
                if tsm.get('position') - 35.0 < 0.00001:
                    print("PLACE_TSM")
                    self.test = True
                    await restin.put([
                        RESTRequests.placeOrders( 
                            orders = [ 
                                Order(acctId = acctId,conid=tsm.get('conid'), side=OrderSide.BUY, orderType=OrderType.LIMIT, price=130, quantity=1, tif=OrderTIF.DAY) ,
                                #Order(acctId = acctId,conid=msft.get('conid'), side=OrderSide.BUY, orderType=OrderType.LIMIT, price=400, quantity=1, tif=OrderTIF.DAY) 
                            ],
                            accountId = str(acctId)
                        ) 
                    ])'''

        self.balance = True

        print("[mainloop]")



async def IBKRMain():
    ib_rest = RESTRequestSession()
    ib_ws = WSSession()
    mb = Bot(rest = ib_rest, ws = ib_ws)
    await asyncio.gather( ib_rest.restClientSession(), mb.run() )


def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler = AsyncIOScheduler(({'event_loop': asyncio.get_event_loop()}))
    scheduler.start()
    loop.create_task(IBKRMain())
    loop.run_forever()
    loop.close()

if __name__ == '__main__':
    run()


