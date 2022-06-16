import pandas as pd
from datetime import datetime, date
#https://docs.etherscan.io/api-endpoints/accounts - API ETHER

api_token='AEQ3BNUI9Y75SRCW5QETTN98JIKC4T6R91' #токен получен после регистрации на etherscan.io
your_ether_address = '0xd0Dd94f50A15d07b0FFf2E20641Dced97E4e9399'.lower() 
# здесь получаем транзакции поcредством эфирного адреса
transactions_url = 'https://api.etherscan.io/api?module=account&action=txlist&address=' + your_ether_address + \
                    '&startblock=0&endblock=99999999&page=1&offset=10&sort=asc&apikey='+api_token
# API for tokens
#https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=0xdac17f958d2ee523a2206206994597c13d831ec7&address=0xd0dd94f50a15d07b0fff2e20641dced97e4e9399&page=1&offset=100&startblock=0&endblock=27025780&sort=asc&apikey=AEQ3BNUI9Y75SRCW5QETTN98JIKC4T6R91

df = pd.read_json(transactions_url)
transactions = df['result']
#print(transactions)
#print(transactions[0])
print("--------------------------------------------------------------")

def get_tokens(smart_addr, tran_hash):
    #оказалось ненужным, т.к. если операция не с эфиром, то в качестве контрагента указан не эфирный адрес (кошелька), а номер смартконтракта
            # #здесь получаем адрес смартконтракта посредством хэша транзакции
            # smart_url='https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash='+ tran_hash+ '&apikey='+api_token
            # smart_df=pd.read_json(smart_url)
            # print(smart_df['result']['to'])
            # smart_addr=smart_df['result']['to']
    #здесь получаем данные по токенам посредством эфирного адреса и адреса смартконтракта, если операция с токенами
    token_url = 'https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=' + smart_addr + \
                '&address=' + your_ether_address + '&page=1&offset=100&startblock=0&endblock=27025780&sort=asc&apikey='+api_token
 #   https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=0xdac17f958d2ee523a2206206994597c13d831ec7&address=0xd0dd94f50a15d07b0fff2e20641dced97e4e9399&page=1&offset=100&startblock=0&endblock=27025780&sort=asc&apikey=AEQ3BNUI9Y75SRCW5QETTN98JIKC4T6R91
 #   https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=&address=0xd0dd94f50a15d07b0fff2e20641dced97e4e9399&page=1&offset=100&startblock=0&endblock=27025780&sort=asc&apikey=AEQ3BNUI9Y75SRCW5QETTN98JIKC4T6R91'

    tdf = pd.read_json(token_url)
    print("---------------------------------------------------------")
    token_tran = tdf['result']
    for tran in token_tran:
        #отфильтровываю только то, что в текущей транзакции посредством hash
        if tran['hash']==tran_hash:
            print("from_addr: "+tran['from']+ " to_addr: "+ tran['to'] +" Token: "+ tran['tokenSymbol'] + " value: " + str(int(tran['value'])) + " date: "+ date.fromtimestamp(int(tran['timeStamp'])).strftime("%d.%m.%Y"))

    


#print("--------расход---------")
for tran in transactions:
     #кошелек можент дублироваться, берем один раз
    #for inp in tran['inputs']:
    #    print("from_addr: "+inp['prev_out']['addr']+" BTC_value: " + str(inp['prev_out']['value'])+ " time: "+ str(date.fromtimestamp(tran['time'])))
    #if str(tran['from'])==your_ether_address:
        #проверка на смартконтакт
    if int(tran['value'])==0: 
        get_tokens(tran['to'],tran['hash'])
    else:
        print("from_addr: "+tran['from']+ " to_addr: "+ tran['to'] +" Token: ETH  value: " + str(int(tran['value'])) + " date: "+ date.fromtimestamp(int(tran['timeStamp'])).strftime("%d.%m.%Y"))


# print("--------приход---------")
# for tran in transactions:
#     if str(tran['to'])==your_ether_address:
#         print("from_addr: "+tran['from']+ " to_addr: "+ tran['to'] +" Token: ETH  value: "  + str(int(tran['value'])) + " date: "+ date.fromtimestamp(int(tran['timeStamp'])).strftime("%d.%m.%Y"))
#         #проверка на смартконтакт
#         if int(tran['value'])==0:
#             get_tokens(tran['to'],tran['hash'])

         
