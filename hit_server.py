from __future__ import print_function
from bottle import (Bottle, route, run, request, response, server_names,
                    ServerAdapter, abort)
import datahandler

# SSL subclass of bottle cribbed from:
# http://dgtool.blogspot.com.au/2011/12/ssl-encryption-in-python-bottle.html

# Declaration of new class that inherits from ServerAdapter
# It's almost equal to the supported cherrypy class CherryPyServer
AUTH_TOKEN = "lemmein"

class MySSLCherryPy(ServerAdapter):
    def run(self, handler):
        import cherrypy
        from cherrypy import wsgiserver
        cherrypy.config.update('cherrypy.config')
        # print(cherrypy.config.items())
        server = cherrypy.wsgiserver.CherryPyWSGIServer(
                                                        (self.host, self.port),
                                                        handler,
                                                        numthreads=1,
                                                        max=1)
        # print(server.requests._threads)
        # If cert variable is has a valid path, SSL will be used
        # You can set it to None to disable SSL
        cert = 'data/server.pem'  # certificate path
        server.ssl_certificate = cert
        server.ssl_private_key = cert
        try:
            server.start()
        finally:
            server.stop()

# Add our new MySSLCherryPy class to the supported servers
# under the key 'mysslcherrypy'
server_names['sslbottle'] = MySSLCherryPy

# data = datahandler.DataHandler(just_the_hits=True)
# HITS = data.get_all_hits()
data = None
app = Bottle()


def hit_for_id(hit_id):
    for hit in HITS:
        if hit['id'] == hit_id:
            return hit

def authenticate(auth):
    if auth == AUTH_TOKEN:
        return True
    abort(401, '-_-')
# actual bottle stuff

@app.route('/hits')
def get_hits():
    auth = request.get_header('Authorization')
    if not authenticate(auth):
        return
    # update data
    global data
    if not data:
        data = datahandler.DataHandler(just_the_hits=True)
    hits = data.get_all_hits()
    return {'hits': hits}


@app.route('/ok')
def retweet():
    auth = request.get_header('Authorization')
    if not authenticate(auth):
        return
    hit_id = int(request.query.id)
    hit = hit_for_id(hit_id)
    # return str(hit_id) + hit
    return "retweeted '%s' and '%s'" % (hit['tweet_one']['text'], hit['tweet_two']['text'])


@app.route('/del')
def delete():
    hit_id = int(request.query.id)
    data.remove_hit(hit_id)
    return "success"


run(app, host='localhost', port=8080, debug=True, server='sslbottle')

# if __name__ == "__main__":
#     print hit_for_id(1368809545607)
