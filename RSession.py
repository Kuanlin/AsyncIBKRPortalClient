import aiohttp
import asyncio, json
from typing import Union

MAX_CHAIN_LENGTH = 200
IBKRClientPortalURI = "https://localhost:5000"
#IBKRClientPortalURI = "https://httpbin.org"
DEFAULT_TIMEOUT = 10
DEFAULT_ACCOUNTID = "DEFAULT_ACCOUNTID"
DEFAULT_CURRENCY = "USD"
DEFAULT_PRICE_DECIMALS = 3
DEFAULT_QUANTITY_DECIMALS = 3
DEFAULT_ORDER_CONFIRM = True

class OrderSide:
    BUY = "buy"
    SELL = "sell"
_OrderSide = [ OrderSide.__getattribute__(OrderSide, x) for x in OrderSide.__dict__ if not x.startswith("__") and not x.endswith("__") ]

class OrderType:
    MARKET = "MKT"
    LIMIT = "LMT"
_OrderType = [ OrderType.__getattribute__(OrderType, x) for x in OrderType.__dict__ if not x.startswith("__") and not x.endswith("__") ]

class OrderTIF:
    DAY = "DAY"
_OrderTIF = [ OrderTIF.__getattribute__(OrderTIF, x) for x in OrderTIF.__dict__ if not x.startswith("__") and not x.endswith("__") ]

class OrderStatus:
    NONE = "None"
    INACTIVE = "Inactive"
    PENDINGSUBMIT ="PendingSubmit"
    PRESUBMITTED = "PreSubmitted"
    SUBMITTED = "Submitted"
    FILLED = "Filled"
    PENDINGCANCEL = "PendingCancel"
    CANCELLED = "Cancelled"
    WARNSTATE = "WarnState"
    SORTBYTIME = "SortByTime"
_OrderStatus = [ OrderStatus.__getattribute__(OrderStatus, x) for x in OrderStatus.__dict__ if not x.startswith("__") and not x.endswith("__") ]


class Order:
    def __init__(
        self,
        conid:int,
        side:str,
        orderType:str,
        price:float,
        quantity:float,
        tif:str,
        priceDecimals:int = DEFAULT_PRICE_DECIMALS,
        quantityDecimals:int = DEFAULT_QUANTITY_DECIMALS,
        acctId:str = DEFAULT_ACCOUNTID,
    ):
        assert type(conid) == int 
        assert side in _OrderSide
        assert orderType in _OrderType
        assert type(price)==int or type(price)==float
        assert type(quantity)==int or type(quantity)==float
        assert tif in _OrderTIF
        assert type(priceDecimals)==int
        assert type(quantityDecimals)==int
        assert type(acctId)==str

        self.conid = conid
        self.side = side
        self.orderType = orderType
        self.price = price
        self.quantity = quantity
        self.tif = tif
        self.priceDecimals = priceDecimals
        self.quantityDecimals = quantityDecimals
        self.acctId = acctId

        self.price_str = format( round(
            self.price, self.priceDecimals), 
            f".{self.priceDecimals}f" )

        self.quantity_str = format( round(
            self.quantity, self.quantityDecimals), 
            f".{self.quantityDecimals}f" )


    def toDict( self ) -> dict:
        return {
            "acctId" : self.acctId,
            "conid" : self.conid,
            "side" : self.side,
            "price" : self.price_str,
            "quantity" : self.quantity_str,
            "orderType" : self.orderType,
            "tif" : self.tif
        }
        

restOrderConfirmed = DEFAULT_ORDER_CONFIRM

class RESTRequests:

    async def liveOrders(
        filters: list = [], 
        force: bool = True, 
        accountId: str = DEFAULT_ACCOUNTID, 
        timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str
        assert len(accountId) > 0
        assert type(force) == bool
        fil = ",".join(filters)
        fil = "filters="+fil+"&"
        fc = "force=true&" if force else "force=false&"
        return {
            "method": r"GET",
            "url": f"/v1/api/iserver/account/orders?{fil}{fc}accountId={accountId}",
            "params": "",
            "timeout": timeout
        }


    async def orderStatus(orderId: Union[int, str], timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(orderId) != int and type(orderId) != str
        assert type(orderId) == int or type(orderId) == str
        oid = str( orderId if type(orderId)==int else int(orderId) )
        return {
            "method": r"GET",
            "url": f"/v1/api/iserver/account/order/status/{oid}",
            "params": "",
            "timeout": timeout
        }


    async def placeOrdersRaw(
        ordersDict: dict, 
        accountId: str = DEFAULT_ACCOUNTID, 
        timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert restOrderConfirmed == True


    async def placeOrders(
        orders: list, 
        accountId: str = DEFAULT_ACCOUNTID, 
        timeout: int = DEFAULT_TIMEOUT) -> dict:

        assert restOrderConfirmed == True
        assert type(orders) == list
        assert len(orders) > 0
        assert all( [ type(od) == Order for od in orders ] )
        assert type(accountId) == str
        assert len(accountId) > 0

        acctId = accountId
        orderListStr = json.dumps( {"orders": [ od.toDict() for od in orders ]} )

        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/account/{accountId}/orders",
            "params": orderListStr,
            "respchain": RESTRequests.respondChain_OrdersApprov,
            "respchain_kwarg": { "accountId": accountId },
            "timeout": timeout
        }


    async def modifyOrderRaw(timeout: int = DEFAULT_TIMEOUT):
        pass

    async def modifyOrder(timeout: int = DEFAULT_TIMEOUT):
        pass

    async def modifyOrders():
        pass

    async def respondChain_OrdersApprov(responds, **kwargs):
        return {
            "method": r"POST",
            "url": r"/v1/api/iserver/reply/{{ replyId }}",
            "params": "APPROV HERE",
            "timeout": kwargs.get("timeout") if kwargs.get("timeout") else DEFAULT_TIMEOUT
        }

    async def cancelOrderRaw(timeout: int = DEFAULT_TIMEOUT):
        pass

    async def cancelOrder(
        orderId: Union[int, str],
        accountId: str = DEFAULT_ACCOUNTID,
        timeout: int = DEFAULT_TIMEOUT):
        assert type(accountId) == str and len(accountId) > 0
        assert type(orderId) == int or type(orderId) == str
        oid = str( orderId if type(orderId)==int else int(orderId) )
        return {
            "method": r"DELETE",
            "url": f"/v1/api/iserver/account/{accountId}/order/{oid}"
        }


    #how we get future's conid
    async def securityFuturesBySymbols(symbols:list = [], timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(symbols) == list
        assert len(symbols) > 0
        assert all( [ type(s) == str and len(s) > 0 for s in symbols ] )
        sbs = ",".join(symbols)
        return {
            "method": r"GET",
            "url": f"/v1/api/trsrv/futures?symbols={sbs}",
            "params": "",
            "timeout": timeout
        }


    #how we get stock's conid
    async def securityStocksBySymbols(symbols:list = [], timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(symbols) == list
        assert len(symbols) > 0
        assert all( [ type(s) == str and len(s) > 0 for s in symbols ] )
        sbs = ",".join(symbols)
        return {
            "method": r"GET",
            "url": f"/v1/api/trsrv/stocks?symbols={sbs}",
            "params": "",
            "timeout": timeout
        }


    async def profitAndLoss(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": r"/v1/api/iserver/account/pnl/partitioned",
            "params": "",
            "timeout": timeout
        }


    async def portfolioAccounts(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": r"/v1/api/portfolio/accounts",
            "params": "",
            "timeout": timeout
        }


    async def portfolioSubaccounts(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": r"/v1/api/portfolio/subaccounts",
            "params": "",
            "timeout": timeout
        }


    async def portfolioSubaccountsL(page: int = 0, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(page) == int and len(page) >= 0
        return {
            "method": r"GET",
            "url": r"/v1/api/portfolio/subaccounts2",
            "params": f"page={page}",
            "timeout": timeout
        }

    
    async def specificAccountPortfolioInfo(accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        if accountId == None:
            raise ValueError
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/meta",
            "params": "",
            "timeout": timeout
        }

    
    async def portfolioAllocation(accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/allocation",
            "params": "",
            "timeout": timeout
        }


    async def portfolioAllocations(accountIds: list = [DEFAULT_ACCOUNTID], timeout: int = DEFAULT_TIMEOUT) -> dict:
        if type(accountIds) == list and len(accountIds) == 0:
            raise ValueError
        else:
            for s in accountIds:
                if type(s) != str or len(s) == 0:
                    raise ValueError

        json_content = json.dumps( { "acctIds" : accountIds } )
        return {
            "method": r"POST",
            "url": f"/v1/api/portfolio/allocation",
            "params": f"json={json_content}",
            "timeout": timeout
        }


    async def positions(pageId: int = 0, accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        assert type(pageId) == int and pageId >= 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/positions/{pageId}",
            "params": "",
            "timeout": timeout
        }
    

    async def positionsAll(pageId: int = 0, accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        assert type(pageId) == int and pageId >= 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/positions/{pageId}",
            "params": "",
            "timeout": timeout,
            "respchain": RESTRequests.respondChain_PositionNextPage,
            "respchain_kwarg": { "accountId": accountId, "pageId" : pageId+1, "timeout": timeout },
        }


    async def respondChain_PositionNextPage(response, **kwargs):
        content = (await response.content.read()).decode('utf8')
        if content == "" or content=="[]":
            return None
        accountId = kwargs["accountId"]
        pageId = kwargs["pageId"]
        timeout = kwargs["timeout"]
        assert type(accountId) == str and len(accountId) > 0
        assert type(pageId) == int and len(pageId) >= 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/positions/{pageId}",
            "params": "",
            "timeout": timeout,
            "respchain": RESTRequests.respondChain_PositionNextPage,
            "respchain_kwarg": { "accountId": accountId, "pageId" : pageId+1 },
        }


    async def positionsbyConid(conid: str = None, acctId: str = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(acctId) == str and len(acctId) > 0
        assert type(conid) == str and len(conid) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{acctId}/position/{conid}",
            "params": "",
            "timeout": timeout
        }

    
    #Invalidate Backend Portfolio Cache not impl.
    async def invalidateBackendPortfolio():
        raise NotImplementedError


    async def portfolioSummary(accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/summary",
            "params": "",
            "timeout": timeout
        }

    async def portfolioLedger(accountId: str = DEFAULT_ACCOUNTID, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(accountId) == str and len(accountId) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/{accountId}/ledger",
            "params": "",
            "timeout": timeout
        }
    
    async def PositionNContractInfo(conid: str = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(conid) == str and len(conid) > 0
        return {
            "method": r"GET",
            "url": f"/v1/api/portfolio/positions/{conid}",
            "params": "",
            "timeout": timeout
        }
    
    #Account Performance not impl
    async def accountPerformance():
        raise NotImplementedError

    async def transactionHistory(
        accountIds: list = None, 
        conids: list = None, 
        days: int = 1,
        currency: str = DEFAULT_CURRENCY,  
        timeout: int = DEFAULT_TIMEOUT ) -> dict:

        assert type(accountIds) == list and len(accountIds) > 0
        assert all( [ type(a) == str and len(a) > 0 for a in accountIds ] )
        assert type(conids) == list and len(conids) > 0
        assert all( [ type(c) == int for c in conids] )
        assert type(currency) == str
        assert type(days) == int
        assert days > 0

        json_content = json.dumps({ 
            "acctIds" : accountIds, 
            "conids" : conids, 
            "currency" : currency,
            "days" : days} )

        return {
            "method": r"POST",
            "url": f"/v1/api/pa/transactions",
            "params": f"json={json_content}",
            "timeout": timeout
        }

    #Iserver Scanner Parameters
    def iserverScannerParameters():
        raise NotImplementedError

    #Iserver Market Scanner
    def iserverMarketScanner():
        raise NotImplementedError

    #HMDS Scanner Parameters
    def HMDSScannerParameters():
        raise NotImplementedError
    
    #HMDS Market Scanner
    def HMDSMarketScanner():
        raise NotImplementedError

    def authenticationStatus(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"POST",
            "url": f"/v1/api/iserver/auth/status",
            "params": "json=",
            "timeout": timeout
        }

    #Initialize Brokerage Session
    def initializeBrokerageSession():
        raise NotImplementedError


    def logout(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"POST",
            "url": f"/v1/api/logout",
            "params": "json=",
            "timeout": timeout
        }

    def pingServer(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"POST",
            "url": f"/v1/api/tickle",
            "params": "json=",
            "timeout": timeout
        }

    def validSSO(timeout: int = DEFAULT_TIMEOUT) -> dict:
        return {
            "method": r"GET",
            "url": f"/v1/api/sso/validate",
            "params": "",
            "timeout": timeout
        }


    #??????? rows type?
    def createWatchlist(id: str = None, name: str = None, conids: list = [], timeout: int = DEFAULT_TIMEOUT) -> dict:
        assert type(id) == str and len(id) > 0
        assert type(name) == str and len(name) > 0
        assert type(conids) == list

        rows = []
        for c in conids:
            rows.append({"C":c})
        return {
            "id": id,
            "name": name,
            "rows": rows
        }
    
    def getAllWatchlists(timeout: int = DEFAULT_TIMEOUT) -> dict:
        pass

    def getWatchlistInfo(timeout: int = DEFAULT_TIMEOUT) -> dict:
        pass

    def deleteWatchlist(id: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
        pass


from collections import deque
import traceback, sys
restin = asyncio.Queue()
resterrout = asyncio.Queue()

class RESTRequestSession:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.reconnect_sleep_time = 10
    
    async def restClientSession(self) -> None:
        headers = {"User-Agent":"JAGMAGMAG/0.0.1 GGCG"}
        while(True):
            try:
                await self.onClientInit()
                while(True):
                    await asyncio.sleep(0)
                    async with aiohttp.ClientSession(IBKRClientPortalURI, connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                        request_coroutines = deque(await self.aquireRequestList()) #deque to avoid race condition
                        resps = []
                        for index, request_coro in enumerate(request_coroutines):
                            request_name = request_coro.__name__
                            request = await request_coro
                            
                            #logger.debug(f"REST_REQUEST:{request}")
                            #print(IBKRClientPortalURI+"/"+request["method"].lower())
                            session_request = asyncio.ensure_future(
                                session.request(
                                    method = request["method"],
                                    url = request["url"],
                                    headers = headers | {} if not request.get("headers") else request.get("headers"),
                                    params = request["params"],
                                    allow_redirects = False,
                                    timeout = request["timeout"] ) )
                            try:
                                resp = await session_request
                                resps.append(
                                    { "req" : request_name, "rsp": resp}
                                )
                                await self.onResponse(
                                    { "req" : request_name, "rsp": resp})
                                #chain
                                m = request.get("respchain")
                                chain_length = 0
                                while( m != None ):
                                    if chain_length > MAX_CHAIN_LENGTH:
                                        raise Exception("MAX_CHAIN_ERROR")
                                    chain_length = chain_length + 1
                                    request_name = m.__name__
                                    request = await m(resp, **request.get("respchain_kwarg"))
                                    if request != None:
                                        session_request = asyncio.ensure_future(
                                            session.request(
                                                method = request["method"],
                                                url = request["url"],
                                                headers = headers | {} if not request.get("headers") else request.get("headers"),
                                                params = request["params"],
                                                allow_redirects = False,
                                                timeout = request["timeout"] ) )
                                                
                                        resp = await session_request
                                        resps.append(
                                            { "req" : request_name, "rsp": resp})
                                        await self.onResponse(
                                            { "req" : request_name, "rsp": resp})
                                        m = request.get("respchain")
                                    else:
                                        m = None
                                #print("before on Response")

                            except aiohttp.ServerTimeoutError as e:
                                print("aiohttp.ServerTimeoutError")
                                await resterrout.put({
                                    "timeout" : request,
                                    "not_requested" : list(request_coroutines)[index+1:] })
                                raise Exception("REST request timeout -> Recovering")
                            except aiohttp.client_exceptions.ClientConnectorError as e:
                                print("aiohttp.client_exceptions.ClientConnectorError")
                                for request_coro in list(request_coroutines)[index+1:]:
                                    await request_coro
                                raise Exception("REST Client ConnectorError -> Recovering")
                            await asyncio.sleep(0)

                        await self.onResponseList(resps)
                        await self.onCallback()   
                        await asyncio.sleep(0)

            except Exception as e:
                print(f"Exception in REST :: {e}")
                print(f"Trace:{traceback.format_exc()}")
                #logger.info(f"Exception in REST :: {e}")
                #logger.info(f"Trace:{traceback.format_exc()}")
                #await resterrout.put(e)
                await asyncio.sleep(self.reconnect_sleep_time)
                #logger.info(f"REST Reconnecting..")
                next


    async def onClientInit(self):
        pass

    async def aquireRequestList(self):
        pass

    async def onResponse(self, resp):
        pass

    async def onResponseList(self, resps):
        pass

    async def onCallback(self):
        pass
    