import pandas as pd
from datetime import datetime, date
#https://docs.etherscan.io/api-endpoints/accounts - API ETHER

your_ether_address = '0xd0Dd94f50A15d07b0FFf2E20641Dced97E4e9399'.lower() 
transactions_url = 'https://api.etherscan.io/api?module=account&action=txlist&address=' + your_ether_address + \
"&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey=AEQ3BNUI9Y75SRCW5QETTN98JIKC4T6R91"

df = pd.read_json(transactions_url)
print(df.columns)
transactions = df['result']
print(transactions)
print(transactions[0])
print("--------------------------------------------------------------")

print("--------расход---------")
for tran in transactions:
     #кошелек можент дублироваться, берем один раз
    #for inp in tran['inputs']:
    #    print("from_addr: "+inp['prev_out']['addr']+" BTC_value: " + str(inp['prev_out']['value'])+ " time: "+ str(date.fromtimestamp(tran['time'])))
    if str(tran['from'])==your_ether_address:
        print("from_addr: "+tran['from']+ " to_addr: "+ tran['to'] +"  attoEther_value: " + str(int(tran['value'])) + " date: "+ date.fromtimestamp(int(tran['timeStamp'])).strftime("%d.%m.%Y"))

print("--------приход---------")
for tran in transactions:
    if str(tran['to'])==your_ether_address:
        print("from_addr: "+tran['from']+ " to_addr: "+ tran['to'] +"  attoEther_value: " + str(int(tran['value'])) + " date: "+ date.fromtimestamp(int(tran['timeStamp'])).strftime("%d.%m.%Y"))
