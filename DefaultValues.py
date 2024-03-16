import json
jf = open("config.json","r")
acctId = "U"+json.load(jf)["id"]

MAX_CHAIN_LENGTH = 200
IBKRClientPortalURI = "https://localhost:5000"
#IBKRClientPortalURI = "https://httpbin.org"
DEFAULT_TIMEOUT = 10
DEFAULT_ACCOUNTID = acctId
DEFAULT_CURRENCY = "USD"
DEFAULT_PRICE_DECIMALS = 3
DEFAULT_QUANTITY_DECIMALS = 3
DEFAULT_ORDER_CONFIRM = True