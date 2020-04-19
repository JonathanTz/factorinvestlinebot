from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage
from linebot.exceptions import LineBotApiError

CHANNEL_ACCESS_TOKEN = "iJvVhBuIm2RmZLHspWhJ3tSTF4scPukXc5ZdBvfz28QwkaGDf9Ff5pE0nnr+zEQk6Ga4uSbpuk2aEifyjvtVhW81iI0QK5FgsOA8NNRDqn3i+CuY81hHyXqebVvJdZWay7UhGG4aUQjfRg4TtLiMoAdB04t89/1O/w1cDnyilFU="
to = "Ue0b9ad86d3ee3b289f52393c6183e722"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

#文字訊息

try:
    line_bot_api.push_message(to, TextSendMessage(text='台科大電腦研習社'))
except LineBotApiError as e:
    # error handle
    raise e
