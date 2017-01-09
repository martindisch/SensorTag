import web
import json

def dictify(timeTempHum):
    package = [
        timeTempHum[0],
        timeTempHum[1],
        timeTempHum[2]
    ]
    return package

urls = (
    '/latest', 'latest',
    '/history', 'history'
)

class latest:
    def GET(self):
        try:
            with open("latest.csv", 'r') as f:
                timeTempHum = f.readlines()[0].strip("\n").split(",")
            package = dictify(timeTempHum)
            return json.dumps(package)
        except:
            return "Could not read latest data"

class history:
    def GET(self):
        try:
            with open("history.csv", 'r') as f:
                lines = [x.strip("\n") for x in f.readlines()]
            package = []
            # limit to approximately 2 MB of transmitted JSON
            lines = lines[-48770:]
            for line in lines:
                timeTempHum = line.split(",")
                package.append(dictify(timeTempHum))
            return json.dumps(package)
        except:
            return "Could not read historic data"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
