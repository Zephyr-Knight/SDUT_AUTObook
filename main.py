import ddddocr
import requests
from PIL import Image
import io
import base64
from datetime import datetime
# 定义常量
DATE_FORMAT = '%Y-%m-%d'
# 初始化OCR
ocr = ddddocr.DdddOcr()

#  设置登录信息
std_ID = '' # 学号
password = '' # 图书馆密码
# 设置server酱推送信息
SCKEY = ""
#bark通知
BARK_PUSH = "https://api.day.app/************/" # 格式：https://api.day.app/*********/


def serverJ( content: str) -> None:
    """
    通过 serverJ 推送消息。
    """
    if not SCKEY:
        print("serverJ 服务的 PUSH_KEY 未设置!!\n取消推送")
        return
    print("serverJ 服务启动")

    data = {"text": "图书馆预约通知", "channel":9,"desp": content}
    url = f'https://sc.ftqq.com/{SCKEY}.send'
    response = requests.post(url, data=data).json()
    print(f'serverJ 推送状态：{response}')

def bark(content: str) -> None:
    """
    使用 bark 推送消息。
    """
    if not BARK_PUSH:
        print("bark 服务的 BARK_PUSH 未设置!!\n取消推送")
        return
    print("bark 服务启动")
    url = f"{BARK_PUSH}图书馆预约通知/{content}"
    requests.get(url)


# 定义函数，用于获取验证码
def get_captcha():
    url = 'http://222.206.65.16/sdutseat/auth/createCaptcha'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to retrieve captcha')

def decode_captcha(image_data):
    decoded_data = base64.b64decode(image_data)
    # 以下代码用于显示验证码图片
    # image = Image.open(io.BytesIO(decoded_data))
    # image.show()
    return decoded_data

#  以下代码用于识别验证码
def recognize_captcha(ocr, captcha_data):
    return ocr.classification(captcha_data)

#  定义登录函数,用于获取token
def login(std_id, password, captcha_id, captcha_result):
    url = f'http://222.206.65.16/sdutseat/rest/auth?username={std_id}&password={password}&answer={captcha_result}&captchaId={captcha_id}'
    response = requests.post(url)
    if response.json()['status']== 'success':
        return response.json()['data']['token']
    else:
        print("登录失败",response.json())
        return  None

def book_history(token):
    url = f'http://222.206.65.16/sdutseat/rest/v2/history/1/6?page=1&pageSize=6&token={token}'
    response = requests.get(url)
    if response.json()['status'] == 'success':
        return response.json()['data']['reservations']
    else:
        return None

#  定义取消预定座位函数
def  cancel_booking(token):
    data = book_history(token)
    reserved_data = [item for item in data if item['stat'] == 'RESERVE']
    if not reserved_data:
        print('没有可取消的预定')
        return
    id =  reserved_data[0]['id']
    url = f'http://222.206.65.16/sdutseat/rest/v2/cancel/{id}?id={id}&token={token}'
    response = requests.get(url)
    if response.json()['status'] == 'success':
        print('取消成功')
    else:
        print('取消失败')

# 验证token是否有效
def is_token_valid(token):
    url = f'http://222.206.65.16/sdutseat/rest/v2/user?token={token}'
    response = requests.get(url).json()
    if response['status'] == 'success':
        print('Token有效')
        return True
    else:
        return False

# 获取token
def get_token(std_id, password):
    captcha = get_captcha()
    captcha_data = decode_captcha(captcha['captchaImage'][22:])
    captcha_result = recognize_captcha(ocr, captcha_data)
    token = login(std_id, password, captcha['captchaId'], captcha_result)
    if token:
        return token
    else:
        return 0


#  定义预定座位函数
def book_seat(seat_id, start_time, end_time) -> None:
    token = get_token(std_ID,password)
    date =  datetime.now().strftime('%Y-%m-%d')
    url = f'http://222.206.65.16/sdutseat/rest/v2/freeBook?token={token}'
    data = {
        'startTime': start_time,
        'endTime': end_time,
        'seat': seat_id,
        'date': date,
    }
    response = requests.post(url, data=data)
    response_text = response.json()
    print(response_text)
    serverJ(response_text)
    bark(response_text)









if __name__ == '__main__':
    date = datetime.now().strftime('%Y-%m-%d')
    print(date)
    book_text = book_seat('', '', '')
    print(book_text)
