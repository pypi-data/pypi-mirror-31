import unittest

from selenium.webdriver.support.ui import WebDriverWait

from regulations.uitests.base_test import BaseTest


class InterpTest(BaseTest, unittest.TestCase):

    job_name = 'Interp test'

    def test_interps(self):
        self.driver.get(self.test_url + '/1005-2/2012-12121')
        html = self.driver.find_element_by_tag_name('html')
        WebDriverWait(self.driver, 30).until(
            lambda driver: 'selenium-start' in html.get_attribute('class'))

        interp_dropdown = self.driver.find_element_by_xpath(
            '//*[@id="1005-2-h"]/section')

        # interp should know who it belongs to
        self.assertEquals(interp_dropdown.get_attribute('data-interp-for'),
                          '1005-2-h')

        # interp section should know what is in it
        self.assertEqual(interp_dropdown.get_attribute('data-interp-id'),
                         '1005-18-a')

        # should have the appropriate header
        self.assertIn('OFFICIAL INTERPRETATION TO 2(h)',
                      interp_dropdown.text)

        self.driver.execute_script(
            'p10052h = document.getElementById("1005-2-h").offsetTop')
        self.driver.execute_script('window.scrollTo(0, p10052h)')

        # body should be hidden
        interp_text = self.driver.find_element_by_xpath(
            '//*[@id="1005-2-h"]/section/section')
        interp_dropdown.click()

        WebDriverWait(self.driver, 120).until(
            lambda driver: driver.find_element_by_css_selector(
                '.inline-interpretation.open'))

        # header should update
        self.assertIn('HIDE', interp_dropdown.text)

        # should contain the appropriate reg section
        WebDriverWait(self.driver, 10).until(
            lambda driver: interp_text.text)
        self.assertIn('clicked. A finances centripetally curiousest '
                      'stronghold cemeteries', interp_text.text)

        self.driver.find_element_by_xpath(
            '//*[@id="1005-2-h"]/section/header/a').click()

        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.find_element_by_css_selector(
                '.inline-interpretation:not(.open)'))

        # header should reflect close
        self.assertIn('SHOW', interp_dropdown.text)
