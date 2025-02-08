import json
import requests
from .essentials.settings import Settings

class TypeGPT():
    def __init__(self):
        pass
    def models(self):
        toreturn = []
        r = requests.get("https://chat.typegpt.net/api/openai/v1/models")
        r = r.json()
        for z in r['data']:
            z['api'] = "sk-123"
            i = "typegpt*"
            z['id'] = i + z['id']
            toreturn.append(z)
        return toreturn
    def generate(self, chat, model, settings= None):
        if(settings == None):
            settings = Settings()
        url = "https://chat.typegpt.net/api/openai/v1/chat/completions"

        headers = {
            "accept": "application/json, text/event-stream",
            "accept-language": "en-US,en;q=0.9,en-GB;q=0.8,en-IN;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Microsoft Edge\";v=\"132\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

        body = {
            "messages": chat,
            "stream": True,
            "model": model,
            "temperature": 0.5,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_p": 1,
            "max_tokens": 4000
        }

        response = requests.post(url, headers=headers, json=body, stream=True)
        if(response.status_code !=200):
            print(response.text)
            raise Exception("Request Ended with non 200 status code",response.status_code)
        return self.parse(response)
    def parse(self,response):
        final_response = ""
        for line in response.iter_lines():
            line = line.decode('utf-8')
            final_response = final_response+'\n'+line
            if(line.startswith('data: ')):
                line = line.strip().split("data: ")[1]
                try:
                    line = json.loads(line)
                except:
                    pass
                try:
                    yield line['choices'][0]['delta']['content']
                except:
                    pass
        self.final_response = final_response



if __name__ == "__main__":
    typegpt = TypeGPT()
    for z in typegpt.generate([{'role':'user','content':"hello"}],"chatgpt-4o-latest"):
        print(z,end="")