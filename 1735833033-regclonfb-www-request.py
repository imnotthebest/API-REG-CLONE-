import tls_client
from bs4 import BeautifulSoup
import time
import re
import random
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from nacl.public import SealedBox, PublicKey
import nacl.utils
import time
import requests
import re
import threading
import string
import urllib.parse




def get_random_line(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return random.choice(lines).strip()


def check_otp(email, max_attempts=10, delay=3):
    url = f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                messages = response.json()
                
                # Kiểm tra từng email trong danh sách
                for message in messages:
                    subject = message.get("subject", "")
                    if "FB-" in subject:
                        # Bóc tách mã OTP từ subject
                        otp = subject.split("FB-")[1].split()[0]
                        print(f"OTP Found: {otp}")
                        return otp
            else:
                print(f"Request failed with status: {response.status_code}")
        
        except Exception as e:
            print(f"Error occurred: {e}")
        
        # Chờ trước khi thử lại
        print(f"Attempt {attempt + 1}/{max_attempts}. Retrying in {delay} seconds...")
        time.sleep(delay)
    
    print("OTP not found after maximum attempts.")
    return None


def Check_Live_Fb(uid):
    url = f"https://graph2.facebook.com/v3.3/{uid}/picture?redirect=0"
    response = requests.get(url, timeout=30)
    check_data = response.json()
    
    if not check_data.get('data', {}).get('height') or not check_data.get('data', {}).get('width'):
        return 'DIE'
    return 'LIVE'

def Encrypt_Password(public_key_data, password):
    try:
        current_time = str(int(time.time()))
        key_id = int(public_key_data['keyId'])
        public_key = bytes.fromhex(public_key_data['publicKey'])
        if len(public_key) != 32:
            raise ValueError('Public key is not valid')

        password_bytes = password.encode('utf-8')
        timestamp_bytes = current_time.encode('utf-8')
        key = nacl.utils.random(32)
        aes_gcm = AESGCM(key)
        encrypted_data = aes_gcm.encrypt(bytes(12), password_bytes, timestamp_bytes)
        sealed_box = SealedBox(PublicKey(public_key))
        sealed_key = sealed_box.encrypt(key)
        t = bytearray(48 + 2 + len(sealed_key) + len(encrypted_data))
        u = 0
        t[u] = 1
        u += 1
        t[u] = key_id
        u += 1
        t[u:u+2] = len(sealed_key).to_bytes(2, 'little')
        u += 2
        t[u:u+len(sealed_key)] = sealed_key
        u += len(sealed_key)
        t[u:u+16] = encrypted_data[-16:]
        u += 16
        t[u:] = encrypted_data[:-16]
        hashed_password = base64.b64encode(t).decode('utf-8')
        return f"#PWD_BROWSER:5:{current_time}:{hashed_password}"
    except Exception as error:
        print("Error encrypting password:", error)
        return None


class ProxyHandler:
    def __init__(self, file_path):
        # Mở tệp proxy và đọc toàn bộ các dòng vào
        with open(file_path, 'r') as file:
            self.proxies = [line.strip() for line in file.readlines() if line.strip()]  # Đọc và loại bỏ khoảng trắng thừa
        self.current_line = 0  # Dòng hiện tại sẽ bắt đầu từ 0

    def get_next_proxy(self):
        if self.current_line < len(self.proxies):
            # Lấy proxy tại dòng hiện tại
            proxy_line = self.proxies[self.current_line]
            self.current_line += 1  # Tăng chỉ số dòng lên 1 sau mỗi lần lấy proxy
            return self.parse_proxy(proxy_line)
        else:
            # Nếu đã hết proxy, trả về None
            return None, None, None

    def parse_proxy(self, proxy_line):
        # Tách proxy, user và pass từ dòng
        try:
            user_pass_proxy = proxy_line.split('@')
            user_pass = user_pass_proxy[0]
            proxy = user_pass_proxy[1]
            
            proxy_user, proxy_pass = user_pass.split(':')
            return proxy, proxy_user, proxy_pass
        except Exception as e:
            print(f"Error parsing proxy line: {proxy_line}, Error: {e}")
            return None, None, None

def Facebook_Register(ho, ten, phone, password, proxy_handler):
    # Tạo session
    session = tls_client.Session(
        client_identifier="chrome_131"
    )

    proxy, proxy_user, proxy_pass = proxy_handler.get_next_proxy()
    # print(proxy_user)
    proxies = {
        "http": f"http://{proxy_user}:{proxy_pass}@{proxy}",
        "https": f"http://{proxy_user}:{proxy_pass}@{proxy}"
    }
    session = requests.Session()
    session.proxies = proxies
    headers_get = {
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.facebook.com/',
    }

    try:
        URL = "https://www.facebook.com/"
        print("GỬI YÊU CẦU GET TỚI: "+URL+" ")
        response_get = session.get(url=URL,headers=headers_get)
    


        public_key_pattern = r'"publicKey":"([a-zA-Z0-9]+)"'
        key_id_pattern = r'"keyId":(\d+)'
        
        public_key_match = re.search(public_key_pattern, response_get.text)
        key_id_match = re.search(key_id_pattern, response_get.text)

        public_key_data = {
            'publicKey': public_key_match.group(1),
            'keyId': int(key_id_match.group(1)) 
        }

        password_encrypt = Encrypt_Password(public_key_data, password)

        cookies = response_get.cookies
        datr = None
        fr = None
        sb = None
        for cookie in cookies:
            if cookie.name == 'datr':
                datr = cookie.value
            elif cookie.name == 'fr':
                fr = cookie.value
            elif cookie.name == 'sb':
                sb = cookie.value

        URL = "https://www.facebook.com/r.php?entry_point=login"
        print("GỬI YÊU CẦU GET TỚI "+URL+" ")
        response_get = session.get(url=URL,headers=headers_get)
    
        soup = BeautifulSoup(response_get.text, 'html.parser')
        hidden_inputs = soup.find_all('input', type='hidden')
        form_data = {}
        for input_field in hidden_inputs:
           name = input_field.get('name')
           value = input_field.get('value', '')
           form_data[name] = value
        jazoest = form_data.get('jazoest')
        lsd = form_data.get('lsd')
        ri = form_data.get('ri')
        locale = form_data.get('locale')
        reg_instance = form_data.get('reg_instance')
        ignore = form_data.get('ignore')
        captcha_persist_data = form_data.get('captcha_persist_data')
        hsi_match = re.search(r'"hsi":"(\d+)"', response_get.text)
        hsi = hsi_match.group(1) if hsi_match else None
        spin_r_match = re.search(r'"__spin_r":(\d+)', response_get.text)
        spin_r = spin_r_match.group(1) if spin_r_match else None
        spin_t_match = re.search(r'"__spin_t":(\d+)', response_get.text)
        spin_t = spin_t_match.group(1) if spin_t_match else None

        data = {
            'jazoest': jazoest,
            'lsd': lsd,
            'lastname': ho,
            'firstname': ten, 
            'birthday_day': str(random.randint(1, 31)),
            'birthday_month': str(random.randint(1, 12)),
            'birthday_year': str(random.randint(1988, 2006)),
            'birthday_age': '',
            'did_use_age': 'false',
            'sex': str(random.randint(1, 2)),
            'preferred_pronoun': '',
            'custom_gender': '',
            'reg_email__': phone,
            'reg_email_confirmation__': '',
            'reg_passwd__': password_encrypt,
            'referrer': '',
            'asked_to_login': '0',
            'use_custom_gender': '',
            'terms': 'on',
            'ns': '0',
            'ri': ri,
            'action_dialog_shown': '',
            'invid': '',
            'a': '',
            'oi': '',
            'locale': locale,
            'app_bundle': '',
            'app_data': '',
            'reg_data': '',
            'app_id': '',
            'fbpage_id': '',
            'reg_oid': '',
            'reg_instance': reg_instance,
            'openid_token': '',
            'uo_ip': '',
            'guid': '',
            'key': '',
            're': '',
            'mid': '',
            'fid': '',
            'reg_dropoff_id': '',
            'reg_dropoff_code': '',
            'ignore': 'captcha|reg_email_confirmation__',
            'captcha_persist_data': captcha_persist_data,
            'captcha_response': '',
            '__user': '0',
            '__a': '1',
            '__req': '6',
            '__hs': '20084.BP:DEFAULT.2.0.0.0.0',
            'dpr': '1',
            '__ccg': 'EXCELLENT',
            '__rev': '1019085267',
            '__s': 'lxucyo:t0561u:xdnp5s',
            '__hsi': '7453027861273714271',
            '__dyn': '7xe6EsK36Q5E5ObwKBWg5S1Dxu13wqovzEdEc8uw9-3K0lW4o3Bw5VCwjE3awdu0FE2awpUO0n24o5-0me1Fw5uwbO0KU3mwaS0zE5W08HwSyE1582ZwrU1Xo1UU3jwea',
            '__csr': '',
            '__spin_r': spin_r,
            '__spin_b': 'trunk',
            '__spin_t': spin_t
        }

        headers = {
            'x-asbd-id': '129477',
            'sec-ch-ua-platform': '"Windows"',
            'x-fb-lsd': lsd,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'content-type': 'application/x-www-form-urlencoded',
            'sec-ch-ua-mobile': '?0',
            'accept': '*/*',
            'origin': 'https://www.facebook.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors', 
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.facebook.com/r.php?entry_point=login',
            'priority': 'u=1, i'
        }
        URL = "https://www.facebook.com/ajax/register.php";
        print("GỬI YÊU CẦU TỚI "+URL+" ")
        response_post = session.post(url=URL, headers=headers,data=data)

        if "registration_succeeded" in response_post.text:
            json_text = response_post.text.replace("for (;;);", "")
            response_data = json.loads(json_text)

            if response_data["payload"].get("registration_succeeded") == True:
                print('Thay đổi confirm tài khoản sang mail')

                ConfirmeMail = session.post(url="https://facebook.com/confirmemail.php?next=https%3A%2F%2Fwww.facebook.com%2F", headers=headers)

                match = re.search(r'"LSD",\[\],\{"token":"(.*?)"\}', ConfirmeMail.text)

                if match:
                    lsdUpdate = match.group(1)
                    print(f"Found LSD token: {lsd}")
                else:
                    print("LSD token not found.")

                match = re.search(r'"rev":(\d+)', ConfirmeMail.text)

                if match:
                    rev = int(match.group(1))

                soup = BeautifulSoup(ConfirmeMail.text, 'html.parser')
                hidden_inputs = soup.find_all('input', type='hidden')
                
                form_data = {}

                for input_field in hidden_inputs:
                   name = input_field.get('name')
                   value = input_field.get('value', '')
                   form_data[name] = value
                   

                fb_dtsg = form_data.get('fb_dtsg')
        

                cookies = response_post.cookies
                cookie_string = ''.join(f"{cookie.name}={cookie.value};" for cookie in cookies)
                print("Cookie:", cookie_string)
            
                start = cookie_string.find('c_user=') + 7
                end = cookie_string.find(';', start)
                c_user = cookie_string[start:end]


                Check_live = Check_Live_Fb(c_user)
                if Check_live == 'DIE':
                    return(f"{c_user}| ADD MAIL BỊ CHECKPOINT")

                print(c_user+"|"+password)

                print('CHỜ LẤY MAIL ẢO...')

                headers = {
                    "accept": "application/json, text/plain, */*",
                    "accept-encoding": "gzip, deflate, br, zstd",
                    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
                    "application-name": "web",
                    "application-version": "2.4.2",
                    "content-type": "application/json;charset=UTF-8",
                    "origin": "https://temp-mail.io",
                    "priority": "u=1, i",
                    "referer": "https://temp-mail.io/",
                    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                }

                # Payload
                payload = {
                    "min_name_length": 6,
                    "max_name_length": 10
                }


                response = requests.post("https://api.internal.temp-mail.io/api/v3/email/new", headers=headers, json=payload)
                print(response.text)
       
                if response.status_code == 200:
                    EmailAdd = response.json().get("email")
                    print(EmailAdd)
                else:
                    return("Failed Get Mail:", response.status_code, response.text)

                data = {
                   'jazoest': jazoest,
                   'fb_dtsg': fb_dtsg,
                   'next': '',
                   'contactpoint': EmailAdd,
                   '__user': c_user,
                   '__a': '1',
                   '__req': '6',
                   '__hs': '20084.BP:DEFAULT.2.0.0.0.0',
                   'dpr': '1',
                   '__ccg': 'EXCELLENT',
                   '__rev': rev,
                   '__s': 'lymdd5:5ssppg:e9596t',
                   '__hsi': '7453046681482997643',
                   '__dyn': '7xeUmBwjbg7ebwKBAg5S3G2O5U4e1Fx-ewSwMxW0DUS2S0im4E9ohwem0nCq1ew8y11wdu0FE5_wEwt81s8hwnU5W0IU9k2C1Fw5uwaO0OU3mwkE5G0zE5W0HU1IEow46wbS1Lwqo1wU1UU7u1rwea',
                   '__csr': '',
                   'lsd': lsdUpdate,
                   '__spin_r': spin_r,
                   '__spin_b': 'trunk', 
                   '__spin_t': spin_t
                }

                headers_post = {
                    'x-asbd-id': '129477',
                    'sec-ch-ua-platform': '"Windows"',
                    'x-fb-lsd': lsdUpdate,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    'content-type': 'application/x-www-form-urlencoded',
                    'sec-ch-ua-mobile': '?0',
                    'accept': '*/*',
                    'origin': 'https://www.facebook.com',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors', 
                    'sec-fetch-dest': 'empty',
                    'referer': 'https://www.facebook.com/r.php?entry_point=login',
                    'priority': 'u=1, i'
                }

                print('POST ADD MAIL: https://www.facebook.com/add_contactpoint/dialog/submit/')
                Submit = session.post(url="https://www.facebook.com/add_contactpoint/dialog/submit/", headers=headers_post, data=data)

                
                json_text = Submit.text.replace("for (;;);", "")
                response_data = json.loads(json_text)

                if response_data.get("error") == 1340013:
                   print("Email đã được sử dụng!")
                   return

                if "jsmods" in response_data and "define" in response_data["jsmods"]:
                   if "ServerRedirect" in str(response_data["jsmods"]["require"]):
                        print("Đã gửi OTP về Mail!")

                        otp = check_otp(EmailAdd)
                        if otp:
                            print(f"Tìm thấy OTP: {otp}")
                        else:
                            print("Không nhận được OTP.")
                            return
                        headers = {
                            "accept": "*/*",
                            "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
                            "content-length": "421",
                            "content-type": "application/x-www-form-urlencoded",
                            "origin": "https://m.facebook.com",
                            "priority": "u=1, i",
                            "referer": "https://m.facebook.com/confirmemail.php?next=https%3A%2F%2Fwww.facebook.com%2F&soft=hjk",
                            "sec-ch-prefers-color-scheme": "dark",
                            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                            "sec-ch-ua-full-version-list": '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
                            "sec-ch-ua-mobile": "?1",
                            "sec-ch-ua-model": '"Nexus 5"',
                            "sec-ch-ua-platform": '"Android"',
                            "sec-ch-ua-platform-version": '"6.0"',
                            "sec-fetch-dest": "empty",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-site": "same-origin",
                            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
                            "x-asbd-id": "129477",
                            "x-fb-lsd": lsdUpdate,
                            "x-requested-with": "XMLHttpRequest",
                            "x-response-format": "JSONStream",
                        }
                        postdata = {
                            "fb_dtsg": fb_dtsg,
                            "jazoest": jazoest,
                            "lsd": lsdUpdate,
                            "__dyn": "1KQdAG1mws8-t0BBBwno4a2i5U4e1FwKwSwMxW0Horx60zU3ex60Vo1a852q1ew2io0D24o1sE9k2C2G0pS0H83bw4FwmE2ewnE2Lwg81soow46wbS1LwqobU1kU1UU7u1rw",
                            "__csr": "",
                            "__req": "3",
                            "__fmt": "1",
                            "__a": "AYma88p13pvO3SELZ1rylXnU5g_Lp730wLdcUboGMoxqrIwXdDyK1UaDKiN6Booi9SSuQ2ytCL8_qd4KQjUHKWAqi1xX2mM7B9IoVkP7NglhVA",
                            "__user": c_user,
                        }

                        Url = "https://m.facebook.com/confirmation_cliff/?contact="+urllib.parse.quote(EmailAdd)+"&type=submit&is_soft_cliff=false&medium=email&code="+otp+""
                        print('XÁC THỰC OTP')
                        SubmitCode = session.post(url=Url, headers=headers, data=postdata)
                        print(SubmitCode.text)
                        if SubmitCode.text.startswith("for (;;);"):
                            json_data = SubmitCode.text[9:] 
                            try:
                                data = json.loads(json_data)
                   
                                actions = data.get("payload", {}).get("actions", [])
                                redirect_url = None
                                for action in actions:
                                    if action.get("cmd") == "redirect":
                                        redirect_url = action.get("uri")
                                
                                        if redirect_url == "/home.php?confirmed_account":
                                            Check_live = Check_Live_Fb(c_user)
                                            if Check_live == 'DIE':
                                                return(f"{c_user}| XÁC THỰC MAIL XONG DIE.")
                                            
                                            print(f"THÀNH CÔNG: {c_user}")
                                            with open('success.txt', 'a') as f:
                                                f.write(f"{EmailAdd}|{password}|{cookie_string}\n")
                                            print("Account saved to success.txt")
                                        break  
                                if not redirect_url == "/home.php?confirmed_account":
                                    print(" Xác thực xịt Không tìm thấy trường 'redirect' với URL đúng.")
                            except json.JSONDecodeError:
                                print("Không thể giải mã JSON.")
                        else:
                            print("Không phải dạng redirect.")


            else:
               print("Đăng ký không thành công")
               print(response_post.text)
        else:
           print("Response không đúng định dạng")
           print(response_post.text)

    except Exception as e:
        print(f"Error: {e}")


# Hàm xử lý việc đăng ký tài khoản
def process_registration(proxy_handler):
    while True:
        password = ''.join(random.choice(string.ascii_letters) for i in range(15))
        lastname = get_random_line('ho.txt')  
        firstname = get_random_line('ten.txt')
        
        random_phone_number = "+19043" + ''.join(random.choices('0123456789', k=6))  # Tạo số điện thoại ngẫu nhiên

        FacebolReg = Facebook_Register(lastname, firstname, random_phone_number, password, proxy_handler)
        print(FacebolReg)

file_path = 'proxies.txt'
proxy_handler = ProxyHandler(file_path)
# Lấy từng dòng proxy từ trên xuống trong tệp định dạng
# user:pass@host:port
# user:pass@host:port

threads = []
for _ in range(1):  
    thread = threading.Thread(target=process_registration, args=(proxy_handler,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()