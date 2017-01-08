import web
import cPickle as pickle
import json

def dictify(timeTempHum):
    package = {
        "time": timeTempHum[0],
        "temperature": {
            "value": timeTempHum[1],
            "unit": "degrees Celsius"
        },
        "humidity": {
            "value": timeTempHum[2],
            "unit": "relative humidity"
        }
    }
    return package

urls = (
    '/latest', 'latest',
    '/history', 'history'
)

class latest:
    def GET(self):
        try:
            with open("latest.p", 'r') as f:
                timeTempHum = pickle.load(f)
            package = dictify(timeTempHum)
            return json.dumps(package)
        except:
            return "Could not read latest data"

class history:
    def GET(self):
        try:
            with open("history.p", 'r') as f:
                history = pickle.load(f)
            package = []
            for timeTempHum in history:
                package.append(dictify(timeTempHum))
            return json.dumps(package)
        except:
            return "Could not read historic data"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
