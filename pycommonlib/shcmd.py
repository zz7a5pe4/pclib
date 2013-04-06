#!/usr/bin/python

import shlex, subprocess
import pexpect

#bash treat return value 0 as success
class ShellResult:
    output = ""
    error = ""
    def __init__(self,v=127):
        self.ret = v

    def __str__(self):
        if self.ret == 0:
            return self.output
        else:
            return "Fail: {0}".format(self.error)

    def __nonzero__(self):
        if self.ret == 0:
            return True
        else:
            return False


def syncexec(shellcmds):
    if not shellcmds:
        return None
    args = shlex.split(shellcmds)
    ret = ShellResult(0)
    p = subprocess.Popen(args,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret.output,ret.error = p.communicate()
    ret.ret = p.returncode
    return ret

def syncexec_timeout(shellcmds, t=600):
    if not shellcmds:
        return None
    ret = ShellResult(-1)
    child = None
    try:
        child = pexpect.spawn('/bin/bash', ['-c', shellcmds], timeout=t)
        #index = p.expect ([pexpect.EOF, pexpect.TIMEOUT])
        while(1):
            i = child.readline()
            ret.output += i
            if not i:
                break
    except pexpect.TIMEOUT as e:
        ret.error = "Timeout while running: {0}".format(shellcmds)
    except pexpect.ExceptionPexpect as e:
        ret.error = str(e)
    else:
        if child.isalive():
            child.wait()
        ret.ret = child.exitstatus if not child.exitstatus == None else -1
        ret.output = ret.output.rstrip()
        ret.error = ret.output
    finally:
        if child:
            child.close()
    
    return ret

def syncexec_generater(shellcmds, t=600):
    if not shellcmds:
        return

    child = None
    try:
        child = pexpect.spawn('/bin/bash', ['-c', shellcmds], timeout=t)
        #index = p.expect ([pexpect.EOF, pexpect.TIMEOUT])
        while(1):
            i = child.readline()
            if i:
                yield i.rstrip()
            else:
                break
    except pexpect.TIMEOUT as e:
        yield "Timeout while running: {0}".format(shellcmds)
    except pexpect.ExceptionPexpect as e:
        yield str(e)
    #else:
        #yield str(child.exitstatus)
    finally:
        if child:
            child.close()
    return

def main():
    if len(sys.argv) < 2:
        cmd = r"ls -al ."
    else:
        cmd = sys.argv[1]
    
    #print "generator:"
    #for i in syncexec_generater(cmd,10):
    #    print i
    
    print "normal:"
    r = syncexec_timeout(cmd)
    print r
    print "success" if r else r.ret
    

if __name__ == '__main__':
    import sys
    main()
