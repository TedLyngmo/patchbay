#!/usr/bin/python

import sys
import subprocess
from patchbay import PatchBay

with open('merged.log', 'w') as log:
    p1 = subprocess.Popen(['./program1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(['./program2'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pb = PatchBay({p1.stdout: [log],
                   p1.stderr: [log, sys.stdout],
                   p2.stdout: [log],
                   p2.stderr: [log, sys.stderr]})
    stream_data = pb.collect()
    print '====================== Data collected per in-stream:'
    for fh, data in stream_data.iteritems():
        print "fd={} -------------------------------------------------".format(fh.fileno())
        print "data={}".format(data)
