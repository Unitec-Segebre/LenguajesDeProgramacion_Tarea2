from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import collections
import re
import http.client
import base64

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

        try:
          conn = http.client.HTTPSConnection("maps.googleapis.com")
          conn.request("GET", mapsLink.replace("https://maps.googleapis.com", ""))
          routes = json.loads(conn.getresponse().read())
        except Exception as err:
          print(err)
          self.send_response(500)
          self.send_header("Content-type", "application/json")
          self.end_headers()
          response = collections.defaultdict(list)
          response["error"] = "Opps, ha ocurrido un error :/"
          self.wfile.write(str.encode(json.dumps(response)))
          conn.close()
          return

        routes = routes["routes"][0]["legs"][0]["steps"]
        response = collections.defaultdict(list)
        response["ruta"].append({"lat": routes[0]["start_location"]["lat"], "lon": routes[0]["start_location"]["lng"]})
        for location in routes:
          response["ruta"].append({"lat": location["end_location"]["lat"], "lon": location["end_location"]["lng"]})
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(str.encode(json.dumps(response)))
        conn.close()
        return
      elif (self.path == '/ejercicio2'):
        coordinatesLink = "https://maps.googleapis.com/maps/api/geocode/json?address=ADDRESS&key=AIzaSyDxkk38M1uRTyD6vw7OyBUQ8x_2W2qOsEU"
        coordinatesLink = coordinatesLink.replace("ADDRESS", request['origen'].replace(" ", "+"))
        print(coordinatesLink)

        try:
          conn = http.client.HTTPSConnection("maps.googleapis.com")
          conn.request("GET", coordinatesLink.replace("https://maps.googleapis.com", ""))
          coordinates = json.loads(conn.getresponse().read())
        except Exception as err:
          print(err)
          self.send_response(500)
          self.send_header("Content-type", "application/json")
          self.end_headers()
          response = collections.defaultdict(list)
          response["error"] = "Opps, ha ocurrido un error :/"
          self.wfile.write(str.encode(json.dumps(response)))
          conn.close()
          return
          
        coordinates = coordinates["results"][0]["geometry"]["location"]

        nearMeLink = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=LAT,LNG&radius=3000&types=food&name=cruise&key=AIzaSyCx14BVgeJ89yixorOA7gaab-uscUWlNFU"
        Lat = str(coordinates['lat'])
        Lng = str(coordinates['lng'])
        nearMeLink = nearMeLink.replace("LAT", Lat)
        nearMeLink = nearMeLink.replace("LNG", Lng)
        print(nearMeLink)

        try:
          conn.request("GET", nearMeLink.replace("https://maps.googleapis.com", ""))
          restaurants = json.loads(conn.getresponse().read())
        except Exception as err:
          print(err)
          self.send_response(500)
          self.send_header("Content-type", "application/json")
          self.end_headers()
          response = collections.defaultdict(list)
          response["error"] = "Opps, ha ocurrido un error :/"
          self.wfile.write(str.encode(json.dumps(response)))
          conn.close()
          return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        restaurants = restaurants["results"]
        response = collections.defaultdict(list)
        for restaurant in restaurants:
          response["restaurantes"].append({"nombre": restaurant["name"], "lat": restaurant["geometry"]["location"]["lat"], "lon": restaurant["geometry"]["location"]["lng"]})
        self.wfile.write(str.encode(json.dumps(response)))
        conn.close()
        return
      elif (self.path == '/ejercicio3'):
        decodedImg = bytearray(base64.b64decode(request["data"]))
        print(type(base64.b64decode(request["data"])))
        decodedImgWidth = int(decodedImg[0x12])
        decodedImgHeight = int(decodedImg[0x16])
        decodedImgPixelArray = int(decodedImg[0x0A])
        print(type(decodedImg), decodedImgWidth, decodedImgHeight, decodedImgPixelArray)

        for i in range(0, decodedImgHeight):
          for j in range(0, decodedImgWidth):
            pos = decodedImgPixelArray+(i*decodedImgWidth*4)+(j*4)  # There are 4 bytes in each pixel
            greyPixel = ((decodedImg[pos]) + (decodedImg[pos+1]) + (decodedImg[pos+2]))//3
            # print(greyPixel)
            decodedImg[pos] = greyPixel
            decodedImg[pos+1] = greyPixel
            decodedImg[pos+2] = greyPixel

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = collections.defaultdict(list)
        response['nombre'] = request['nombre'].replace(".", "(blanco y negro).")
        response['data'] = base64.b64encode(bytes(decodedImg)).decode('utf-8')
        self.wfile.write(str.encode(json.dumps(response)))
        # print(bytes(base64.b64encode(decodedImg)))


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
      if (self.path == '/ejercicio1' or self.path == '/ejercicio2'):
        conn.close()
      return


def startServer():
  print('Starting server...')

  server_address = ('localhost', 8080)
  httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
  print('Server up!')
  httpd.serve_forever()

startServer()