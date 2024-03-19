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
        self.initialized = {
            "portfolioLedger":False,
            "positionsAll":False,
        }
        self.balance = False
        self.orderSubmitted = False
        self.orderApproveReplied = True
        self.test = False
        self.myPositions = {}
        self.myLiveOrders = {}

        self.positions = {}
        self.liveOrders = {}

        self.cashbalance = None
        self.netliquidationvalue = None
        self.stockmarketvalue = None
        self.dividends = None


        #self.config =  {x:group_proportion[x] for x in group_proportion}
        #pp(self.config)
        self.stkp = stk_param 
        pp(self.stkp)
        self.symbols = list( self.stkp.keys() )

        self.grouped_quota = {}

        self.symbol2conid = {}
        self.conid2symbol = {}
        self.conids = []

        jobs = self.scheduler.get_jobs()
        await restin.put([RESTRequests.securityStocksBySymbols(
            symbols = self.symbols
        )])
        for i in jobs:
            i.remove()

        self.scheduler.add_job(self.getInfoRequests, 'interval', seconds=5)


    async def getInfoRequests(self):
        print(self.conids)
        await restin.put([
            RESTRequests.portfolioLedger(), #to get balance
            RESTRequests.positionsAll(), #to get current positions
            RESTRequests.liveOrders(), #to get liveOrders
        ])
        histRequest = [RESTRequests.transactionHistory(conid = x, days=7) for x in self.conids]
        await restin.put( histRequest )


    @BotBase.restResponse
    def onSecurityStocksBySymbolsResp(self, name, content):
        jc = json.loads(content)
        self.symbol2conid = {
            x:jc[x][0]['contracts'][0]['conid'] for x in self.symbols
        }
        self.conid2symbol = {
            value:key for key, value in self.symbol2conid.items()
        }
        self.conids = list(self.symbol2conid.values())
        #print(f"##symbol2conid : ", end="")
        #pp(self.symbol2conid)
        #print(f"##conid2symbol : ", end="")
        #pp(self.conid2symbol)
        #print(f"##conids : ", end="")
        #pp(self.conids)


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
        #print(f"##{name} : {self.myLiveOrders}")

    @BotBase.restResponse
    def onPositionsAllResp(self, name, content):
        #print(f"##{name} : {content}")
        jc = json.loads(content)
        self.myPositions = { p.get('contractDesc'):p for p in jc }
        if len(self.myPositions) < 30:
            self.positions = {
                x:{
                    "mktPrice":self.myPositions[x]["mktPrice"],
                    "position":self.myPositions[x]["position"],
                    "mktValue":self.myPositions[x]["mktValue"]
                } for x in self.symbols
            }
            self.initialized[name] = True

    @BotBase.restResponse
    def onRespondChain_PositionNextPageResp(self, name, content):
        #print(f"##{name} : {content}")
        jc = json.loads(content)
        newPositions = { p.get('contractDesc'):p for p in jc }
        self.myPositions = self.myPositions | newPositions
        if len(newPositions) < 30 and len(newPositions)>0:
            self.positions = {
                x:{
                    "mktPrice":self.myPositions[x]["mktPrice"],
                    "position":self.myPositions[x]["position"]
                } for x in self.symbols
            }
            self.initialized[name] = True
       
    @BotBase.restResponse
    def onPortfolioLedgerResp(self, name, content):
        jc = json.loads(content)
        c = jc[DEFAULT_CURRENCY]
        self.cashbalance = c.get("cashbalance")
        self.stockmarketvalue = c.get("stockmarketvalue")
        self.dividends = c.get("dividends")
        self.netliquidationvalue = c.get("netliquidationvalue")
        self.initialized[name] = True

    @BotBase.restResponse
    def onModifyOrderResp(self, name, content ):
        print(f"##{name} : {content}")

    @BotBase.restResponse
    def onRespondChain_ModifyOrdersApprovResp(self, name, content ):
        print(f"##{name} : {content}")


    async def mainloop(self):
        await asyncio.sleep(1)
        try:
            if all(self.initialized.values()):
                print(f"cash = {self.cashbalance} | ", end="")
                print(f"stockmarketvalue = {self.stockmarketvalue} | ", end="")
                print(f"total = {self.netliquidationvalue} | ", end="", flush=True)
                quota = self.netliquidationvalue
                #grouped_quota = { x: self.config[x]*quota for x in self.config.keys() }
                #stock_quota = {
                #    x: self.stkp[x]["in_group_proportion"]*grouped_quota[self.stkp[x]["group"]]
                #    for x in self.stkp.keys() }
                #print(f">> QUOTA::{quota} => {grouped_quota} => {stock_quota}")
                pp(self.positions)

            else:
                print("[waiting for initialized]", end="", flush=True)
        except Exception as e:
            print(e)


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
                orders = [ Order(conid=6223250, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=140, quantity=1, tif=OrderTIF.DAY)],
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(conid=6223250, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=141, quantity=1, tif=OrderTIF.DAY)],
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(conid=6223250, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=142, quantity=1, tif=OrderTIF.DAY)],
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(conid=6223250, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=143, quantity=1, tif=OrderTIF.DAY)],
            ),
            RESTRequests.placeOrders( 
                orders = [ Order(conid=6223250, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=144, quantity=1, tif=OrderTIF.DAY)],
            ),
        ])'''

#await restin.put([
#    RESTRequests.modifyOrder(orderId = "2096356379", accountId=acctId, conid=6223250, price = 119, quantity = 1)
#])

#await restin.put([
#    RESTRequests.modifyOrder(
#        orderId = "1533554647", 
#        conid=6223250, 
#        price = 146, 
#        orderType = OrderType.LIMIT,
#        quantity = 1, 
#        side=OrderSide.SELL, 
#        tif = OrderTIF.DAY)
#])  