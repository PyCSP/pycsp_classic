#!/usr/bin/env python
# -*- coding: latin-1 -*-
# Copyright (c) 2007 John Markus Bjørndalen, jmb@cs.uit.no.
# See LICENSE.txt for licensing details (MIT License).

# trick to allow us to import pycsp without setting PYTHONPATH
import sys
sys.path.append("..")
import pycsp    # noqa E402


def avg(vals):
    "Returns the average of values"
    return sum(vals) / len(vals)
