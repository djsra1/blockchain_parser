from pickle import TRUE
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import time

# https://www.blockchain.com/ru/api/blockchain_api API BTC
# датафреймы для накопления информации агрегированной детальной
aggregate_columns=['number', 'addr', 'balance','received_BTC','sent_BTC','received_RUB','sent_RUB']
detail_columns=['type', 'date', 'from_addr','to_addr','BTC','USD','RUB']
df_aggregate_excel=pd.DataFrame(columns=aggregate_columns)
df_detail_excel=pd.DataFrame(columns=detail_columns)
    
#btc_address = '1HmRvpayvaxMn84Gte2Evn6VrHcQxx5NKU'#'1H3yFtTD2f4doKeSQkYyiuh16bY7rVUBZ4'
#transactions_url = 'https://blockchain.info/rawaddr/' + your_btc_address

#файлы со списком адресов, курсами 
BTC_addr_list=pd.read_csv("./btc_addr_list.csv",sep=';',header = 0,  dtype = {'number': int,'btc_addr': str})
BTC_USD=pd.read_csv("./Courses/btc_usd.csv",sep=';',header = 0,  dtype = {'date': str,'value': float})
USD_RUB=pd.read_csv("./Courses/usd_rub.csv",sep=';',header = 0,  dtype = {'date': str,'value': float})
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
    #если нет курса на дату - идем вниз по дням, пока не встретим. ограничение 20
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
    #локальные данные для тестирования
    #df = pd.read_json("./blockchain-parser/"+your_btc_address+".json")
    
    
    all_received_BTC=df['total_received'][0]
    all_sent_BTC=df['total_sent'][0]
    balance=df['final_balance'][0]
    
    transactions = df['txs']

    print(str(num)+" --------операции по адресу:  "+your_btc_address)

    all_received_RUB=0
    all_sent_RUB=0
    
    for tran in transactions:
        #Проверка типа транзакции 1-to-n, n-to-1, m-to-n
        tran_type=True #отслеживаемая
        where_addr=''#input or output
        if len(tran['inputs'])>1 and len(tran['out'])>1:
            tran_type=False #неотслеживаемая
            tran_type_str=str(len(tran['inputs']))+'-to-'+str(len(tran['out'])) # inputs-to-outputs


    #проверяем списания (входы)
        for input in tran['inputs']:
            tran_date=date.fromtimestamp(tran['time']).strftime("%d.%m.%Y")
            #отслеживаемая транзакция один вход много выходов, наш на входе
            if input['prev_out']['addr']==your_btc_address and tran_type and len(tran['out'])>1:
                for out in tran['out']:
                    BTC_value=out['value']/100000000
                    #агрегирую отправленные рубли
                    all_sent_RUB=all_sent_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                    #Добавление в детальный датафрейм
                    df_detail_excel.loc[len(df_detail_excel)] = ['Списание', tran_date, input['prev_out']['addr'], out['addr'], BTC_value, round(BTC_to_USD(tran_date)*BTC_value,3), round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)]
                    
                    print("Списание | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(out['value'])+ " | time: "+ tran_date + " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))        
            #отслеживаемая транзакция много входов один выход, наш на входе
            if input['prev_out']['addr']==your_btc_address and tran_type and len(tran['out'])==1:
                BTC_value=input['prev_out']['value']/100000000
                #агрегирую отправленные рубли
                all_sent_RUB=all_sent_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                #Добавление в детальный датафрейм
                for out in tran['out']:
                    df_detail_excel.loc[len(df_detail_excel)] = ['Списание', tran_date, input['prev_out']['addr'], out['addr'], BTC_value, round(BTC_to_USD(tran_date)*BTC_value,3), round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)]
                    print("Списание | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(input['prev_out']['value'])+ " | time: "+ tran_date + " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))        
            

            #неотслежимаемая транзакция (адрес в пуле входов)
            if input['prev_out']['addr']==your_btc_address and not tran_type:
                BTC_value=input['prev_out']['value']/100000000
                #агрегирую отправленные рубли
                all_sent_RUB=all_sent_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                #Добавление в детальный датафрейм
                df_detail_excel.loc[len(df_detail_excel)] = ['Списание', tran_date, input['prev_out']['addr'], tran_type_str, BTC_value, round(BTC_to_USD(tran_date)*BTC_value,3), round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)]
                    
                print("Списание | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ tran_type_str +" |  Satoshi: " + str(input['prev_out']['value'])+ " | time: "+ tran_date + " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))                 
    
    #проверяем пополнения (выходы)
        for out in tran['out']:
            tran_date=date.fromtimestamp(tran['time']).strftime("%d.%m.%Y")
            #отслеживаемая транзакция много входов один выход, наш на выходе
            if out['addr']==your_btc_address and tran_type and len(tran['inputs'])>1:
                for input in tran['inputs']:
                    BTC_value=input['prev_out']['value']/100000000
                    #агрегирую полученные рубли
                    all_received_RUB=all_received_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                    #Добавление в детальный датафрейм
                    df_detail_excel.loc[len(df_detail_excel)] = ['Пополнение', tran_date, input['prev_out']['addr'], out['addr'], BTC_value, round(BTC_to_USD(tran_date)*BTC_value,3), round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)]
                    print("Пополнение | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(input['prev_out']['value'])+ " | time: "+ tran_date + " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))
            
            #отслеживаемая транзакция один вход много выходов, наш на выходе
            if out['addr']==your_btc_address and tran_type and len(tran['inputs'])==1:
                BTC_value=out['value']/100000000
                    #агрегирую полученные рубли
                all_received_RUB=all_received_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                    #Добавление в детальный датафрейм
                for input in tran['inputs']:    
                    df_detail_excel.loc[len(df_detail_excel)] = ['Пополнение', tran_date, input['prev_out']['addr'], out['addr'], BTC_value, round(BTC_to_USD(tran_date)*BTC_value,3), round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)]
                    print("Пополнение | from_addr: "+input['prev_out']['addr']+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(out['value'])+ " | time: "+ tran_date + " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))
                    
            #неотслеживаемая транзакция (адрес в пуле выходов)
            if out['addr']==your_btc_address and not tran_type:
                BTC_value=out['value']/100000000
                #агрегирую полученные рубли
                all_received_RUB=all_received_RUB+round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)
                #Добавление в детальный датафрейм
                df_detail_excel.loc[len(df_detail_excel)] = ['Пополнение', tran_date, tran_type_str, out['addr'],  BTC_value, round(BTC_to_USD(tran_date)*BTC_value,3), round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)]
                
                print("Пополнение | from_addr: "+tran_type_str+ " | to_addr: "+ out['addr'] +" |  Satoshi: " + str(out['value'])+ " | time: "+ tran_date + " | BTC: " + str(BTC_value)+" | USD: " + str(round(BTC_to_USD(tran_date)*BTC_value,3)) + " | RUB: " + str(round(BTC_to_USD(tran_date)*USD_to_RUB(tran_date)*BTC_value,2)))        
    
    print('Баланс:'+ str(balance/100000000) + " | Получено BTC: "+ str(all_received_BTC/100000000)+ " | Отправлено BTC: "+ str(all_sent_BTC/100000000)+ " | Получено RUB: "+ str(all_received_RUB) + " | Отправлено RUB: "+ str(all_sent_RUB))
    
    #Добавление в датафрейм агрегатов
    df_aggregate_excel.loc[len(df_aggregate_excel)] = [num, your_btc_address ,balance/100000000, all_received_BTC/100000000, all_sent_BTC/100000000, all_received_RUB, all_sent_RUB]
    #Добавление в детальный файл Excel
    df_detail_excel.index=df_detail_excel.index+1
    df_detail_excel.to_excel('./Details/'+your_btc_address+'.xlsx', index=True)
    
    #print(df_addr_excel)
    return 0

for addr_idx in BTC_addr_list.index:
    #print(BTC_addr_list['number'].iloc[addr_idx],BTC_addr_list['btc_addr'].iloc[addr_idx])
    get_BTC_addr_info(BTC_addr_list['number'].iloc[addr_idx],BTC_addr_list['btc_addr'].iloc[addr_idx])
    df_detail_excel=df_detail_excel[0:0]
    #задержка для API
    time.sleep(10)

#print(df_aggregate_excel)
#Добавление в агрегатный(индексный) файл Excel
df_aggregate_excel.to_excel('./index.xlsx', index=False)
