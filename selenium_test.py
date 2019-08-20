import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json

# option = webdriver.ChromeOptions()
# option.add_argument('headless')
driver = webdriver.Chrome(
    executable_path='chromedriver.exe',
    # options=option,
)
url = 'http://jwc.gdlgxy.com/default2.aspx'
driver.get(url=url)
# cookie = driver.get_cookie(name='ASP.NET_SessionId')
cookies = {}
_cookie = driver.get_cookies()[0]
cookies[_cookie['name']] = _cookie['value']
print(cookies)
driver.set_window_size(1920, 1080)
username = WebDriverWait(driver, 10).until(
    lambda d: d.find_element_by_xpath('//input[@id="txtUserName"]')
)
password = WebDriverWait(driver, 10).until(
    lambda d: d.find_element_by_xpath('//input[@id="TextBox2"]')
)

url2 = 'http://jwc.gdlgxy.com/CheckCode.aspx'
req = requests.get(url2, cookies=cookies)

url3 = 'http://127.0.0.1:5000/captcha'
a = requests.post(url=url3, data=req.content).text
print(a)

yzm = WebDriverWait(driver, 10).until(
    lambda d: d.find_element_by_xpath('//input[@id="txtSecretCode"]')
)
sumbit = WebDriverWait(driver, 10).until(
    lambda d: d.find_element_by_xpath('//input[@name="Button1"]')
)

username.send_keys('xxxxxxxx')
password.send_keys('xxxxxx')
yzm.send_keys(a)
sumbit.click()