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


def load_driver(url, executable_path):
    driver_options = Options()
    driver_options.headless = True
    driver = webdriver.Firefox(executable_path=executable_path, options=driver_options)

    # Open url
    driver.get(url)

    return driver


def refresh_page(driver, main_url, executable_path):
    try:
        driver.refresh()
    except InvalidSessionIdException:
        driver = load_driver(main_url, executable_path)

    return driver


def find_next_clickable_element(driver, main_url, handled, executable_path, tried_refresh=False):
    try:
        elements = driver.find_elements_by_css_selector("*")

        # Go through all elements on page and look where the cursor is a pointer
        for k, element in enumerate(elements):
            if element.size['height'] > 0 and element.size['width'] > 0 and not is_valid_link(element.get_attribute("href")) and element.value_of_css_property(
                    "cursor") == "pointer" and element.value_of_css_property("display") != "none":
                el_id = make_element_id(element)
                if el_id not in handled and el_id is not None:
                    return element, el_id, driver

    except InvalidSessionIdException:
        if not tried_refresh:
            driver = load_driver(main_url, executable_path)
            return find_next_clickable_element(driver, main_url, handled, executable_path, True)

    return None, None, driver


def find_element_by_id(driver, element_id):
    elements = driver.find_elements_by_css_selector("*")

    for el in elements:
        el_id = make_element_id(el)
        if el_id == element_id:
            return el
    return None


def get_new_urls_with_click(driver, click_next_element, next_element_id, base_url, executable_path, tried_refresh=False):
    new_urls_on_page = []

    if click_next_element is None:
        click_next_element = find_element_by_id(driver, next_element_id)
        if click_next_element is None:
            return new_urls_on_page, driver

    try:
        click_next_element.click()

        if driver.current_url != base_url:
            # reload the page if the url changed
            driver.get(base_url)

        # sleep to allow for eventual ajax to load
        time.sleep(3)

        new_urls_on_page = [link.get_attribute("href") for link in \
                            driver.find_elements_by_css_selector("a") \
                            if is_valid_link(link.get_attribute("href"))]

    except ElementClickInterceptedException:
        if not tried_refresh:
            # couldn't click on element, try once again with page refresh
            driver = refresh_page(driver, base_url, executable_path)
            return get_new_urls_with_click(driver, None, next_element_id, base_url, executable_path, True)
    except Exception:
        pass

    return new_urls_on_page, driver


def get_hrefs_js_complex(response, follow_foreign_hosts=False, executable_path='geckodriver'):
    urls = []
    parsed_response_url = urlparse(response.url)

    # get driver
    driver = load_driver(response.url, executable_path)

    base_url = driver.current_url

    urls_on_page = [link.get_attribute("href") for link in \
                    driver.find_elements_by_css_selector("a") \
                    if is_valid_link(link.get_attribute("href"))]

    urls += handle_url_list_js(urls, urls_on_page, parsed_response_url, follow_foreign_hosts)

    # get clickable elements
    handled_elements = []
    iterations = 0
    while iterations < 500:

        iterations += 1

        click_next_element, next_id, driver = find_next_clickable_element(driver, response.url, handled_elements, executable_path)

        if click_next_element is None:
            break

        handled_elements.append(next_id)

        new_urls_on_page, driver = get_new_urls_with_click(driver, click_next_element, next_id, base_url, executable_path)

        urls += handle_url_list_js(urls, new_urls_on_page, parsed_response_url, follow_foreign_hosts)

    driver.close()

    return urls
