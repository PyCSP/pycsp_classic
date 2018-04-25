#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
Contains common CSP processes such as Id, Delta, Prefix etc. 

Copyright (c) 2007 John Markus Bjørndalen, jmb@cs.uit.no.
See LICENSE.txt for licensing details (MIT License). 
"""

from pycsp import process, Channel, ChannelPoisonException, Parallel

@process
def Identity(cin, cout):
    """Copies its input stream to its output stream, adding a one-place buffer
    to the stream."""
    while 1:
        t = cin()
        cout(t)

@process
def Prefix(cin, cout, prefixItem=None):
    t = prefixItem
    while True:
        cout(t)
        t = cin()

@process
def ParDelta2(cin, cout1, cout2):
    # We need two helper processes (_sender) to send on the two output channels in parallel. 
    # The overhead of this is probably going to be fairly high as we're starting and stopping threads for every iteration. 
    # We could optimize it with re_usable threads, but if we create a separate channel to each of them we're more or
    # less recreating the problem with another mini-delta in the middle.
    # The other alternative is threads that don't disappear until we leave the context they were created in and that can be
    # re-started inside a Par (or similar) context. This quickly complicates the API and could make it harder to understand. 
    @process
    def _sender(ochan, val):
        ochan(val)
    while True:
        t = cin()
        for c in [cout1, cout2]:
            # TODO: Had to add a poison workaround as Parallel and Process don't propagate poison by re-raising
            # exceptions. Instead, they rely on the procesess catching poison by accessing a channel.
            # Delta2 will only be poisoned directly when trying to read the cin channel, so we need to 
            # manually check the other two here and raise it manually if necessary.
            # We need a solution that works both when we want to propagate poison and when we want to filter it. 
            if c._chan.poisoned:
                raise ChannelPoisonException() 
        Parallel(_sender(cout1, t),
                 _sender(cout2, t))

@process
def SeqDelta2(cin, cout1, cout2):
    # The JCSP version sends the output in parallel. This one essentially runs it in a SEQ instead.
    # The above Delta2 process solves this with significant thread overhead. 
    while True:
        t = cin()
        cout1(t)
        cout2(t)

Delta2 = ParDelta2
            
@process
def Successor(cin, cout):
    """Adds 1 to the value read on the input channel and outputs it on the output channel.
    Infinite loop.
    """
    while True:
        cout(cin()+1)

@process
def SkipProcess():
    pass

@process
def Mux2(cin1, cin2, cout):
    alt = Alternative(cin1, cin2)
    while True:
        c = alt.priSelect()
        cout(c())
