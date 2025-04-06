# send-message-to-telegram.py
# by www.ShellHacks.com

import requests

def send_to_telegram(message):

    apiToken = '5082654068:AAF7quCLZ4xuTq2FBdo3POssdJsM_FRHwTs'
    chatID = '515382482'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

send_to_telegram("Hello from Python!")
