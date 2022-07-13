#https://iss.moex.com/iss/reference/
#http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/vtbr.json?iss.json=extended&from=2022-01-01
#https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?iss.meta=off&iss.only=marketdata&marketdata.columns=SECID,LAST,WAPRICE,OPEN,LOW,HIGH


import requests,datetime,pandas,os,aiogram, tabulate ,asyncio , re

SECurl='https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?iss.meta=off&iss.only=marketdata&marketdata.columns=SECID,LAST,WAPRICE,OPEN,LOW,HIGH'
HISTurl='http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{sec}.json?from={date}'

LIQTIMER= 60*60*24*7 #1 week
LIQPERIOD=150 #days

CMD='top([0-9]*)([wd])([0-9]*)s([1-9])'

BOT = aiogram.Bot(token=os.getenv('MOEXLeaders'))
DP = aiogram.Dispatcher(BOT)


SEC_DICT=dict()
HIST_DICT=dict()


def fill_DICT(dic,data):
    for k,v in enumerate(data):
        dic[v]=k

def liquidList():
    global SECurl
    global HISTurl 
    global SEC_DICT
    global HIST_DICT   

    turnovers = []
      
    dtFrom=datetime.date.today()-datetime.timedelta(days=LIQPERIOD)

    secs=requests.get(SECurl).json()  

    if not SEC_DICT:
        fill_DICT(SEC_DICT,secs['marketdata']['columns'])    

    for s in secs['marketdata']['data']:      
        url=HISTurl.format(sec=s[SEC_DICT['SECID']],date=dtFrom.strftime('%Y-%m-%d'))
        sec_hist=requests.get(url).json()
        if not HIST_DICT:
            fill_DICT(HIST_DICT,sec_hist['history']['columns']) 
        turnovers.append({'sec':s[SEC_DICT['SECID']],'to':pandas.DataFrame(sec_hist['history']['data']).sum()[HIST_DICT['VALUE']]})
        
    turnovers.sort(key=lambda x:x['to'],reverse=True)    
    with open('seclist.txt','w') as file:
        for v in turnovers:
            file.write(v['sec']+'\n')



@DP.message_handler(commands=['help','start'])
async def help(message:  aiogram.types.Message):  
    with open('README.md','r', encoding="utf-8") as help:       
        await BOT.send_message(message.from_user.id,help.read() )     


@DP.message_handler(commands=['top'])
async def default(message:  aiogram.types.Message):
    await main(message, re.match( CMD,'top40w1s2'))

@DP.message_handler(aiogram.dispatcher.filters.RegexpCommandsFilter(regexp_commands=[CMD]))   
async def main(message: aiogram.types.Message, regexp_command):
    global SEC_DICT
    global HIST_DICT
    global SECurl
    global HISTurl

    topcount=int(regexp_command.group(1))
    period=regexp_command.group(2)
    periodcount=int(regexp_command.group(3))
    volatileMultiplier=int(regexp_command.group(4))

    if not os.path.isfile('seclist.txt'):
        print('making liquidList')
        liquidList()
            
    with open('seclist.txt','r') as file:
        secs=file.read().splitlines()    

    if period=='w':
        dtFrom=datetime.date.today()-datetime.timedelta(weeks=periodcount)
    else: 
        dtFrom=datetime.date.today()-datetime.timedelta(days=periodcount)     
    print(dtFrom)

    top_secs=[]
    for sec in secs[0:topcount]:
        url=HISTurl.format(sec=sec,date=dtFrom.strftime('%Y-%m-%d'))
        sec_hist=requests.get(url).json()
        if not HIST_DICT:
            fill_DICT(HIST_DICT,sec_hist['history']['columns'])  
        prices=[]                
        for price in sec_hist['history']['data']:
            prices.extend([
                price[HIST_DICT['OPEN']],
                price[HIST_DICT['LOW']],
                price[HIST_DICT['HIGH']],
                price[HIST_DICT['WAPRICE']],
                price[HIST_DICT['CLOSE']]
                ])
            #"OPEN", "LOW", "HIGH", "LEGALCLOSEPRICE", "WAPRICE", "CLOSE"

        top_secs.append({'sec':sec,
            'oldPrice':sec_hist['history']['data'][0][HIST_DICT['CLOSE']],
            'prevClose':sec_hist['history']['data'][len(sec_hist['history']['data'])-1][HIST_DICT['CLOSE']],
            'stdev':pandas.DataFrame(prices).std()[0]})

    secs_last=requests.get(SECurl).json()  
    if not SEC_DICT:
        fill_DICT(SEC_DICT,secs_last['marketdata']['columns'])  
    secs_last= secs_last['marketdata']['data']  


    for sec in top_secs: 
        for last in secs_last:
            if last[SEC_DICT['SECID']] ==sec['sec']:
                if last[SEC_DICT['LAST']]==None:
                    sec['lastPrice']=sec['prevClose']
                else:    
                    sec['lastPrice']=last[SEC_DICT['LAST']]
                sec['delta']=round(100*(sec['lastPrice']-sec['oldPrice'])/sec['oldPrice'],1)

    top_secs.sort(key=lambda x:x['delta'],reverse=False)

   
    table=[]
    for s in top_secs:  
        table.append([
            s['sec'].ljust(5),
            f"{s['delta']:+.1f}",             
            #round(s['oldPrice'],0 if s['oldPrice']>999  else 1 if s['oldPrice']>10  else 4),
            round(s['lastPrice'],0 if s['oldPrice']>999  else 1 if s['oldPrice']>10  else 4),
            round(100*s['stdev']/ s['oldPrice'],1),
            round(s['lastPrice']-volatileMultiplier*s['stdev'],0 if s['oldPrice']>999  else 1 if s['oldPrice']>10  else 4)
            ])       
    table.append(['-------','-------', '-------', '-------','-------'])    
    headers=['SEC','Δ%','LAST', 'std%', 'Sloss']        
    table.append(headers)
    await BOT.send_message(message.from_user.id, tabulate.tabulate(table, headers=headers))     


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(LIQTIMER, repeat, coro, loop)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(LIQTIMER, repeat, liquidList, loop)
    aiogram.executor.start_polling(DP,loop=loop)