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
        return
      elif (self.path == '/ejercicio4'):
        decodedImg = bytearray(base64.b64decode(request["data"]))
        decodedImgWidth = int(decodedImg[0x12])
        decodedImgHeight = int(decodedImg[0x16])
        decodedImgPixelArray = int(decodedImg[0x0A])
        groupWidthBy = int(decodedImg[0x12])//request["tamaño"]["ancho"]
        coverWidthFor = int(decodedImg[0x12])%request["tamaño"]["ancho"]
        groupHeightBy = int(decodedImg[0x16])//request["tamaño"]["alto"]
        coverHeightFor = int(decodedImg[0x16])%request["tamaño"]["alto"]

        # resizedImg = bytearray(decodedImgPixelArray+(request["tamaño"]["ancho"]*request["tamaño"]["alto"]*4))
        # resizedImg[:decodedImgPixelArray] = decodedImg[:decodedImgPixelArray]
        resizedImg = decodedImg[:decodedImgPixelArray]

        # MAGIC START
        for i in range(0, request["tamaño"]["alto"]):
          for j in range(0, request["tamaño"]["ancho"]):
            resultB = 0
            resultG = 0
            resultR = 0
            resultA = 0
            pos = (((groupWidthBy*j)+(j if j<coverWidthFor else coverWidthFor))+(decodedImgWidth*((groupHeightBy*i)+(i if i<coverHeightFor else coverHeightFor))))*4
            for k in range(0, groupHeightBy+(1 if i<coverHeightFor else 0)):
              for l in range(0, groupWidthBy+(1 if j<coverWidthFor else 0)):
                resultB += decodedImg[pos+(l*4)]
                resultG += decodedImg[pos+(l*4)+1]
                resultR += decodedImg[pos+(l*4)+2]
                resultA += decodedImg[pos+(l*4)+3]
              pos += decodedImgWidth
            # print(resultB)
            divisor = int((groupHeightBy+(1 if i<coverHeightFor else 0))*(groupWidthBy+(1 if j<coverWidthFor else 0)))
            # resizedImg[decodedImgPixelArray+i*j*4] = (resultB//divisor)
            # resizedImg[decodedImgPixelArray+i*j*4+1] = (resultG//divisor)
            # resizedImg[decodedImgPixelArray+i*j*4+2] = (resultR//divisor)
            # resizedImg[decodedImgPixelArray+i*j*4+3] = (resultA//divisor)
            resizedImg.append(resultB//divisor)
            resizedImg.append(resultG//divisor)
            resizedImg.append(resultR//divisor)
            resizedImg.append(resultA//divisor)
        # MAGIC END

        resizedImg[0x02] = (len(resizedImg))&0xFF
        resizedImg[0x03] = ((len(resizedImg))>>8)&0xFF
        resizedImg[0x04] = ((len(resizedImg))>>16)&0xFF
        resizedImg[0x05] = (len(resizedImg))>>24
        resizedImg[0x12] = (request["tamaño"]["ancho"])&0xFF
        resizedImg[0x13] = ((request["tamaño"]["ancho"])>>8)&0xFF
        resizedImg[0x14] = ((request["tamaño"]["ancho"])>>16)&0xFF
        resizedImg[0x15] = (request["tamaño"]["ancho"])>>24
        resizedImg[0x16] = (request["tamaño"]["alto"])&0xFF
        resizedImg[0x17] = ((request["tamaño"]["alto"])>>8)&0xFF
        resizedImg[0x18] = ((request["tamaño"]["alto"])>>16)&0xFF
        resizedImg[0x19] = (request["tamaño"]["alto"])>>24
        resizedImg[0x22] = (len(resizedImg)-decodedImgPixelArray)&0xFF
        resizedImg[0x23] = ((len(resizedImg)-decodedImgPixelArray)>>8)&0xFF
        resizedImg[0x24] = ((len(resizedImg)-decodedImgPixelArray)>>16)&0xFF
        resizedImg[0x25] = (len(resizedImg)-decodedImgPixelArray)>>24

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = collections.defaultdict(list)
        response['nombre'] = request['nombre'].replace(".", "(blanco y negro).")
        response['data'] = base64.b64encode(bytes(resizedImg)).decode('utf-8')
        self.wfile.write(str.encode(json.dumps(response)))
        return

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

  server_address = ('0.0.0.0', 8080)
  httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
  print('Server up!')
  httpd.serve_forever()

startServer()