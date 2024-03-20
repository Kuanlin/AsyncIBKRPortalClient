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

    async def newStock(self, jsdata):
        await self.lock.acquire()

    async def config(self, jsdata):
        await self.lock.acquire()





#
#
#Base = declarative_base()
#class Order(Base):
#    __tablename__ = "Orders"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    uid = Column(LargeBinary)
#    accid = Column(LargeBinary)
#    timestamp = Column(Integer)
#    lastupdatetimestamp = Column(Integer)
#    tradeable = Column(String)
#    direction = Column(String)
#    quantity = Column(String)
#    filled = Column(String)
#    limitprice = Column(String)
#    ordertype = Column(String)
#    reduceonly = Column(Boolean)
#    __table_args__ = (
#        UniqueConstraint(
#            'uid', 'lastupdatetimestamp', 
#            name='ord_uid_lastupdate_uc'),)
#    
#class Execute(Base):
#    __tablename__ = "Executes"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    uid = Column(LargeBinary)
#    timestamp = Column(Integer)
#    quantity = Column(String)
#    price = Column(String)
#    markprice = Column(String)
#    exetype = Column(String)
#    limitfilled = Column(Boolean)
#    usdvalue = Column(String)
#    orderpositionsize = Column(String)
#    orderfee = Column(String)
#    orderuid = Column(LargeBinary, ForeignKey("Orders.uid"))
#    oldtakerorderuid = Column(LargeBinary)
#    __table_args__ = (
#        UniqueConstraint(
#            'uid', name='exec_uid_uc'),)
#    
#class PUC(Base): #Place Update Cancel
#    __tablename__ = "PUC"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    uid = Column(LargeBinary)
#    timestamp = Column(Integer)
#    lastupdatetimestamp = Column(Integer)
#    status = Column(String)
#    orderuid = Column(LargeBinary, ForeignKey("Orders.uid"))
#    reason = Column(String)
#    ordererror = Column(String)
#    __table_args__ = (
#        UniqueConstraint(
#            'uid', 'lastupdatetimestamp', 'status',
#            name='puc_uid_lastupdate_status_uc'),)
#
#class Fill(Base):
#    __tablename__ = "Fills"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    fillid = Column(LargeBinary)
#    symbol = Column(String)
#    side = Column(String)
#    orderid = Column(LargeBinary)
#    size = Column(Numeric)
#    price = Column(Numeric)
#    filltime = Column(Integer)
#    filltype = Column(String)
#    __table_args__ = (
#        UniqueConstraint(
#            'fillid',
#            name='fill_fillid_uc'),)
#
#class ParamsHistory(Base):
#    __tablename__ = "Params"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    timestamp = Column(Integer)
#    remark = Column(Text)
#    actions = Column(Text)
#    modelparams = Column(Text)     
#
#
#class BotDb:
#    def __init__(self):
#        self.engine = create_async_engine(
#            "sqlite+aiosqlite:///file:saved.db?uri=True", echo=False )
#        self.lock = asyncio.Lock()
#
#    async def async_init(self):
#        meta = Base.metadata
#        async with self.engine.begin() as conn:
#            await conn.run_sync(meta.create_all)
#
#    async def insertOrderDatas(self, jsdata):
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            try:
#                for ele in jsdata["elements"]:
#                    #print(ele)
#                    evt = ele.get("event")
#                    statuskey = list(evt.keys())[0]
#                    _status = evt.get(statuskey)
#                    if statuskey=="OrderUpdated":
#                        order = _status.get("newOrder")
#                    elif statuskey=="OrderEditRejected":
#                        order = _status.get("attemptedOrder")
#                    else:
#                        order = _status.get("order")
#                    if (k:=statuskey)=="OrderUpdated":
#                        evtk = ele.get("event").get(k)
#                        order_dict = evtk.get("newOrder")
#                        stmt = insert(Order).prefix_with("OR IGNORE").values(
#                                uid = bytes(uuid.UUID(order_dict.get("uid")).hex,'ascii'),
#                                accid = bytes(uuid.UUID(order_dict.get("accountUid")).hex,'ascii'),
#                                timestamp = order_dict.get("timestamp"),
#                                lastupdatetimestamp = order_dict.get("lastUpdateTimestamp"),
#                                tradeable = order_dict.get("tradeable"),
#                                direction = order_dict.get("direction"),
#                                quantity = order_dict.get("quantity"),
#                                filled = order_dict.get("filled"),
#                                limitprice = order_dict.get("limitPrice"),
#                                ordertype = order_dict.get("orderType"),
#                                reduceonly = order_dict.get("reduceOnly"))
#                        await asession.execute(stmt)
#                        order_dict = evtk.get("oldOrder")
#                        stmt = insert(Order).prefix_with("OR IGNORE").values(
#                                uid = bytes(uuid.UUID(order_dict.get("uid")).hex,'ascii'),
#                                accid = bytes(uuid.UUID(order_dict.get("accountUid")).hex,'ascii'),
#                                timestamp = order_dict.get("timestamp"),
#                                lastupdatetimestamp = order_dict.get("lastUpdateTimestamp"),
#                                tradeable = order_dict.get("tradeable"),
#                                direction = order_dict.get("direction"),
#                                quantity = order_dict.get("quantity"),
#                                filled = order_dict.get("filled"),
#                                limitprice = order_dict.get("limitPrice"),
#                                ordertype = order_dict.get("orderType"),
#                                reduceonly = order_dict.get("reduceOnly"))
#                        await asession.execute(stmt)
#                    elif (k:=statuskey)=="OrderEditRejected":
#                        evtk = ele.get("event").get(k)
#                        order_dict = evtk.get("attemptedOrder")
#                        stmt = insert(Order).prefix_with("OR IGNORE").values(
#                                uid = bytes(uuid.UUID(order_dict.get("uid")).hex,'ascii'),
#                                accid = bytes(uuid.UUID(order_dict.get("accountUid")).hex,'ascii'),
#                                timestamp = order_dict.get("timestamp"),
#                                lastupdatetimestamp = order_dict.get("lastUpdateTimestamp"),
#                                tradeable = order_dict.get("tradeable"),
#                                direction = order_dict.get("direction"),
#                                quantity = order_dict.get("quantity"),
#                                filled = order_dict.get("filled"),
#                                limitprice = order_dict.get("limitPrice"),
#                                ordertype = order_dict.get("orderType"),
#                                reduceonly = order_dict.get("reduceOnly"))
#                        await asession.execute(stmt)
#                        order_dict = evtk.get("oldOrder")
#                        stmt = insert(Order).prefix_with("OR IGNORE").values(
#                                uid = bytes(uuid.UUID(order_dict.get("uid")).hex,'ascii'),
#                                accid = bytes(uuid.UUID(order_dict.get("accountUid")).hex,'ascii'),
#                                timestamp = order_dict.get("timestamp"),
#                                lastupdatetimestamp = order_dict.get("lastUpdateTimestamp"),
#                                tradeable = order_dict.get("tradeable"),
#                                direction = order_dict.get("direction"),
#                                quantity = order_dict.get("quantity"),
#                                filled = order_dict.get("filled"),
#                                limitprice = order_dict.get("limitPrice"),
#                                ordertype = order_dict.get("orderType"),
#                                reduceonly = order_dict.get("reduceOnly"))
#                        await asession.execute(stmt)
#                    else:
#                        order_dict = ele.get("event").get(k).get("order")
#                        stmt = insert(Order).prefix_with("OR IGNORE").values(
#                                uid = bytes(uuid.UUID(order_dict.get("uid")).hex,'ascii'),
#                                accid = bytes(uuid.UUID(order_dict.get("accountUid")).hex,'ascii'),
#                                timestamp = order_dict.get("timestamp"),
#                                lastupdatetimestamp = order_dict.get("lastUpdateTimestamp"),
#                                tradeable = order_dict.get("tradeable"),
#                                direction = order_dict.get("direction"),
#                                quantity = order_dict.get("quantity"),
#                                filled = order_dict.get("filled"),
#                                limitprice = order_dict.get("limitPrice"),
#                                ordertype = order_dict.get("orderType"),
#                                reduceonly = order_dict.get("reduceOnly"))
#                        await asession.execute(stmt)
#                    stmt = insert(PUC).prefix_with("OR IGNORE").values(
#                        uid = bytes(uuid.UUID(ele.get("uid")).hex,'ascii'),
#                        timestamp = ele.get("timestamp"),
#                        lastupdatetimestamp = order.get("lastUpdateTimestamp"),
#                        status = statuskey,
#                        orderuid = bytes(uuid.UUID(order.get("uid")).hex,'ascii'),
#                        reason = _status.get("reason"),
#                        ordererror = (lambda x:"" if x is None else x)(_status.get("orderError")) ) 
#                    await asession.execute(stmt)
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#
#    async def insertExecuteDatas(self, jsdata):
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            try:
#                for ele in jsdata["elements"]:
#                    exec_dict = ele.get("event").get("execution").get("execution")
#                    if (_oldtakerorderuid := exec_dict.get("oldTakerOrder")):
#                        _oldtakerorderuid = bytes(uuid.UUID(_oldtakerorderuid.get("uid")).hex,'ascii')
#                    else:
#                        _oldtakerorderuid = None
#                    stmt = insert(Execute).prefix_with("OR IGNORE").values(
#                        uid = bytes(uuid.UUID(exec_dict.get("uid")).hex,'ascii'),
#                        timestamp = exec_dict.get("timestamp"),
#                        quantity = exec_dict.get("quantity"),
#                        price = exec_dict.get("price"),
#                        markprice = exec_dict.get("markPrice"),
#                        limitfilled = exec_dict.get("limitFilled"),
#                        exetype = exec_dict.get("executionType"),
#                        usdvalue = exec_dict.get("usdValue"),
#                        orderpositionsize = exec_dict.get("orderData").get("positionSize"),
#                        orderfee = exec_dict.get("orderData").get("fee"),
#                        orderuid = bytes(uuid.UUID(exec_dict.get("order").get("uid")).hex,'ascii'),
#                        oldtakerorderuid = _oldtakerorderuid )
#                    await asession.execute(stmt)
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#
#    async def insertFillDatas(self, jsdata):
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            try:
#                for fi in jsdata["fills"]:
#                    utctimestamp = int(
#                        datetime.strptime(
#                            "2020-07-22T13:37:27.077Z", 
#                            "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()*1000)
#                    stmt = insert(Fill).prefix_with("OR IGNORE").values(
#                        fillid = bytes(uuid.UUID(fi.get("fill_id")).hex, 'ascii'),
#                        symbol = fi.get("symbol"),
#                        side = fi.get("side"),
#                        orderid = bytes(uuid.UUID(fi.get("order_id")).hex, 'ascii'),
#                        size = fi.get("size"),
#                        price = fi.get("price"),
#                        filltime = utctimestamp,
#                        filltype = fi.get("fillType"))
#                    await asession.execute(stmt)
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#
#            
#    async def lastExecuteTimestamp(self):
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            result = 0
#            try:
#                q = select(func.max(Execute.timestamp))
#                result = (await asession.execute(q)).first()[0]
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#        if not result:
#            result = 0
#        return result
#
#    async def lastOrderEvtTimestamp(self):
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            result = 0
#            try:
#                q = select(func.max(Order.lastupdatetimestamp))
#                result = (await asession.execute(q)).first()[0]
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#        if not result:
#            result = 0
#        return result
#
#    async def unfilled(self):
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            query = text( \
#                "SELECT * FROM Orders WHERE uid in ("
#                "SELECT orderuid FROM " \
#                "(SELECT *, max(lastupdatetimestamp) FROM PUC " \
#                "WHERE status='OrderPlaced' or status='OrderUpdated' or status='OrderCancelled' " \
#                "GROUP BY orderuid " \
#                "ORDER BY id) " \
#                "WHERE orderuid NOT IN (SELECT orderuid FROM Executes WHERE 1) and status!='OrderCancelled' );")
#            try:
#                result = (await asession.execute(query)).mappings()
#                resultmodels = [Order(**x) for x in result]
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#        return resultmodels
#
#    async def quantitiesInOpenPosition(self): #postive buy long position, negative: sell short position
#        await self.lock.acquire()
#        try:
#            async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#            asession = async_session()
#            query = text( \
#                """
#                SELECT (sumbuy-sumsell) FROM (
#                (SELECT SUM(CAST(quantity AS DOUBLE)) AS sumbuy
#                FROM Executes 
#                WHERE orderuid in (
#                SELECT uid 
#                FROM Orders 
#                WHERE direction='Buy')),
#                (SELECT SUM(CAST(quantity AS DOUBLE)) AS sumsell
#                FROM Executes 
#                WHERE orderuid in (
#                SELECT uid 
#                FROM Orders 
#                WHERE direction='Sell')));"""
#                )
#            try:
#                result = (await asession.execute(query)).fetchone()[0]
#                await asession.commit()
#            finally:
#                await asession.close()
#        finally:
#            self.lock.release()
#        return result
#        
#botDB = BotDB()
#
#
#ParamBase = declarative_base()
#class Params(ParamBase):
#    __tablename__ = "Params"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    timestamp = Column(Integer)
#    remark = Column(Text)
#    actions = Column(Text)
#    modelparams = Column(Text)
#
#class ParamsDB:
#
#    def __init__(self):
#        self.engine = create_async_engine(
#            "sqlite+aiosqlite:///file:param.db?mode=ro&uri=True", echo=False )
#
#    async def async_init(self):
#        meta = ParamBase.metadata
#        async with self.engine.begin() as conn:
#            await conn.run_sync(meta.create_all)
#
#    async def getlastparams(self):
#        async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
#        asession = async_session()
#        result = 0
#        try:
#            q = select([Params, func.max(Params.timestamp)])
#            result = (await asession.execute(q)).first()[0]
#            await asession.commit()
#        finally:
#            await asession.close()
#        return result
#
#paramsDB = ParamsDB()
#
#
#BotSysBase = declarative_base()
#class BotInfo(BotSysBase):
#    __tablename__ = "SysInfo"
#    id = Column(Integer, primary_key = True, autoincrement = True)
#    timestamp = Column(Integer)
#    info = Column(Text)
#
#class BotInfoDB:
#    def __init__(self):
#        self.engine = create_async_engine(
#            "sqlite+aiosqlite:///file:sysinfo.db?&uri=True", echo=False )
#
#    async def async_init(self):
#        meta = BotSysBase.metadata
#        async with self.engine.begin() as conn:
#            await conn.run_sync(meta.create_all)
#
#    async def loginfo(self, str):
#        pass
#
#botInfoDB = BotInfoDB()