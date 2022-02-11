import json
import re
import os
import sys
import zipfile
import winreg
import requests
import time
import pyperclip
from seleniumwire import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach', True)
chrome_options.add_experimental_option('w3c', False)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--auto-open-devtools-for-tabs")

url = 'http://npm.taobao.org/mirrors/chromedriver/'


def get_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_chrome_version():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
    version, types = winreg.QueryValueEx(key, 'version')
    return version


def get_driver_version():
    version = os.popen('chromedriver --version').read()
    try:
        out = version.split(' ')[1]
    except:
        return 0
    return out


def get_driver_server_versions():
    version_list = []
    response = requests.get("https://registry.npmmirror.com/-/binary/chromedriver")
    response_body = json.loads(response.text)
    for version in response_body:
        version_list.append(version['name'].replace("/", "").split(".")[0])
    return version_list


def get_driver_download_url(chrome_main_version):
    response1 = requests.get("https://registry.npmmirror.com/-/binary/chromedriver")
    driver_version_list = json.loads(response1.text)

    version_url = ""
    for driver_version in driver_version_list:
        driver_main_version = driver_version["name"].replace("/", "").split(".")[0]
        if driver_main_version == chrome_main_version.__str__():
            version_url = driver_version["url"]

    if len(version_url) == 0:
        print("暂无法找到与Chrome兼容的Chromedriver版本，请在 http://npm.taobao.org/mirrors/chromedriver/ 核实。")
        input('按 Enter 键退出...')
        sys.exit()

    response2 = requests.get(version_url)
    driver_platform_list = json.loads(response2.text)

    download_url = ""
    for driver_platform in driver_platform_list:
        if driver_platform["name"] == "chromedriver_win32.zip":
            download_url = driver_platform["url"]

    if len(download_url) == 0:
        print("暂无法找到与Chrome兼容的Chromedriver版本，请在 http://npm.taobao.org/mirrors/chromedriver/ 核实。")
        input('按 Enter 键退出...')
        sys.exit()

    return download_url


def get_server_chrome_versions():
    version_list = []
    rep = requests.get(url).text
    result = re.compile(r'\d.*?/</a>.*?Z').findall(rep)
    for i in result:
        version = re.compile(r'.*?/').findall(i)[0]
        version_list.append(version[:-1])  # 将所有版本存入列表
    return version_list


def download_driver(chrome_main_version):
    # 获取 Chromedriver 下载地址
    driver_download_url = get_driver_download_url(chrome_main_version)
    if len(driver_download_url) == 0:
        print("暂无法找到与Chrome兼容的Chromedriver版本，请在 http://npm.taobao.org/mirrors/chromedriver/ 核实。")
        input('按 Enter 键退出...')
        sys.exit()

    print("Chromedriver下载地址：" + driver_download_url)

    # 下载 Chromedriver，保存文件到脚本所在目录
    file = requests.get(driver_download_url)
    with open("chromedriver.zip", 'wb') as zip_file:
        zip_file.write(file.content)
        print('下载 Chromedriver 成功。')

    # 解压 Chromedriver
    path = get_path()
    # print('当前路径为：', path)
    unzip_driver(path)
    os.remove("chromedriver.zip")
    print('解压 Chromedriver 成功。')

    # 返回更新后的版本号
    dri_version = get_driver_version()
    if dri_version == 0:
        return 0
    else:
        print('当前Chromedriver版本：', dri_version)
        return 1


def unzip_driver(path):
    f = zipfile.ZipFile("chromedriver.zip", 'r')
    for file in f.namelist():
        f.extract(file, path)


def check_update_chromedriver():
    try:
        chrome_version = get_chrome_version()
        print("当前Chrome版本：" + chrome_version)
    except:
        print('未安装Chrome！请先自行下载并安装Chrome后再试！')
        input('按 Enter 键退出...')
        sys.exit()

    chrome_main_version = int(chrome_version.split(".")[0])  # chrome主版本号

    try:
        driver_version = get_driver_version()
        driver_main_version = int(driver_version.split(".")[0])  # chromedriver主版本号
    except:
        print('未安装Chromedriver，正在为您自动下载>>>')
        if download_driver(chrome_main_version) == 0:
            return 0
        driver_version = get_driver_version()
        driver_main_version = int(driver_version.split(".")[0])  # chromedriver主版本号

    if driver_main_version != chrome_main_version:
        print("Chromedriver版本与Chrome浏览器不兼容，更新中>>>")
        if download_driver(chrome_main_version) == 0:
            return 0
    else:
        print("Chromedriver版本已与Chrome浏览器相兼容，无需更新Chromedriver版本！")


def parse_copy_cookie(cookie):
    for item in cookie.split('; '):
        if 'pt_pin' in item:
            pt_pin = item
        if 'pt_key' in item:
            pt_key = item
    jd_cookie = pt_pin + ';' + pt_key + ';'
    pyperclip.copy(jd_cookie)
    return jd_cookie


def submit_cookie(cookie):
    try:
        req_headers = {'Content-Type': 'application/json'}
        req_body = json.dumps({"cookie": cookie})
        response = requests.post("http://49.232.79.109:8090/jd/cookie/put", data=req_body, headers=req_headers)
    except requests.exceptions.ConnectionError:
        print("提交Cookie失败，服务器连接失败。")
    except requests.exceptions.ConnectTimeout:
        print("提交Cookie失败，服务器连接超时。")
    except requests.exceptions.ReadTimeout:
        print("提交Cookie失败，服务器响应超时。")
    else:
        if response.status_code == 200:
            print(response.text)
            res_body = json.loads(response.text)
            if res_body['status']:
                print("提交Cookie成功")
            else:
                print("提交Cookie失败，错误信息：" + res_body['message'])
        else:
            print("提交Cookie失败，HTTP状态码：" + response.status_code.__str__())


def main():
    print('请在弹出的网页中登录账号。')
    driver = webdriver.Chrome(executable_path=(get_path() + "\chromedriver.exe"), options=chrome_options)
    driver.get("https://plogin.m.jd.com/login/login")
    input('登陆后按 Enter 键继续...')

    driver.get("https://home.m.jd.com/myJd/newhome.action")
    print('3秒后开始解析Cookie...')
    time.sleep(3)

    for request in driver.requests:
        if request.response:
            if request.path == "/myJd/newhome.action":
                cookie = request.headers["cookie"]

    jd_cookie = parse_copy_cookie(cookie)
    print('Cookie：', jd_cookie)
    print('已复制Cookie到剪切板！')

    submit_cookie(jd_cookie)

    input('按 Enter 键退出...')
    driver.close()


if __name__ == '__main__':
    check_update_chromedriver()
    main()
