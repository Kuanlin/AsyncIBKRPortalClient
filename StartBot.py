import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from BotBase import BotBase
from RSession import *
from WSession import *
from pprint import pprint as pp
from DefaultValues import *


class Bot(BotBase):

    async def restInit(self):
        print("---restInit")
        self.balance = False
        self.orderSubmitted = False
        self.orderApproveReplied = True
        self.test = False
        self.myPositions = {}
        self.myLiveOrders = {}

        self.stock2conid = {}
        self.conid2stock = {}

        self.cashbalance = None
        self.netliquidationvalue = None
        self.stockmarketvalue = None
        self.dividends = None
        jobs = self.scheduler.get_jobs()
        for i in jobs:
            i.remove()
        self.scheduler(self.getInfoRequests, 'interval', seconds=5)


    async def getInfoRequests():
        await restin.put([
            RESTRequests.positionsAll(),
            RESTRequests.liveOrders(),
            RESTRequests.portfolioLedger(),
            RESTRequests.transactionHistory(conids = [6223250]),
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
        print(f"##{name} : {content}")

    @BotBase.restResponse
    def onLiveOrdersResp(self, name, content):
        jc = json.loads(content)
        self.myLiveOrders = jc.get('orders')
        print(f"##{name} : {self.myLiveOrders}")

    @BotBase.restResponse
    def onPositionsAllResp(self, name, content):
        jc = json.loads(content)
        self.myPositions = { p.get('contractDesc'):p for p in jc }
        print(f"##{name} : ", end="")
        if len(self.myPositions) < 30:
            pp(self.myPositions)

    @BotBase.restResponse
    def onRespondChain_PositionNextPageResp(self, name, content):
        jc = json.loads(content)
        newPositions = { p.get('contractDesc'):p for p in jc }
        self.myPositions = self.myPositions | newPositions
        if len(newPositions) < 30 and len(newPositions)>0:
            pp(self.myPositions)


    @BotBase.restResponse
    def onSecurityStocksBySymbolsResp(self, name, content):
        jc = json.loads(content)
       
    @BotBase.restResponse
    def onPortfolioLedgerResp(self, name, content):
        jc = json.loads(content)
        c = jc[DEFAULT_CURRENCY]
        self.cashbalance = c.get("cashbalance")
        self.stockmarketvalue = c.get("stockmarketvalue")
        self.dividends = c.get("dividends")
        self.netliquidationvalue = c.get("netliquidationvalue")
        print(f"#{name}")
        print(f"cash = {self.cashbalance}")
        print(f"stockmarketvalue = {self.stockmarketvalue}")
        print(f"total = {self.netliquidationvalue}")
        
    async def mainloop(self):
        await asyncio.sleep(0.5)
        #calculate all

        if not self.balance:
            pageId = 0

        tsm=self.myPositions.get('TSM')
        msft=self.myPositions.get('MSFT')
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

#await restin.put([
#    RESTRequests.modifyOrder(orderId = "2096356379", accountId=acctId, conid=6223250, price = 119, quantity = 1)
#])
