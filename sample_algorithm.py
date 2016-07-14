import greennav
from queue import PQueue
import math

gn = greennav.GreenNav()

def runAlgorithm(startNode, endNode):
  # SAMPLE ALGORITHM
  
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
    
    # if node['id'] in gn.wayCache:
    #   print("YES ITS IN WAYCACHE")
    #   print(gn.wayCache[node['id']])
    #   for key,val in gn.wayCache[node['id']].iteritems():
    #     nextNodes.append(gn.nodeCache[key])
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


gn.defineRunAlgorithm(runAlgorithm)
gn.startServer()