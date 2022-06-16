import pandas as pd
from datetime import datetime, date

# https://www.blockchain.com/ru/api/blockchain_api API BTC

your_btc_address = '1H3yFtTD2f4doKeSQkYyiuh16bY7rVUBZ4'
transactions_url = 'https://blockchain.info/rawaddr/' + your_btc_address

df = pd.read_json(transactions_url)
#print(df.columns)
transactions = df['txs']
# print(transactions)
# print(transactions[0])
# print("--------------------------------------------------------------")
# print(transactions[0]['inputs'])
# print("--------------------------------------------------------------")
# print(transactions[0]['inputs'][0])
# print("--------------------------------------------------------------")
# print(transactions[0]['inputs'][0]['prev_out'])
# print("--------------------------------------------------------------")
# print(transactions[0]['time'])
# print(transactions[0]['inputs'][0]['prev_out']['value'])
# print(transactions[0]['inputs'][0]['prev_out']['addr'])
# print(transactions[0]['out'][0]['value'])
# print(transactions[0]['out'][0]['addr'])

BTC_USD=pd.read_excel("./blockchain-parser/btc_usd.xls")
USD_RUB=pd.read_excel("./blockchain-parser/usd_rub.xls")
#BTC_USD=BTC_USD.loc[BTC_USD['date'] == '31.03.2021'].iloc[0]['value']
#print(BTC_USD)
# result=BTC_USD.
# print(result)
def BTC_to_USD(date):
    try:
        result=BTC_USD.loc[BTC_USD['date'] == date].iloc[0]['value']
    except:
        result=0
    return result

def USD_to_RUB(date):
    #USD_RUB1=USD_RUB.loc[USD_RUB['date'] == date] 
    #result=USD_RUB1.iloc[0]['value']
    try:
        result=USD_RUB.loc[USD_RUB['date'] == date].iloc[0]['value']
    except:
        result=0
    return result

print("--------операции по адресу:  "+your_btc_address)
for tran in transactions:
     #кошелек можент дублироваться, берем один раз
    #for inp in tran['inputs']:
    #    print("from_addr: "+inp['prev_out']['addr']+" BTC_value: " + str(inp['prev_out']['value'])+ " time: "+ str(date.fromtimestamp(tran['time'])))
    for out in tran['out']:
        tran_date=date.fromtimestamp(tran['time']).strftime("%d.%m.%Y")
        BTC_value=out['value']/1000000000
        #перевод с исследуемого адреса
        if tran['inputs'][0]['prev_out']['addr']==your_btc_address:
            print("Списание from_addr: "+tran['inputs'][0]['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  nanoBTC_value: " + str(out['value'])+ " | time: "+ tran_date +\
                 " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))        #перевод на исследуемый адрес
        if out['addr']==your_btc_address:
            print("Списание from_addr: "+tran['inputs'][0]['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  nanoBTC_value: " + str(out['value'])+ " | time: "+ tran_date +\
                 " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))


