from bottle import get, post, request, HTTPResponse, run, static_file
import json
import math
import requests
import os
from queue import PQueue

root = os.getcwd()

# Static Routes
@get('/lib/<filename:re:.*\.js>')
def javascripts(filename):
  return static_file(filename, root= (root + '/lib'))

@get('/lib/<filename:re:.*\.css>')
def stylesheets(filename):
  return static_file(filename, root= str(root + '/lib'))

@get('/lib/images/<filename:re:.*\.png>')
def stylesheets(filename):
  return static_file(filename, root= str(root + '/lib/images'))

@get('/api/cache')
def req_handle():
  try:
    # GET request then write the data to text file 
    url = "http://overpass-api.de/api/interpreter?data=[out:json];(node(53.8138072,10.6801245,53.853807200000006,10.720124499999999);way(bn););out meta;"
    data = requests.get(url)
    data = json.loads(data.content)

    f1 = open('cachedata.json', 'w')
    f1.write(json.dumps(data))
    f1.close()
    body = json.dumps({"Success": "cached data successfully"})
    return HTTPResponse(status=200, body=body)

  except:
    body = json.dumps({"Error": "could not cache data properly"})
    return HTTPResponse(status=400, body=body)

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
      f2 = open('cachedata.json', 'r')
      data = json.loads(f2.read())
      elements = data['elements']

      # setup node and way caches
      nodeCache = {}
      wayCache = {}

      for i in range(0, len(elements)):
          if elements[i]['type'] == 'way':
              
              for ii in range(0, len(elements[i]['nodes']) - 1):
                  lastNode = elements[i]['nodes'][ii]
                  currentNode = elements[i]['nodes'][ii+1]

                  if not (lastNode in wayCache):
                      wayCache[lastNode] = {}

                  wayCache[lastNode][currentNode] = True
                  
          elif elements[i]['type'] == 'node':
              
              nodeCache[elements[i]['id']] = {
                  'lat': elements[i]['lat'],
                  'lon': elements[i]['lon'],
                  'id': elements[i]['id']
              }

      # hardcode the start and end nodes for now
      start = nodeCache[1949570796]
      goal = nodeCache[301451595]
      # startNode = json.loads(request.forms.get('startNode'))
      # endNode = json.loads(request.forms.get('endNode'))


      # define helper methods
      def nodeWithShortestDistance(frontier):
          distance = float('inf')
          shortestId = None
          
          for key, val in frontier.iteritems():
              if val['distance'] < distance:
                  distance = val['distance']
                  shortestId = key
          
          return nodeCache[shortestId]

      def getNextNodes(node):
          nextNodes = []
          
          if node['id'] in wayCache:
              for key,val in wayCache[node['id']].iteritems():
                  nextNodes.append(nodeCache[key])
          
          return nextNodes              

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
        return costBetweenTwoNodes(start, node)

      def costTillGoal(node):
        return costBetweenTwoNodes(node, goal)


      # final json for visualization
      circles = []
      path = {}

      # start the computation!
      maxSteps = 1000

      node = start
      node['prevCost'] = 0

      pq = PQueue()
      alreadyExplored = {}
      # cost function = costTillNow + costTillGoal
      fstart = 0 + costTillGoal(node)
      pq.put(node, fstart)

      while not pq.isEmpty() and maxSteps > 0:
          curNode = pq.get()

          if curNode['id'] in alreadyExplored:
            maxSteps = maxSteps - 1
            continue

          alreadyExplored[curNode['id']] = True

          # if goal found
          if curNode == goal:
              latLng = []
              while 'previous' in curNode:
                  latLng.append({'nodeLat': curNode['lat'], 'nodeLong': curNode['lon']})
                  curNode = curNode['previous']
                  
              path['pTime'] = 10000 - maxSteps*10
              path['pathLine'] = latLng
              break
          
          # for each neighbor node
          nextNodes = getNextNodes(curNode)
          for i in range(0, len(nextNodes)):
              nextNode = nextNodes[i]

              if nextNode['id'] in alreadyExplored:
                continue

              nextNode['previous'] = curNode
              nextNode['prevCost'] = curNode['prevCost'] + costBetweenTwoNodes(curNode, nextNode) 

              # cost function = costTillNow + costTillGoal
              fn = nextNode['prevCost'] + costTillGoal(nextNode)
              pq.put(nextNode, fn)

              circles.append({'circleLat': curNode['lat'], 'circleLong': curNode['lon'], 'circleTime': 10000 - maxSteps*10})

          maxSteps = maxSteps - 1

      body = json.dumps({
        "circles": circles,
        "path": path
      })

      return HTTPResponse(status=200, body=body)

    except:
      body = json.dumps({"Error": "an error occurred."})
      return HTTPResponse(status=400, body=body)

run(host='localhost', port=8080)
