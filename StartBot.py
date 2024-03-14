import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from BotBase import BotBase
from RSession import *
from WSession import *

class Bot(BotBase):

    async def restInit(self):
        print("---restInit")
        self.balance = False
        self.orderSubmitted = False
        self.orderApproveReplied = True

        await restin.put ([
            RESTRequests.transactionHistory(
                accountIds = ["ABC", "DEF"], conids = [123, 456] ) ])

    @BotBase.restResponse
    def onPlaceOrdersResp(self, name, content):
        self.orderApproveReplied = False
        print("---onPlaceOrdersResp")

    @BotBase.restResponse
    def onRespondChain_OrdersApprovResp(self, name, content):
        self.orderApproveReplied = True
        print("---onRespondChain_OrdersApprovResp")

    @BotBase.restResponse
    def onTransactionHistoryResp(self, name, content):
        print("---onTransactionHistoryResp")

    @BotBase.restResponse
    def onLiveOrdersResp(self, name, content):
        print("---onLiveOrdersResp")

    @BotBase.respResponse
    def onPositionsAllResp(self, name, content):
        print("---onPositionsAllResp")

    @BotBase.respResponse
    def onRespondChain_PositionNextPageResp(self, name, content):
        print("---onRespondChain_PositionNextPageResp")

    async def mainloop(self):
        await asyncio.sleep(0.5)
        #calculate all
        if not self.balance and self.orderApproveReplied:
            await restin.put([
                RESTRequests.placeOrders([
                    Order(conid=1234, side=OrderSide.BUY, orderType=OrderType.LIMIT, price=3.1415, quantity=10000.333445, tif=OrderTIF.DAY),
                    Order(conid=5678, side=OrderSide.SELL, orderType=OrderType.LIMIT, price=3.1415, quantity=9999, tif=OrderTIF.DAY),
                    Order(conid=9101, side=OrderSide.BUY, orderType=OrderType.MARKET, price=550, quantity=10000.333445, tif=OrderTIF.DAY) ]) ])
            self.balance = True

        print("[mainloop]")



async def IBKRMain():
    ib_rest = RESTRequestSession()
    ib_ws = WSSession()
    mb = Bot(rest = ib_rest, ws = ib_ws)
    await asyncio.gather(
        ib_rest.restClientSession(), mb.run() )


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scheduler = AsyncIOScheduler(({'event_loop': asyncio.get_event_loop()}))
    scheduler.start()
    loop.create_task(IBKRMain())
    loop.run_forever()
    loop.close()



