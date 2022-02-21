import hashlib
import time
import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
import requests

token = "hogehoge"
global_level = 0
def main():
    print("名前を英語で入力してください")
    name = input()
    print("float型のパラメータ名を入力してください：defaultは[lovense]")
    param_name = input()
    if param_name == "":
        param_name = "lovense"

    response = requests.post('https://api.lovense.com/api/lan/getQrCode',
                             data={
                                 "token": token,
                                 "uid": name,
                                 "uname": name,
                                 "utoken": hashlib.md5(name.encode('utf-8')).hexdigest()
                             })
    print(response.text)  # HTTPのステータスコード取得
    print("ctrl + Cとかを押すとおわります")
    osc_server_up(name, param_name)



def lovense_enable(unused_addr, args, value):
    # print("receive:", args[0], value)
    global global_level
    level = int(value * 20)

    if level != global_level:
        print(level)
        global_level = level
        response = requests.post('https://api.lovense.com/api/lan/v2/command',
                                 data={
                                     "token": token,
                                     "uid": args[0],
                                     "command": "Function",
                                     "action": "Stop",
                                     "timeSec": "60",
                                     "utoken": hashlib.md5(args[0].encode('utf-8')).hexdigest()
                                 })

        response = requests.post('https://api.lovense.com/api/lan/v2/command',
                                 data={
                                     "token": token,
                                     "uid": args[0],
                                     "command": "Function",
                                     "action": "Vibrate:" + str(level),
                                     "timeSec": "60",
                                     "utoken": hashlib.md5(args[0].encode('utf-8')).hexdigest()
                                 })


def osc_server_up(name, param_name):
    parser = argparse.ArgumentParser()
    parser.add_argument("---ip", default="127.0.0.1", help="The ip to listem on")
    parser.add_argument("---port", type=int, default=9001, help="The port to listen on")

    args = parser.parse_args()
    dispatchers = dispatcher.Dispatcher()
    dispatchers.map("/avatar/parameters/" + param_name, lovense_enable, name)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatchers)
    print("Serving on {}", format(server.server_address))
    server.serve_forever()


if __name__ == "__main__":
    main()
