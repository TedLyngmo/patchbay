PatchBay 0.1
============

PatchBay is a python class used to connect multiple (1-many) in-streams with multiple (0-many) out-streams.

Examples
--------

Run two programs and log stdout and stderr from both program in the same file.
stderr from program1 is also sent to sys.stdout and
stderr from program2 is also sent to sys.stderr
The data from the four individual in-streams are also returned in a dictionary
where the in-streams are the keys.

```python
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
```

License
-------
This is free and unencumbered software released into the public domain.
See [https://github.com/TedLyngmo/patchbay/blob/master/LICENSE.md].
