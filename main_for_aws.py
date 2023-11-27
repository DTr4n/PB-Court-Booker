import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# GLOBAL VARIABLES
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]


def book_slot(driver: 'WebDriver', desired_slot_time : str) -> bool:
    """
    Book the desired time slot.
    Args:
        driver (WebDriver): The web driver to use for booking.
        desired_slot_time (str): The time slot to book.
    Returns:
        bool: True if the slot was successfully booked, False otherwise.
    """

    # Order of courts to try booking
    courts = [3, 2, 4, 1]
    for i in courts:
        print("Court", i)
        court_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".text-primary:nth-child({i}) > .text-primary")))
        court_button.click()

        time.sleep(1)

        # Find all booking slot items
        booking_slots = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".booking-slot-item")))

        # Iterate over the booking slot items
        for slot in booking_slots:
            slot_text = slot.find_element(By.TAG_NAME, "strong").text
            print(slot_text)
            button = slot.find_element(By.TAG_NAME, "button")

            if button.text == "Book Now" and slot_text == desired_slot_time:
                print("Found")
                button.click()
                # Wait for the page to refresh
                WebDriverWait(driver, 10).until(EC.staleness_of(button))
                return True

    return False


def run(desired_slot_text: list) -> None:
    """
    Runs the automated process to book pickleball courts at UC Irvine.
    Args:
        desired_slot_text (list): A list of strings representing the desired time slots to book.
    """

    # Create a new instance of the Chrome driver
    chrome_options = Options()
    chrome_service = Service("/opt/chromedriver")
    chrome_options.binary_location = '/opt/chrome/chrome'
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280x1696")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument('--user-data-dir=/tmp/chrome-user-data')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)

    # Navigate to the website
    driver.get("https://my.campusrec.uci.edu/booking/e06954a1-5e89-4d78-abcd-995ddb8249fb")

    time.sleep(1)

    # Enter Username
    username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtEmailUsernameLogin")))
    username_field.send_keys(USERNAME)

    # Click on the "Next" button
    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnNextSignInFirst")))
    next_button.click()

    time.sleep(1)

    # Enter Password
    password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtSignInPassword")))
    password_field.send_keys(PASSWORD)

    # Click on the "Sign In" button
    sign_in_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnSignIn")))
    sign_in_button.click()

    # Store the sign-in state (cookies or tokens)
    sign_in_cookies = driver.get_cookies()

    # Refresh the page
    driver.refresh()

    # Restore the sign-in state (add cookies)
    for cookie in sign_in_cookies:
        driver.add_cookie(cookie)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Click on the furthest available date
    date_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".date-selector-btn-secondary:nth-child(3)")))
    date_button.click()

    time.sleep(1)

    # Book the desired time slots
    for time_slot in desired_slot_text:
        book_slot(driver, time_slot)

    # Close the browser
    driver.quit()


def handler(event, context) -> None:
    """
    Lambda handler function.
    Args:
        event: The event data.
        context: The context data.
    """

    run(event["desired_slot_text"])