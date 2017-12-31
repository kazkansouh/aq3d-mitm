#! /usr/bin/python

import sys
sys.path.append('..')

import socket
import threading
import time

from aq3dmitm import main
import samplepackets

test_shutdown = False
noout = False

def write(s) :
    global noout
    if not noout :
        print s

def server_process(cli_sock) :
    """
    Main loop that represents the remote server. Just hexdumps all tcp
    frames received.
    """
    global test_shutdown
    cli_sock.settimeout(0.01)
    while not test_shutdown :
        try :
            data = cli_sock.recv(1024)
            if len(data) > 0 :
                write("Mock server received packet: {}".format(data.encode("hex")))
            else :
                test_shutdown = True
        except socket.timeout :
            pass
        except socket.error :
            traceback.print_exc()
            write("Test server failed to read from socket")
            test_shutdown = True

def server_main(port) :
    global test_shutdown
    svr_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svr_sock.bind(("localhost", port))
    svr_sock.listen(1)
    svr_sock.settimeout(0.1)
    while not test_shutdown :
        try :
            cli_sock, addr = svr_sock.accept()
            server_process(cli_sock)
            break
        except socket.timeout :
            pass
        except socket.error :
            break
    write("Test server shut down")

def client(pkts, host, port) :
    """
    Sends packets over a tcp connection identified by host and port
    """
    global test_shutdown
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to server and send data
        s.connect((host, port))
    except socket.error as e :
        write(str(e))
        test_shutdown = True
        return
    try :
        for pkt in pkts :
            data = "".join(map(chr,pkt))
            write("Test client sending packet to proxy: {}".format(data.encode("hex")))
            s.sendall(data)
            time.sleep(0.1)
    except socket.error :
        write("Test client received an error while sending data")
    # the proxy will drop all links when client closes connection, so
    # wait a short time
    time.sleep(1)
    s.close()

if __name__ == "__main__" :
    write("Running in test mode")

    tid_svr = threading.Thread(target=server_main, args=(5589,))
    tid_svr.start()

    tid_proxy = threading.Thread(target=main.main, args=("localhost", 5588, "localhost", 5589, False))
    tid_proxy.start()

    write("Preparing injector:")
    for i in range(2,-1,-1) :
        print "..{}".format(i)
        time.sleep(1)

    write("Starting packet injection")
    # comment the following line to see more debug information
    noout = True
    client(samplepackets.packet_bytes, "localhost", 5588)

    time.sleep(1)
    main.shutdown = True
    test_shutdown = True
    noout = False

    write("Cleanup test")
    tid_svr.join()
    write("Joined test server")
    tid_proxy.join()
    print "Joined proxy"
