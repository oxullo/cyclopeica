#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import libavg
from libavg.app import keyboardmanager as kbmgr

SEGPOS_CONFIG = 'segpos.json'


class MyDiv(libavg.app.MainDiv):
    STATE_IDLE = 'STATE_IDLE'
    STATE_SETTING_SEGPOS = 'STATE_SETTING_SEGPOS'

    def onInit(self):
        self.state = None
        self.todo = []
        self.current = None

        base = libavg.avg.ImageNode(href='img/base.png', parent=self)
        base.subscribe(base.CURSOR_DOWN, self.onMouseDown)

        self.states = {}
        for i in xrange(0, 23):
            wanted = 'img/states/%02d.png' % i
            if os.path.isfile(wanted):
                self.states[i] = libavg.avg.ImageNode(href=wanted, parent=self)

        self.stateText = libavg.avg.WordsNode(text='STATE', parent=self)
        self.info = libavg.avg.WordsNode(text='NO INFO', pos=(0, 18), parent=self)

        self.loadSegPos()
        self.reset()
        self.changeState(self.STATE_IDLE)
        kbmgr.bindKeyDown('b', self.startSegPos, 'Adjust segment trigger positions')
        kbmgr.bindKeyDown('r', self.reset, 'Reset segment states')
        kbmgr.bindKeyDown('a', self.setAllActive, 'Set all segment states to active')

        for id, pos in self.segPos.iteritems():
            trigger = libavg.avg.CircleNode(r=10, fillopacity=0.4, fillcolor='ff3333',
                    opacity=0, pos=pos, parent=self)
            trigger.subscribe(trigger.CURSOR_DOWN, lambda e, id=id: self.onTriggered(id))

    def changeState(self, newState):
        self.state = newState
        self.stateText.text = newState

    def startSegPos(self):
        self.changeState(self.STATE_SETTING_SEGPOS)
        if not self.todo:
            kbmgr.bindKeyDown('n', self.nextSegPos, 'Next position assoc')
        self.todo = self.segPos.keys()
        self.nextSegPos()

    def nextSegPos(self):
        if not self.todo:
            print 'Done with segment triggers'
            kbmgr.unbindKeyDown('n')
            self.current = None
            self.info.text = 'Done'
            self.changeState(self.STATE_IDLE)
            self.saveSegPos()
        else:
            self.current = self.todo.pop(0)
            self.info.text = 'Click segment %d' % self.current

    def onMouseDown(self, event):
        if self.state == self.STATE_SETTING_SEGPOS:
            print 'Current segment: %d pos: %s' % (self.current, event.pos)
            self.segPos[self.current] = tuple(event.pos)
            self.nextSegPos()

    def onTriggered(self, id):
        self.states[id].active = not self.states[id].active

    def loadSegPos(self):
        if os.path.isfile(SEGPOS_CONFIG):
            segPosStr = json.load(open(SEGPOS_CONFIG))
            self.segPos = {}
            for k, v in segPosStr.iteritems():
                self.segPos[int(k)] = v
            print 'Segment positions loaded from %s' % SEGPOS_CONFIG
        else:
            print 'Segpos config not found, initializing'
            self.segPos = dict([(seg, (0, 0)) for seg in self.states.keys()])

    def saveSegPos(self):
        json.dump(self.segPos, open(SEGPOS_CONFIG, 'w'))
        print 'Segpos config saved to %s' % SEGPOS_CONFIG

    def reset(self):
        for state in self.states.itervalues():
            state.active = False

    def setAllActive(self):
        for state in self.states.itervalues():
            state.active = True

if __name__ == '__main__':
    libavg.app.App().run(MyDiv(), app_resolution='303x763')
