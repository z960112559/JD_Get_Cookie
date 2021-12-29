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


def get_server_chrome_versions():
    version_list = []
    rep = requests.get(url).text
    result = re.compile(r'\d.*?/</a>.*?Z').findall(rep)
    for i in result:
        version = re.compile(r'.*?/').findall(i)[0]  # 提取版本号
        version_list.append(version[:-1])  # 将所有版本存入列表
    return version_list


def download_driver(download_url):
    file = requests.get(download_url)
    with open("chromedriver.zip", 'wb') as zip_file:  # 保存文件到脚本所在目录
        zip_file.write(file.content)
        print('下载Chromedriver成功')


def download_lase_driver(download_url, chrome_version, chrome_main_version):
    version_list = get_server_chrome_versions()
    if chrome_version in version_list:
        download_url = f"{url}{chrome_version}/chromedriver_win32.zip"
    else:
        for version in version_list:
            if version.startswith(str(chrome_main_version)):
                download_url = f"{url}{version}/chromedriver_win32.zip"
                break
        if download_url == "":
            print("暂无法找到与Chrome兼容的Chromedriver版本，请在 http://npm.taobao.org/mirrors/chromedriver 核实。")

    download_driver(download_url=download_url)
    path = get_path()
    print('当前路径为：', path)
    unzip_driver(path)
    os.remove("chromedriver.zip")
    dri_version = get_driver_version()
    if dri_version == 0:
        return 0
    else:
        print('更新后的Chromedriver版本为：', dri_version)


def get_driver_version():
    version = os.popen('chromedriver --version').read()
    try:
        out = version.split(' ')[1]
    except:
        return 0
    return out


def unzip_driver(path):
    f = zipfile.ZipFile("chromedriver.zip", 'r')
    for file in f.namelist():
        f.extract(file, path)


def check_update_chromedriver():
    try:
        chrome_version = get_chrome_version()
        print("Chrome版本：" + chrome_version)
    except:
        print('未安装Chrome，请在官网 https://www.google.cn/chrome 下载。')
        input('按 Enter 键退出...')
        sys.exit()

    chrome_main_version = int(chrome_version.split(".")[0])  # chrome主版本号

    try:
        driver_version = get_driver_version()
        driver_main_version = int(driver_version.split(".")[0])  # chromedriver主版本号
    except:
        print('未安装Chromedriver，正在为您自动下载>>>')
        download_url = ""
        if download_lase_driver(download_url, chrome_version, chrome_main_version) == 0:
            return 0
        driver_version = get_driver_version()
        driver_main_version = int(driver_version.split(".")[0])  # chromedriver主版本号

    download_url = ""
    if driver_main_version != chrome_main_version:
        print("Chromedriver版本与Chrome浏览器不兼容，更新中>>>")
        if download_lase_driver(download_url, chrome_version, chrome_main_version) == 0:
            return 0
    else:
        print("Chromedriver版本已与Chrome浏览器相兼容，无需更新Chromedriver版本！")


def find_and_paste(cookie):
    for item in cookie.split('; '):
        if 'pt_pin' in item:
            pt_pin = item
        if 'pt_key' in item:
            pt_key = item
    jd_cookie = pt_pin + ';' + pt_key + ';'
    pyperclip.copy(jd_cookie)
    return jd_cookie


def put_cookie(cookie):
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
    driver = webdriver.Chrome(executable_path=get_path() + "\chromedriver.exe", options=chrome_options)
    driver.get("https://plogin.m.jd.com/login/login")
    input('登陆后按 Enter 键继续...')

    driver.get("https://home.m.jd.com/myJd/newhome.action")
    time.sleep(2)

    for request in driver.requests:
        if request.response:
            if request.path == "/myJd/newhome.action":
                cookie = request.headers["cookie"]

    jd_cookie = find_and_paste(cookie)
    print('Cookie：', jd_cookie)
    print('Cookie已复制到剪切板！')

    put_cookie(jd_cookie)

    input('按 Enter 键退出...')

    driver.close()


if __name__ == '__main__':
    check_update_chromedriver()
    main()
