import os
import csv
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
    os.system("CloudflareST")
    ret = []
    with open(result_file, "r") as f:
        reader = csv.reader(f)
        for row in list(reader)[1:]:
            ret.append(f"{row[0]}:443#CFIP")
    return ret
    

if __name__ == "__main__":
    os.system('git pull origin main --no-ff') 
    default_ip = """icook.hk:443#HK
icook.tw:443#TW
8.218.207.169:443#HK
47.243.173.187:2083#HK
8.217.85.14:2083#HK
47.245.55.94:2083#JP
47.74.24.109:2053#JP
47.245.13.93:8443#JP
45.66.128.215:51357#JP
47.245.8.185:2096#JP
47.245.57.38:8443#JP""".split()
    yes_ip = get_cf_yes()
    test_ip = get_local_test()
    total = list(set(test_ip+yes_ip+default_ip))
    with open("./best-cf", "w") as handler:
        handler.write("\n".join(total))
    os.system('git commit -m "update" best-cf')
    os.system('git push origin main')
