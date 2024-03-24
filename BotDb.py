import asyncio, asyncpg

'''
class StockDB:
    pass

class ConfigDB:
    pass

class PnLsDB:
    pass'''

class BotDB:
    def __init__(self):
        self.conn = None

    async def async_init(self):
        self.conn = await asyncpg.connect(
            user='ibkrusr', password='ibkrpwd',
            database='', host='127.0.0.1')
        stmt = (
            r"DO $$ "
            r"BEGIN"
                r"IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'IBKRDB') THEN"
                    r"CREATE DATABASE IBKRDB;"
                r"END IF;"
            r"END $$;" )
        self.conn.execute(stmt)
        self.conn = await asyncpg.connect(
            user='ibkrusr', password='ibkrpwd',
            database='ibkrdb', host='127.0.0.1')
        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN"
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status') THEN"
                    r"CREATE TYPE status AS ENUM ('stop', 'active', 'liquidating', 'deprecated');"
                r"END IF;"
            r"END $$;" )
        #print(stmt)
        self.conn.execute(stmt)
        stmt = (
            r"CREATE TABLE IF NOT EXISTS stocks ("
                r"id SERIAL, conid INT, "
                r"name Varchar(255),"
                r"exchange Varchar(255), timestamps timestamp,"
                r"PRIMARY KEY(id)"
            r");" )
        #print(stmt)
        self.conn.execute(stmt)
        stmt = (
            r"CREATE TABLE IF NOT EXISTS configs ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"initvalue numeric(20,5) NOT NULL, "
                r"leverage numeric(10, 5) NOT NULL, "
                r"numofsinglespread INT NOT NULL, "
                r"spreadsteppriceratio numeric(12, 5) NOT NULL, "
                r"spreadsteppriceminimal numeric(12, 5) NOT NULL, "
                r"statuscode status, timestamps timestamp, "
                r"PRIMARY KEY(id), FOREIGN KEY(stkid) REFERENCES stocks( id ) "
            r");" )
        #print(stmt)
        self.conn.execute(stmt)
        stmt = (
            r"CREATE TABLE IF NOT EXISTS pnls ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"realizedpnl numeric(20,5), timestamps timestamp, "
                r"PRIMARY KEY(id), FOREIGN KEY(stkid) REFERENCES stocks( id ) "
            r");" )
        #print(stmt)
        self.conn.execute(stmt)
        stmt = (
            r"CREATE OR REPLACE VIEW lateststockpnlview AS"
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.name, s.conid, p.realizedpnl, p.timestamps AS timestamp "
            r"FROM stocks s "
            r"JOIN pnls P ON s.id = p.stkid "
            r"ORDER BY s.id, s.conid, p.timestamps DESC;" )
        #print(stmt)
        self.conn.execute(stmt)
        stmt = (
            r"CREATE OR REPLACE VIEW latestconfigview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.conid, s.name, c.initvalue, c.leverage, c.statuscode, "
                r"c.numofsinglespread, c.spreadsteppriceratio, c.spreadsteppriceminimal, "
                r"c.timestamps AS timestamp "
            r"FROM stocks s "
            r"JOIN configs c ON s.id = c.stkid "
            r"ORDER BY s.id, s.conid, c.timestamps DESC;" )
        #print(stmt)
        self.conn.execute(stmt)


    async def getStock(self, stk = True) -> list: 
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(
                r"SELECT * FROM stocks WHERE name = $1;", stk )
        elif type(stk)==int:
            fetch = self.conn.fetch(
                r"SELECT * FROM stocks WHERE conid = $1;", stk )
        elif type(stk)==bool:
            fetch = self.conn.fetch(
                r"SELECT * FROM stocks WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        return values


    async def getConfig(self, stk = None) -> list:
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE name = $1;", stk )
        elif type(stk)==int:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE conid = $1;", stk )
        elif type(stk)==bool:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        return values
    

    async def newStock(self, stockname, conid:int = None, exchange = None):
        assert type(conid) == int
        stmt = (
            r"INSERT INTO stocks (name, conid, exchange) "
            r"VALUES ($1, $2, $3);" )
        await self.conn.execute(stmt, stockname, conid, exchange)

    async def delStock(self, conid:int = None):
        assert type(conid) == int
        stmt = r"DELETE FROM stocks WHERE conid = $1;"
        await self.conn.execute(stmt, conid)

    async def updateStockDataByName(self, stkname:str, conid:int, exchange:str):
        assert type(conid) == int
        stmt = (
            r"UPDATE stocks "
            r"SET conid = $1, exchange = $2"
            r"WHERE name = $3;" )
        await self.conn.execute(stmt, conid, exchange, stkname)

    async def updateStockDataByConid(self, conid:int, stkname:str, exchange:str):
        assert type(conid) == int
        stmt = (
            r"UPDATE stocks "
            r"SET name = $1, exchange = $2"
            r"WHERE conid = $3;" )
        await self.conn.execute(stmt, stkname, exchange, conid)

    async def updateConfig(self, stk = None):
        raise NotImplemented
        assert type(stk) == int
        result = await self.getConfig(stk)
        id = 0 ### result??? and other params
        
        stmt = (
            r"INSERT INTO configs ( ) VALUES ( );"
        )
        await self.conn.execute(stmt, id)

    async def getPnL(self, stk = None):
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE name = $1;", stk)
        elif type(stk)==int:
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE conid = $1;", stk)
        elif type(stk)==None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        return values
    
botDB = BotDB()



async def botDBMain():
    await botDB.async_init()
    pnls = await botDB.getPnL()
    print(pnls)

async def asyncBotDB():
    await asyncio.gather( botDBMain() )#, test() )
#
def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(asyncBotDB())
    loop.run_forever()
    loop.close()
#
if __name__ == '__main__':
    run()

#
#values = await self.conn.fetch(
#    'SELECT * FROM mytable WHERE id = $1',
#    10,
#)
#await self.conn.close()
#
#botDB = BotDB()
#async def test():
#    while(True):
#        await asyncio.sleep(0.5)
#        #print(".",end="", flush=True)
#
#
#import aioconsole
#from pprint import pprint as pp
#
#async def botDBMain():
#    await botDB.async_init()
#
#    #stks = await botDB.allStocks()
#    #print(f"stks:{stks}")
#    #conf = await botDB.viewConfig()
#    #print(f"config:{conf}")
#    spnl = await botDB.viewPnL()
#    print(f"stocks pnl:")
#    pp(spnl)
#    
#    print(r"1. Stocks:")
#    print(r"2. Configs:")
#    print(r"3. PnLs:")
#    print(r"4. Exit")
#    user_input = await aioconsole.ainput()
#    while(True):
#        match(user_input):
#            case '1':
#                print("Stocks")
#            case '2':
#                print("Configs")
#            case '3':
#                print("PnLs")
#            case '4':
#                exit()
#        user_input = await aioconsole.ainput()
#    '''
#    result = await botDB.allStocks()
#    r = [ (i+1, x.name, x.conid, x.exchange) for i, x in enumerate(result) ]
#    #pp(r)
#    await botDB.allStocksAndPnL()
#    print("Input Stock Name:")
#    user_input = await aioconsole.ainput()'''
#
#
#async def asyncBotDB():
#    await asyncio.gather( botDBMain(), test() )
#
#def run():
#    loop = asyncio.new_event_loop()
#    asyncio.set_event_loop(loop)
#    loop.create_task(asyncBotDB())
#    loop.run_forever()
#    loop.close()
#
#if __name__ == '__main__':
#    run()
#