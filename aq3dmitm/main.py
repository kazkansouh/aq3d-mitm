#! /usr/bin/python

from aq3dmitm.proxy import Proxy

import socket
import os
import sys
import threading
from time import sleep

shutdown = False

def server_loop(proxies, threads, svr_sock, remoteaddress, remoteport) :
    """
    Loop that listens for client connections and spawns threads to process
    each new connection from an aq3d client.
    """
    svr_sock.settimeout(0.1)
    while True :
        # loop is broken when the svr_sock is closed, and after a timeout
        # event has occoured. on next attempt at the "acceept" method,
        # an exception is raised.
        try :
            cli_sock, addr = svr_sock.accept()
            print "Proxy connection received from: " + str(addr)
            p = Proxy(remoteaddress, remoteport)
            proxies.append(p)
            tid = threading.Thread(target=Proxy.run,args=(p, cli_sock))
            threads.append(tid)
            tid.start()
        except socket.timeout :
            pass
        except socket.error :
            break
    print "server shut down"

def main(bindaddr, localport, remoteaddress, remoteport, interactive=True) :
    """
    Entry point.
    """
    global shutdown
    proxies = []
    threads = []

    svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svr_sock.bind((bindaddr, localport))
    svr_sock.listen(10)

    tid_svr = threading.Thread(target=server_loop, args=(proxies, threads, svr_sock, remoteaddress, remoteport))
    threads.append(tid_svr)
    tid_svr.start()

    print "Proxy Server listening on {}:{}".format(bindaddr, localport)

    try :
        while not shutdown :
            if interactive :
                line = sys.stdin.readline()
                for p in proxies :
                    p.attack()
            else :
                sleep(0.01)

    except KeyboardInterrupt :
        print "Ctrl-C caught"
    finally :
        print "Proxy Shutting down"
        svr_sock.close()
        for p in proxies :
            p.shutdown()
        print "Proxy joining threads (cleanup)"
        for tid in threads :
            tid.join()
