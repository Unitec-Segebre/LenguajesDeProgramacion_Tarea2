from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import collections
import re
import http.client

class HTTPServer_RequestHandler(BaseHTTPRequestHandler):

  def do_POST(self):
    try:
      content_length = int(self.headers['Content-Length'])
      request = json.loads(self.rfile.read(content_length))
      
      if (self.path == '/ejercicio1'):
        mapsLink = "https://maps.googleapis.com/maps/api/directions/json?origin=ORIGIN&destination=DESTINATION&key=AIzaSyA7sQSQEOesLMKtCLmqISRpv7YHeWL67-c"
        mapsLink = mapsLink.replace("ORIGIN", request['origen'].replace(" ", "+"))
        mapsLink = mapsLink.replace("DESTINATION", request['destino'].replace(" ", "+"))
        print(mapsLink)

        conn = http.client.HTTPSConnection("maps.googleapis.com")
        conn.request("GET", mapsLink.replace("https://maps.googleapis.com", ""))
        res = conn.getresponse()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        routes = json.loads(res.read())
        routes = routes["routes"][0]["legs"][0]["steps"]
        response = collections.defaultdict(list)
        response["ruta"].append({"lat": routes[0]["start_location"]["lat"], "lon": routes[0]["start_location"]["lng"]})
        for location in routes:
          response["ruta"].append({"lat": location["end_location"]["lat"], "lon": location["end_location"]["lng"]})
        # directions["ruta"] = r.json()
        # self.wfile.write(str.encode(json.dumps(directions)))
        self.wfile.write(str.encode(json.dumps(response)))
        return
      elif (self.path == '/ejercicio2'):
        coordinatesLink = "https://maps.googleapis.com/maps/api/geocode/json?address=ADDRESS&key=AIzaSyDxkk38M1uRTyD6vw7OyBUQ8x_2W2qOsEU"
        coordinatesLink = coordinatesLink.replace("ADDRESS", request['origen'].replace(" ", "+"))
        print(coordinatesLink)

        
      else:
        self.send_response(500)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = collections.defaultdict(list)
        response["error"] = "Opps, ha ocurrido un error :/"
        self.wfile.write(str.encode(json.dumps(response)))
        return


    except Exception as err:
      print(err)
      self.send_response(400)
      self.send_header("Content-type", "application/json")
      self.end_headers()
      response = collections.defaultdict(list)
      response["error"] = "No se especifico origen"
      self.wfile.write(str.encode(json.dumps(response)))
      return


def startServer():
  print('Starting server...')

  server_address = ('localhost', 8080)
  httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
  print('Server up!')
  httpd.serve_forever()

startServer()