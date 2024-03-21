import asyncio, uuid, json
from datetime import datetime
from sqlalchemy import select, insert, func, text, \
                        Column, ForeignKey, Integer, Numeric, \
                        String, Text, LargeBinary, Boolean#, Float
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base#, relationship


BotDBBase = declarative_base()
class Stock(BotDBBase):
    __tablename__ = "Stock"
    id = Column(Integer, primary_key = True, autoincrement = True)
    conid = Column(Integer)
    name = Column(String)
    exchange = Column(String)
    timestamp = Column(Integer)
    __table_args__ = (
        UniqueConstraint(
            'conid', 
            name='conid_uc'),)

class Config(BotDBBase):
    __tablename__ = "Config"
    id = Column(Integer, primary_key = True, autoincrement = True)
    stkid = Column(LargeBinary, ForeignKey("Stock.id"))
    initvalue = Column(Numeric)
    leverage = Column(Numeric)
    singlesidespreadquantity = Column(Integer)
    spreadsteppriceratio = Column(Numeric)
    spreadsteppriceminimal = Column(Numeric)
    timestamp = Column(Integer)

class PnL(BotDBBase):
    __tablename__ = "PnL"
    id = Column(Integer, primary_key = True, autoincrement = True)
    stkid = Column(LargeBinary, ForeignKey("Stock.id"))
    realizedpnl = Column(Numeric)
    timestamp = Column(Integer)


class BotDB:
    def __init__(self):
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///file:bot.db?uri=True", echo=True )
        self.lock = asyncio.Lock()

    async def async_init(self):
        meta = BotDBBase.metadata
        async with self.engine.begin() as conn:
            await conn.run_sync(meta.create_all)

        await self.create_pnl_view()

    async def create_pnl_view(self):
        await self.lock.acquire()
        try:
            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            asession = async_session()
            stmt = text( "CREATE VIEW IF NOT EXISTS stockpnlview AS "\
            f"SELECT Stock.id, Stock.conid, Stock.name, Stock.exchange, PnL.realizedpnl, PnL.timestamp "\
            f"FROM Stock JOIN PnL ON Stock.id = PnL.stkid;" )
            await asession.execute(stmt)
            await asession.commit()
        finally:
            self.lock.release()

    async def insertStock(
            self, stockname, conid, exchange, timestamp):
        await self.lock.acquire()
        try:
            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            asession = async_session()
            stmt = insert(Stock).prefix_with("OR IGNORE").values(
                conid = conid,
                stockname = stockname,
                exchange = exchange,
                timestamp = timestamp,
            )
            await asession.execute(stmt)
            await asession.commit()
        finally:
            self.lock.release()


    async def config(
            self, stock, initvalue, leverage, 
            singlesidespreadquantity,
            spreadsteppriceratio,
            spreadsteppriceminimal,
            timestamp):
        await self.lock.acquire()
        try:
            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            asession = async_session()
            stmt = insert(Stock).prefix_with("OR IGNORE").values(
                conid = stock.conid,
                initvalue = initvalue,
                leverage = leverage,
                singlesidespreadquantity = singlesidespreadquantity,
                spreadsteppriceratio = spreadsteppriceratio,
                spreadsteppriceminimal = spreadsteppriceminimal,
                timestamp = timestamp
            )
            await asession.execute(stmt)
            await asession.commit()
        finally:
            self.lock.release()

    async def realized(self, stock, realizedpnl, timestamp):
        await self.lock.acquire()
        try:
            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            asession = async_session()
            stmt = insert(Stock).prefix_with("OR IGNORE").values(
                conid = stock.conid,
                realizedpnl = realizedpnl,
                timestamp = timestamp
            )
            await asession.execute(stmt)
            await asession.commit()
        finally:
            self.lock.release()

    async def allStocks(self):
        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        asession = async_session()
        result = 0
        try:
            q = select(Stock).where(True)
            result = (await asession.execute(q)).all()
            await asession.commit()
        finally:
            await asession.close()
        return next(zip(*result))
    
    async def allStocksAndPnL(self):
        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        asession = async_session()
        result = 0
        try:
            stock = [ i for i in await self.allStocks() ]
            print(f"stockids={stock}")
            q = text( \
                f"SELECT Stock.id, Stock.conid, Stock.name, Stock.exchange, t2.realizedpnl, t2.timestamp "\
                f"FROM Stock LEFT JOIN (SELECT stkid, realizedpnl MAX(timestamp) FROM Pnl WHERE 1=1) AS t2 ON Stock.id = t2.stkid;" )
            result = (await asession.execute(q)).all()
            print(result)
        finally:
            await asession.close()
      

    async def findStockByName(self, stockname):
        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        asession = async_session()
        result = 0
        try:
            q = select(Stock).where(Stock.name == stockname)
            result = (await asession.execute(q)).all()
            await asession.commit()
        finally:
            await asession.close()
        return next(zip(*result))

    async def findConfigByStock(self, stockname):
        pass




botDB = BotDB()
async def test():
    while(True):
        await asyncio.sleep(0.5)
        #print(".",end="", flush=True)


import aioconsole
from pprint import pprint as pp

async def botDBMain():
    await botDB.async_init()

    result = await botDB.allStocks()
    r = [ (i+1, x.name, x.conid, x.exchange) for i, x in enumerate(result) ]
    pp(r)
    await botDB.allStocksAndPnL()
    print("Input Stock Name:")
    user_input = await aioconsole.ainput()




async def asyncBotDB():
    await asyncio.gather( botDBMain(), test() )

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(asyncBotDB())
    loop.run_forever()
    loop.close()

if __name__ == '__main__':
    run()
