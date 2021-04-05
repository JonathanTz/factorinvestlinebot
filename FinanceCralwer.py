##get Cmoney Stock Price --20200202
import pandas as pd
import requests
from requests import get
from bs4 import BeautifulSoup as bs
from pandas.io.json import json_normalize
import urllib
from datetime import datetime, timedelta 
from pymongo import *
import optparse
import os

def resText(resTxt):
    return resTxt
def getCMStkPrcPer(stkID,dtCnt=250):
    ##get CmKey
    url_key = 'http://www.cmoney.tw/finance/technicalanalysis.aspx?s=2330'
    response_key = get(url_key)
    html_soup_key = bs(response_key.text, 'html.parser')
    cmkey=urllib.parse.quote(html_soup_key.find_all('li', class_ = 'primary-navi-now')[0].find_all("a")[0]['cmkey'])
    
    ##get Stock Price
    url = "http://www.cmoney.tw/finance/ashx/MainPage.ashx?action=GetTechnicalData&stockId={0}&time=d&range={1}&cmkey={2}".format(stkID,dtCnt,cmkey)
    header = {'Referer':'http://www.cmoney.tw/finance/technicalanalysis.aspx?s={}'.format(stkID),
              'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    res = requests.get(url,headers=header).json()
    
    if(len(res)>0):
        pxArray=json_normalize(res)
        pxArray=pxArray[[u'Date',u'OpenPr',u'HighPr',u'LowPr',u'ClosePr',u'DealQty']]
        pxArray[u'stkID']=stkID
        
        pxArray['Date'] = pd.to_datetime(pxArray['Date'])
        pxArray=pxArray.set_index(u'Date')
        return pxArray
def getAlphaStkPrcPer(stkID):
    apiApha='SHVGNPLKQXZV04J0'
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={0}&apikey={1}'.format(stkID,apiApha)
    res = requests.get(url).json()
    pxArray = pd.DataFrame.from_dict(res['Time Series (Daily)']).T
    pxArray.columns = ['OpenPr','HighPr','LowPr','ClosePr','DealQty']
    pxArray.index=pd.to_datetime(pxArray.index)
    pxArray=pxArray.sort_index(ascending=True)
    return pxArray
def getStkReturn(stkArray,cntRetArray=[10,30,90]):
    stkID=stkArray
    outputTxt=''
    for i in range(0,len(stkID)):
        ticker=stkID.iloc[i,:]['stkID']
        tpArea=stkID.iloc[i,:]['tpArea']
        if (tpArea=='TW'):
            stk=getCMStkPrcPer(ticker)
        elif (tpArea=='GB'):
            stk=getAlphaStkPrcPer(ticker)
        prcNow=float(stk.iloc[-1,:]['ClosePr'])
        outputTxt=outputTxt+('股票 {0} {1}, 目前價格為 {2} 元'.format(ticker,stkID.iloc[i,:]['stkName'],prcNow))
        outputTxt=outputTxt+'\n'
        
        ret=(prcNow-float(stk.iloc[-(1),:]['OpenPr']))/float(stk.iloc[-(1),:]['OpenPr'])
        outputTxt=outputTxt+('近一日漲跌幅為{0:.4%}'.format(ret))+'\n'
        outputTxt=outputTxt+'/ '.join(map(str, cntRetArray))+'日漲跌幅'
        for j in cntRetArray:
            ret=(prcNow-float(stk.iloc[-(j),:]['ClosePr']))/float(stk.iloc[-(j),:]['ClosePr'])
            outputTxt=outputTxt+('{0:.4%}'.format(ret))+'/'
        outputTxt=outputTxt[:-1]+'\n=========================\n'

    if (outputTxt==''):
        outputTxt='查無資料!'
    return outputTxt.rstrip()
        

def covtStr2ID(stkStr,dataSrc):
    ##get CmKey
    if (dataSrc=='CMoney'):
        url_key = 'http://www.cmoney.tw/finance/f00025.aspx'
        response_key = get(url_key)
        html_soup_key = bs(response_key.text, 'html.parser')
        cmkey=urllib.parse.quote(html_soup_key.find_all('li', class_ = 'primary-navi-now')[0].find_all("a")[0]['cmkey'])
        
        ##get Stock Price
        url = "http://www.cmoney.tw/finance/ashx/mainpage.ashx?action=GetAllStockData&cmkey={0}".format(cmkey)
        header = {'Referer':'http://www.cmoney.tw/finance/f00025.aspx',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        res = requests.get(url,headers=header).json()
        stkArray=json_normalize(res)
        stkArray.columns=['stkID','stkName']
        stkArray['tpArea']='TW'
        output=pd.DataFrame(columns=['stkID', 'stkName'])
        for stk in stkStr:
            output=pd.concat([output,stkArray[(stkArray["stkID"]==stk) | (stkArray["stkName"]==stk) ]],axis=0)
        return output
    elif (dataSrc=='alphavantage'):
        apiApha='SHVGNPLKQXZV04J0'
        output=pd.DataFrame(columns=['stkID', 'stkName'])
        
        for stk in stkStr:
            url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={0}&apikey={1}'.format(stk,apiApha)
            res = requests.get(url).json()
            stkArray = pd.DataFrame.from_dict(res['bestMatches'])
            stkArray = stkArray[['1. symbol','2. name']]
            stkArray.columns=['stkID','stkName']
            stkArray['tpArea']='GB'
            output=pd.concat([output,stkArray[(stkArray["stkID"]==stk) | (stkArray["stkName"]==stk) ]],axis=0)
        return output
    elif (dataSrc=='cnyes'):
        url = "https://ws.api.cnyes.com/universal/api/v1/quote?type=ALLFX&page=0&limit=30&column=C_FORMAT"
        res = requests.get(url).json()
        fxArray=json_normalize(res["data"]["items"])[['0','200009']]
        fxArray.columns=['fxID','fxName']
        fxArray["fxID"]=fxArray["fxID"]

        output=pd.DataFrame(columns=['fxID', 'fxName'])
        for stk in stkStr:
            output=pd.concat([output,fxArray[fxArray["fxID"].str.contains(stk) | fxArray["fxName"].str.contains(stk) ]],axis=0)
        return output
        
        
def getFxPrc(tpFx,n=365):
    dtNowEd=datetime.now().timestamp()
    dtNowSt=(datetime.now()-timedelta(days = n)).timestamp() 
    url='https://ws.api.cnyes.com/api/v1/charting/history?symbol=FX:{0}:FOREX&resolution=D&from={1}&to={2}'.format(tpFx,str(int(dtNowEd)),str(int(dtNowSt)))
    res = requests.get(url).json()
    listOfDate  = res["t"]
    listOfOpen  = res["o"]
    listOfHigh  = res["h"]
    listOfLow  = res["l"]
    listOfClose  = res["c"]
    zippedList =  list(zip(listOfDate, listOfOpen, listOfHigh,listOfLow,listOfClose))
    pxArray = pd.DataFrame(zippedList, columns = ['Date' , 'Open', 'High','Low','Close']) 
    pxArray.Date=pd.to_datetime(pxArray.Date, unit='s')
    pxArray=pxArray.sort_index(axis = 0) 
    return pxArray
def getFxReturn(FxArray,cntRetArray=[10,30,90]):
    fxID=covtStr2ID(FxArray,'cnyes')
    outputTxt=''
    for i in range(0,len(FxArray)):
        ticker=fxID.iloc[i,:]['fxID']
        ticker=ticker.split(":")[1]
        fx=getFxPrc(ticker)
        prcNow=fx.iloc[-1,:]['Close']
        outputTxt=outputTxt+('匯率 {0} {1}, 目前價格為 {2} 元'.format(ticker,fxID.iloc[i,:]['fxName'],prcNow))
        outputTxt=outputTxt+'\n'
        
        ret=(prcNow-float(fx.iloc[-(1),:]['Open']))/float(fx.iloc[-(1),:]['Open'])
        outputTxt=outputTxt+('近一日漲跌幅為{0:.4%}'.format(ret))+'\n'
        outputTxt=outputTxt+'/ '.join(map(str, cntRetArray))+'日漲跌幅'

        for j in cntRetArray:
            ret=(prcNow-fx.iloc[-(j),:]['Open'])/fx.iloc[-(j),:]['Open']
            outputTxt=outputTxt+('{0:.4%}'.format(ret))+'/'
        outputTxt=outputTxt[:-1]+'\n=========================\n'

    return outputTxt.rstrip()

def addHldData(userID,hldStk,flagUpdate,tpArea='TW'):
    hldStkName=hldStk['stkName'].tolist()
    hldStk=hldStk['stkID'].tolist()
    mongoID=os.getenv('MONGOID')
    mongoPwd=os.getenv('MONGOPWD')
    myClient =  MongoClient("mongodb+srv://{0}:{1}@cluster0.mlmdi.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(mongoID,mongoPwd))
    myDB=myClient["jojodb"]
    myDB.authenticate(mongoID,mongoPwd)
    myCollection=myDB["hldData"]
    qryString={"userID":userID,"tpArea":tpArea}
    cursor = myCollection.find_one(qryString)
    if(cursor!=None):
        hldStk_origin=cursor.get("hldStk")
        if(flagUpdate=='+'):
            hldStk_new=hldStk_origin+hldStk
            content='新增股票'+', '.join(hldStkName)+' 成功 \n'
        elif(flagUpdate=='-'):
            hldStk_new=[x for x in hldStk_origin if x not in hldStk]
            content='刪除股票'+', '.join(hldStkName)+' 成功 \n'
        else:
            content=''
            return
        hldStk_new=list(set(hldStk_new))
        newvalues = { "$set": { "hldStk": hldStk_new }}
        myCollection.update_one(qryString,newvalues)
    else:
        if(flagUpdate=='+'):
            myCollection.insert_one({"userID":userID,"hldStk":hldStk,"tpArea":tpArea})
            content='新增股票 '+', '.join(hldStkName)+' 成功 \n'
        elif(flagUpdate=='-'):
            content="觀察清單無資料 請輸入 +股票代號 更新清單"
    return content.rstrip()
def getHldData(userID,tpArea='TW'):
    mongoID=os.getenv('MONGOID')
    mongoPwd=os.getenv('MONGOPWD')
    myClient =  MongoClient("mongodb+srv://{0}:{1}@cluster0.mlmdi.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(mongoID,mongoPwd))
    myDB=myClient["jojodb"]
    myDB.authenticate(mongoID,mongoPwd)
    myCollection=myDB["hldData"]
    qryString={"userID":userID,"tpArea":tpArea}
    cursor = myCollection.find_one(qryString)
    hldStk_origin=[]
    if(cursor!=None):
        hldStk_origin=cursor.get("hldStk")
    return hldStk_origin
getStkReturn(covtStr2ID(['1234','2330','9999'],'CMoney'))
    ##myCollection.insert_one({"userID":userID,"hldStk":hldStk})
    ##myCollection.delete_one({"userID":"aasd","hldStk":['2330']})
##getStkReturn(['1234','3552'])
##addHldData('Ue0b9ad86d3ee3b289f52393c6183e722',['1234','6274'])
##date = datetime.datetime.fromtimestamp(int(b.ljust(13,'0')) / 1e3)
##str(int (date.timestamp())).ljust(13,'0')
##datetime.datetime.fromtimestamp(int(str(int(datetime.datetime.now().timestamp())).ljust(13,'0'))/1e3)
