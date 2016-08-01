from bottle import get, post, request, HTTPResponse, run, static_file
import json
import requests
import os
root = os.getcwd()

## Define Web Server
@get('/')
def req_handle():
  try:
    return static_file('editor.html', root=root)
  except:
    body = json.dumps({"Error": "could not load home page"})
    return HTTPResponse(status=400, body=body)

@post('/api/runcode')
def req_handle():
  try:
    code = request.params['code']

    return HTTPResponse(status=200, body={})

  except:
    body = json.dumps({"Error": "could not cache data properly"})
    return HTTPResponse(status=400, body={})

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
run(host='localhost', port=9091)
