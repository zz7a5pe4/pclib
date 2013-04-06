#!/usr/bin/python

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler
import SimpleHTTPServer
import traceback,sys,os,select,socket
import SocketServer
import urlparse
import json
from shcmd import syncexec_generater as RUNNING


class HTTPServer(SocketServer.ForkingTCPServer):

    allow_reuse_address = 1
    def server_bind(self):
        """Override server_bind to store the server name."""
        SocketServer.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port



def chunkedwrap(oldstr):
    if oldstr:
        l = len(oldstr)
        ret = ""
        ret += "{0}\r\n".format(hex(l)[2:])
        ret += "{0}\r\n".format(oldstr)                                                                                                                      
    else:
        ret = "0\r\n\r\n"
    return ret


class ChunkedHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    _cmdmaps={"who": "w",}
    def init(self, CMDS):
        if CMDS:
            for i in CMDS.keys():
                self._cmdmaps[i] = CMDS[i]
        
    def chunkedheader(self):
        self.protocol_version="HTTP/1.1"
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.send_header('Transfer-Encoding', "chunked")
        self.end_headers()


    def do_GET(self):
        try:
            cmd = self.path[1:]
            if cmd in self._cmdmaps.keys(): 
                self.chunkedheader()
                self.wfile.write(chunkedwrap(self._cmdmaps[cmd]))
                self.wfile.write(chunkedwrap(None))
            else:
                SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        except:
            print("unknown error")
            traceback.print_exc(file=sys.stdout)


    def do_POST(self):
        try:
            cmd = self.path[1:] 
            if cmd in self._cmdmaps.keys(): 
                self.chunkedheader()
                self.processcmd(self._cmdmaps[cmd])
                self.wfile.write(chunkedwrap(None))
            else:
                self.wfile.write("not supported" + cmd)
        except:
            print("unknown error")
            traceback.print_exc(file=sys.stdout)
        return

    def processcmd(self, fullcmd):
        msg="<p>" + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + "</p>"
        self.wfile.write(chunkedwrap(msg))

        x = RUNNING(fullcmd)
        for i in x:
            r = chunkedwrap("{0}</br>".format(i))
            self.wfile.write(r)
        self.wfile.write(chunkedwrap("<b>End of Cmd</b>")) 

def main():
    try:
        server = HTTPServer(('', 8002), ChunkedHandler)
        print 'start httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'stop server'
        server.socket.close()

if __name__ == '__main__':
    main()
