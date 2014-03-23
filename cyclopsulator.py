#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import Queue
import time
import json

import requests
import libavg

SEGMAP_CONFIG = 'segmap.json'
DATASOURCE_URL = 'http://localhost:5000/'
CHAR_DELAY = 800


class Requestor(threading.Thread):
    def __init__(self, *args, **kargs):
        super(Requestor, self).__init__(*args, **kargs)
        self.queue = Queue.Queue()
        self.setDaemon(True)

    def run(self):
        print 'Requestor (%s) starting up' % self
        while True:
            while self.queue.qsize() >= 5:
                time.sleep(1)

            try:
                req = requests.get(DATASOURCE_URL)
            except Exception, e:
                print 'Exception (%s): %s' % (self, e)
                time.sleep(10)

            phrase = req.json()['phrase']
            self.queue.put(phrase)
            print 'Enqueued phrase: %s' % phrase

    def getPhrase(self):
        try:
            return self.queue.get(block=False)
        except Queue.Empty:
            return None


class Cyclopsulator(libavg.app.MainDiv):
    def onInit(self):
        libavg.player.setWindowTitle('Cyclopsulator')

        self.states = {}
        self.buffer = None

        libavg.avg.ImageNode(href='img/base.png', parent=self)

        for i in xrange(0, 23):
            wanted = 'img/states/%02d.png' % i
            if os.path.isfile(wanted):
                self.states[i] = libavg.avg.ImageNode(href=wanted, parent=self)

        self.loadSegMap()
        self.reset()
        self.setAllActive()
        
        self.requestor = Requestor()
        self.requestor.start()

        libavg.player.setInterval(CHAR_DELAY, self.nextChar)

    def setChar(self, char):
        self.reset()
        if not char in self.segMap:
            char = '#'

        for id in self.segMap[char]:
            self.states[id].active = True

    def nextChar(self):
        if not self.buffer:
            self.buffer = [ch.upper() for ch in self.requestor.getPhrase()]
            self.setChar('~')
        else:
            self.setChar(' ')
            libavg.player.setTimeout(20, lambda: self.setChar(self.buffer.pop(0)))

    def loadSegMap(self):
        if os.path.isfile(SEGMAP_CONFIG):
            self.segMap = json.load(open(SEGMAP_CONFIG))
            print 'Segment map loaded from %s' % SEGMAP_CONFIG
        else:
            print 'Segment map config not found, initializing'
            self.segMap = dict([(ch, []) for ch in ASCIISET])

    def reset(self):
        for state in self.states.itervalues():
            state.active = False

    def setAllActive(self):
        for state in self.states.itervalues():
            state.active = True


if __name__ == '__main__':
    libavg.app.App().run(Cyclopsulator(), app_resolution='303x763')
