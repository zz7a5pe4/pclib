#!/usr/bin/python

from __future__ import print_function
import sys

def prtwrapper(sep=' ', end='\n', file=sys.stdout):
    def xxprt(*args, **ignore):
        print(*args, sep=sep, end=end, file=file)
        pass
    return xxprt

#LOGPARA, LOGPERF, LOGFUNNAME, LOGEXC, LOGSTDOUT, LOGRET

LOGNONE=0
LOGALL= int('0b'+'1'*32,2)

LOGPARA= 0x1 << 1
LOGPERF= 0x1 << 2
LOGFUNNAME= 0x1 << 3
LOGEXC= 0x1 << 4
LOGSTDOUT= 0x1 << 5
LOGRET= 0x1 << 6


# tell me what you want to log
def VLOG(type, dest=sys.stdout):
    if type == LOGNONE:
        vprt = None
    else:
        vprt = prtwrapper(file=dest)
    def logfun(fn):
        def f(*argt, **argd):
            if(type & LOGFUNNAME):
                vprt(('Enter %s' % fn).center(80, '='))
            if(type & LOGPARA):
                vprt("argus: "+str(argt)+str(argd))
            try:
                ret = None
                exception_info = ""
                if vprt:print("original output".center(80,'-'))
                ret = fn(*argt, **argd)
            except BaseException as e:
                if(type & LOGEXC):
                    exception_info = e.__class__.__name__ + ":\n"
                    exception_info += str(e)
                raise
            finally:
                if vprt:print("-"*80)
                if(type & LOGEXC):
                    vprt("raise exception: ",exception_info)
                if(type & LOGRET):
                    vprt("return: ",str(ret))
                if(type & LOGFUNNAME):
                    vprt(('Exit  %s' % fn).center(80, '='))
            return ret
        return f
    return logfun



# (logcmd=False, logrst=False, outputfile=sys.stdout)
# if logcmd:myprt("something")
# if logrst:myprt("othering")

# @VLOG(LOGALL)
# def hello(v,logcmd=False, logrst=False, outputfile=sys.stdout):
#     myprt = prtwrapper(file=outputfile)
#     myprt("hello")
#     if logcmd:myprt("something")
#     if logrst:myprt("othering")
#     myprt(LOGALL, LOGPARA)
#     #raise KeyboardInterrupt("sdfasdfasfa")
#     raise NotImplementedError("hello")

# def main():
#     out = open("tep.log", "w")
#     hello("sdfeasdfe",logcmd=True, logrst=True)
#     out.close()

# if __name__ == '__main__':
#     main()