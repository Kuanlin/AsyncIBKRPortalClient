import asyncio, asyncpg, aioconsole

DEFAULT_USER = 'DEFAULT_USER'
DEFAULT_PWD = 'DEFAULT_PWD'
DEFAULT_DB = 'DEFAULT_DB'

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
            user=DEFAULT_USER, password=DEFAULT_PWD,
            database='', host='127.0.0.1')
        stmt = (
            r"SELECT datname FROM pg_catalog.pg_database WHERE datname = $1;"
        )
        result = await self.conn.fetch(stmt, DEFAULT_DB)
        if (len(result)==0):
            await self.conn.execute(f"CREATE DATABASE {DEFAULT_DB}")
        self.conn = await asyncpg.connect(
            user=DEFAULT_USER, password=DEFAULT_PWD,
            database=DEFAULT_DB, host='127.0.0.1')
        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status') THEN "
                    r"CREATE TYPE status AS ENUM ('stop', 'active', 'liquidating', 'deprecated');"
                r"END IF;"
            r"END $$;" )
        #print(stmt)
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE TABLE IF NOT EXISTS stocks ("
                r"id SERIAL, conid INT, "
                r"name Varchar(255),"
                r"exchange Varchar(255), timestamps timestamp,"
                r"PRIMARY KEY(id)"
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)

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
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE TABLE IF NOT EXISTS pnls ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"realizedpnl numeric(20,5), timestamps timestamp, "
                r"PRIMARY KEY(id), FOREIGN KEY(stkid) REFERENCES stocks( id ) "
            r");" )
        #print(stmt)
        await self.conn.execute(stmt)

        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sidetype') THEN "
                    r"CREATE TYPE sidetype AS ENUM ('BUY', 'SELL');"
                r"END IF;"
            r"END $$;" )
        await self.conn.execute(stmt)

        stmt = (
            r"BEGIN;"
            r"DO $$"
                r"BEGIN "
                r"IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'ordertype') THEN "
                    r"CREATE TYPE ordertype AS ENUM ('LMT', 'MKT');"
                r"END IF;"
            r"END $$;" ) 
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE TABLE IF NOT EXISTS OrderHistory ( "
                r"id SERIAL, stkid INT NOT NULL, "
                r"cfgid INT NOT NULL, "
                r"side sidetype, "
                r"price numeric(20,5), "
                r"quantity numeric(20,5), "
                r"type ordertype, "
                r"timestamps timestamp, "
                r"PRIMARY KEY(id), "
                r"FOREIGN KEY(stkid) REFERENCES stocks(id), "
                r"FOREIGN KEY(cfgid) REFERENCES configs(id) "
            r");" )
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE OR REPLACE VIEW orderhistoryview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.name, s.conid, h.cfgid, h.side, h.price, h.quantity, h.type, h.timestamps "
            r"FROM stocks s "
            r"JOIN orderhistory h ON s.id = h.stkid "
            r"ORDER BY s.id, s.conid, h.timestamps DESC;" )
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE OR REPLACE VIEW lateststockpnlview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.name, s.conid, p.realizedpnl, p.timestamps "
            r"FROM stocks s "
            r"JOIN pnls P ON s.id = p.stkid "
            r"ORDER BY s.id, s.conid, p.timestamps DESC;" )
        #print(stmt)
        await self.conn.execute(stmt)

        stmt = (
            r"CREATE OR REPLACE VIEW latestconfigview AS "
            r"SELECT DISTINCT ON (s.id, s.conid) "
                r"s.id, s.conid, s.name, c.initvalue, c.leverage, c.statuscode, "
                r"c.numofsinglespread, c.spreadsteppriceratio, c.spreadsteppriceminimal, "
                r"c.timestamps "
            r"FROM stocks s "
            r"JOIN configs c ON s.id = c.stkid "
            r"ORDER BY s.id, s.conid, c.timestamps DESC;" )
        #print(stmt)
        await self.conn.execute(stmt)
        await self.conn.execute("COMMIT;")



    async def getStock(self, stk = True, usedict = True) -> list: 
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
        if usedict:
            values = [dict(x.items()) for x in values]
        return values


    async def getConfig(self, stk = None, usedict = True) -> list:
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE name = $1;", stk )
        elif type(stk)==int:
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE conid = $1;", stk )
        elif stk == None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(
                r"SELECT * FROM latestconfigview WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
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

    async def getPnL(self, stk = None, usedict = True):
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE name = $1;", stk)
        elif type(stk)==int:
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE conid = $1;", stk)
        elif stk==None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(r"SELECT * FROM lateststockpnlview WHERE True;")
        else:
            raise AssertionError
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
        return values

    async def getOrderHistory(self, stk = None, todayonly=False, usedict = True):
        fetch = None
        if type(stk)==str:
            fetch = self.conn.fetch(r"SELECT * FROM orderhistory WHERE name = $1;", stk)
        elif type(stk)==int:
            fetch = self.conn.fetch(r"SELECT * FROM orderhistory WHERE conid = $1;", stk)
        elif stk==None or (type(stk)==bool and stk==True):
            fetch = self.conn.fetch(r"SELECT * FROM orderhistory WHERE True;")
        else:
            raise AssertionError 
        values = await fetch
        if usedict:
            values = [dict(x.items()) for x in values]
        return values
    
botDB = BotDB()


from pprint import pprint as pp
async def botDBMain():
    try:
        await botDB.async_init()
        '''
        pnls = await botDB.getPnL()
        #pnls_dict = [dict(x.items()) for x in pnls]
        configs = await botDB.getConfig()
        #configs_dict = [dict(x.items()) for x in configs]
        stks = await botDB.getStock()
        #stks_dict = [dict(x.items()) for x in stks]
        print("pnls:")
        pp(pnls)
        print("configs:")
        pp(configs)
        print("stks:")
        pp(stks)'''
        while(user_input != "4"):
            print("1 Show PnLs\n2 Show Configs\n3 Show Stocks")
            user_input = await aioconsole.ainput()
            match(user_input):
                case "1":
                    pp(await botDB.getPnL())
                case "2":
                    pp(await botDB.getConfig())
                case "3":
                    pp(await botDB.getStock())
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)

    user_input = await aioconsole.ainput()\
                
async def st01():
    while(user_input != "4"):
        print("1 Show PnLs\n2 Show Configs\n3 Show Stocks")
        user_input = await aioconsole.ainput()
        match(user_input):
            case "1":
                pp(await botDB.getPnL())
            case "2":
                pp(await botDB.getConfig())
            case "3":
                pp(await botDB.getStock())
            case "4":
                return 





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