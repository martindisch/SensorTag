import web
import cPickle as pickle
import json

urls = (
    '/latest', 'latest',
    '/history', 'history'
)

class latest:
    def GET(self):
        try:
            with open("latest.p", 'r') as f:
                latest = pickle.load(f)
            return json.dumps(latest)
        except:
            return "Could not read latest data"

class history:
    def GET(self):
        try:
            with open("history.p", 'r') as f:
                history = pickle.load(f)
            return json.dumps(history)
        except:
            return "Could not read historic data"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
