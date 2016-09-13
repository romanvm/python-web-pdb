# coding: utf-8
# Created on: 13.09.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import time
from unittest import TestCase, main
from subprocess import Popen
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

cwd = os.path.dirname(os.path.abspath(__file__))
db_py = os.path.join(cwd, 'db.py')


class WebPdbTestCase(TestCase):
    """
    This class provides basic functionality testing for Web-PDB
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', db_py], shell=False)
        cls.browser = webdriver.PhantomJS()
        time.sleep(1)
        cls.browser.get('http://127.0.0.1:5555')
        cls.stdin = cls.browser.find_element_by_id('stdin')
        cls.send_btn = cls.browser.find_element_by_id('send-btn')

    @classmethod
    def tearDownClass(cls):
        cls.stdin.clear()
        cls.stdin.send_keys('q')
        cls.send_btn.click()
        cls.db_proc.kill()

    def test_1_set_trace(self):
        """
        Test if the back-end correctly sends and the front-end JS
        correctly renders debugging data.
        """
        filename_tag = self.browser.find_element_by_id('filename')
        self.assertEqual(filename_tag.text, db_py)
        curr_line_tag = self.browser.find_element_by_id('curr_line')
        self.assertEqual(curr_line_tag.text, '7')
        curr_frame_tag = self.browser.find_element_by_id('curr_frame_code')
        self.assertIn('foo = \'foo\'', curr_frame_tag.text)
        vars_tag = self.browser.find_element_by_id('vars')
        self.assertIn('foo = \'foo\'', vars_tag.text)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('-> bar = \'bar\'', stdout_tag.text)
        # Test if Prismjs syntax coloring actually works
        self.assertIn('foo <span class="token operator">=</span> <span class="token string">\'foo\'</span>',
                      self.browser.page_source)

    def test_2_next_command(self):
        """
        Test sending PDB commands
        """
        self.stdin.send_keys('n')
        self.send_btn.click()
        # Wait for the front-end to refresh data via ajax
        time.sleep(0.5)
        curr_line_tag = self.browser.find_element_by_id('curr_line')
        self.assertEqual(curr_line_tag.text, '8')
        vars_tag = self.browser.find_element_by_id('vars')
        self.assertIn('bar = \'bar\'', vars_tag.text)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('-> ham = \'spam\'', stdout_tag.text)
        self.assertEqual(self.stdin.get_attribute('value'), '')
        self.stdin.send_keys('h ll')
        self.send_btn.click()
        time.sleep(0.5)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('longlist | ll', stdout_tag.text)

    def test_3_history(self):
        """
        Test for the recent commands history
        """
        self.stdin.send_keys(Keys.ARROW_UP)
        self.assertEqual(self.stdin.get_attribute('value'), 'h ll')
        self.stdin.send_keys(Keys.ARROW_UP)
        self.assertEqual(self.stdin.get_attribute('value'), 'n')


if __name__ == '__main__':
    main()
