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
from BeautifulSoup import BeautifulSoup
import os
import re
import logging


class Train:
  def __init__(self, time, distance, route, stop):
    if(time == 'Arriving'):
      self.time = 0
    else:
      self.time = int(time)
    self.distance = distance
    self.route = route.replace('KT-Ingleside/Third Street','T-Third').replace('M-Ocean View','M-Ocean')
    self.stop = stop.replace('Inbound','').replace('Intbound','').replace('Outbound','')

  def is_past(self):
    return (self.timeleft() < 0)
  
  def timeleft(self):
    return self.time - self.distance
    
  def stop_short(self):
    return re.sub(r'\b(St|Ave)\b','',self.stop)

  def route_short(self):
    return self.route[0]

  def __cmp__(self,other):
    if self.is_past() and other.is_past():
      return cmp(self.time,other.time)
    if(self.timeleft() == other.timeleft()):
      return cmp(self.distance,other.distance)
    return cmp(self.timeleft(),other.timeleft())

class Muni:
  def __init__(self):
    self.trains = []
  
  def addStop(self,url,distance):
    
    result = urlfetch.fetch(url)
    times = []
    route = 'unknown'
    stop = 'unknown'
    if result.status_code == 200:
      soup = BeautifulSoup(result.content, convertEntities="html")
      #logging.info(result.content)
      try:
        route = soup.find(text=re.compile('Route:')).findNext('b').string
        stop = soup.find(text=re.compile('Stop:')).findNext('b').string
        # this route
        pos = soup.find(text=re.compile('Next vehicle')).findNext('table').findNext('table')
        for i in range(0, 3):
          pos = pos.findNext('tr')
          time = pos.td.span.string.lstrip()
          self.trains.append(Train(time,distance,route,stop))

        # other routes
        pos = soup.find(text=re.compile('other routes')).findNext('table')
        for i in range(0, 6):
          pos = pos.findNext('tr')
          tds = pos.findAll('td')
          
          time = tds[0].div.font.b.string.lstrip()
          route = tds[2].div.font.string.lstrip()
          route = re.match('\((.*) (In|Out)bound to .*\)',route).group(1)
          self.trains.append(Train(time,distance,route,stop))
        
      except AttributeError:
        pass
        
    self.trains.sort()
      

class MainPage(webapp.RequestHandler):
  
  def get(self):
    
    config = {
      'who': 'Paul',
      'stops': [
        {
          'url': 'http://www.nextbus.com/wireless/miniPrediction.shtml?a=sf-muni&r=N&d=N__IB3&s=7318',
          'distance': 6
        },
        {
          'url': 'http://www.nextbus.com/wireless/miniPrediction.shtml?a=sf-muni&r=J&d=J__IB2&s=4006',
          'distance': 8
        },
        {
          'url': 'http://www.nextbus.com/wireless/miniPrediction.shtml?a=sf-muni&r=KT&d=KT__IB1&s=5726',
          'distance': 10
        }
      ]
    }
    
    muni = Muni();
    for stop in config['stops']:
      muni.addStop(stop['url'],stop['distance'])
    
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