# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


class ZhenziSmsClient(object):
    def __init__(self, apiUrl, appId, appSecret):
        self.apiUrl = apiUrl
        self.appId = appId
        self.appSecret = appSecret

    def send(self, number, message, messageId=''):
        data = {
            'appId': self.appId,
            'appSecret': self.appSecret,
            'message': message,
            'number': number,
            'messageId': messageId
        }

        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(self.apiUrl + '/sms/send.do', data=data)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        res = res.decode('utf-8')
        return res

    def balance(self):
        data = {
            'appId': self.appId,
            'appSecret': self.appSecret
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(self.apiUrl + '/account/balance.do', data=data)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return res

    def findSmsByMessageId(self, messageId):
        data = {
            'appId': self.appId,
            'appSecret': self.appSecret,
            'messageId': messageId
        }
        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(self.apiUrl + '/smslog/findSmsByMessageId.do', data=data)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return res


if __name__ == '__main__':
    apiUrl = "https://sms_developer.zhenzikj.com"
    appId = 101830
    appSecret = "84f62ff5-977b-4266-aedd-09538199f44b"
    client = ZhenziSmsClient(apiUrl, appId, appSecret)
    result = client.send('17603094608', '您的验证码为2323')
    print(result)
