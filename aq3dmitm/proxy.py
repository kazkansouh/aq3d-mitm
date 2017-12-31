from aq3dmitm.util import *
from aq3dmitm.aq3d.commands import *
from aq3dmitm.aq3d.sensitive import key

import threading
import json
import socket
import collections
from time import sleep
import traceback

class Context :
    def __init__(self, act, unk_act) :
        "create empty context"
        self.accum = []
        self.action = act
        self.action_unknown = unk_act

    def processRawPacket(self, raw) :
        "processes raw packets read from a tcp frame"
        self.accum = self.accum + map(ord,raw)

        idx = contains(self.accum, 0x00)
        while idx >= 0 : # idx should never == 0
            bytes = encdec(key, self.accum[:idx])

            cmd = None
            try :
                cls = Type(bytes[0])
                cmd = subtype(cls)(bytes[1])
            except :
                print "not supported command: " + str(bytes[0]) + "/" + str(bytes[1])
                if not self.action_unknown(bytes) :
                    return

            if cmd != None :
                # uncomment to print the raw packet before parsing
                # print "raw: " + "".join(map(chr,bytes[2:]))
                jsonpkt = json.loads("".join(map(chr,bytes[2:])))

                if not self.action(jsonpkt) :
                    return

            self.accum = self.accum[idx + 1:]
            idx = contains(self.accum, 0x00)

class Bind() :
    """
    Binds two sockets together, from the output of one to the input of
    another.

    call start() to start the threads running.
    """
    def __init__(self, logger, sock_a, sock_b, tag) :
        self.sock_a = sock_a
        self.sock_b = sock_b
        self.close = False
        self.sock_a.settimeout(0.1)
        self.logger = logger
        self.outqueue = collections.deque()
        self.tid_out = threading.Thread(target=Bind.send, args=(self,), name=tag + "_out")
        self.tid_in = threading.Thread(target=Bind.bind, args=(self,), name=tag + "_in")

    def start(self, processPacket) :
        """
        Starts threads running and sets the raw packet processor. The
        processor should make use of the self.outqueue to send
        messages.
        """
        self.processPacket = processPacket
        self.tid_out.start()

    def write(self, s, level=LogLevel.Medium) :
        """Write a log message"""
        self.logger("Bind: {}".format(s), level)

    def send(self) :
        """
        Runs in a separate thread (and starts the input thread), reads from
        output queue and sends data.  To send data, enqueue it to
        "outqueue" with "append".
        """
        self.tid_in.start()
        while not self.close :
            try :
                self.sock_b.sendall(self.outqueue.popleft())
            except IndexError :
                sleep(0.01) # 10ms
            except socket.error :
                self.write("Socket write error", LogLevel.Low)
                self.shutdown()
            except :
                self.write("Unknown error while sending data", LogLevel.High)
                self.shutdown()
        self.write("send thread exit", LogLevel.Low)

    def bind(self) :
        """
        Generic function to read from one socket and call a processing
        function for the frame.
        """
        while not self.close :
            try :
                data = self.sock_a.recv(1024)
                if len(data) > 0 :
                    self.processPacket(data)
                else :
                    self.write("binder received 0 length data", LogLevel.Low)
                    self.shutdown()
            except socket.timeout :
                pass
            except socket.error :
                traceback.print_exc()
                self.write("Failed to read from socket", LogLevel.Medium)
                self.shutdown()
        self.write("bind thread exit", LogLevel.Low)

    def shutdown(self) :
        if not self.close :
            self.close = True
            self.write("Shutting down binder", LogLevel.Medium)
            if threading.current_thread().ident != self.tid_out.ident :
                self.tid_out.join()
            if threading.current_thread().ident != self.tid_in.ident :
                self.tid_in.join()
            self.write("Joined threads", LogLevel.Low)

import re
import random

class Proxy() :
    """
    Implements required logic to bind two sockets with mitm capabilities.
    """

    def __init__(self, remotehost, remoteport) :
        self.finished = False
        self.log = open(str(hex(id(self))) + ".log", 'w')
        self.filter = None
        self.spellid = 0
        self.entities = {}
        self.playerpos = {"posZ":0, "posX":0 ,"posY":0}
        self.remotehost = remotehost
        self.remoteport = remoteport

    def write(self, s, level=LogLevel.Medium) :
        """Write a log message"""
        if level >= LogLevel.Medium :
            print "{}: {}".format(str(hex(id(self))), s)
        if self.log != None and level >= LogLevel.Low :
            self.log.write("{}\n".format(s))

    def shutdown(self) :
        if not self.finished :
            self.finished = True
            self.write("Shuttingdown binders", LogLevel.Low)
            self.ctos.shutdown()
            self.stoc.shutdown()

            self.write("Closing sockets", LogLevel.Low)
            try :
                self.client_sock.shutdown(socket.SHUT_RDWR)
                self.client_sock.close()
            except socket.error :
                pass
            try :
                self.proxy_sock.shutdown(socket.SHUT_RDWR)
                self.proxy_sock.close()
            except socket.error :
                pass
            self.write("Closed sockets", LogLevel.Medium)
            if self.log != None :
                self.log.flush()
                self.log.close()
                self.log = None

    def buildCommand(self, j=None, msg=None, cls=0, cmd=0) :
        """
        Constructs a frame that can be sent, i.e. applies the encdec
        function and relavant header bytes.

        Returns the raw byte stream and the json dumped to string
        """
        if not j == None :
            msg = json.dumps(j, separators=(',', ':'))
            pkt = chr(j["type"]) + chr(j["cmd"]) + msg
        else :
            pkt = chr(cls) + chr(cmd) + msg
        pkt = "".join(map(chr,encdec(key, map(ord,pkt))))
        return (pkt + chr(0), msg)

    def processFrame(self, dir, queue, j, acts) :

        """
        Writes the json object back to destination socket. This function
        is covered by the try clause of the bind function. Non
        critical errors should be handled here.

        """
        try :
            (pkt, msg) = self.buildCommand(j)

            # can assume these will succeed when the processFrame is called
            cls = Type(j["type"])
            cmd = subtype(cls)(j["cmd"])

            l = LogLevel.Low
            if dir == "ctos" or (not self.filter == None and re.search(self.filter, msg)) :
                l = LogLevel.Medium
            self.write("{}: [{: >16} {: <22}] {}".format(dir, str(cls), str(cmd), msg), l)

            queue.append(pkt)

            if acts.has_key((cls,cmd)) :
                acts[(cls,cmd)](j)
        except KeyError :
            traceback.print_exc()
            self.shutdown()
            return False
        return True

    def processUnknownFrame(self, dir, queue, d) :
        """
        Copies the unknown data to the output channel to maintain proxy function.

        """
        try :
            self.write("{}: unknown frame: {}".format(dir, "".join(map(chr,d)).encode("hex")))
            pkt = "".join(map(chr,encdec(key, d)))
            pkt = pkt + chr(0)

            queue.append(pkt)
        except KeyError :
            traceback.print_exc()
            self.shutdown()
            return False
        return True

    def spellRequest(self, spellid=1, targetid="") :
        """
        Inject a spell request into the server. An example of the command is as follows:
          {"cmd":1,"spellTemplateID":11,"targetIDs":[-2144900295],"targetTypes":[2],"type":12,"ID":88}
        """
        self.spellid = self.spellid + 1
        cmd = '{{"cmd":1,"spellTemplateID":{},"targetIDs":[{}],"targetTypes":[2],"type":12,"ID":{}}}'.format(
            spellid,
            targetid,
            self.spellid
        )

        self.write("injecting command {} to server".format(cmd), LogLevel.High)
        (pkt, msg) = self.buildCommand(msg=cmd, cls=12, cmd=1)
        self.ctos.outqueue.append(pkt)

    def playerMove(self, vec) :
        """
        Inject a Type.Move CmdMove.Full command to position the player on the map.

        This command should be used with caution, as it does not
        update the position in the client.
        """
        cmd = '{{"rotY":{},"cmd":1,"posZ":{},"posX":{},"posY":{},"type":1}}'.format(
            random.randint(0,355),
            vec["posZ"],
            vec["posX"],
            vec["posY"]
        )
        self.write("injecting command {} to server".format(cmd), LogLevel.High)
        (pkt, msg) = self.buildCommand(msg=cmd, cls=1, cmd=1)
        self.ctos.outqueue.append(pkt)
        self.updatePosition(vec)

    def updateFilter(self, j) :
        """
        Implements a handle that is called for the following client to server command:
          Type.Login, CmdLogin.Token
        This has an example payload of:
          {"token":"JKIUYGGQIJDFLFKKDKDK","cmd":1,"type":3,"id":1000000}
        Here, the id is the unique id of the player and is used to build a regex to
        filter the commands by to only display relevant payloads on the terminal.
        """
        self.filter = re.compile(str(j["id"]))

    def updateSpellID(self, j) :
        """
        Implements a handle that is called for the following client to server command:
          Type.Combat CmdCombat.SpellRequest
        This has an example payload of:
          {"cmd":1,"spellTemplateID":11,"targetIDs":[-2144900295],"targetTypes":[2],"type":12,"ID":88}
        Here, the id is a strictly increasing unique id of the spell. Its used by the
        server to handle the case where multiple requests are received in quick succession.
        """
        try :
            self.spellid = j["ID"]
        except KeyError :
            self.write("error in message format of spell request, please check", LogLevel.High)

    def updatePosition(self, j) :
        """
        Implements a handle that is called for the following client to server command:
          Type.Move CmdMove.Full
        This has an example payload of:
          {"rotY":319,"cmd":1,"posZ":248.511581,"posX":172.198135,"posY":11.0850611,"type":1}
        """
        try :
            self.playerpos["posZ"] = j["posZ"]
            self.playerpos["posX"] = j["posX"]
            self.playerpos["posY"] = j["posY"]
        except KeyError :
            self.write("error in message format of player move full, please check", LogLevel.High)

    def registerEntity(self, entity) :
        """
        Registers an entity in the internal database of entities
        """
        self.entities[entity["ID"]] = entity
        self.write("registered entity {} of type {} ({})".format(entity["ID"], entity["name"], entity["NPCID"]), LogLevel.Medium)

    def deregisterEntity(self, eid) :
        """
        Deregisters an entity in the internal database of entities
        """
        if self.entities.has_key(eid) :
            del self.entities[eid]
            self.write("de-registered entity {}".format(eid), LogLevel.Low)

    def enterCell(self, entityids, j) :
        """
        Implements a handle that is called for the following server to client command:
          Type.Cell CmdCell.Join
        The example is too large to place here, but is transmitted on change of map and
        contains details such as: NPCs active in the new map.
        """
        self.entities = {}
        self.write("cleared entities", LogLevel.Low)
        try :
            for e in j["entities"] :
                for eid in entityids :
                    if e["type"] == 2 and eid == e["NPCID"] :
                        self.registerEntity(e)
                        break
        except KeyError :
            self.write("error in message format of cell join, please check", LogLevel.High)
            traceback.print_exc()

    def npcSpawn(self, entityids, j) :
        """
        Implements a handle that is called for the following server to client command:
          Type.NPC CmdNPC.Spawn
        This is called when a entity spawns and might need to be added to the database.
        """
        try :
            for eid in entityids :
                if eid == j["entity"]["NPCID"] :
                    self.registerEntity(j["entity"])
                    break
        except KeyError :
            self.write("error in message format of npc spawn, please check", LogLevel.High)

    def npcDespawn(self, j) :
        """
        Implements a handle that is called for the following server to client command:
          Type.NPC CmdNPC.Despawn
        This is called when a entity is removed from the map and might need to be removed
        from the database.
        """
        try :
            self.deregisterEntity(j["ID"])
        except KeyError :
            self.write("error in message format of npc despawn, please check", LogLevel.High)

    def npcMove(self, j) :
        """
        Implements a handle that is called for the following server to client command:
          Type.NpcMove CmdNpcMove.Path
        This is called when a entity moves.
        """
        try :
            if self.entities.has_key(j["ID"]) :
                vec = j["Path"][-1]
                e = self.entities[j["ID"]]
                e["posZ"] = vec["z"]
                e["posX"] = vec["x"]
                e["posY"] = vec["y"]
        except KeyError :
            self.write("error in message format of npc move path, please check", LogLevel.High)

    def getDrops(self, lootids, j) :
        """
        Implements a handle that should be called for the following server to client command:
          Type.Loot CmdLoot.AddDropBag
        Example too large to put here, but details the items in the drop bag and indicates
        the entity has been removed from the map.
        """
        try :
            self.deregisterEntity(j["Loot"]["ID"])
            for item in j["Loot"]["Items"] :
                for id in lootids :
                    if id == item["ID"] :
                        self.write("found {} items of type {} ({}) in loot bag".format(item["Qty"], item["Name"], item["ID"]), LogLevel.High)
                        cmd = '{{"ItemID":{},"cmd":3,"LootID":{},"type":16,"Qty":{}}}'.format(item["ID"], j["Loot"]["ID"], item["Qty"])
                        self.write("injecting command {} to server".format(cmd), LogLevel.High)
                        (pkt, msg) = self.buildCommand(msg=cmd, cls=16, cmd=3)
                        self.ctos.outqueue.append(pkt)
        except KeyError :
            traceback.print_exc()
            self.write("missing items in payload, please check format", LogLevel.High)

    def attack(self) :
        """
        First attempt at attacking, lists monsters that are within a 4 unit range
        """
        candidate = None
        candidate_distance = 0xFFFFFFF
        try :
            for e in self.entities :
                distance = distance3d(self.entities[e], self.playerpos)
                if distance <= 4 :
                    self.write("canditate for attack {} at distance of {}".format(e, distance))
                    if distance < candidate_distance :
                        candidate = e
                        candidate_distance = distance
            if candidate != None :
                self.write("selected target id {} of type {} for attacking".format(candidate, self.entities[e]["name"]))
                # self.playerMove(self.entities[e])
                self.spellRequest(11, candidate)
            else :
                self.write("no targets identified within a distance of {}".format(4))
        except KeyError :
            # its possible the entity is removed during the execution of the function
            pass

    def run(self, client_sock) :
        """
        Entry point for client thread.
        """
        self.client_sock = client_sock

        self.proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            self.proxy_sock.connect((self.remotehost, self.remoteport))
            self.write("remote connect", LogLevel.Medium)
        except socket.error :
            self.write("failed to remote connect to {}:{}".format(self.remotehost, self.remoteport), LogLevel.High)
            self.proxy_sock = None
            self.finished = True
            self.client_sock.shutdown(socket.SHUT_RDWR)
            self.client_sock.close()
            return

        self.ctos = Bind((lambda s, l: self.write("ctos: {}".format(s), l)),
                         self.client_sock,
                         self.proxy_sock,
                         "ctos")
        self.stoc = Bind((lambda s, l: self.write("stoc: {}".format(s), l)),
                         self.proxy_sock,
                         self.client_sock,
                         "stoc")

        ctos_ctx = Context(
            lambda j : Proxy.processFrame(self,
                                          "ctos",
                                          self.ctos.outqueue,
                                          j,
                                          {
                                              (Type.Login, CmdLogin.Token): lambda j: self.updateFilter(j),
                                              (Type.Combat, CmdCombat.SpellRequest): lambda j: self.updateSpellID(j),
                                              (Type.Move, CmdMove.Full): lambda j: self.updatePosition(j),
                                              (Type.Move, CmdMove.Synch): lambda j: self.updatePosition(j),
                                          }),
            lambda d : Proxy.processUnknownFrame(self, "ctos", self.ctos.outqueue, d))

        stoc_ctx = Context(
            lambda j : Proxy.processFrame(self,
                                          "stoc",
                                          self.stoc.outqueue,
                                          j,
                                          {
                                              (Type.Loot, CmdLoot.AddDropBag): lambda j: self.getDrops([1489, 1490], j), # Fangs (1489) and Blood Fangs (1490)
                                              (Type.Cell, CmdCell.Join): lambda j: self.enterCell([718], j), # Look for Ghoul Minion (718)
                                              (Type.NPC, CmdNPC.Spawn): lambda j: self.npcSpawn([718], j), # Look for Ghoul Minion (718)
                                              (Type.NPC, CmdNPC.Despawn): lambda j: self.npcDespawn(j),
                                              (Type.NpcMove, CmdNpcMove.Path): lambda j: self.npcMove(j)
                                          }),
            lambda d : Proxy.processUnknownFrame(self, "stoc", self.stoc.outqueue, d))

        self.ctos.start(lambda d: ctos_ctx.processRawPacket(d))
        self.stoc.start(lambda d: stoc_ctx.processRawPacket(d))
        # small delay to allow the second thread to be started in the
        # above calls
        sleep(0.1)

        self.write("running!", LogLevel.High)

        tids = [self.ctos.tid_in, self.ctos.tid_out,
                self.stoc.tid_in, self.stoc.tid_out]

        while True :
            for tid in tids :
                if not tid.is_alive() :
                    self.write("Controlled shutdown initiated by {}".format(tid.name), LogLevel.Low)
                    self.shutdown()
                    return
            sleep(0.01)
