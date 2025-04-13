import socket, sys, os

helpbanner ="""
┌────────────────────────────────────────────────────────────┐
│ Command syntax: nefser.py [arg] [value]                    │
│════════════════════════════════════════════════════════════│
│--help : Show this help menu.                               │
│-recv [file/path] :Open a TCP server to receive a file.     │
│-send [file/path] :Open a TCP server to send a file.        │
│-i [IP/FQDN] :Set the IP/FQDN used to send/receive data.    │
│-p [port] :Set the network port used to send/receive data.  │                        
│-t [sec] :Set the listening duration to receive data.       │
│════════════════════════════════════════════════════════════│
│If no arguments are given, the default option is:           │
│ -recv nefser.bytes -i 0.0.0.0 -p 8080 -t 10                │
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                       
│Command ex: nefser.py -recv file.txt -p 5050 -t 50          │
│Command ex: nefser.py -send file.txt -127.0.0.1 -p 5050     │
└────────────────────────────────────────────────────────────┘
"""

def progress_barr(received, total):
    progress = int((received / total) * 100)
    blocks = int((received / total) * 30)
    barr = '█' * blocks + '-' * (30 - blocks)
    print(f"\r[{barr}]{progress}%", end='', flush=True)

class Nefser:

    def __init__(self,operation_type= '-recv' ,file_io='nefser.bytes', ip_fqdn='0.0.0.0',port=8080, timeouts=10):

        self.ip_fqdn = ip_fqdn
        self.port = port
        self.timeouts = timeouts
        self.file_io = file_io
        self.operation_type = operation_type

        print(f"Current socket settings: {self.ip_fqdn}:{self.port}|{self.timeouts}|{self.file_io}|{self.operation_type.strip('-').upper()}")

    def start_recv(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((self.ip_fqdn,self.port))
            s.settimeout(self.timeouts)
            s.listen(1)
            conn, addr = s.accept()
            print(f"TCP server listening on: {self.ip_fqdn}:{self.port}...")
            print(f"Connection received from: {addr[0]}:{addr[1]}")

        except TimeoutError:
            print(f"[#]> Listening timeout has been reached. Current Timeout: {self.timeouts}s")
            s.close()
            exit()

        except:
            print("[#]> Error creating socket. Check PERMISSIONS, DNS, IP/FQDN and PORT.")
            exit()

        filelength = int(conn.recv(5).decode()) # File name recv (5bytes = 1 TB)

        if os.path.isfile(self.file_io):
            self.file_io = '_copy_' + self.file_io

        with open(self.file_io,'wb') as file:
            received_bytes = 0
            while received_bytes < filelength:
                msg = conn.recv(1024)
                if not msg:
                    break
                file.write(msg)
                received_bytes += len(msg)
                progress_barr(received_bytes,filelength)

    def start_send(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((self.ip_fqdn,self.port))
            print(f"TCP server connecting on: {self.ip_fqdn}:{self.port}...")

        except:
            print(f"[#]> Unable to connect to {self.ip_fqdn}:{self.port}")
            s.close()
            exit()

        try:
            filelength = os.path.getsize(self.file_io)

        except:
            print("[#]> File not found.")
            exit()

        s.send(str(filelength).zfill(5).encode()) # File length send

        with open(self.file_io,'rb') as file:
            sent_bytes = 0
            while True:
                data = file.read(1024)
                if not data:
                    break

                s.sendall(data)
                sent_bytes += len(data)
                progress_barr(sent_bytes,filelength)

if __name__ == '__main__':

    args = {}

    if len(sys.argv[1:]) != 0:

        if any(e in ['-i','-p','-t','--help','-send','-recv'] for e in sys.argv[1:]):

            try:

                for i in sys.argv:

                    if i == '-i':

                        try:

                            if len(sys.argv[sys.argv.index('-i')+1].split('.')) == 4 and all(item.isnumeric() and int(item) >= 0 <= 255 for item in sys.argv[sys.argv.index('-i')+1].split('.')): # IPv4 Validation
                                args['ip_fqdn'] = str(sys.argv[sys.argv.index('-i')+1])

                            elif len(str(sys.argv[sys.argv.index('-i') + 1])) < 255 and '.' in str(sys.argv[sys.argv.index('-i')+1]):
                                args['ip_fqdn'] = socket.gethostbyname(str(sys.argv[sys.argv.index('-i')+1]))

                            else:
                                print("[#]> It's not a valid IP address or domain name.")
                                exit()

                        except (IndexError, ValueError, socket.gaierror):
                            print("[#]> This option requieres a valid [host] specification.")
                            exit()

                    elif i == '-p':

                        try:

                            if 1 < int(sys.argv[sys.argv.index('-p') + 1]) < 65535:
                                args['port'] = int(sys.argv[sys.argv.index('-p')+1])
                            else:
                                print("[#]> Reserved or invalid port.")
                                exit()

                        except (IndexError, ValueError):
                                print("[#]> This option requieres a valid [port] specification.")
                                exit()

                    elif i == '-t':

                        try:
                            args['timeouts'] = int(sys.argv[sys.argv.index('-t')+1])

                        except (IndexError, ValueError):
                            print("[#]> This option requieres a [timeout] specification.")
                            exit()

                    elif i == '-send' or i == '-recv':

                        try:
                            if not any(c in ["<", ">", "\"","\'","|","?","*"] for c in sys.argv[sys.argv.index(i)+1]):
                                args['file_io'] = str(sys.argv[sys.argv.index(i) + 1])
                                args['operation_type'] = str(i)
                            else:
                                print("[#]> You can't use special caracters.")
                                exit()

                        except IndexError:
                            print("This option requieres a [file] specification.")
                            exit()

                    elif i == '--help':
                        print(helpbanner)
                        exit()

                myclassobject = Nefser(**args)
                if '-send' in args.values():
                    myclassobject.start_send()

                else:
                    myclassobject.start_recv()

            except IndexError:
                print("[#]> Invalid argument. Use --help to see the options.")
                exit()
        else:
            print("[#]> Invalid argument. Use --help to see the options.")
            exit()
    else:
        myclassobject = Nefser()
        myclassobject.start_recv()
