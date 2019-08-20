import requests
from io import BytesIO
from lxml.html import fromstring
from PIL import Image


class ZhengFangSpider:
    
    def __init__(self, account, password, course):
        self.account = account
        self.password = password
        self.course = course
        self.login_url = 'http://jwc.gdlgxy.com/default2.aspx'
        self.captcha_url = 'http://jwc.gdlgxy.com/CheckCode.aspx'
        self.predict_url = 'http://127.0.0.1:5000/captcha'
        self.chance_course_url = f'http://jwc.gdlgxy.com/xf_xsyxxxk.aspx? \
                                 xh={self.account}&xm=%E9%99%88%E5%98%89%E9%91%AB&gnmkdm=N121208'

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                          AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'Origin': 'http://jwc.gdlgxy.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml; \
                      q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': f'http://jwc.gdlgxy.com/xf_xsyxxxk.aspx? \
                        xh={self.account}&xm=%E9%99%88%E5%98%89%E9%91%AB&gnmkdm=N121208',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        self.session = requests.Session()
        self.session.headers = self.headers

    def login(self):
        login_resp = self.session.get(url=self.login_url)
        if login_resp.status_code != 200:
            print('登录页请求失败')
            return False
        # 获取提交表单的数据
        VIEWSTATE, VIEWSTATEGENERATOR = self.csrf_token(login_resp)

        # 访问验证码的url
        captcha_resp = self.session.get(url=self.captcha_url)
        if captcha_resp != 200:
            print('获取验证码失败')
            return False
        # 将验证码以二进制的形式提交到识别的接口
        predict_resp = self.session.post(url=self.predict_url, data=captcha_resp.content)
        # 接受识别后的验证码
        code = predict_resp.text
        print(code)
        
        login_data = {
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            'txtUserName': '1512402602007',
            'TextBox2': 'qq8852077',
            'txtSecretCode': code,
            'RadioButtonList1': '学生'.encode('gbk'),
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': '',
        }

        info_resp = self.session.post(url=self.login_url, data=login_data)
        if info_resp.status_code != 200:
            print('提交登录数据错误')
            return False
        info_html = fromstring(info_resp.text)
        student_name = info_html.xpath('//span[@id="xhxm"]/text()')[0]
        print(student_name)

    @staticmethod
    def csrf_token(response):
        text = fromstring(response.text)
        VIEWSTATE = text.xpath('//input[@name="__VIEWSTATE"]/@value')[0]
        VIEWSTATEGENERATOR = text.xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
        return VIEWSTATE, VIEWSTATEGENERATOR

    def strive_chance_course(self):
        course_resp = self.session.get(url=self.chance_course_url)
        if course_resp != 200:
            print('获取课程页失败')
            return False
        VIEWSTATE, VIEWSTATEGENERATOR = self.csrf_token(course_resp)

        get_course_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            'ddl_kcxz': '',
            'ddl_kcgs=': '',
            'ddl_ywyl': '有'.encode('gbk'),
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGridtxtPageSize': '150',
            'ddl_xqbs': '2',
            '__VIEWSTATE': VIEWSTATE,
        }

        course_code = ''
        # 先获取所有课程
        course_resp = self.session.post(url=self.chance_course_url, data=get_course_data)
        if course_resp != 200:
            print('获取所有课程失败')
            return False
        course_html = fromstring(course_resp.text)
        # 查找课程
        course_table = course_html.xpath('//tr')
        for i in course_table:
            course_name = i.xpath('./td[3]//text()')[0]
            # print(kc_name)
            if course_name == self.course:
                course_code = i.xpath('./td[1]//@name')[0]
        if course_code:
            print(course_code)
        else:
            print('找不到该课程')
            return False

        # 获取新的 csrf_token
        VIEWSTATE, VIEWSTATEGENERATOR = self.csrf_token(course_resp)

        change_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            'ddl_kcgs': '',
            'ddl_ywyl': '有'.encode('gbk'),
            # 'ddl_ywyl': '',
            'Button1': '  提交  '.encode('gbk'),
            'ddl_sksj': '',
            'ddl_xqbs': '2',
            '__VIEWSTATE': VIEWSTATE,
            course_code: 'on'
        }

        change_course_resp = self.session.post(url=self.chance_course_url, data=change_data)
        if change_course_resp.status_code != 200:
            print('提交选课请求失败')
            return False
        print(change_course_resp.text)


def run(account, password, course):
    spider = ZhengFangSpider(account, password, course)
    spider.login()
    spider.strive_chance_course()


if __name__ == '__main__':
    your_account = ''
    your_password = ''
    your_course = ''
    run(your_account, your_password, your_course)
