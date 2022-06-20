import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import time

# https://www.blockchain.com/ru/api/blockchain_api API BTC


    
btc_address = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'#'1H3yFtTD2f4doKeSQkYyiuh16bY7rVUBZ4'
#transactions_url = 'https://blockchain.info/rawaddr/' + your_btc_address

#df = pd.read_json(transactions_url)
#print(df.columns)
#transactions = df['txs']

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
BTC_addr_list=pd.read_csv("./blockchain-parser/btc_addr_list.csv",sep=';',header = 0,  dtype = {'number': int,'btc_addr': str})
BTC_USD=pd.read_csv("./blockchain-parser/btc_usd.csv",sep=';',header = 0,  dtype = {'date': str,'value': float})
USD_RUB=pd.read_csv("./blockchain-parser/usd_rub.csv",sep=';',header = 0,  dtype = {'date': str,'value': float})
#BTC_USD=pd.read_excel("./blockchain-parser/btc_usd.xls")
#USD_RUB=pd.read_excel("./blockchain-parser/usd_rub.xls")
#rty='04.02.2020'
#USD_RUB['date']=USD_RUB['date'].
#BTC_USD=BTC_USD.loc[BTC_USD['date'] == '04.02.2020'].iloc[0]['value']
#USD_RUB=USD_RUB.loc[USD_RUB['date'] == '04.02.2020'].iloc[0]['value']
#print(BTC_addr_list)
#print(BTC_USD)
#print(USD_RUB)
# result=BTC_USD.
# print(result)
def BTC_to_USD(date):
    try:
        result=BTC_USD.loc[BTC_USD['date'] == date].iloc[0]['value']
    except:
        result=0
    return result

def USD_to_RUB(tran_date):
    date_time_obj = datetime.strptime(tran_date, '%d.%m.%Y') #привожу к дате
    #print(tran_date)
    #print(str(datetime.isoweekday(date_time_obj.date())))
    #проверка выходных
    #if datetime.isoweekday(date_time_obj)==6:
    #    date_time_obj=date_time_obj-timedelta(days=1)
    #elif datetime.isoweekday(date_time_obj)==7:
    #    date_time_obj=date_time_obj-timedelta(days=2)
    #возврат к строке
    #tran_date=date_time_obj.strftime("%d.%m.%Y")
    #print(tran_date)
    i=0
    while i<20: #гоняю максимум 20 раз понижаю дату
        try:
            result=USD_RUB.loc[USD_RUB['date'] == tran_date].iloc[0]['value']
            break
        except:
            date_time_obj=date_time_obj-timedelta(days=1) #минус день
            tran_date=date_time_obj.strftime("%d.%m.%Y")  #возврат к строке
            i=i+1
            result=0
    #print(result)
    return result

def get_BTC_addr_info(num,your_btc_address):
    
    transactions_url = 'https://blockchain.info/rawaddr/' + your_btc_address
    df = pd.read_json(transactions_url)
    #print(df.columns)
    all_received_BTC=df['total_received'][0]
    all_sent_BTC=df['total_sent'][0]
    balance=df['final_balance'][0]
    
    transactions = df['txs']

    print(str(num)+" --------операции по адресу:  "+your_btc_address)

    all_received_RUB=0
    all_sent_RUB=0
    
    for tran in transactions:
        #Проверка типа транзакции
        tran_type=True
        if len(tran['inputs'])>1 and len(tran['out'])>1:
            tran_type=False
            tran_type_str=str(len(tran['inputs']))+'-to-'+str(len(tran['out']))
    #проверяем списания (входы)
        for input in tran['inputs']:
            tran_date=date.fromtimestamp(tran['time']).strftime("%d.%m.%Y")
            #отслеживаемая транзакция один вход много выходов
            if input['prev_out']['addr']==your_btc_address and tran_type:
                for out in tran['out']:
                    BTC_value=out['value']/100000000
                    #агрегирую отправленные рубли
                    all_sent_RUB=all_sent_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                    print("Списание | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(out['value'])+ " | time: "+ tran_date +\
                         " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))        
            #неотслежимаемая транзакция (адрес в пуле входов)
            if input['prev_out']['addr']==your_btc_address and not tran_type:
                BTC_value=input['prev_out']['value']/100000000
                #агрегирую отправленные рубли
                all_sent_RUB=all_sent_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                print("Списание | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ tran_type_str +" |  Satoshi: " + str(input['prev_out']['value'])+ " | time: "+ tran_date +\
                     " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))                 
    #проверяем пополнения (выходы)
        for out in tran['out']:
            tran_date=date.fromtimestamp(tran['time']).strftime("%d.%m.%Y")
            #отслеживаемая транзакция много входов один выход
            if out['addr']==your_btc_address and tran_type:
                for input in tran['inputs']:
                    BTC_value=input['prev_out']['value']/100000000
                    #агрегирую полученные рубли
                    all_received_RUB=all_received_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                    print("Пополнение | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(input['prev_out']['value'])+ " | time: "+ tran_date +\
                         " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))
            #неотслеживаемая транзакция (адрес в пуле выходов)
            if out['addr']==your_btc_address and not tran_type:
                BTC_value=out['value']/100000000
                #агрегирую полученные рубли
                all_received_RUB=all_received_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                print("Пополнение | from_addr: "+tran_type_str+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(out['value'])+ " | time: "+ tran_date +\
                     " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))        
    
    print('Баланс:'+ str(balance/100000000) + " | Получено BTC: "+ str(all_received_BTC/100000000)+ " | Отправлено BTC: "+ str(all_sent_BTC/100000000)+ " | Получено RUB: "+ str(all_received_RUB) + " | Отправлено RUB: "+ str(all_sent_RUB))
    return 0

for addr_idx in BTC_addr_list.index:
    #print(BTC_addr_list['number'].iloc[addr_idx],BTC_addr_list['btc_addr'].iloc[addr_idx])
    get_BTC_addr_info(BTC_addr_list['number'].iloc[addr_idx],BTC_addr_list['btc_addr'].iloc[addr_idx])
    
    time.sleep(5)