# import requests

# # Cấu hình proxy
# proxy_url = "198.23.239.134:6540"
# username = "yoncxpdq"
# password = "vn4jj2w247v5"

# # Thiết lập proxy với thông tin xác thực
# proxies = {
#     "http": f"http://{username}:{password}@{proxy_url}",
#     "https": f"http://{username}:{password}@{proxy_url}"
# }

# # Kiểm tra kết nối qua proxy và lấy IP
# try:
#     response = requests.get("https://httpbin.org/ip", proxies=proxies)
#     if response.status_code == 200:
#         print("Kết nối qua proxy thành công!")
#         # In ra IP trả về từ httpbin
#         ip_info = response.json()  # Đọc dữ liệu JSON từ phản hồi
#         print("IP từ proxy:", ip_info["origin"])  # Lấy địa chỉ IP từ phản hồi JSON
#     else:
#         print("Không thể kết nối qua proxy. HTTP status:", response.status_code)
# except Exception as e:
#     print("Lỗi khi kết nối qua proxy:", str(e))

import requests

def check_facebook_proxy(proxy):
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    test_url = "https://www.facebook.com/r.php?entry_point=login"
    
    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working and can access Facebook.")
            return True
        elif response.status_code == 403:
            print(f"Proxy {proxy} is blocked by Facebook (403 Forbidden).")
            return False
        elif response.status_code == 429:
            print(f"Proxy {proxy} is rate-limited by Facebook (429 Too Many Requests).")
            return False
        else:
            print(f"Proxy {proxy} returned status code {response.status_code} when accessing Facebook.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Proxy {proxy} failed: {e}")
        return False

# Example usage
proxy = "yoncxpdq:vn4jj2w247v5@198.23.239.134:6540"
is_clean = check_facebook_proxy(proxy)