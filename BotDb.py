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
    stockname = Column(String)
    exchange = Column(String)
    timestamp = Column(Integer)

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


if __name__ == '__main__':
    pass