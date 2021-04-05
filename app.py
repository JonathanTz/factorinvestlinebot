# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import FinanceCralwer as Fin
import os
app = Flask(__name__)

# 填入你的 message api 資訊
line_bot_api = LineBotApi(os.getenv('LINE_BOT_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_BOT_CHANNEL_ACCESS_SECRET'))

# 設定你接收訊息的網址，如 https://YOURAPP.herokuapp.com/callback
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("Handle: reply_token: " + event.reply_token + ", message: " + event.message.text)
    user_id = event.source.user_id
    content=''
    if(event.message.text[0] == '+' or event.message.text[0] == '-'):
        stkID=event.message.text[1:].split()
        stkArray_TW=Fin.covtStr2ID(stkID,'CMoney') ##更新台股觀察
        
        if len(stkArray_TW)!=0:
            content=Fin.addHldData(user_id,stkArray_TW,event.message.text[0])
        else:
            stkArray_GB=Fin.covtStr2ID(stkID,'alphavantage')##更新海外股觀察            
            if len(stkArray_GB)!=0:     
                content=content+ Fin.addHldData(user_id,stkArray_GB,event.message.text[0],'GB')

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return
    elif(event.message.text=='jojo'):
        carousel_template_message = TemplateSendMessage(
        alt_text='請選擇服務',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                            thumbnail_image_url='https://i.imgur.com/xQF5dZT.jpg',
                            title='選擇服務',
                            text='請選擇',
                            actions=[
                                #MessageAction(
                                #     label='股票觀察清單資訊',
                                #     text='jojoStock'
                                # ),
                                PostbackAction(
                                    label = '台股觀察清單資訊',  # 在按鈕模板上顯示的名稱
                                    #display_text = '查詢中,請稍後...',  # 點擊會顯示的文字
                                    data = 'jojoStock'  # 這個...我真的就不知道了～
                                ),
                                PostbackAction(
                                    label = '海外股觀察清單資訊',  # 在按鈕模板上顯示的名稱
                                    #display_text = '查詢中,請稍後...',  # 點擊會顯示的文字
                                    data = 'jojoStock_GB'  # 這個...我真的就不知道了～
                                ),
                                PostbackAction(
                                    label = '外匯觀察清單',  # 在按鈕模板上顯示的名稱
                                    #display_text = '查詢中,請稍後...',  # 點擊會顯示的文字
                                    data = 'jojoStock_GB'  # 這個...我真的就不知道了～
                                )]
                        )
                    ]
                )
            )

        line_bot_api.reply_message(event.reply_token, carousel_template_message)
        return
    elif(event.message.text=='jojoStock'):
        stkID=Fin.getHldData(user_id)
        if(len(stkID)==0):
            content="[台股]觀察清單無資料 請輸入 +股票代號 更新清單"
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
            return 
        else:    
            stkArray=Fin.covtStr2ID(stkID,'CMoney')
    elif(event.message.text=='jojoStock_GB'):
        stkID=Fin.getHldData(user_id,tpArea="GB")
        if(len(stkID)==0):
            content="[海外股]觀察清單無資料 請輸入 +股票代號 更新清單"
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
            return 
        else:    
            stkArray=Fin.covtStr2ID(stkID,'alphavantage')
    else:
        stkID=event.message.text.split()
        stkArray=Fin.covtStr2ID(stkID,'CMoney')
        stkArray_TW=Fin.covtStr2ID(stkID,'CMoney') ##更新台股觀察
        print(stkID)
        sys.stdout.flush()
        if len(stkArray_TW)!=0:
            stkArray=stkArray_TW
        elif (stkID[0]!='F' & stkID[0]!='S') :
            stkArray=Fin.covtStr2ID(stkID,'alphavantage')##更新海外股觀察  
       
        
    
    if (stkID[0]=='F'):
        stkContent = Fin.getFxReturn(stkID[1:])
        content = "{}".format(stkContent)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    elif (stkID[0]=='S'):
        stkContent = Fin.getStkReturn(stkID[1:])
        content = "{}".format(stkContent)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    else:
        stkContent = Fin.getStkReturn(stkArray)
        content = "{}".format(stkContent)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        
@handler.add(PostbackEvent)
def handle_postback(event):
    postBack=event.postback.data
    if (postBack=="jojoStock"):
        user_id = event.source.user_id
        stkID=Fin.getHldData(user_id)
        if(len(stkID)==0):
            content="觀察清單無資料 請輸入 +股票代號 更新清單"
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
            return 
        else:    
            stkArray=Fin.covtStr2ID(stkID,'CMoney')
            stkContent = Fin.getStkReturn(stkArray)
            content = "{}".format(stkContent)
            print(content)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
            return
    elif(postBack=='jojoStock_GB'):
        user_id = event.source.user_id
        stkID=Fin.getHldData(user_id,'GB')
        if(len(stkID)==0):
            content="觀察清單無資料 請輸入 +股票代號 更新清單"
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
            return 
        else:    
            stkArray=Fin.covtStr2ID(stkID,'alphavantage')
            stkContent = Fin.getStkReturn(stkArray)
            content = "{}".format(stkContent)
            print(content)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=content))
            return

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])