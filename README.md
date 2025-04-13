
# 📁 nefser_file_transfer

**Nefser** is a command-line tool for fast and simple file transfer over a network using a single command.

---

## ✅ Requirements

- Python installed on both machines (sender and receiver)

---

## 🚀 How to Use

```bash
python3 nefser.py [argument] [value]
python3 nefser.py --help       # View the help menu
```

---

## ⚙️ Options

| Option               | Description                                             |
|----------------------|---------------------------------------------------------|
| `--help`             | Show the help menu                                      |
| `-recv [file/path]`  | Start a TCP server to receive a file                    |
| `-send [file/path]`  | Start a TCP client to send a file                       |
| `-i [IP/FQDN]`       | Set the IP address or FQDN for sending/receiving data  |
| `-p [port]`          | Set the network port to use                             |
| `-t [sec]`           | Set the listening time (in seconds) for receiving data |

---

## 📝 Default Behavior

If no arguments are provided, the default command is:

```bash
python3 nefser.py -recv nefser.bytes -i 0.0.0.0 -p 8080 -t 10
```

---

## 💡 Examples

Receive a file:

```bash
python3 nefser.py -recv file.txt -p 5050 -t 50
```

Send a file:

```bash
python3 nefser.py -send file.txt -i 127.0.0.1 -p 5050
```

---

## 🔒 Notes

- Make sure the receiving side is already listening before sending the file.
- Works on LAN and over the internet if port forwarding is properly configured.

---

Made by NeannGH
