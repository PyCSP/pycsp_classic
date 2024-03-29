#!/usr/bin/env python3

# Based on the version from
# https://github.com/kevin-chalmers/cpp-csp/blob/master/demos/stressedalt.cpp
# https://www.researchgate.net/publication/315053019_Development_and_Evaluation_of_a_Modern_CCSP_Library

import common   # noqa E402
from pycsp import process, One2OneChannel, Parallel, Alternative, Any2OneChannel
import time

N_RUNS    = 10
N_SELECTS = 10000
N_CHANNELS = 10
N_PROCS_PER_CHAN = 1000
N_PROCS_PER_CHAN = 100

print("--------------------- Stressed Alt --------------------")
# common.handle_common_args()


@process
def stressed_writer(cout, ready, writer_id):
    "Stressed alt writer"
    ready(42)
    while True:
        cout(writer_id)


@process
def stressed_reader(channels, ready, n_writers, writers_per_chan):
    print("Waiting for all writers to get going")
    for _ in range(n_writers):
        ready()
    print("- writers ready, reader almost ready")

    print(f"Setting up alt with {writers_per_chan} procs per channel and {len(channels)} channels.")
    print(f"Total writer procs : {writers_per_chan * len(channels)}")
    alt = Alternative(*[ch.read for ch in channels])

    if 0:
        print("Select using async with : ")
        for run in range(N_RUNS):
            t1 = time.time()
            for i in range(N_SELECTS):
                with alt as ch:
                    _ = ch()
            t2 = time.time()
            dt = t2 - t1
            us_per_select = 1_000_000 * dt / N_SELECTS
            print(f"Run {run:2}, {N_SELECTS} iters, {us_per_select} us per select/iter")

    print("Select using alt.select() : ")
    for run in range(N_RUNS):
        t1 = time.time()
        for i in range(N_SELECTS):
            ch = alt.select()
            _ = ch()
        t2 = time.time()
        dt = t2 - t1
        us_per_select = 1_000_000 * dt / N_SELECTS
        print(f"Run {run:2}, {N_SELECTS} iters, {us_per_select} us per select/iter")

    for ch in channels:
        ch.poison()


def run_bm():
    ready = Any2OneChannel("ready")
    chans = [One2OneChannel(f'ch {i}') for i in range(N_CHANNELS)]
    procs = []
    for cno, ch in enumerate(chans):
        for c_pid in range(N_PROCS_PER_CHAN):
            writer_id = (cno, c_pid)
            procs.append(stressed_writer(ch.write, ready.write, writer_id))
    procs.append(stressed_reader(chans, ready.read, N_CHANNELS * N_PROCS_PER_CHAN, N_PROCS_PER_CHAN))
    Parallel(*procs)


run_bm()
