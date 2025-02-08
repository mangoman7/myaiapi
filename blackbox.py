from essentials.settings import Settings
import requests
import json
class BlackBox():
    def __init__(self):
        pass
    def generate(self,chat,model,settings=Settings()):
        url = "https://api.blackbox.ai/api/chat"

        payload = json.dumps({
        "messages": chat,
        "model": model,
        "max_tokens": "16000",
        "stream":True
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload, stream=True)
        return self.parser(response)
    def parser(self,response):
        for z in response.iter_lines():
            z = z.decode('utf-8')
            yield z