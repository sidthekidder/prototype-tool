import sqlite3
from bottle import get, post, request, HTTPResponse, run, static_file
import json
import requests
import webbrowser
import os
root = os.getcwd()

# HARDCODED DATA
N1 = {'id': 3428474040, 'lat': 7.4185151, 'lon': 43.7353633}
N2 = {'id': 3428473993, 'lat': 7.4180124, 'lon': 43.7341179}

## define GreenNav class
class GreenNav():
  def __init__(self):

    # connect to sqlite3 database
    conn = sqlite3.connect('data/data.db')
    c = conn.cursor()

    # setup node and way caches
    self.nodeCache = {}
    self.wayCache = {}

    nodes = c.execute('SELECT * FROM nodes;')    
    for node in nodes:
      self.nodeCache[node[0]] = {
          'lat': node[4],
          'lon': node[3],
          'id': node[0]
      }

    ways = c.execute('SELECT * FROM ways;')
    for way in ways:
      self.wayCache[way[0]] = {}

    waynodes = c.execute('SELECT * FROM way_nodes;')
    for waynode in waynodes:
      self.wayCache[waynode[0]][waynode[2]] = True 

    # setup visualization for circles/line
    self.circles = []
    self.path = {}

  def defineRunAlgorithm(self, runFunction):
    self.runFunction = runFunction

  def drawCircle(self, node):
    self.circles.append(node)

  def drawLine(self, path):
    self.path = path

  def clearData(self):
    self.circles = []
    self.path = {}

  def startServer(self):
    
    ## Define Web Server
    @get('/home')
    def req_handle():
      try:
        return static_file('home.html', root=root)
      except:
        body = json.dumps({"Error": "could not load home page"})
        return HTTPResponse(status=400, body=body)

    @post('/api/route')
    def req_handle():
      try:
        self.clearData()
        self.runFunction(N1, N2)
        print("No of circles: ", len(self.circles))
        print(self.path)

        body = json.dumps({
          "circles": self.circles,
          "path": self.path
        })
        return HTTPResponse(status=200, body=body)

      except:
        body = json.dumps({"Error": "could not cache data properly"})
        return HTTPResponse(status=400, body=body)

    # Static Routes
    @get('/static/<filename:re:.*\.js>')
    def javascripts(filename):
      return static_file(filename, root= (root + '/static'))

    @get('/static/<filename:re:.*\.css>')
    def stylesheets(filename):
      return static_file(filename, root= str(root + '/static'))

    @get('/static/images/<filename:re:.*\.png>')
    def stylesheets(filename):
      return static_file(filename, root= str(root + '/static/images'))

    # open up server automatically
    run(host='localhost', port=8080)
    webbrowser.open('http://localhost:8080/home')
