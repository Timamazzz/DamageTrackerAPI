import requests

API_URL = 'https://sms.ru/sms/send'
API_ID = '39083F8A-7E1F-6866-F828-CC07F15C8A2F'


class SMSRU:
    @staticmethod
    def send_sms(to, msg, json=1):
        params = {
            'api_id': API_ID,
            'to': to,
            'msg': msg,
            'json': json
        }
        response = requests.get(API_URL, params=params)
        return response.json()
