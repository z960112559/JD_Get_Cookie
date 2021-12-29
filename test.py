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


if __name__ == '__main__':
    put_cookie("")
