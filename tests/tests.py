# coding: utf-8
# Created on: 13.09.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
from unittest import TestCase, main
from subprocess import Popen
from selenium import webdriver
from bs4 import BeautifulSoup

cwd = os.path.dirname(os.path.abspath(__file__))
db_py = os.path.join(cwd, 'db.py')


class SetTraceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', db_py], shell=False)
        cls.browser = webdriver.PhantomJS()
        cls.browser.get('http://127.0.0.1:5555')

    @classmethod
    def tearDownClass(cls):
        cls.db_proc.kill()

    def test_set_trace(self):
        soup = BeautifulSoup(self.browser.page_source, 'html5lib')
        filename_tag = soup.find('span', {'id': 'filename'})
        self.assertEqual(filename_tag.text, db_py)
        curr_line_tag = soup.find('span', {'id': 'curr_line'})
        self.assertEqual(curr_line_tag.text, '7')
        curr_frame_tag = soup.find('code', {'id': 'curr_frame_code'})
        self.assertIn('foo = \'foo\'', curr_frame_tag.get_text())
        vars_tag = soup.find('code', {'id': 'vars'})
        self.assertIn('foo = \'foo\'', vars_tag.get_text())


if __name__ == '__main__':
    main()
