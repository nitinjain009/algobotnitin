# send-message-to-telegram.py
# by www.ShellHacks.com

import requests

def send_to_telegram(message):

    apiToken = '8017759392:AAEwM-W-y83lLXTjlPl8sC_aBmizuIrFXnU'
    chatID = '711856868'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

send_to_telegram("Hello from Python!")
