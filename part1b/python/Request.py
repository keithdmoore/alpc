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


import cStringIO
import cgi
import re
import urllib
import sys

# match a percent, followed by two hex digits
kEntityPattern = re.compile(r'%([0-9A-Fa-f]{2})')

class AHttpException(Exception):
   def __init__(self, code, str):
      self.code = code
      self.str = str




   
class ARequest(object):
   '''
      Class to represent the incoming client request and our reponse to that
      request.
   
      @ivar command: HTTP verb for this request.
      @ivar path: list of path components (IOW, path/to/file is represented as 
            ['path', 'to', 'file']
      @ivar query: dict mapping each keys in the query string to a list of
            values
      @ivar headers: dict containing HTTP headers received from the client
      @ivar client: string containing client IP address
      @ivar postData: dict containing un-encoded post data (key, [list-of-values])
      @ivar responseCode: HTTP response code sent by our code.
      @ivar responseHeaders: dict of HTTP headers to return to the client
      @ivar output: list of strings to return as body of response message
      @ivar outputLength: sum of the lengths of the strings in the output list
      @ivar outputFile: open file object to return to the client as the output
            body -- note that we cannot use both C{output} and C{outputFile}
            at the same time.

      @ivar rawPath: full path to the page currently being displayed
      @ivar basePath: portion of path preceding any '?' that may be present
   '''
   def __init__(self, cmd, path=None, headers=None, client=None, postData=None):
      ''' 
         Create a new request object, using as many of the input parameters
         as we are provided with. We will use the same request object to hold
         the data that we would like to have sent back to the client.

      '''
      self.command = cmd
      if headers:
         self.headers = dict([(k.lower(), v) for (k, v) in headers.items()])
      self.client = client
      self.postData = postData
      self.responseCode = 200
      self.responseHeaders = {}
      self.output = []
      self.outputLength = None
      self.outputFile = None
      self.rawPath = path
      self.basePath = ''
      self.ParsePath(path)


   def SetHeader(self, key, value):
      self.responseHeaders[key] = value

   def GetRequestHeader(self, key):
      try:
         return self.headers[key]
      except KeyError:
         return None

   def SetResponseCode(self, code):
      self.responseCode = code

   def Redirect(self, location):
      '''
         @param location: path that the browser is told to redirect to. We
               serve up  a '302' (temporary) redirect.
      '''
      self.SetResponseCode(302)
      self.SetHeader("Location", location)

   def GetQueryData(self, key, fullList=False):
      ''' if the specified key is present in the query data dict, returns it.
          if the 'fullList' parameter is set to TRUE, returns the data as a
          list. otherwise returns a single element.
          If the key isn't present in the query returns None.
      '''
      val = None
      if self.query:
         val = self.query.get(key)
         if val:
            if not fullList:
               val = val[0]
      return val

   def GetPostData(self, key, fullList = False):
      ''' if the specified key is present in the post data dict, returns it.
          if the 'fullList' parameter is set to TRUE, returns the data as a
          list. otherwise returns a single element. If the requested key isn't
          present in the post data, returns None.
      '''
      val = None
      if self.postData:
         val = self.postData.get(key)
         if val:
            if not fullList:
               val = val[0]
      return val
         

   def Write(self, txt):
      ''' add 'txt' to the list of strings that we're going to send back to
      the client, also updating the output length as we go.
      '''
      self.outputFile = None
      self.output.append(txt)
      if not self.outputLength:
         self.outputLength = 0
      self.outputLength += len(txt)
      

   def SetOutputFile(self, outputFile, fileLength):
      ''' used to return a file of data, instead of a string. '''
      self.outputFile = outputFile
      self.output = []
      if not self.outputLength:
         self.outputLength = 0
      self.outputLength = fileLength

   def ParsePath(self, pathStr):
      # break off query string if it's there...
      components = pathStr.split("?")
      self.query = {}
      if len(components) > 1:
         # parse the query string into a dict (retaining any keys that have
         # empty values.
         queryVals = cgi.parse_qs(components[1], True)
         for key, val in queryVals.items():
            self.query[key.lower()] = val
            
      else:
         pass
      self.basePath = components[0]
      pathComponents = components[0].split('/')
      # the first path component will always be '' because we get a leading
      # slash -- there can't be anything preceding it -- just throw that one
      # away (similarly, throw away anything that comes after a trailing slash)
      self.path = [urllib.unquote_plus(p).lower() for p in pathComponents if len(p)]


