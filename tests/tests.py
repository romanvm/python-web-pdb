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
        cls.send_btn = cls.browser.find_element_by_id('send_btn')

    @classmethod
    def tearDownClass(cls):
        cls.stdin.clear()
        cls.stdin.send_keys('q')
        cls.send_btn.click()
        time.sleep(1)
        cls.db_proc.kill()
        cls.browser.quit()

    def test_1_set_trace(self):
        """
        Test back-end/front-end interaction during debugging
        """
        filename_tag = self.browser.find_element_by_id('filename')
        self.assertEqual(filename_tag.text, 'db.py')
        curr_line_tag = self.browser.find_element_by_id('curr_line')
        self.assertEqual(curr_line_tag.text, '14')
        curr_file_tag = self.browser.find_element_by_id('curr_file_code')
        self.assertIn('foo = \'foo\'', curr_file_tag.text)
        globals_tag = self.browser.find_element_by_id('globals')
        self.assertIn('foo = \'foo\'', globals_tag.text)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('-> bar = \'bar\'', stdout_tag.text)
        # Test if Prismjs syntax coloring actually works
        self.assertIn('foo <span class="token operator">=</span> <span class="token string">\'foo\'</span>',
                      self.browser.page_source)

    def test_2_next_command(self):
        """
        Test sending PDB commands
        """
        self.stdin.clear()
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        curr_line_tag = self.browser.find_element_by_id('curr_line')
        self.assertEqual(curr_line_tag.text, '15')
        globals_tag = self.browser.find_element_by_id('globals')
        self.assertIn('bar = \'bar\'', globals_tag.text)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('-> ham = \'spam\'', stdout_tag.text)
        self.assertEqual(self.stdin.get_attribute('value'), '')

    def test_3_history(self):
        """
        Test for the recent commands history
        """
        self.stdin.clear()
        self.stdin.send_keys('h')
        self.send_btn.click()
        time.sleep(1)
        self.stdin.send_keys(Keys.ARROW_UP)
        self.assertEqual(self.stdin.get_attribute('value'), 'h')
        self.stdin.send_keys(Keys.ARROW_UP)
        self.assertEqual(self.stdin.get_attribute('value'), 'n')

    def test_4_breakpints(self):
        """
        Test for highlighting breakpoints
        """
        self.stdin.clear()
        self.stdin.send_keys('b 20')
        self.send_btn.click()
        time.sleep(1)
        line_numbers_rows = self.browser.find_element_by_css_selector('span.line-numbers-rows')
        line_spans = line_numbers_rows.find_elements_by_tag_name('span')
        self.assertEqual(line_spans[19].get_attribute('class'), 'breakpoint')

    def test_5_unicode_literal(self):
        """
        Test for highlighting breakpoints
        """
        self.stdin.clear()
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('-> name =', stdout_tag.text)

    def test_6_entering_unicode_string(self):
        """
        Test for entering unicode literal via console
        """
        self.stdin.clear()
        self.stdin.send_keys(u'p u\'python - питон\'')
        self.send_btn.click()
        time.sleep(1)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('u\'python -', stdout_tag.text)

    def test_7_local_vars(self):
        """
        Test for displaying local variables
        """
        self.stdin.clear()
        self.stdin.send_keys('c')
        self.send_btn.click()
        time.sleep(1)
        locals_tag = self.browser.find_element_by_id('locals')
        self.assertIn('spam = \'spam\'', locals_tag.text)
        globals_tag = self.browser.find_element_by_id('globals')
        self.assertNotEqual(globals_tag.text, locals_tag.text)


class PatchStdStreamsTestCase(TestCase):
    """
    This class tests patching sys.std* streams
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', os.path.join(cwd, 'db_ps.py')], shell=False)
        cls.browser = webdriver.PhantomJS()
        time.sleep(1)
        cls.browser.get('http://127.0.0.1:5555')
        cls.stdin = cls.browser.find_element_by_id('stdin')
        cls.send_btn = cls.browser.find_element_by_id('send_btn')

    @classmethod
    def tearDownClass(cls):
        cls.stdin.clear()
        cls.stdin.send_keys('q')
        cls.send_btn.click()
        time.sleep(1)
        cls.db_proc.kill()
        cls.browser.quit()

    def test_patching_std_streams(self):
        """
        Test if std streams are correctly redirected to the web-console
        """
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('Enter something:', stdout_tag.text)
        self.stdin.send_keys('spam')
        self.send_btn.click()
        time.sleep(1)
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        self.assertIn('You have entered: spam', stdout_tag.text)


class CatchPostMortemTestCase(TestCase):
    """
    This class tests patching sys.std* streams
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', os.path.join(cwd, 'db_pm.py')], shell=False)
        cls.browser = webdriver.PhantomJS()
        time.sleep(1)
        cls.browser.get('http://127.0.0.1:5555')
        cls.stdin = cls.browser.find_element_by_id('stdin')
        cls.send_btn = cls.browser.find_element_by_id('send_btn')

    @classmethod
    def tearDownClass(cls):
        cls.stdin.clear()
        cls.stdin.send_keys('q')
        cls.send_btn.click()
        time.sleep(1)
        cls.db_proc.kill()
        cls.browser.quit()

    def test_catch_post_mortem(self):
        """
        Test if std streams are correctly redirected to the web-console
        """
        curr_line_tag = self.browser.find_element_by_id('curr_line')
        self.assertEqual(curr_line_tag.text, '14')
        curr_file_tag = self.browser.find_element_by_id('curr_file_code')
        self.assertIn('assert False, \'Oops!\'', curr_file_tag.text)
        stdout_tag = self.browser.find_element_by_id('stdout')
        self.assertIn('AssertionError', stdout_tag.text)


if __name__ == '__main__':
    main()
