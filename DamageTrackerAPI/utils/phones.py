import requests

API_URL = 'https://sms.ru/sms/send'
API_ID = '39083F8A-7E1F-6866-F828-CC07F15C8A2F'


class SMSRU:
    @staticmethod
    def send_sms(to, msg, json=True):
        params = {
            'api_id': API_ID,
            'to': to,
            'msg': msg,
            'json': 1 if json else 0
        }
        response = requests.get(API_URL, params=params)
        return response.json() if json else response.text
