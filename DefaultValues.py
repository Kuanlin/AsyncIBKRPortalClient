import json
jf = open("config.json","r")
_configjs = json.load(jf)

group_proportion = _configjs["group_proportion"]
stk_param = _configjs["stk_param"]


IBKRClientPortalURI = "https://localhost:5000"
#IBKRClientPortalURI = "https://httpbin.org"
DEFAULT_TIMEOUT = 10
DEFAULT_ACCOUNTID = "U"+_configjs["acctid"]
DEFAULT_CURRENCY = _configjs["currency"]
DEFAULT_PRICE_DECIMALS = 3
DEFAULT_QUANTITY_DECIMALS = 3
DEFAULT_ORDER_CONFIRM = True
MAX_CHAIN_LENGTH = 200