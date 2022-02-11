import json
import requests


def put_cookie(cookie):
    try:
        req_headers = {'Content-Type': 'application/json'}
        req_body = json.dumps({"cookie": ""})
        response = requests.post("http://127.0.0.1:8090/jd/cookie/put", data=req_body, headers=req_headers)
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


def get_driver_download_url(chrome_main_version):
    response1 = requests.get("https://registry.npmmirror.com/-/binary/chromedriver")
    driver_version_list = json.loads(response1.text)

    version_url = ""
    for driver_version in driver_version_list:
        driver_main_version = driver_version["name"].replace("/", "").split(".")[0]
        if driver_main_version == chrome_main_version:
            version_url = driver_version["url"]

    if version_url == "":
        print("暂无法找到与Chrome兼容的Chromedriver版本，请在 http://npm.taobao.org/mirrors/chromedriver/ 核实。")

    response2 = requests.get(version_url)
    driver_platform_list = json.loads(response2.text)

    download_url = ""
    for driver_platform in driver_platform_list:
        if driver_platform["name"] == "chromedriver_win32.zip":
            download_url = driver_platform["url"]

    if download_url == "":
        print("暂无法找到与Chrome兼容的Chromedriver版本，请在 http://npm.taobao.org/mirrors/chromedriver/ 核实。")

    print("Chromedriver下载地址：" + download_url)
    return download_url


if __name__ == '__main__':
    download_url = get_driver_download_url("97")

    print(1)
