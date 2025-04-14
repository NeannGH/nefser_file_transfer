import socket, sys, os, hashlib

# Banner
helpbanner ="""
┌────────────────────────────────────────────────────────────┐
│     ███╗   ██╗███████╗███████╗███████╗███████╗██████╗      │
│     ████╗  ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔══██╗     │
│     ██╔██╗ ██║█████╗  █████╗  ███████╗█████╗  ██████╔╝     │
│     ██║╚██╗██║██╔══╝  ██╔══╝  ╚════██║██╔══╝  ██╔══██╗     │
│     ██║ ╚████║███████╗██║     ███████║███████╗██║  ██║     │
│     ╚═╝  ╚═══╝╚══════╝╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝     │                      
│════════════════════════════════════════════════════════════│
│Command syntax: s.py [arg] [value]                          │
│--help : Show this help menu.                               │
│-recv [file/path] :Open a TCP server to receive a file.     │
│-send [file/path] :Open a TCP server to send a file.        │
│-i [IP/FQDN] :Set the IP/FQDN used to send/receive data.    │
│-p [port] :Set the network port used to send/receive data.  │                        
│-t [sec] :Set the listening duration to receive data.       │
│════════════════════════════════════════════════════════════│
│If no arguments are given, the default option is:           │
│-recv nefser.bytes -i 0.0.0.0 -p 8080 -t 10                 │
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│                       
│Command ex: s.py -recv file.txt -p 5050 -t 50               │
│Command ex: s.py -send file.txt -127.0.0.1 -p 5050          │
└────────────────────────────────────────────────────────────┘
"""

# Progress barr function
def progress_barr(received, total):

    progress = int((received / total) * 100)
    blocks = int((received / total) * 30)
    barr = '█' * blocks + '-' * (30 - blocks)
    print(f"\r[#]> [{barr}]{progress}%", end='', flush=True)

# Hash function
def check_integrity(path):

    file_hash = hashlib.new('md5')
    with open(path, 'rb') as file:
        while True:
            data = file.read(8192) # Read in blocks of 8192 bytes, useful for not consuming RAM by reading all the bytes of the file at once.
            if not data:
                break
            file_hash.update(data)
        return file_hash.hexdigest()

# Main program
class Nefser:

    def __init__(self,operation_type= '-recv' ,file_io='nefser.bytes', ip_fqdn='0.0.0.0',port=8080, timeouts=10):

        self.ip_fqdn = ip_fqdn
        self.port = port
        self.timeouts = timeouts
        self.file_io = file_io
        self.operation_type = operation_type

        # Show socket current settings
        # print(f"[#]> Current settings: {self.operation_type.strip('-').upper()}|{self.ip_fqdn}:{self.port}|{self.file_io}|{self.timeouts}")

    # Receive method
    def start_recv(self):

        # Opening network socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((self.ip_fqdn,self.port))
            s.settimeout(self.timeouts)
            s.listen(1)
            print(f"[#]> TCP server listening on: {self.ip_fqdn}:{self.port}")
            conn, addr = s.accept()
            print(f"[#]> Connection received from: {addr[0]}:{addr[1]}")

        except TimeoutError:
            print(f"[#]> Listening timeout has been reached. Current Timeout: {self.timeouts}s")
            s.close()
            exit()

        except:
            print("[#]> Error creating socket. Check PERMISSIONS, DNS, IP/FQDN and PORT.")
            exit()

        # Receiving metadata
        filelength = int.from_bytes(conn.recv(5), byteorder='big') # Fist 5 bytes is always the file length (5bytes = 1 TB)
        originalfilehash = conn.makefile(mode='r',encoding='utf-8', newline='\n').readline().strip()  # Next 33 bytes is always the file hash + '\n' (33 bytes)

        # File exists validation
        if os.path.isfile(self.file_io): # If file exists, creates a new file with _copy_ as a prefix
            self.file_io = '_copy_' + self.file_io

        # Receiving data
        with open(self.file_io,'wb') as file:
            received_bytes = 0
            while received_bytes < filelength:
                msg = conn.recv(min(1024, filelength - received_bytes)) # Connection always receive the missing bytes
                if not msg:
                    print("\n[#]> Network error, could not receive all expected bytes.")
                    exit()

                file.write(msg)
                received_bytes += len(msg)
                progress_barr(received_bytes,filelength)

        # Integrity validation
        if check_integrity(self.file_io) != originalfilehash:
            print(f"\n[#]> Received file | MD5 Check status: {"\033[41m"}(Corrupted file){"\033[0m"}")
            conn.send('COR\n'.encode())

        elif check_integrity(self.file_io) == originalfilehash:
            print(f"\n[#]> Received file | MD5 Check status: {"\033[32m"}(Valid file){"\033[0m"}")
            conn.send('VAL\n'.encode())

        else:
            print(f"\n[#]> Received file | MD5 Check status: Unable to validate integrity")

    # Send method
    def start_send(self):

        # Opening network socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.connect((self.ip_fqdn,self.port))
            print(f"[#]> TCP client connecting on: {self.ip_fqdn}:{self.port}")

        except:
            print(f"[#]> Unable to connect to {self.ip_fqdn}:{self.port}")
            s.close()
            exit()

        try:
            filelength = os.path.getsize(self.file_io)
            originalfilehash = check_integrity(self.file_io)

        except:
            print("[#]> File not found.")
            exit()

        # Sending metadata
        s.send(filelength.to_bytes(5, byteorder='big')) #  5 bytes for File length send
        s.send((originalfilehash + '\n').encode())# 33 bytes for md5 hash + '\n' send

        # Sending file
        with open(self.file_io,'rb') as file:

            sent_bytes = 0
            while sent_bytes < filelength:
                data = file.read(1024)
                try:
                    s.sendall(data)
                except:
                    print("\n[#]> Network error, could not send all bytes.")
                    exit()

                sent_bytes += len(data)
                progress_barr(sent_bytes,filelength)

        # Receiving hash validation
        hashvalidation = s.recv(1024).decode().strip()

        if hashvalidation == 'COR':
            print(f"\n[#]> file sent successfully | MD5 Check status: {"\033[41m"}(Corrupted file){"\033[0m"}")

        elif hashvalidation == 'VAL':
            print(f"\n[#]> file sent successfully | MD5 Check status: {"\033[32m"}(Valid file){"\033[0m"}")

        else:
            print(f"\n[#]> file sent successfully | MD5 Check status: Unable to validate integrity")


# Command line execute
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
                            print("[#]> This option requieres a [file] specification.")
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
