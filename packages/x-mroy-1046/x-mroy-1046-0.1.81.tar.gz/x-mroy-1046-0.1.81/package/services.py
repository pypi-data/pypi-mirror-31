from socketserver import BaseRequestHandler, UDPServer
from socket import socket, AF_INET, SOCK_DGRAM
from socket import timeout
import time
import base64
import json
import sys
import os
from socketserver import BaseRequestHandler, UDPServer

import rsa
from package.libs import pubip_rsa
from package.libs import Rsa
from package.libs import Format, deFormat
from package.libs import loger
import package.oscmd as oscmd
from package.oscmd import Os
from package.oscmd import FileHandle
from package.daemon import Daemon

log = loger()
UDP_PORT = 60077
UDP_PORT_BAK = 60078

class DaemonServer(BaseRequestHandler):
    def handle(self):
        msg, self.sock = self.request
        resp = time.ctime()
        log.info(resp + " | %d len recv" % len(msg)  + str(self.client_address))
        self.just_go(msg)

    def reply(self, id, op, msg, decoder=''):
        if decoder == 'json' and isinstance(msg, dict):
            msg = json.dumps(msg)

        e = Format(msg, op=op, id=id, decoder=decoder)
        self.sock.sendto(e, self.client_address)

    def just_go(self, msg):
        recived_msg = deFormat(msg)
        id = recived_msg['id']
        op = recived_msg['op']
        from_id = recived_msg['from_id']
        msg = recived_msg['msg']
        if_decrypted = recived_msg['if_rsa']
        log.info(b"operating: " + op)
        if op == b"reg":
            self.reg(from_id, msg, if_decrypted)
        elif op == b'os':
            if msg.decode().count("::") > 0:
                cmd, arg = msg.decode("utf8").split("::", 1)
                m = 'Os'
            elif msg.decode().count("::") > 1:
                m, cmd, arg = msg.decode('utf8').split("::",2)
            else:
                arg = None
            self.os_run(from_id, cmd, arg, module=m)

        elif op == b'base':
            self.base_init(from_id)
        elif op == b'circle':
            circle = oscmd.ProxyCircle()
            if msg.decode().count("::") > 0:
                cmds = msg.decode().split("::")
                cmd = cmds.pop(0)
                r = getattr(circle, cmd)
                res = r(*cmds)
            else:
                r = getattr(circle, msg.decode().strip())
                res = r()
            s = {'result' : res}
            self.reply(from_id, "reply", s, decoder='json')


        elif op == b'reset':
            self.reset(from_id)

        elif op == b'check':
            o = Os()
            msgr = {}
            for i in ['python3', 'pip3', 'tor', 'proxychains', 'sslocal']:
                if o.check(i):
                    log.info("[o] -> " + i)
                    msgr[i] = True
                else:
                    log.info("[x] -> " + i)
                    msgr[i] = False
            self.reply(from_id, "reply", msgr, decoder='json')

        elif op == b'log':
            line = msg
            self.os_log(from_id, line)

        elif op == b'reinstall':
            if msg == 'main':
                os.popen("x-rexlay stop || pip3 uninstall -y x-mroy-1046 && pip3 install x-mroy-1046  --no-cache-dir && x-relay start ")
            elif msg == 'bak':
                os.popen("x-bak stop || pip3 uninstall -y x-mroy-1046 && pip3 install x-mroy-1046  --no-cache-dir && x-bak start ")

    def base_init(self, id):
        circle = oscmd.ProxyCircle()
        pids = circle.GetStatus()
        self.reply(id, "reply", pids, decoder='json')

    def reset(self, id):
        o = Os()
        self.reply(id, "reply", "reset to clear", decoder='str')
        o.Uninstall("tor")
        o.Uninstall("proxychains")

    def reg(self,id, msg, if_decrypted):
        log.info("if pass load key : " + str(if_decrypted))
        if not if_decrypted:
            pubip_rsa.import_key(msg)
            log.info("reply" + str(self.client_address))
            server_pub = pubip_rsa.export_key()
            self.reply(id, "pub_key", server_pub, decoder='base64')

    def os_run(self, id,command, args, module='Os'):
        if hasattr(oscmd, module):
            M = getattr(oscmd, module)
        else:
            M = Os
        os_controller = M()
        if hasattr(os_controller, command):
            c = getattr(os_controller, command)
            if args == None:
                res = {'result': c()}
            else:
                res = {'result': c(args)}
            self.reply(id, "reply", res, decoder='json')
        else:
            self.reply(id, "reply", "not found method" + command, decoder='str')

    def exchange_pub(self, ip):
        b = Bitter(ip)
        b.regist_to_server()

    def get_pub(self, id, pub):
        k = pubip_rsa.export_key()
        pubip_rsa.import_key(k)
        self.sock.sendto(k, self.client_address)

    def os_log(self, id, line):
        os_controller = Os()
        res = os_controller.stdout(line)
        log.info(res)
        if isinstance(res, bytes):
            res = res.decode("utf8")
        self.reply(id, "reply", res, decoder='log')


class Bitter:
    def __init__(self, ip, port=UDP_PORT):
        self.ip = ip
        self.port = port

    def log(self, id=id, line=5):
        recv = self.sendto(str(line), op='log')
        return recv

    def upload(self, file, dest,id=None):
        if os.path.exists(file):
            f = FileHandle(b64=True)
            d = f.pack(file)
            return self.sendto("::".join(["Upload", d.decode("utf8"), dest]), op='os',id=id)

    def _sock_send(self, msg):
        for i in range(3):
            s = socket(AF_INET, SOCK_DGRAM)
            s.settimeout(5)
            try:
                s.sendto(msg, (self.ip, self.port))
                recv = s.recv(int(65535/2))
                return recv
            except timeout:
                continue
        raise TimeoutError("can not connect to ")

    def check(self):
        return self.sendto("", op='check')

    def install(self):
        return self.sendto("", op='base')

    def reload(self, main=True):
        if main:
            b = Bitter(self.ip, UDP_PORT_BAK)
            return b.sendto("main", op='reinstall')
        else:
            return self.sendto("bak", op="reinstall")


    def sendto(self, msg, id=None, op="msg"):
        if not id:
            for f in os.listdir(pubip_rsa.home):
                if f.startswith(self.ip):
                    id = f.split(".pub")[0].strip()
                    log.info("Found server's Pub key: " + id)
                    break

        if id == None and isinstance(msg, str):
            msg = msg.encode("utf8")
        s = socket(AF_INET, SOCK_DGRAM)
        msg = Format(msg, op=op, id=id)
        log.info("sending...")
        rec = self._sock_send(msg)
        log.info("send [ok]")
        res = deFormat(rec)
        s.close()
        return res

    def regist_to_server(self):
        k = pubip_rsa.export_key()
        try:
            id, op, msg, if_rsa = self.sendto(k, op='reg')
            msg = base64.b64decode(msg)
            pubip_rsa.import_key(msg)
        except Exception as e:

            return if_rsa


class DaemonSeed(Daemon):

    def run(self):
        serv = UDPServer(('0.0.0.0', UDP_PORT), DaemonServer)
        log.info("Start server: {}".format(UDP_PORT))
        serv.serve_forever()

class DaemonSeedBak(Daemon):
    def run(self):
        serv = UDPServer(('0.0.0.0', UDP_PORT_BAK), DaemonServer)
        log.info("Start bak server: {}".format(UDP_PORT_BAK))
        serv.serve_forever()


def test_key_reg(ip):
    b = Bitter(ip)
    k = pubip_rsa.export_key()
    return b.sendto(k, op='reg')

def main():
    app = DaemonSeed("/tmp/seed.pid")
    if len(sys.argv) < 2:
        log.error("need 'start' or 'stop'")
        sys.exit(0)
    if sys.argv[1] == 'start':
        app.start()
    elif sys.argv[1] == 'stop':
        app.stop()

def main_start_bak():

    app = DaemonSeed("/tmp/seed_bak.pid")
    if len(sys.argv) < 2:
        log.error("need 'start' or 'stop'")
        sys.exit(0)
    if sys.argv[1] == 'start':
        app.start()
    elif sys.argv[1] == 'stop':
        app.stop()

if __name__ == "__main__":
    app = DaemonSeed("/tmp/seed.pid")
    if len(sys.argv) < 2:
        s = UDPServer(('0.0.0.0', UDP_PORT), DaemonServer)
        log.info("Start server: {}".format(UDP_PORT))
        s.serve_forever()
    else:
        if sys.argv[1] == 'start':
            app.start()
        else:
            app.stop()
