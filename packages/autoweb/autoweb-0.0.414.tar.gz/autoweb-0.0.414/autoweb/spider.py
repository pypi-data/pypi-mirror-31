"""
对于selenium的爬虫功能的项目封装

4.根据元素属性
　　1)精准匹配：
　　　　[A]  driver.findElement(By.cssSelector("input[name=username]"));属性名=属性值,id,class,等都可写成这种形式
      [B]  driver.findElement(By.cssSelector("img[alt]"));存在属性。例如img元素存在alt属性
　　　　[C]  driver.findElement(By.cssSelector("input[type='submit'][value='Login']"));多属性
　　2)模糊匹配：（正则表达式匹配属性）
　　　　[A]  ^=  driver.findElement(By.cssSelector(Input[id ^='ctrl']));匹配到id头部 如ctrl_12
　　　　[B]  $=  driver.findElement(By.cssSelector(Input[id $='ctrl']));匹配到id尾部 如a_ctrl
　　　　[C]  *=  driver.findElement(By.cssSelector(Input[id *= 'ctrl']));匹配到id中间如1_ctrl_12
　　　　更多正则匹配原则请查看CSS3 选择器——属性选择器  http://www.w3cplus.com/css3/attribute-selectors


    "canvas:nth-child(1)" 取首个canvas标签
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
import random
import platform
import getpass
import os
from .error import *
from xbase import *


class CAutoWeb4Spider(object):
    def __init__(self, driver_type='chrome'):
        self._driver = None
        executable_path = self.__get_selenium_driver_path(driver_type)
        if driver_type == 'phantomjs':  # 在函数计算LINUX容器中线上使用
            self._driver = webdriver.PhantomJS(executable_path=executable_path)
        elif driver_type == 'chrome':  # 本地开发以及WINDOWS线上使用
            self._driver = webdriver.Chrome(executable_path=executable_path)
        else:
            assert False
        # 不能设置页面超时时间，会产生异常导致百度的JS无法正常执行。
        # self._driver.set_page_load_timeout(20)
        # self._driver.set_script_timeout(20)

    def __del__(self):
        if self._driver is not None:
            self._driver.quit()

    # 目前只支持两种浏览器类型chrome用于本地开发、phantomjs用于线上部署
    def __get_selenium_driver_path(self, browser_type='chrome'):
        # 自动判断当前运行平台的操作系统类型进行自适应识别
        os_type = platform.system().lower()
        driver_type = 'chromedriver' if browser_type == 'chrome' else 'phantomjs'

        # 自动找当前目录以及上级目录的bin目录位置下的驱动程序包
        def get(list):
            if len(list) == 0:
                return None
            path = os.path.sep.join(list) + '/bin/%s/%s' % (os_type, driver_type)
            if os.path.exists(path):
                return path
            else:
                list.pop()
                return get(list)

        prefix_path = xpath(__file__)
        list = prefix_path.split(os.path.sep)
        return get(list)

    def __get_dom_list(self, selector):
        try:
            return self._driver.find_elements_by_css_selector(selector)
        except NoSuchElementException:
            raise ERRAutoWeb4Spider4NotExistSelectorDom(self._driver.current_url, selector)

    def __get_dom(self, selector):
        try:
            return self._driver.find_element_by_css_selector(selector)
        except NoSuchElementException:
            raise ERRAutoWeb4Spider4NotExistSelectorDom(self._driver.current_url, selector)

    def __get_dom_attribute(self, dom, selector, attribute):
        try:
            if selector is None:
                return dom.get_attribute(attribute)
            else:
                return dom.find_element_by_css_selector(selector).get_attribute(attribute)
        except NoSuchElementException:
            raise ERRAutoWeb4Spider4NotExistSelectorDom(self._driver.current_url, selector)

    def visit(self, url, wait_seconds_to_visit=1, auto_refresh=False):
        self._driver.get(url)
        if auto_refresh:
            self._driver.refresh()  # 解决网址重定向问题，强制刷新一下
        if wait_seconds_to_visit is None or wait_seconds_to_visit == 0:
            return
        time.sleep(wait_seconds_to_visit)  # 解决ajax动态渲染页面延时一会加载
        return

    def get_text(self, selector):
        return self.__get_dom(selector).text

    def get_regex_text(self, selector, regex, group=1):
        return re.search(regex, self.__get_dom(selector).text).group(group)

    def get_attribute(self, selector, attribute):
        return self.__get_dom_attribute(self.__get_dom(selector), None, attribute)

    def input(self, selector, value):
        self.__get_dom(selector).send_keys(value)
        return

    def click(self, selector):
        self.__get_dom(selector).click()
        return

    def hover_click(self, selector, xoffset=0, yoffset=0):
        return ActionChains(self._driver).move_to_element_with_offset(self.__get_dom(selector), xoffset=xoffset,
                                                                      yoffset=yoffset).click().perform()

    # 全局发送按键（解决canvas中的按键输入问题）
    def send_keys(self, keys, is_input_enter=False):
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        if is_input_enter:
            ActionChains(self._driver).send_keys(keys).send_keys(Keys.ENTER).perform()
        else:
            ActionChains(self._driver).send_keys(keys).perform()

    # # 下拉列表模拟点击操作
    # # https://blog.csdn.net/huilan_same/article/details/52246012
    # def select_click(self, selector, value):
    #     from selenium.webdriver.support.select import Select
    #     dom = Select(self.__get_dom(selector))
    #     return

    def wait_until_dom_exist(self, selector, timeout_seconds=20):
        # 最简单的方法模拟等待DOM出现超时，规避SELENIUM非常烂的实现方法。
        for x in range(timeout_seconds):
            try:
                self.__get_dom(selector)
                return
            except ERRAutoWeb4Spider4NotExistSelectorDom:
                # ignore error
                pass
            time.sleep(1)
        raise TimeoutError

    # 随机数等待时间避免触发服务器的验证码（绕过反爬虫程序）
    def wait(self, seconds=0):
        if seconds == 0:
            seconds = random.choice(range(10, 30))
        time.sleep(seconds)
        return

    def wait_forever(self):
        while True:
            time.sleep(1)

    def download_dir(self):
        if platform.system() == 'Darwin':
            download_dir = '/Users/%s/Downloads' % getpass.getuser()
        elif platform.system() == 'Windows':
            download_dir = 'c:/Users/%s/Downloads' % getpass.getuser()
        else:
            assert False
        return download_dir

    def wait_download_success(self, filename, timeout_seconds=3600):
        """
        根据下载的文件名在指定下载目录下是否存在间接判断下载是否成功
        :param filename:
        :param timeout_seconds: 下载超时时间。
        :return:
        """
        assert timeout_seconds > 0
        for i in range(timeout_seconds):
            time.sleep(1)
            path = self.download_dir() + '/' + filename
            if os.path.exists(path):
                return
        raise ERRAutoWeb4Spider4DownloadTimeout(filename)
