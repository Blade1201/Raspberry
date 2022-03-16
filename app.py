from http.server import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
Reguest = None

class RequestHandler_httpd(BaseHTTPRequestHandler):
  def do_GET(self):
    global Reguest
    messagetosend = bytes('Hello World!',"utf")
    self.send_response(200)
    self.send_header('Content-Type', 'text/plain')
    self.send_header('Content-Length', len(messagetosend))
    self.end_headers()
    self.wfile.write(messagetosend)
    Reguest = self.requestline
    Reguest = Reguest[5 : int(len(Reguest)-9)]
    print(Reguest)
    if Reguest == 'ON':
      GPIO.output(21,True)
    if Reguest == 'OFF':
      GPIO.output(21,False)
    if Reguest == 'futeson':
      GPIO.output(18,True)
    if Reguest == 'futesoff':
      GPIO.output(18,False)
    if Reguest =='klimaon':
      GPIO.output(6,True)
    if Reguest =='klimaoff':
      GPIO.output(6,False)
    return


server_address_httpd = ('192.168.0.109',8080)
httpd = HTTPServer(server_address_httpd, RequestHandler_httpd)
print('Starting server:')
httpd.serve_forever()
GPIO.cleanup()