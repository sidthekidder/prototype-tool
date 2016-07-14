# Prototyping Tool for Green Navigation

## Running the Prototype Tool Demo

Install the following Python modules:
- requests
- sqlite3

```pep install requests sqlite3```

Run sample_algorithm.py and navigate to http://localhost:8080/home. Click on 'Test Algorithm' to see the current algorithm running. The start and end nodes are currently close together. Their geo-coordinates are hardcoded at the beginning of greennav.py. They will be taken dynamically from the front-end in the next iteration.


## Writing a Routing Algorithm

Read 'sample_algorithm.py' to see what a sample program using the greennav module would look like. Here are the steps to prototype a routing algorithm using the greennav python module-

- import the greennav module
```import greennav ```

- instantiate a new GreenNav object
```gn = greennav.GreenNav()```

- define the routing algorithm. The function signature is 
``` 
def runAlgorithm(startNode, endNode):
  # YOUR ALGORITHM HERE
```

- this routing function MUST call ```gn.drawCircle()``` and ```gn.drawLine()``` with the following schema -
```
gn.drawCircle({
  'circleLat': 123.123,    # decimal geocoordinate
  'circleLong': 123.123,   # decimal geocoordinate
  'circleTime': 123        # time in milliseconds after which this circle is visualized
})

gn.drawLine({
  'pTime': 123,            # time in milliseconds after which this line is visualized
  'pathLine': [
    {'nodeLat': 123.123, 'nodeLong': 123.123},
    {'nodeLat': 456.456, 'nodeLong': 456.456}
    # etc
  ]
})

```
- Call drawCircle() when you want to show a circle/node on the map as having been considered/passed through by the algorithm. The milliseconds associated with each node are used as a measure of time taken to reach that node. Call drawLine() to show the final path found (from start to target node) passing through multiple circles (the pathLine array) after pTime. Generally the algorithm should end after calling gn.drawLine().

- finally pass the routing function to gn.defineRunAlgorithm
```gn.defineRunAlgorithm(runAlgorithm)```

- start the server using 
```gn.startServer()```

- navigate to http://localhost:8080/home and click 'Test Algorithm' to run the algorithm and see the output visualization.