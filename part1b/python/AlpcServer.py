#! /usr/bin/env python
# Copyright (c) 2010 Art & Logic Software Development, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import BaseHTTPServer
import cgi
import cStringIO
import datetime
import mimetypes
import optparse
import os
import shutil
import SimpleHTTPServer
import socket
import sys
import traceback

from Completer import ACompleter
from Request import ARequest
import Request

__version__ = "1.0.0"

kDefaultFilename = 'index.html'

class AAlpcHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
   server_version = "ALPC/%s" % __version__
   protocol_version = "HTTP/1.0"

   def do_GET(self):
      self.postData = None
      self.HandleRequest("GET")

   def do_HEAD(self):
      pass

   def do_PUT(self):
      pass

   def do_POST(self):
      ''' 
         Read the post data from the socket, parse it out into a dict mapping
         keywords to lists of values, and pass the request along to our common
         L{Handler} method.

         @note: we do not handle posts that don't have a C{content-length}
         header.
      '''
      postLength = self.headers.getheader("content-length")
      if postLength:
         postLength = int(postLength)
         postData = self.rfile.read(postLength)
         "actual length = %d" % len(postData)
         # convert the encoded post string into a dict of value-lists
         self.postData = cgi.parse_qs(postData)
      self.HandleRequest("POST")
      self.postData = None

   def HandleRequest(self, command):      
      r = ARequest(command, self.path, self.headers,
       self.client_address, self.postData)

      try:
         self.server.HandleRequest(r)
         self.send_response(r.responseCode)
         for header, value in r.responseHeaders.items():
            self.send_header(header, value)
         if r.outputLength:
            self.send_header("Content-Length", str(r.outputLength))
         self.end_headers()
         if r.outputFile:
            # use the shutil module to copy the file efficiently.
            shutil.copyfileobj(r.outputFile, self.wfile)
            r.outputFile.close()
         else:
            # send the output, one chunk at a time
            for chunk in r.output:
               self.wfile.write(chunk)
      except Request.AHttpException, e:
         f = cStringIO.StringIO()
         traceback.print_exc(file=f)
         tb = f.getvalue()
         print "Http exception == %d, %s" % (e.code, e.str)
         self.send_response(e.code)
         self.send_header("Content-type", "text/plain")
         self.send_header("Content-length", str(len(tb) + len(e.str)))
         self.send_header('Connection', 'close')
         self.end_headers()
         self.wfile.write(tb)
         self.wfile.write(e.str)




class AAlpcHttpServer(BaseHTTPServer.HTTPServer):
   def __init__(self, serverAddress, handlerClass, completer, root):
      '''
         @param serverAddress tuple containing ('', portNum) to serve on
         @param handlerClass Class derived from SimpleHTTPRequestHandler to
            actually take care of incoming requests.
         @param completer Instance of an ACompleter object to complete partial
            words
         @param root Local file path holding static files to be served.
      ''' 
      BaseHTTPServer.HTTPServer.__init__(self, serverAddress, handlerClass)
      self.completer = completer
      self.root = root

   def HandleRequest(self, req):
      command = req.command.title()
      try:
         handler = getattr(self, command)
         handler(req)
      except AttributeError:
         # we don't know how to do what they're asking -- 
         raise Request.AHttpException(501, "%s not implemented." % req.command)

   def Get(self, req):
      if 0 == len(req.path):
         # if they requested '/', try to serve 'index.html'
         req.path = [kDefaultFilename]

      if 'words' == req.path[0].lower():
         try:
            matches = self.completer.Complete(req.path[1])
            if matches:
               req.Write(",".join([w for w in matches]))
               req.SetHeader("Content-type", "text/plain")
            else:
               # nothing matches, let caller know that there's no content
               # coming back.
               req.responseCode = 204
               
         except IndexError:
            # no prefix specified -- just send back a 'bad request' error
            raise Request.AHttpException(400, "Parameter missing")
      else:
         # look for and return a file.
         filePath = os.path.join(self.root, *req.path)
         filePath = os.path.normpath(filePath)
         if os.path.exists(filePath):
            if os.path.isdir(filePath):
               # prohibit user from accessing a directory - look for an 
               # index.html file inside that directory. 
               filePath = os.path.join(filePath, kDefaultFilename)
            # open the file, etc
            mimeType = mimetypes.guess_type(filePath)
            mimeType = mimeType[0]
            if not mimeType:
               mimeType = "text/plain"
               openMode = "r"

            fileObj = open(filePath, "rb")
            statVal = os.stat(filePath)
            fileLength = statVal.st_size
            lastModified = datetime.datetime.fromtimestamp(statVal.st_mtime)
            # set up (and respond to) conditional GET requests -- if the file
            # is unmodified, just let the requesting browser know that; don't
            # re-send the file.
            clientLastModified = req.GetRequestHeader("if-modified-since")
            if clientLastModified:
               if lastModified == clientLastModified:
                  raise Request.AHttpException(304, "Not Modified")
            req.SetHeader("Content-type", mimeType)
            req.SetHeader("Last-Modified", lastModified)
            req.SetOutputFile(fileObj, fileLength)
         else:
            raise Request.AHttpException(404, "File not found")

   def server_bind(self):
      ''' bind the server to the socket, and set the socket up so that it
      times out once a second instead of blocking forever.'''

      BaseHTTPServer.HTTPServer.server_bind(self)
      self.socket.settimeout(1)
    
   def get_request(self):
      while 1:
         try:
            sock, addr = self.socket.accept()
            sock.settimeout(None)
            return (sock, addr)
         except socket.timeout:
            pass


   def serve_forever(self):
      while 1:
         try:
            self.handle_request()
         except KeyboardInterrupt:
            print "\nReceived [Ctrl+C] -- exiting!"
            return
         except socket.error:
            pass

if __name__ == "__main__":
   import optparse
   parser = optparse.OptionParser()
   parser.add_option('-p', '--port', help="HTTP port to serve pages on (default = 8080)",
    dest='port', action='store', type='int', default=8080)
   parser.add_option('-r', '--root', help="root directory containing pages (default = '.')",
    dest='root', action='store', type='string', default='.')
   parser.add_option('-w', '--words', help="filename containing words (default = 'wordTest.txt')",
    dest = 'wordFile', default='wordTest.txt')

   opts, args = parser.parse_args()

   serverAddress = ('', opts.port)
   completer = ACompleter(opts.wordFile)
   root = opts.root

   httpd = AAlpcHttpServer(serverAddress, AAlpcHandler, completer, root)
   sa = httpd.socket.getsockname()
   print "Art & Logic Programming Challenge Server"
   print "\nfor command line help: python AlpcServer.py --help\n"
   print "Completing words from file '%s'" % opts.wordFile
   print "Serving pages from directory '%s'" % opts.root
   print "Serving HTTP on %s:%s..." % (sa[0], sa[1])
   print "(Press [Ctrl+C] to exit server)\n\n"

   httpd.serve_forever()







