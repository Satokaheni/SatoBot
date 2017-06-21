import re
import socket
import sys
import time
import pickle
import select
import twitch
import requests as rq
from datetime import datetime as date

# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.chat.twitch.tv"  # Hostname of the IRC-Server in this case twitch's
PORT = 80  # Default IRC-Port
CHAN = ''#"#" + sys.argv[1]  # Channelname = #{Nickname}

NICK = "sato_chat"  # Nickname = Twitch username
PASS = "oauth:u53r9or2zqejkdknxf5314cd2wpupz"  # www.twitchapps.com/tmi/ will help to retrieve the required authkey


# --------------------------------------------- End Settings -------------------------------------------------------


# --------------------------------------------- Start Functions ----------------------------------------------------
def send_pong(msg):
    con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))


def send_message(chan, msg):
    con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))


def send_nick(nick):
    con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))


def send_pass(password):
    con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))


def join_channel(chan):
    con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))


def part_channel(chan):
    con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))


def send_member():
    con.send(bytes('CAP REQ :twitch.tv/membership\r\n', 'utf-8'))
    con.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'utf-8'))
    con.send(bytes('CAP REQ :twitch.tv/commands\r\n', 'utf-8'))


# --------------------------------------------- End Functions ------------------------------------------------------


# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(message):
    m = ''
    i = 5
    m += message[4][1:] + ' '
    l = len(message)
    while i < l:
        m += message[i] + ' '
        i += 1
    return m


def parse_message(msg):
    if len(msg) >= 1:
        msg = msg.split(' ')
        options = {'!test': command_test,
                   '!asdf': command_asdf}
        if msg[0] in options:
            options[msg[0]]()


def get_list(self):
    viewers = []
    try:
        v = rq.get('http://tmi.twitch.tv/group/user/' + CHAN[1:] + '/chatters').json()

        for t in v['chatters']:
            for p in v['chatters'][t]:
                if p not in viewer_list:
                    viewer_list[p] = (t, [date.now()])
                    viewer_state[p] = 'IN'
                    viewer_sub[p] = False
                    timeout_num[p] = 0
                viewers.append(p)

        for p in viewer_list:
            if p not in viewers:
                if viewer_state[p] != 'OUT':
                    viewer_list[p][1].append(date.now())
                    viewer_state[p] = 'OUT'

    except Exception as e:
        print('List error: ' + str(e))


def get_sub(tags, name):
    tags = tags.split(';')
    status = False
    if 'subscriber' in tags[0]:
        status = True
    if name not in viewer_list:
        viewer_list[name] = ('viewers', [date.now()])
        viewer_state[name] = 'IN'
        viewer_sub[name] = status
    if not viewer_sub[name]:
        viewer_sub[name] = status


def ban_len(tags):
    tags = tags.split(';')
    length = -1
    for i in range(len(tags)):
        t = tags[i].split('=')
        try:
            if '@ban-duration' == t[0]:
                length = int(t[-1])
        except:
            break

    return length


# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Command Functions --------------------------------------------
def command_test():
    send_message(CHAN, 'testing some stuff')


def command_asdf():
    send_message(CHAN, 'asdfster')


# --------------------------------------------- End Command Functions ----------------------------------------------
viewer_list = {}
viewer_state = {}
viewer_sub = {}
timeout_num = {}
bans = []
last_message = {}
messages = []
labels = []
auth_label = []
sub_label = []
def create_socket():
    global con
    con = socket.socket()

def run(channel):
    con.connect((HOST, PORT))
    api = twitch.API('fhnt4blmgnt0m2l0tfe6myghpjuavxi')
    CHAN = '#' + channel
    send_pass(PASS)
    send_nick(NICK)
    send_member()
    join_channel(CHAN)
    follow_diff = 0
    print(str(date.now()) + ': Joined: ' + CHAN + '\'s channel')

    data = ""
    pinged = 0
    chat_logs = []
    channel_log = {}
    data_split = []
    errors = 0
    start = time.time()
    game = api.stream(CHAN[1:])['stream']
    if game:
        game = game['game']
    else:
        print('premature end')
        sys.exit(0)

    online = True

    while online:

        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            print(channel + ' data')
            print(sys.stdin.readlines())
            break

        try:

            data = data + con.recv(2048).decode('UTF-8')
            # print(data)
            data_split = re.split(r"[~\r\n]+", data)
            data = data_split.pop()

            for line in data_split:
                si = False
                try:
                    line = str.rstrip(line)
                    line = str.split(line)

                    if len(line) >= 1:
                        if line[0] == 'PING':
                            send_pong(line[1])

                    if len(line) > 2:
                        si = True
                        if line[2] == 'PRIVMSG':
                            user = get_sender(line[1])
                            message = get_message(line)
                            get_sub(line[0], user)
                            pinged = 0
                            last_message[user] = len(messages)
                            messages.append((user, message, game))
                            labels.append(0)
                            auth_label.append(viewer_list[user][0])
                            sub_label.append(viewer_sub[user])

                        if line[2] == 'CLEARCHAT':
                            name = line[-1][1:]
                            length = ban_len(line[0])
                            #						if length != -1:
                            #							print(name + ' banned for ' + str(length) + ' seconds')
                            #						else:
                            #							print(name + ' banned permanently')

                            if name not in timeout_num:
                                timeout_num[name] = 0
                            timeout_num[name] += 1
                            #						print(name + ' has been banned ' + str(timeout_num[name]) + ' times')
                            labels[last_message[name]] = 1
                            try:
                                bans.append((messages[last_message[name]], length, name,
                                             viewer_sub[name], timeout_num[name]))
                            except:
                                viewer_sub[name] = sub_label[last_message[name]]
                                bans.append((messages[last_message[name]], length, name,
                                             viewer_sub[name], timeout_num[name]))

                                #					if line[1] == 'HOSTTARGET':
                                #						print('HOSTTARGET: ' + str(line))


                                #				else:
                                #					print('ELSE')
                                #					print(line)
                                #					print(len(line))
                except Exception as e1:
                    print(line)
                    print(si)
                    print(len(line))
                    print('Inner Error: ' + str(e1))

                if (time.time() - start) >= 60:
                    call = api.stream(CHAN[1:])['stream']
                    if not call:
                        online = False
                    else:
                        game = call['game']
                    start = time.time()

            time.sleep(.1)
        except Exception as e:
            print(data_split)
            print(e)
        except socket.error:
            print("Socket died")

        except socket.timeout:
            print("Socket timeout")

        except IndexError:
            continue

        except UnicodeDecodeError:
            continue

        except:
            print('last exception')
            continue

    with open('data/' + CHAN[1:] + '_chat.txt', 'ab') as f:
        pickle.dump({'messages': messages, 'auth-labels': auth_label, 'sub-labels': sub_label,
                     'ban-labels': labels, 'ban-info': bans}, f, protocol=2)

    print(str(date.now()) + ': ' + CHAN + ' has gone offline')


