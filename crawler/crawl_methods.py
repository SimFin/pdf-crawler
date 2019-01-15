from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse, urljoin
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import InvalidSessionIdException, ElementClickInterceptedException
import time


def get_hrefs_html(response, follow_foreign_hosts=False):
    urls = set()
    output = []
    soup = BeautifulSoup(response.text, "lxml")
    parsed_response_url = urlparse(response.url)
    urls_on_page = [link.attrs.get("href") for link in soup.find_all('a')]

    for url in urls_on_page:

        if url not in urls:

            follow = True
            parsed_url = urlparse(url)

            if not parsed_url.path:
                continue

            if not parsed_url.netloc:
                url = urljoin(response.url, parsed_url.path)
                parsed_url = urlparse(url)

            if parsed_response_url.netloc != parsed_url.netloc and not follow_foreign_hosts:
                follow = False

            urls.add(url)
            output.append({"url": url, "follow": follow})

    return output


def handle_url_list_js(output_list, new_urls, parsed_response_url, follow_foreign_hosts):
    urls_present = [x['url'] for x in output_list]
    new_output = []

    for url in new_urls:

        if url not in urls_present:

            follow = True
            parsed_url = urlparse(url)

            if parsed_response_url.netloc != parsed_url.netloc and not follow_foreign_hosts:
                follow = False

            urls_present.append(url)
            new_output.append({"url": url, "follow": follow})

    return new_output


def get_hrefs_js_simple(response, follow_foreign_hosts=False):
    parsed_response_url = urlparse(response.url)
    try:
        response.html.render(reload=False)
        urls_on_page = response.html.absolute_links
    except Exception:
        return get_hrefs_html(response, follow_foreign_hosts)

    return handle_url_list_js([], urls_on_page, parsed_response_url, follow_foreign_hosts)


def is_valid_link(link):
    if not link or link == "#" or link == "":
        return False
    return True


def make_element_id(element):
    id_str = ""

    css_properties = ["font-size", "font-weight", "margin", "padding", "color", "position", "display"]

    try:
        id_str += "text=" + str(element.text) + ";"

        for k, s in element.size.items():
            id_str += str(k) + "=" + str(s) + ";"

        for k, s in element.location_once_scrolled_into_view.items():
            id_str += str(k) + "=" + str(s) + ";"

        for k in css_properties:
            id_str += str(k) + "=" + str(element.value_of_css_property(k)) + ";"

    except Exception:
        return None

    return id_str


class ClickCrawler:

    def __init__(self, process_handler, executable_path, response, follow_foreign_hosts=False):

        self.process_handler = process_handler
        self.executable_path = executable_path
        self.driver = None
        self.handled = []
        self.main_url = response.url
        self.follow_foreign_hosts = follow_foreign_hosts

        self.iterations_limit = 500

    def load_driver(self):

        # kill all other spawned processes in case they are not terminated yet
        self.process_handler.kill_all()

        driver_options = Options()
        driver_options.headless = True
        self.driver = webdriver.Firefox(executable_path=self.executable_path, options=driver_options)

        self.process_handler.register_new_process(self.driver.service.process.pid)

        # Open url
        self.driver.get(self.main_url)

    def refresh_page(self):
        try:
            self.driver.refresh()
        except Exception:
            self.load_driver()

    def find_next_clickable_element(self, tried_refresh=False):
        try:
            elements = self.driver.find_elements_by_css_selector("*")

            # Go through all elements on page and look where the cursor is a pointer
            for k, element in enumerate(elements):
                if element.size['height'] > 0 and element.size['width'] > 0 and not is_valid_link(element.get_attribute("href")) and element.value_of_css_property(
                        "cursor") == "pointer" and element.value_of_css_property("display") != "none":
                    el_id = make_element_id(element)
                    if el_id not in self.handled and el_id is not None:
                        return element, el_id

        except Exception:
            if not tried_refresh:
                self.load_driver()
                return self.find_next_clickable_element(True)

        return None, None

    def find_element_by_id(self, element_id):
        elements = self.driver.find_elements_by_css_selector("*")

        for el in elements:
            el_id = make_element_id(el)
            if el_id == element_id:
                return el
        return None

    def get_new_urls_with_click(self, click_next_element, next_element_id, tried_refresh=False):

        new_urls_on_page = []

        if click_next_element is None:
            click_next_element = self.find_element_by_id(next_element_id)
            if click_next_element is None:
                return new_urls_on_page

        try:
            click_next_element.click()

            if self.driver.current_url != self.main_url:
                # reload the page if the url changed
                self.driver.get(self.main_url)
            else:
                # sleep to allow for eventual ajax to load
                time.sleep(3)

                new_urls_on_page = [link.get_attribute("href") for link in \
                                    self.driver.find_elements_by_css_selector("a") \
                                    if is_valid_link(link.get_attribute("href"))]

        except Exception:
            if not tried_refresh:
                # couldn't click on element, try once again with page refresh
                self.refresh_page()
                return self.get_new_urls_with_click(None, next_element_id, True)

        return new_urls_on_page

    def get_hrefs_js_complex(self):
        urls = []
        parsed_response_url = urlparse(self.main_url)

        # get driver
        self.load_driver()

        self.main_url = self.driver.current_url

        urls_on_page = [link.get_attribute("href") for link in \
                        self.driver.find_elements_by_css_selector("a") \
                        if is_valid_link(link.get_attribute("href"))]

        urls += handle_url_list_js(urls, urls_on_page, parsed_response_url, self.follow_foreign_hosts)

        # get clickable elements
        self.handled = []
        iterations = 0
        while iterations < self.iterations_limit:

            iterations += 1

            click_next_element, next_id = self.find_next_clickable_element()

            if click_next_element is None:
                break

            self.handled.append(next_id)

            new_urls_on_page = self.get_new_urls_with_click(click_next_element, next_id)

            urls += handle_url_list_js(urls, new_urls_on_page, parsed_response_url, self.follow_foreign_hosts)

        self.driver.close()
        self.process_handler.kill_all()

        return urls
