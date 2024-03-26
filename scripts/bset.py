import argparse
import asyncio

async def bset_run():
    try:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        sc = subparsers.add_parser("set-config", aliases = ['sc'])
        sc.set_defaults(act="set-config")
        scgroup = sc.add_mutually_exclusive_group()
        scgroup.add_argument('-id', '--conid', 
            help = r"provide conid of the stock", type = int)
        scgroup.add_argument('-n', '--name',
            help = r"provide name of the stock", type = str)
        sc.add_argument('-lv', '--leverage', 
            help = r"set the leverage", required = True)
        sc.add_argument('-iv', '--initvalue', 
            help = r"set initial value", required = True)
        sc.add_argument('-sc', '--statuscode', choices=[r'stop', r'active', r'liquiding', r'deprecated'],
            help = r"set status code", required = True)
        sc.add_argument('-ns', '--numofspread', 
            help = r"set the number of single side orders to be spread", required = True)
        sc.add_argument('-sr', '--spreadsteppriceratio', 
            help =r"set the price step ratio for orders <1: the further the smaller >1: the further the larger =0: use minimal value", required = True)
        sc.add_argument('-sm', '--spreadsteppriceminimal',
            help =r"set the minimum price step for orders", required = True)
        
        lc = subparsers.add_parser("list-config", aliases = ['lc'])
        lc.set_defaults(act='list-config')
        lcgroup = lc.add_mutually_exclusive_group()
        lcgroup.add_argument('-id', '--conid', 
            help = r"provide conid of the stock", type = int)
        lcgroup.add_argument('-n', '--name',
            help = r"provide name of the stock", type = str)
        lcgroup.add_argument('-a', '--all', action='store_true',
            help = r"list all configurations")
        lc.add_argument('-sc', '--statuscode', choices=[r'stop', r'active', r'liquiding', r'deprecated'],
            help = r"filter by status code -- default = active", required = True, default = r'active')

        ast = subparsers.add_parser("add-stock", aliases = ['ast'])
        ast.set_defaults(act="add-stock")
        ast.add_argument('-id', '--conid', 
            help = r"provide conid of the stock", type = int)
        ast.add_argument('-n', '--name',
            help = r"provide name of the stock", type = str)
        ast.add_argument('-e', '--exchange',
            help = r"provide stock's exchange" , type = str)

        lstk = subparsers.add_parser("list-stock", aliases = ['lst'])
        lstk.set_defaults(act="list-stock")
        

        lpnl = subparsers.add_parser("list-pnl", aliases = ['lpnl'])
        lpnl.set_defaults(act="list-pnl")


        args = parser.parse_args()
        
        print(args.act)
        print(args.conid) 
        print(args.name)
    except:
        import traceback
        tb = traceback.format_exc()


async def bset():
    try:
        await asyncio.gather( bset_run() )
    except:
        import traceback
        tb = traceback.format_exc()
        #print(tb)
    loop = asyncio.get_event_loop()
    loop.stop()

def run():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(bset())
    loop.run_forever()

if __name__ == '__main__':
    run()
