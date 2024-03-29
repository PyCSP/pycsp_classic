#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import os
import psutil
import sys
import time
import common    # noqa : E402
from pycsp import process, Any2OneChannel, One2AnyChannel, Parallel

N_PROCS = 10 if len(sys.argv) < 2 else int(sys.argv[1])


@process
def simple_proc(pid, checkin, cin):
    # check in
    checkin(pid)
    # wait for poison
    while True:
        _ = cin()


@process
def killer(chin, pch, nprocs):
    print("Killer waiting for the other procs to call in")
    for i in range(nprocs):
        _ = chin()
    print("Done, checking memory usage")
    p = psutil.Process(os.getpid())
    rss = p.memory_info().rss
    print(f"RSS now {rss}  {rss/(1024**2)}M")
    print("now poisioning")
    pch.poison()
    return rss


def run_n_procs(n):
    print(f"Running with {n} simple_procs")
    ch = Any2OneChannel()
    pch = One2AnyChannel()
    t1 = time.time()
    tasks = [simple_proc(i, ch.write, pch.read) for i in range(N_PROCS)]
    tasks.append(killer(ch.read, pch, n))
    t2 = time.time()
    res = Parallel(*tasks)
    t3 = time.time()
    rss = res[-1]
    tcr = t2 - t1
    trun = t3 - t2
    print("Creating tasks: {:15.3f} us  {:15.3f} ms  {:15.9f} s".format(1_000_000 * tcr,  1000 * tcr,  tcr))
    print("Running  tasks: {:15.3f} us  {:15.3f} ms  {:15.9f} s".format(1_000_000 * trun, 1000 * trun, trun))
    print("{" + (f'"nprocs" : {n}, "t1" : {t1}, "t2" : {t2}, "t3" : {t3}, "tcr" : {tcr}, "trun" : {trun}, "rss" : {rss}') + "}")


run_n_procs(N_PROCS)
