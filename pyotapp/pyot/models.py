'''
Copyright (C) 2012,2013 Scuola Superiore Sant'Anna (http://www.sssup.it) 
and Consorzio Nazionale Interuniversitario per le Telecomunicazioni 
(http://www.cnit.it).

This file is part of PyoT, an IoT Django-based Macroprogramming Environment.

PyoT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
  
PyoT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with PyoT.  If not, see <http://www.gnu.org/licenses/>.

@author: Andrea Azzara' <a.azzara@sssup.it>
'''

from django.db import models
import logging
from datetime import datetime, timedelta
from exceptions import NotImplementedError
from model_utils.managers import InheritanceManager
from django.contrib.auth.models import User
from django.db.models.signals import post_save
#from django.core.exceptions import ObjectDoesNotExist
import base64
from fields import IPNetworkField,  IPNetworkQuerySet, IPAddressField
from settings import TFMT
from celery.task.control import revoke 

caching = True
defaultCachingInterval = 60
defaultCaching =  {'light':15, 
                   'temp': 120, 
                   'baro': 180 } 

KEEPALIVEPERIOD = 10

cachingUri = ['light','temp','baro']

METHOD_CHOICES = (
    (u'GET', u'GET'),
    (u'PUT', u'PUT'),
    (u'POST', u'POST'),    
    (u'DELETE', u'DELETE'), 
)

LOG_CHOICES = (
    (u'registration', u'registration'),
    (u'clean', u'clean'),
    (u'discovery', u'discovery'),
    (u'ghost', u'ghost'),
)

CELERY_DEFAULT_QUEUE = 'celery'

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, related_name='profile')
    organization = models.CharField(max_length=50, blank=False)
    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.get(user=self.user)
            self.id = existing.id #force update instead of insert
        except UserProfile.DoesNotExist:
            pass 
        models.Model.save(self, *args, **kwargs)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Network(models.Model):
    objects = IPNetworkQuerySet.as_manager()
    network = IPNetworkField()
    hostname = models.CharField(max_length=30)
    pid = models.CharField(max_length=100, null=True, blank=True)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    
    def __unicode__(self):
        return u"%s - %s" % (self.network, self.hostname)
    
    def startRD(self):
        from tasks import coapRdServer
        r = coapRdServer.apply_async(args=[str(self.network)], queue=self.hostname)
        self.pid = r.task_id
        self.save()
        
    def stopRD(self):
        revoke(self.pid, terminate=True)
        self.pid = None
        self.save()    
        
    def isConnected(self, table=None):
        pass      
    
class Host(models.Model):
    ip6address = IPAddressField()
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)  
    lastSeen = models.DateTimeField(blank=True)
    active  = models.BooleanField(default = True)
    keepAliveCount = models.IntegerField(default = 0)
    location = models.CharField(max_length=30, blank=True, default='' )
    kqueue = models.ForeignKey(Network, null = True, blank=True, related_name='queue')
    
    def find_network(self):
        nets = Network.objects.all()
        for net in nets:
            if self.ip6address in net.network:
                return net
        return None
        
    def save(self, *args, **kwargs):
        n = self.find_network()
        if n:
            self.kqueue = n    
        super(Host, self).save(*args, **kwargs)
    
    def getQueue(self):
        if self.kqueue:
            return self.kqueue.hostname
        else:
            return CELERY_DEFAULT_QUEUE
    
    def __unicode__(self):
        return u"%s " % (self.ip6address)

    def PING(self, count=3):
        from tasks import pingTest
        res =  pingHost.apply_async(args=[self.id, count], queue=self.getQueue())
        res.wait()
        return res.result
    def DISCOVER(self):
        if self.active == False:
            return u'Host %s Not Active' % (str(self.ip6address))
        from tasks import coapDiscovery
        res = coapDiscovery.apply_async(args=[str(self.ip6address)], queue=self.getQueue())
        res.wait()
        return res.result

class Resource(models.Model):
    uri = models.CharField(max_length=39)
    host = models.ForeignKey(Host)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True) 
    extra = models.CharField(max_length=30, blank=True, default='' )
    obs = models.BooleanField(default = False)
    
    def __unicode__(self):
        return u"{ip} - {uri}".format(uri=self.uri, ip=self.host.ip6address) 
        
    def GET(self, payload=None, timeout=5):
        if caching == True:
            value = getLastResponse(self) 
            if value != None:
                return value
        from tasks import coapGet
        res = coapGet.apply_async(args=[self.id, payload, timeout], queue=self.host.getQueue())
        res.wait()
        return res.result

    def PUT(self, payload=None, timeout=5):
        from tasks import coapPut
        res = coapPut.apply_async(args=[self.id, payload, timeout], queue=self.host.getQueue())
        res.wait()
        return res.result

    def POST(self, payload=None, timeout=5):
        from tasks import coapPost
        res = coapPost.apply_async(args=[self.id, payload, timeout], queue=self.host.getQueue())
        res.wait()
        return res.result
    
    def asyncGET(self,payload=None, timeout=5):
        from tasks import coapGet
        res = coapGet.apply_async(args=[self.id, payload, timeout], queue=self.host.getQueue())
        return res

    def asyncPOST(self,payload=None, timeout=5):
        from tasks import coapPost
        res = coapPost.apply_async(args=[self.id, payload, timeout], queue=self.host.getQueue())
        return res
    
    def asyncPUT(self,payload=None, timeout=5):
        from tasks import coapPut
        res = coapPut.apply_async(args=[self.id, payload, timeout], queue=self.host.getQueue())
        return res
    
    def OBSERVE(self, duration, handler, renew =False): #TODO handler
        from tasks import coapObserve
        res = coapObserve.apply_async(kwargs={'rid':self.id, 'duration':duration, 'handler':handler, 'renew': renew}, queue=self.host.getQueue())
        return res

class ModificationTrace(models.Model):
    lastModified = models.DateTimeField(auto_now_add=True, blank=True) 
    className = models.CharField(max_length=10, blank=True)
    def __unicode__(self):
        return u"{c} - {l}".format(c=self.className, l=self.lastModified) 
        
class EventHandler(models.Model):
    description = models.CharField(max_length=100)
    activationCount = models.IntegerField(default=0)
    max_activations = models.IntegerField(null=True, blank=True)  
    objects = InheritanceManager()   
    result = models.CharField(max_length=100, null=True, blank=True)
    timeString = models.FloatField(null=True, blank=True)
    active  = models.BooleanField(default = True)
    def action(self, res):
        raise NotImplementedError("Subclasses are responsible for creating this method")
    def __unicode__(self):
        return u"{description} | Activations = {activationCount} | Max = {max_activations} - active={active}".format(description=self.description,
                                                                                             activationCount=self.activationCount,
                                                                                                max_activations=self.max_activations,
                                                                                                active=self.active) 


class Subscription(models.Model):
    resource = models.ForeignKey(Resource)
    duration = models.IntegerField(default = 15)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    pid = models.CharField(max_length=100, blank=True)
    active  = models.BooleanField(default = True)
    handler = models.ForeignKey(EventHandler, null=True, blank=True)
    def __unicode__(self):
        return u"{t} {uri} - duration={duration} - active={active}".format(uri=self.resource,
                                                          #type=self.subtype,
                                                          duration=self.duration,
                                                          #thr=self.threshold,
                                                          t=self.timeadded.strftime(TFMT),
                                                          active=self.active)    
class CoapMsg(models.Model):
    resource = models.ForeignKey(Resource)
    method = models.CharField(max_length=10, blank=False, choices=METHOD_CHOICES)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True) 
    code = models.CharField(max_length=5, null=True, blank=True)
    sub = models.ForeignKey(Subscription, null=True, blank=True)
    _payload = models.TextField(db_column='payload',blank=True, max_length=1024)
    def set_data(self, data):
        self._payload = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._payload)

    payload = property(get_data, set_data)
    def __unicode__(self):
        return u"{t} {method} {uri}: {payload}".format(uri=self.resource.uri,
                                                          method=self.method,
                                                          payload=self.payload,
                                                          t=self.timeadded.strftime(TFMT))      
    
def getLastResponse(resource):
    '''
    Caching mechanism: try to find a recent value received from the resource
    
    '''
    if resource.uri not in cachingUri:
        return None
    try:
        interval = defaultCaching[resource.uri]
    except:
        interval = defaultCachingInterval  
    now = datetime.now()
    i = timedelta(seconds=interval)
    start = now - i
    msgs = CoapMsg.objects.filter(resource__id=resource.id, timeadded__gte=start).exclude(method='PUT').order_by('-id')
    if msgs.count() == 0:
        return None
    return msgs[0].payload
    
class EventHandlerMsg(EventHandler):
    msg = models.ForeignKey(CoapMsg)
    
    def __unicode__(self):
        return u"{meta}".format(meta=self.description)     
    def action(self):
        logging.debug('ACTION')
        from Events import sendMsg 
        if (self.activationCount == self.max_activations):
            logging.debug('max activations reached')
            return
        self.activationCount += 1
        self.result  = sendMsg(self.msg)   
        self.save()

class Log(models.Model):
    type = models.CharField(max_length=30, choices=LOG_CHOICES)
    message = models.CharField(max_length=1024)
    timeadded = models.DateTimeField(auto_now_add=True, blank=True)
    def __unicode__(self):
        return u"{t} {type} {message}".format(type=self.type, message=self.message, t=self.timeadded.strftime(tfmt))      
    
      
