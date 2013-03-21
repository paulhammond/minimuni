# Copyright (c) 2008 Paul Hammond
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import xml.etree.ElementTree as ET
import os
import re
import logging

class Train:
  def __init__(self, time, distance, route, stop, destination, expectedDestination):
    if(time == 'Arriving'):
      self.time = 0
    else:
      self.time = int(time)
    self.distance = distance
    self.expectedDestination = expectedDestination
    self.fullDestination = destination
    self.route = route.replace('KT-Ingleside/Third Street','T-Third').replace('M-Ocean View','M-Ocean')
    self.stop = stop.replace('Inbound','').replace('Intbound','').replace('Outbound','')

  def is_past(self):
    return (self.timeleft() < 0)

  def timeleft(self):
    return self.time - self.distance

  def display(self):
      return (self.timeleft() < 30)

  def stop_short(self):
    return re.sub(r'\b(St|Ave)\b','',self.stop).replace('Sunset Tunnel East Portal','Sunset Tunnel')

  def destination(self):
    return self.fullDestination.replace('Inbound to','').replace('Outbound to','')

  def route_short(self):
    return self.route[0]

  def show_destination(self):
    return self.expectedDestination != self.fullDestination

  def __cmp__(self,other):
    if self.is_past() and other.is_past():
      return cmp(self.time,other.time)
    if(self.timeleft() == other.timeleft()):
      return cmp(self.distance,other.distance)
    return cmp(self.timeleft(),other.timeleft())

class Muni:
  def __init__(self):
    self.trains = []

  def fetch(self,config):
    url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictionsForMultiStops&a=sf-muni'
    for line in config['stops'].keys():
      url = url + '&stops=' + line + '|null|' + config['stops'][line]['stop']
    result = urlfetch.fetch(url)
    if result.status_code == 200:
      tree = ET.fromstring(result.content)
      for p in tree.findall('predictions'):
        distance = config['stops'][p.attrib.get('routeTag')]['distance']
        for d in p.findall('direction'):
          expectedDestination = config['stops'][p.attrib.get('routeTag')]['destination']
          destination = d.attrib.get('title')
          for r in d.findall('prediction'):
            self.trains.append(Train(r.attrib.get('minutes'), distance, p.attrib.get('routeTitle'), p.attrib.get('stopTitle'), destination, expectedDestination))
    self.trains.sort()


class MainPage(webapp.RequestHandler):
  
  def get(self):

    config = {
      'who': 'Paul',
      'stops': {
        'N':  { 'stop': '7318', 'distance': 2,  'destination': 'Inbound to Caltrain Depot'},
        'J':  { 'stop': '4006', 'distance': 4,  'destination': 'Inbound to Embarcadero Station'},
        'KT': { 'stop': '5726', 'distance': 6, 'destination': 'Inbound to Sunnydale & Bayshore'},
        'L':  { 'stop': '5726', 'distance': 6, 'destination': 'Inbound to Embarcadero Station'},
        'M':  { 'stop': '5726', 'distance': 6, 'destination': 'Inbound to Embarcadero Station'},
      }
    }

    muni = Muni();
    muni.fetch(config);
    template_values = {
      'trains': muni.trains,
      'who': config['who'],
    }

    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))

class AboutPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
    self.response.out.write(template.render(path, {}))

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/about/', AboutPage)
],debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()