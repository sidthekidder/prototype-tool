import sys
from queue import PQueue
import math
import StringIO
import sqlite3

codeOut = StringIO.StringIO()
codeErr = StringIO.StringIO()
sys.stdout = codeOut
sys.stderr = codeErr

# HARDCODED DATA
startNode = {'id': 3428474040, 'lat': 7.4185151, 'lon': 43.7353633}
endNode = {'id': 3428473993, 'lat': 7.4180124, 'lon': 43.7341179}
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
    

  def drawCircle(self, node):
    self.circles.append(node)

  def drawLine(self, path):
    self.path = path

  def clearData(self):
    self.circles = []
    self.path = {}

# instantiate a greennav object
gn = GreenNav()

runFunction = """
def overallFunc():
    # define helper methods
    def nodeWithShortestDistance(frontier):
        distance = float('inf')
        shortestId = None
        
        for key, val in frontier.iteritems():
            if val['distance'] < distance:
                distance = val['distance']
                shortestId = key
        
        return gn.nodeCache[shortestId]

    def getNextNodes(node):
      for key in gn.wayCache:
        for inode in gn.wayCache[key]:
          if gn.nodeCache[inode]['id'] == node['id']:
            retArr = []

            for key2 in gn.wayCache[key]:
              retArr.append(key2)
            return retArr
      return []

    def costBetweenTwoNodes(node1, node2):
        radlat1 = math.pi * node1['lat']/180
        radlat2 = math.pi * node2['lat']/180
        radlon1 = math.pi * node1['lon']/180
        radlon2 = math.pi * node2['lon']/180

        theta = node1['lon'] - node2['lon']
        radtheta = math.pi * theta/180

        dist = math.sin(radlat1) * math.sin(radlat2) + math.cos(radlat1) * math.cos(radlat2) * math.cos(radtheta)

        dist = math.acos(dist)
        dist = dist * 180/math.pi
        dist = dist * 60 * 1.1515
        dist = dist * 1.609344 * 1000

        return dist

    def costFromStart(node):
      return costBetweenTwoNodes(startNode, node)

    def costTillGoal(node):
      return costBetweenTwoNodes(node, endNode)

    # start the computation!
    maxSteps = 1000

    node = startNode
    node['prevCost'] = 0

    pq = PQueue()
    alreadyExplored = {}
    # cost function = costTillNow + costTillGoal
    fstart = 0 + costTillGoal(node)
    pq.put(node, fstart)

    print("Starting computation.")

    while not pq.isEmpty() and maxSteps > 0:
      curNode = pq.get()

      if curNode['id'] in alreadyExplored:
        maxSteps = maxSteps - 1
        continue
      alreadyExplored[curNode['id']] = True

      # if goal found
      if curNode['id'] == endNode['id']:
        print("Found a path.")
        
        latLng = []
        while 'previous' in curNode:
            latLng.append({'nodeLat': curNode['lat'], 'nodeLong': curNode['lon']})
            curNode = curNode['previous']

        gn.drawLine({'pTime': 10000 - maxSteps*10, 'pathLine': latLng})
        break
      
      # for each neighbor node
      nextNodes = getNextNodes(curNode)
      for i in range(0, len(nextNodes)):
        nextNode = gn.nodeCache[nextNodes[i]]

        if nextNode['id'] in alreadyExplored:
          continue

        nextNode['previous'] = curNode
        nextNode['prevCost'] = curNode['prevCost'] + costBetweenTwoNodes(curNode, nextNode) 

        # cost function = costTillNow + costTillGoal
        fn = nextNode['prevCost'] + costTillGoal(nextNode)
        pq.put(nextNode, fn)
        gn.drawCircle({'circleLat': curNode['lat'], 'circleLong': curNode['lon'], 'circleTime': 10000 - maxSteps*10})

      maxSteps = maxSteps - 1
"""

exec runFunction

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

overallFunc()

se = codeErr.getvalue()
print "Error: \n%s\n" % se

so = codeOut.getvalue()
print "Output: \n%s\n" % so

codeOut.close()
codeErr.close()