from bs4 import BeautifulSoup # 解析网页
from fake_useragent import UserAgent # 随机生成User-agent
import chardet  # 有时会遇到编码问题 需要检测网页编码
import re, urllib.request, socket, time, random, csv, json
import pandas as pd


socket.setdefaulttimeout(10) #这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置


# 报头设置
def header(website):
    ua = UserAgent()
    headers = ("User-Agent", ua.random)
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    req = opener.open(website).read()
    return req


def get_proxy():
    # 读取网页
    proxy_api = 'http://www.xicidaili.com/nn'
    data = header(proxy_api).decode('utf-8')
    data_soup = BeautifulSoup(data, 'lxml')
    data_odd = data_soup.select('.odd')
    data_ = data_soup.select('.')
    # 解析代理网址 获取ip池（100个）
    ip,port = [],[]
    for i in range(len(data_odd)):
        data_temp = data_odd[i].get_text().strip().split('\n')
        while '' in data_temp:
            data_temp.remove('')
        ip.append(data_temp[0])
        port.append(data_temp[1])
    for i in range(len(data_)):
        data_temp = data_[i].get_text().strip().split('\n')
        while '' in data_temp:
            data_temp.remove('')
        ip.append(data_temp[0])
        port.append(data_temp[1])
    if len(ip) == len(port):
        proxy = [':'.join((ip[i],port[i])) for i in range(len(ip))]
        #print('成功获取代理ip与port！')
        return proxy
    else:
        print('ip长度与port长度不一致！')
proxy = get_proxy()
print(proxy)

def get_data(url, proxy_addr):
    num=random.randint(1,len(proxy_addr)-1)
    proxy = urllib.request.ProxyHandler({'http': proxy_addr[num]})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    headers={
        "User-Agent": UserAgent().random,
        'Cookie': 'JSESSIONID-WYYY=%5CuiUi%5C%2FYs%2FcJcoQ5xd3cBhaHw0rEfHkss1s%2FCfr92IKyg2hJOrJquv3fiG2%2Fn9GZS%2FuDH8PY81zGquF4GIAVB9eYSdKJM1W6E2i1KFg9%5CuZ4xU6VdPCGwp4KOUZQQiWSlRT%2F1r07OmIBn7yYVYN%2BM2MAalUQnoYcyskaXN%5CPo1AOyVVV%3A1516866368046; _iuqxldmzr_=32; _ntes_nnid=7e2e27f69781e78f2c610fa92434946b,1516864568068; _ntes_nuid=7e2e27f69781e78f2c610fa92434946b; __utma=94650624.470888446.1516864569.1516864569.1516864569.1; __utmc=94650624; __utmz=94650624.1516864569.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmb=94650624.8.10.1516864569'
    }
    opener = urllib.request.build_opener()
    opener.addheaders = [headers]
    data = json.loads(opener.open(url).read()) # 注意这句命令
    #data = opener.open(url).read()
    # 一般用上面这个就行，但是微博有点特殊，返回的是类似字典的数据，所以就直接包装了，而且可以避开出现编码的问题
    time.sleep(5)
    yield data # 爬取的数据较多，使用生成器，减少占用内存


text = []
pattern = "#.*?#" # 用来清理掉微博内容中插入#话题#的

#话题对应网页
proto_url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%23%E7%88%B1%E6%83%85%23%26t%3D0&page_type=searchall&page="
#前30页待爬网页列表
url=[]
for i in range(61,120):
    url.append(proto_url+str(i))

# 解析网页
for a in range(len(url)):
    for data in get_data(url[a], proxy[random.randint(3,50)]):
        data = data['data']
        print(data['cards'])
        for i in range(len(data['cards'])):
            for j in range(len(data['cards'][i]['card_group'])):
                content = re.sub(pattern,'',BeautifulSoup(data['cards'][i]['card_group'][j]['mblog']['text'], "lxml").get_text()).strip()
                if content not in text:
                    if len(content)<=100:
                        text.append(content)
            print("已解析%d，未解析%d，共%d链接..." %(a+1, len(url)-a-1, len(url)))
print("All done!")

text= pd.DataFrame(pd.Series(data=text))
text.to_excel('Sina.xls', sheet_name='sheet1')
print("成功写入文件！")

