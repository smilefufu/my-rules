import os
import re
import csv
import base64
from urllib.parse import unquote
import requests


def get_cf_yes():
    colo_map = {
        "HKG": "HK",
        "SJC": "US",
        "LAX": "US"
    }
    url = "https://api.hostmonit.com/get_optimization_ip"
    payload = {"key":"iDetkOys"}
    headers =  {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-HK,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "content-type": "application/json",
        "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }
    res = requests.post(url, json=payload, headers=headers).json()
    ips = res.get("info", [])
    ret = []
    for ip in ips:
        ret.append(f"{ip['ip']}:443#{colo_map.get(ip['colo'], ip['colo'])}")
    return ret

def get_local_test():
    result_file = "./result.csv"
    if os.path.exists(result_file):
        os.remove(result_file)
    os.system("CloudflareST -sl 0.1 -p 3")
    ret = []
    with open(result_file, "r") as f:
        reader = csv.reader(f)
        for row in list(reader)[1:]:
            ret.append(f"{row[0]}:443#CFIP")
    return ret

def validate_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not 0 <= int(part) <= 255:
            return False
    return True

def validate_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

def parse_string(string):
    pattern = r'vless:\/\/.*?@([\d\.]+):(\d+).*?#(.*?)$'
    match = re.match(pattern, string)
    if match:
        ip = match.group(1)
        port = match.group(2)
        memo = match.group(3)
        if validate_ip(ip) and validate_port(port):
            return ip, int(port), memo
    return None

def get_happy_hour():
    txt = requests.get("https://url.happyhour.lol/Happyhour").text
    # base64 解码
    r = base64.b64decode(txt)
    sub = unquote(r.decode('utf-8'))
    ret = []
    for line in sub.split("\n"):
        r = parse_string(line)
        if r:
            ip, port, name = r
            if "mianfei" in name:
                name = "default"
            elif "关注" in name:
                name = "default2"
            if "-" in name:
                name = name.split("-")[-1]
            ret.append(f"{ip}:{port}#{name.replace(' ', '')}·")
    return ret

if __name__ == "__main__":
    os.system('git pull origin main --no-ff') 
    default_ip = []
    hp_ip = get_happy_hour()
    yes_ip = get_cf_yes()
    test_ip = []
    test_ip = get_local_test()
    total = list(set(hp_ip+test_ip+yes_ip+default_ip))
    with open("./best-cf", "w") as handler:
        handler.write("\n".join(total))
    os.system('git commit -m "update" best-cf')
    os.system('git push origin main')
