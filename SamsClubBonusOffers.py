from time import sleep
import argparse
import smtplib
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium.common import NoSuchElementException, TimeoutException
from undetected_chromedriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')
FROM_EMAIL = os.getenv('FROM_EMAIL')

SLEEP_TIME = 1
URL = "https://bonusoffers.samsclub.com/venues"

class SlowChrome(Chrome):
    def __init__(self, *args, **kwargs):
        super(SlowChrome, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        if item in ["get", "find_element"]:
            sleep(SLEEP_TIME)
        return super(SlowChrome, self).__getattribute__(item)

class SamsBonusOffersGrabber:
    def __init__(self, cmd_args):
        if cmd_args.no_prompt is None:
            self.email = input("Enter your email: ")
            self.password = getpass("Enter your password: ")
        else:
            self.email = cmd_args.no_prompt[0]
            self.password = cmd_args.no_prompt[1]

        options = ChromeOptions()
        self.driver = SlowChrome(options=options)

    def send_error_email(self, error_message):
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = 'Sams Club Bonus Offers Script Error'
        body = f"An error occurred while running the Sams Club Bonus Offers script:\n\n{error_message}"
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(FROM_EMAIL, TO_EMAIL, text)
            server.quit()
            print("Error email sent successfully.")
        except Exception as e:
            print(f"Failed to send error email: {e}")    

    def main(self):
        try:
            self.driver.get(URL)

            # Enter email
            try:
                self.driver.find_element(By.XPATH, "//input[@id='email']").send_keys(self.email)
            except (NoSuchElementException, TimeoutException):
                pass

            # Enter password
            try:
                self.driver.find_element(By.XPATH, "//input[@id='password']").send_keys(self.password)
                self.driver.find_element(By.XPATH, "//input[@id='password']").send_keys(Keys.ENTER)
                sleep(10)
            except (NoSuchElementException, TimeoutException):
                pass

            # Click on all buttons and handle pagination
            while True:
                self.click_all_buttons()
                sleep(3)
                if not self.go_to_next_page():
                    break
        except Exception as e:
            error_message = str(e)
            print(f"An error occurred: {error_message}")
            self.send_error_email(error_message)

    def click_all_buttons(self):
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button[@data-test-id='default-offer-tile']")
            print(f"Found {len(buttons)} buttons to click.")

            # If buttons found is 0, raise exception
            if len(buttons) == 0:
                raise NoSuchElementException("No buttons found to click.")

            for button in buttons:
                try:
                    # Check if the button has a child span with text "Get details"
                    span_elements = button.find_elements(By.XPATH, ".//span[text()='Get details']")
                    if span_elements:
                        print("Skipping button with 'Get details' span.")
                        continue

                    # Click the button if it does not have a 'Get details' span
                    button.click()
                    sleep(1)  # Adjust if necessary to avoid rate limits or other issues
                    self.dismiss_overlay()
                except Exception as e:
                    print(f"Failed to click a button: {e}")
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error finding buttons: {e}")

    def dismiss_overlay(self):
        try:
            self.driver.execute_script("document.elementFromPoint(window.innerWidth/2, window.innerHeight/2).click()")
            sleep(1)  # Adjust if necessary to ensure the overlay is dismissed
        except Exception as e:
            print(f"Failed to dismiss overlay: {e}")

    def go_to_next_page(self):
        try:
            pagination_controls = self.driver.find_elements(By.XPATH, "//li[@class='PaginationControl']")
            next_button = pagination_controls[1]
            next_button.click()
            print("Onto the next page")
            sleep(3)  # Adjust if necessary to wait for the next page to load
            return True
        except (NoSuchElementException, TimeoutException, IndexError) as e:
            print(f"No more pages to navigate or an error occurred: {e}")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-prompt", action="store", nargs=2)
    args = parser.parse_args()

    grabber = SamsBonusOffersGrabber(cmd_args=args)
    try:
        grabber.main()
    finally:
        grabber.driver.quit()
