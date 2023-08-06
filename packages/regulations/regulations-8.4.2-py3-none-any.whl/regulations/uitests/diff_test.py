import unittest

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

from regulations.uitests.base_test import BaseTest


class DiffTest(BaseTest, unittest.TestCase):

    job_name = 'Diff test'

    def get_drawer_button(self):
        return self.driver.find_element_by_xpath('//*[@id="timeline-link"]')

    def test_diffs(self):
        self.driver.get(self.test_url + '/1005-2/2011-11111')
        html = self.driver.find_element_by_tag_name('html')
        WebDriverWait(self.driver, 60).until(
            lambda driver: 'selenium-start' in html.get_attribute('class'))

        WebDriverWait(self.driver, 60)
        drawer_button = self.get_drawer_button()
        drawer_button.click()

        WebDriverWait(self.driver, 60).until(
            lambda driver: driver.find_element_by_css_selector(
                '#timeline:not(.hidden)'))

        # drawer button should be active
        self.assertIn('current', drawer_button.get_attribute('class'))

        diff_field = self.driver.find_element_by_css_selector(
            '#timeline .status-list:nth-child(2) form select')
        # select version to compare to
        Select(diff_field).select_by_value('2012-12121')
        diff_field.submit()

        # wait until diff view has loaded
        html = self.driver.find_element_by_tag_name('html')
        WebDriverWait(self.driver, 90).until(
            lambda driver: 'selenium-start' in html.get_attribute('class'))

        WebDriverWait(self.driver, 60)
        # make sure the url is right
        assert self.urlparse().path == '/diff/1005-2/2012-12121/2011-11111'
        assert self.urlparse().query == 'from_version=2011-11111'

        WebDriverWait(self.driver, 60)

        # open diff pane in drawer
        active_drawer_button = self.get_drawer_button()
        active_drawer_button.click()
        WebDriverWait(self.driver, 60).until(
            lambda driver: 'current' in active_drawer_button.get_attribute(
                'class'))

        # navigate to 1005.3
        menu_link = self.driver.find_element_by_id('menu-link')
        WebDriverWait(self.driver, 10).until(
            lambda driver: menu_link.is_enabled() and menu_link.is_displayed())
        menu_link.click()
        WebDriverWait(self.driver, 10).until(
            lambda driver: 'current' in driver.find_element_by_id(
                'table-of-contents').get_attribute('class'))
        toc_link_1005_3 = self.driver.find_element_by_xpath(
            '//*[@id="toc"]/ol/li[3]')
        # drawer should have green bar
        self.assertTrue('modified' in toc_link_1005_3.get_attribute('class'))
        toc_link_1005_3.click()

        # wait until 1005.3 diff loads
        def matches_expected(driver):
            parsed = self.urlparse(driver.current_url)
            return (parsed.path == '/diff/1005-3/2012-12121/2011-11111' and
                    parsed.query == 'from_version=2011-11111')

        WebDriverWait(self.driver, 30).until(matches_expected)

        # make sure new section is greened
        new_section = self.driver.find_element_by_xpath(
            '//*[@id="1005-3-b-1-vi"]')
        self.assertTrue(new_section.find_element_by_tag_name('ins'))

        # make sure changed paragraph has insertions and deletions
        changed_section = self.driver.find_element_by_xpath(
            '//*[@id="1005-3-b-2-ii"]')
        self.assertEqual(len(changed_section.find_elements_by_tag_name('ins')),
                         2)
        self.assertTrue(len(changed_section.find_elements_by_tag_name('del')))

        # go back into diff pane in drawer, stop comparing
        self.get_drawer_button().click()
        stop_button = self.driver.find_element_by_xpath(
            '//*[@id="timeline"]/div[2]/ul/li[2]/div/a')
        stop_button.click()

        # make sure it goes back to the right place
        WebDriverWait(self.driver, 30).until(
            lambda driver:
            self.urlparse(driver.current_url).path == '/1005-3/2011-11111')
