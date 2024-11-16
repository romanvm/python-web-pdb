# Created on: 13.09.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)
#
# Copyright (c) 2016 Roman Miroshnychenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import time
from pathlib import Path
from subprocess import Popen
from unittest import TestCase, main, skipIf

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

CWD = Path(__file__).resolve().parent
DB_PY = CWD / 'db.py'

IS_PY_310 = sys.version_info[:2] >= (3, 10)
IS_PY_313 = sys.version_info[:2] >= (3, 13)

class SeleniumTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform == 'win32':
            cls.browser = webdriver.Firefox()
        else:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('disable-gpu')
            cls.browser = webdriver.Chrome(options=options)
        cls.browser.implicitly_wait(10)
        cls.browser.set_window_size(1280, 1024)
        cls.browser.get('http://127.0.0.1:5555')
        cls.stdin = cls.browser.find_element(By.ID, 'stdin')
        cls.send_btn = cls.browser.find_element(By.ID, 'send_btn')
        cls.stdout_tag = cls.browser.find_element(By.ID, 'stdout')

    @classmethod
    def tearDownClass(cls):
        cls.stdin.clear()
        cls.stdin.send_keys('q')
        cls.send_btn.click()
        time.sleep(1)
        cls.db_proc.kill()
        cls.browser.quit()

    def tearDown(self):
        if hasattr(self, '_outcome'):
            result = self._outcome.result
            if result.failures:
                failed_tests = [test for test, _ in result.failures]
                if self in failed_tests:
                    self.browser.save_screenshot(f'screenshot-{self}.png')

class WebPdbTestCase(SeleniumTestCase):
    """
    This class provides basic functionality testing for Web-PDB
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', str(DB_PY)], shell=False)
        super(WebPdbTestCase, cls).setUpClass()

    def test_1_set_trace(self):
        """
        Test back-end/front-end interaction during debugging
        """
        time.sleep(1)
        filename_tag = self.browser.find_element(By.ID, 'filename')
        self.assertEqual('db.py', filename_tag.text)
        curr_line_tag = self.browser.find_element(By.ID, 'curr_line')
        expected = '13' if IS_PY_313 else '14'
        self.assertEqual(expected, curr_line_tag.text)
        curr_file_tag = self.browser.find_element(By.ID, 'curr_file_code')
        self.assertIn('foo = \'foo\'', curr_file_tag.text)
        globals_tag = self.browser.find_element(By.ID, 'globals')
        self.assertIn('foo = \'foo\'', globals_tag.text)
        if IS_PY_313:
            self.stdin.send_keys('n')
            self.send_btn.click()
            time.sleep(1)
        self.assertIn('-> bar = \'bar\'', self.stdout_tag.text)
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
        curr_line_tag = self.browser.find_element(By.ID, 'curr_line')
        self.assertEqual(curr_line_tag.text, '15')
        globals_tag = self.browser.find_element(By.ID, 'globals')
        self.assertIn('bar = \'bar\'', globals_tag.text)
        self.assertIn('-> ham = \'spam\'', self.stdout_tag.text)
        self.assertEqual('', self.stdin.get_attribute('value'))

    def test_3_history(self):
        """
        Test for the recent commands history
        """
        self.stdin.clear()
        self.stdin.send_keys('h')
        self.send_btn.click()
        time.sleep(1)
        self.stdin.send_keys(Keys.ARROW_UP)
        self.assertEqual('h', self.stdin.get_attribute('value'))
        self.stdin.send_keys(Keys.ARROW_UP)
        self.assertEqual('n', self.stdin.get_attribute('value'))

    def test_4_breakpints(self):
        """
        Test for highlighting breakpoints
        """
        self.stdin.clear()
        self.stdin.send_keys('b 20')
        self.send_btn.click()
        time.sleep(1)
        line_numbers_rows = self.browser.find_element(By.CSS_SELECTOR, 'span.line-numbers-rows')
        line_spans = line_numbers_rows.find_elements(By.TAG_NAME, 'span')
        self.assertEqual('breakpoint', line_spans[19].get_attribute('class'))

    def test_5_unicode_literal(self):
        """
        Test for displaying unicode literals
        """
        self.stdin.clear()
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        self.assertIn('-> name = u\'Монти\'', self.stdout_tag.text)

    def test_6_entering_unicode_string(self):
        """
        Test for entering unicode literal via console
        """
        self.stdin.clear()
        self.stdin.send_keys('p u\'python - питон\'')
        self.send_btn.click()
        time.sleep(1)
        stdout_tag = self.browser.find_element(By.ID, 'stdout')
        self.assertIn('u\'python - питон\'', stdout_tag.text)

    def test_7_local_vars(self):
        """
        Test for displaying local variables
        """
        self.stdin.clear()
        self.stdin.send_keys('c')
        self.send_btn.click()
        time.sleep(1)
        locals_tag = self.browser.find_element(By.ID, 'locals')
        self.assertIn('spam = \'spam\'', locals_tag.text)
        globals_tag = self.browser.find_element(By.ID, 'globals')
        self.assertNotEqual(globals_tag.text, locals_tag.text)


class PatchStdStreamsTestCase(SeleniumTestCase):
    """
    This class tests patching sys.std* streams
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', str(CWD / 'db_ps.py')], shell=False)
        super(PatchStdStreamsTestCase, cls).setUpClass()

    def test_patching_std_streams(self):
        """
        Test if std streams are correctly redirected to the web-console
        """
        time.sleep(1)
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        if IS_PY_313:
            self.stdin.send_keys('n')
            self.send_btn.click()
            time.sleep(1)
        self.assertIn('Enter something:', self.stdout_tag.text)
        self.stdin.send_keys('spam')
        self.send_btn.click()
        time.sleep(1)
        self.stdin.send_keys('n')
        self.send_btn.click()
        time.sleep(1)
        self.assertIn('You have entered: spam', self.stdout_tag.text)


class CatchPostMortemTestCase(SeleniumTestCase):
    """
    This class for catching exceptions
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', str(CWD / 'db_pm.py')], shell=False)
        super(CatchPostMortemTestCase, cls).setUpClass()

    def test_catch_post_mortem(self):
        """
        Test if catch_post_mortem context manager catches exceptions
        """
        time.sleep(1)
        curr_line_tag = self.browser.find_element(By.ID, 'curr_line')
        expected = '13' if IS_PY_310 else '14'
        self.assertEqual(expected, curr_line_tag.text)
        curr_file_tag = self.browser.find_element(By.ID, 'curr_file_code')
        self.assertIn('assert False, \'Oops!\'', curr_file_tag.text)
        stdout_tag = self.browser.find_element(By.ID, 'stdout')
        self.assertIn('AssertionError', stdout_tag.text)


class InspectCommandTestCase(SeleniumTestCase):
    """
    Test for inspect command
    """
    @classmethod
    def setUpClass(cls):
        cls.db_proc = Popen(['python', str(CWD / 'db_i.py')], shell=False)
        super(InspectCommandTestCase, cls).setUpClass()

    def test_inspect_existing_object(self):
        """
        Test inspecting existing object
        """
        time.sleep(1)
        self.stdin.send_keys('i Foo')
        self.send_btn.click()
        time.sleep(1)
        self.assertIn('foo: \'foo\'', self.stdout_tag.text)
        self.assertIn('bar: \'bar\'', self.stdout_tag.text)
        self.stdin.send_keys('i bar')
        self.send_btn.click()
        time.sleep(1)
        self.assertNotIn('NameError: name "bar" is not defined',
                         self.stdout_tag.text)

    def test_inspect_non_existing_object(self):
        """
        Test inspecting non-existing object
        """
        self.stdin.send_keys('i spam')
        self.send_btn.click()
        time.sleep(1)
        self.assertIn('NameError: name "spam" is not defined',
                      self.stdout_tag.text)


if __name__ == '__main__':
    main()
