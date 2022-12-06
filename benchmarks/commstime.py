#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import os
import time
from common import avg
from pycsp import process, One2OneChannel, poisonChannel, Parallel
from pycsp.plugNplay import Prefix, Delta2, ParDelta2, SeqDelta2, Successor


@process
def Consumer(cin, run_no):
    "Commstime consumer process"
    N = 5000
    ts = time.time
    t1 = ts()
    cin()
    t1 = ts()
    for i in range(N):
        cin()
    t2 = ts()
    dt = t2 - t1
    tchan = dt / (4 * N)
    print("Run %d DT = %f. Time per ch : %f/(4*%d) = %f s = %f us" %
          (run_no, dt, dt, N, tchan, tchan * 1000000))
    # print("consumer done, posioning channel")
    poisonChannel(cin)
    results.append(tchan * 1000000)


def CommsTimeBM(run_no, Delta2=Delta2):
    # Create channels
    a = One2OneChannel("a")
    b = One2OneChannel("b")
    c = One2OneChannel("c")
    d = One2OneChannel("d")

    # print("Running commstime test")
    # Rather than pass the objects and get the channel ends wrong, or doing complex
    # addons like in csp.net, i simply pass the write and read functions as channel ends.
    # Note: c.read.im_self == c, also check im_func, im_class
    Parallel(Prefix(c.read, a.write, prefixItem=0),    # initiator
             Delta2(a.read, b.write, d.write),         # forwarding to two
             Successor(b.read, c.write),               # feeding back to prefix
             Consumer(d.read, run_no))                 # timing process


def run_bm(Delta2=Delta2):
    global results
    print(f"Running with Delta2 = {Delta2}")
    results = []
    N_BM = 10
    for i in range(N_BM):
        # print("----------- run %d/%d -------------" % (i+1, N_BM))
        CommsTimeBM(i, Delta2)
    print("Min {} avg {} max {}".format(min(results), avg(results), max(results)))


print("--------------------- Commstime --------------------")
print("ParDelta2")
run_bm(ParDelta2)
print("SeqDelta2")
run_bm(SeqDelta2)

# A bit of a hack, but windows does not have uname()
try:
    os.uname()
except AttributeError:
    print("Sleeping for a while to allow MS Windows users to read benchmark results")
    time.sleep(15)
