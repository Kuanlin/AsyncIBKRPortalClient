import json, os
jf = open("config.json","r")
_configjs = json.load(jf)

saveddir = os.path.dirname(__file__)+'/saved'
saved = os.listdir(saveddir)
lastsaved = None
if len(saved)>0:
    saved.sort(reverse=True)
    lastsaved = saved[0]




#group_proportion = _configjs["group_proportion"]
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