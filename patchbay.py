'''
Objects used to create a patch bay for streams
PatchBay
PatchIO
'''

import os
import fcntl
import select

class PatchBay(object):
    '''
    PatchBay - For duplicating in-streams to multiple out-streams
    {in1 : [out1, out2], in2 : [out1, out2]}
    '''

    def __init__(self, iopatch):
        self._patches = set() # PatchIO objects
        self._bufsize = 128 # default when used as a generator

        if isinstance(iopatch, dict):
            for hin in iopatch:
                self._patches.add(PatchIO(hin, iopatch[hin]))
        else:
            for hin in iopatch:
                self._patches.add(hin)

    def __iter__(self):
        '''the generator will yield tuples (in-stream, data)'''
        while True:
            prl, pwl, pxl = select.select(self._patches, [], [])
            for prd in prl:
                for line in prd.readgen(self._bufsize):
                    yield prd.inobj, line
                if prd.eof():
                    self._patches.remove(prd)
                    if len(self._patches) == 0:
                        return

    def process(self):
        '''Will return when all the in-streams are done (eof)'''
        self._bufsize = 8*1024
        for inobj, line in self:
            pass

    def collect(self):
        '''
        Will return when all the in-streams are done (eof).
        All collected data will be returned in a dict where
        the key is the in-stream.
        '''
        self._bufsize = 8*1024
        data = dict()
        for pio in self._patches:
            data[pio.inobj] = ''
        for inobj, line in self:
            data[inobj] += line
        return data


class PatchIO(object):
    '''
    PatchIO - Holds the mapping between one in-stream and its out-streams
    '''

    def __init__(self, inobj, outlist):
        self.inobj = inobj
        self._fd = PatchIO._fno(inobj)
        PatchIO._set_non_blocking(self._fd)
        self._linebuf = ''
        self._od = set()
        self._eof = False
        for hout in outlist:
            self._od.add(PatchIO._fno(hout))

    @staticmethod
    def _fno(obj):
        return obj if isinstance(obj, int) else obj.fileno()

    @staticmethod
    def _set_non_blocking(filedescriptor):
        currentfl = fcntl.fcntl(filedescriptor, fcntl.F_GETFL)
        fcntl.fcntl(filedescriptor, fcntl.F_SETFL, currentfl | os.O_NONBLOCK)

    def fileno(self):
        '''return the OS file descriptor'''
        return self._fd

    def eof(self):
        '''return True if end-of-stream is reached'''
        return self._eof

    def read(self, bufsize):
        '''read in-stream and write to out-streams'''
        buf = os.read(self._fd, bufsize)
        if buf:
            for outd in self._od:
                os.write(outd, buf)
        else:
            self._eof = True
        return buf

    def readgen(self, bufsize):
        '''
        generator that will yield one os.linesep:arated line at a time
        '''
        buf = self.read(bufsize)
        if not self._eof:
            self._linebuf += buf
            lines = self._linebuf.split(os.linesep)
            # save only the last empty or incomplete line
            self._linebuf = lines.pop()
            for line in lines:
                yield line + os.linesep
        else: # stream closed
            if self._linebuf:
                # the last line was not newline terminated
                yield self._linebuf
