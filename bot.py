import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def create_webdriver(options):
    try:
        return webdriver.Chrome(options=options)
    except WebDriverException as e:
        logging.error(f"Error initializing WebDriver: {e}")
        raise

def book_milford_sound_walk(config, retries=3):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    wait_time = config.get('wait_time', 20)

    for attempt in range(retries):
        driver = None
        try:
            driver = create_webdriver(options)
            wait = WebDriverWait(driver, wait_time)  # Configurable wait time for dynamic content

            logging.info("Opening booking page...")
            driver.get(config['booking_url'])

            logging.info("Filling out the search form...")

            # Assuming there are inputs for date, number of people, etc.
            date_field = wait.until(EC.presence_of_element_located((By.NAME, "Date")))
            date_field.clear()
            date_field.send_keys(config['desired_date'])

            num_people_field = wait.until(EC.presence_of_element_located((By.NAME, "NumPeople")))
            num_people_field.clear()
            num_people_field.send_keys(str(config['number_of_people']))

            # Click search button
            search_button = wait.until(EC.element_to_be_clickable((By.ID, "searchButton")))
            search_button.click()

            # Wait for the search results to load and select a slot
            logging.info("Waiting for search results...")
            time_slot_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//input[@value='{config['desired_time_slot']}']")))
            time_slot_option.click()

            # Click the next button to proceed to booking
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "nextButton")))
            next_button.click()

            # Fill out user details in the booking form
            logging.info("Filling out user details...")
            for field, value in config['user_details'].items():
                input_element = wait.until(EC.presence_of_element_located((By.NAME, field)))
                input_element.clear()
                input_element.send_keys(value)

            # Submit the booking form
            logging.info("Submitting the booking form...")
            submit_button = wait.until(EC.element_to_be_clickable((By.ID, "submitButton")))
            submit_button.click()

            # Wait for and log the confirmation message
            logging.info("Waiting for confirmation...")
            confirmation_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "confirmationMessage")))
            logging.info(f"Booking confirmed: {confirmation_message.text}")
            break  # Exit the loop if booking is successful

        except TimeoutException as e:
            logging.error(f"Timeout occurred on attempt {attempt + 1}/{retries}: {e}")
        except NoSuchElementException as e:
            logging.error(f"Element not found: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            if driver:
                logging.info("Closing the WebDriver...")
                driver.quit()

        if attempt < retries - 1:
            logging.info("Retrying...")
        else:
            logging.error("Max retries reached. Booking failed.")

if __name__ == "__main__":
    config = load_config('config.json')
    book_milford_sound_walk(config)
