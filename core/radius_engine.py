import os
import socket
import binascii
import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary

# --- WINDOWS COMPATIBILITY PATCH ---
import select
if not hasattr(select, "poll"):
    select.POLLIN = 1; select.POLLPRI = 2; select.POLLOUT = 4
    select.POLLERR = 8; select.POLLHUP = 16; select.POLLNVAL = 32
    class WindowsPollAdapter:
        def __init__(self): self.fd = None
        def register(self, fd, eventmask): self.fd = fd
        def modify(self, fd, eventmask): self.fd = fd
        def unregister(self, fd): self.fd = None
        def poll(self, timeout=None):
            if not self.fd: return []
            t = timeout / 1000.0 if timeout is not None else None
            r, w, x = select.select([self.fd], [], [], t)
            if r: return [(self.fd, select.POLLIN)]
            return []
    select.poll = WindowsPollAdapter

# --- DICTIONARY GENERATION ---
DICT_PATH = "dictionary"
if not os.path.exists(DICT_PATH):
    with open(DICT_PATH, "w") as f:
        f.write(
            "ATTRIBUTE User-Name 1 string\n"
            "ATTRIBUTE User-Password 2 string\n"
            "ATTRIBUTE NAS-IP-Address 4 ipaddr\n"
            "ATTRIBUTE Reply-Message 18 string\n"
            "ATTRIBUTE State 24 octets\n"
        )

class RadiusEngine:
    def __init__(self, server_ip, secret, nas_ip):
        self.server_ip = server_ip
        self.secret = secret.encode('utf-8') if isinstance(secret, str) else secret
        self.nas_ip = nas_ip
        self.client = Client(server=self.server_ip, secret=self.secret, dict=Dictionary(DICT_PATH))
        self.client.timeout = 15

    def transmit_auth(self, username, password_or_token, state_hex=None):
        logs = []
        logs.append({"color": "c-gray", "msg": "[DEBUG] Assembling Access-Request (Packet Code: 1)..."})
        
        req = self.client.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username)
        req["User-Password"] = req.PwCrypt(password_or_token)
        req["NAS-IP-Address"] = self.nas_ip

        if state_hex:
            logs.append({"color": "c-gray", "msg": f"[DEBUG] Appending Session State ID: 0x{state_hex[:16]}..."})
            req["State"] = binascii.unhexlify(state_hex)

        logs.append({"color": "c-cyan", "msg": f"[TX] -> Transmitting Payload to UDP {self.server_ip}:1812..."})

        try:
            reply = self.client.SendPacket(req)
            return self._process_reply(reply, logs)
        except Exception as e:
            logs.append({"color": "c-red", "msg": f"[FATAL] Transmission Error: {str(e)}"})
            return {"status": "error", "logs": logs}

    def _process_reply(self, reply, logs):
        if reply.code == pyrad.packet.AccessAccept:
            logs.append({"color": "c-magenta", "msg": "[RX] <- Received Packet (Code: 2 / Access-Accept)"})
            logs.append({"color": "c-green", "msg": "[SUCCESS] 200 OK - ZTAA Access Granted."})
            return {"status": "success", "logs": logs}

        elif reply.code == pyrad.packet.AccessChallenge:
            logs.append({"color": "c-magenta", "msg": "[RX] <- Received Packet (Code: 11 / Access-Challenge)"})
            logs.append({"color": "c-yellow", "msg": "[WARN] IdP triggered Stateful MFA Challenge."})
            
            reply_msg = "MFA Challenge Required"
            if "Reply-Message" in reply:
                raw_msg = reply['Reply-Message'][0]
                reply_msg = raw_msg if isinstance(raw_msg, str) else raw_msg.decode('utf-8', errors='ignore')
                logs.append({"color": "c-gray", "msg": f"[RX-DATA] Reply-Message: '{reply_msg}'"})

            state_hex = ""
            if "State" in reply:
                raw_state = reply["State"][0]
                state_bytes = raw_state.encode('utf-8') if isinstance(raw_state, str) else raw_state
                state_hex = binascii.hexlify(state_bytes).decode('utf-8')

            return {"status": "challenge", "reply_msg": reply_msg, "state_hex": state_hex, "logs": logs}

        elif reply.code == pyrad.packet.AccessReject:
            logs.append({"color": "c-magenta", "msg": "[RX] <- Received Packet (Code: 3 / Access-Reject)"})
            logs.append({"color": "c-red", "msg": "[DENIED] 401 Unauthorized - Authentication Failed."})
            return {"status": "reject", "logs": logs}
            
        else:
            logs.append({"color": "c-red", "msg": f"[RX] <- Unknown Code: {reply.code}"})
            return {"status": "error", "logs": logs}