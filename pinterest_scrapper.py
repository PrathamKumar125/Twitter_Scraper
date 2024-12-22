import logging
import time
import random
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager


# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PinterestScraper:
    def __init__(self, headless=False):
        self.setup_chrome_options(headless)
        self.setup_driver()

    def setup_chrome_options(self, headless):
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument('--headless=new')
        
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def setup_driver(self):
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.chrome_options
            )
            self.wait = WebDriverWait(self.driver, 30)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def safe_find_element(self, element, by, selector):
        """Safely find an element with error handling"""
        try:
            return element.find_element(by, selector)
        except Exception:
            return None

    def safe_get_attribute(self, element, attribute):
        """Safely get an attribute with error handling"""
        try:
            return element.get_attribute(attribute)
        except Exception:
            return None

    def extract_pin_data(self, element):
        """Extract data from a pin element with improved error handling"""
        try:
            pin_data = {
                'image_url': None,
                'alt_text': None
            }
            
            # Try to get image information
            img_element = self.safe_find_element(element, By.TAG_NAME, 'img')
            if img_element:
                pin_data['image_url'] = self.safe_get_attribute(img_element, 'src')
                pin_data['alt_text'] = self.safe_get_attribute(img_element, 'alt')

            # Ensure we have at least some data
            if not any(pin_data.values()):
                logger.warning("No data could be extracted from pin element")
                return None

            return pin_data
            
        except Exception as e:
            logger.error(f"Error extracting pin data: {str(e)}")
            return None

    def scrape_pins(self, search_query, max_pins=50):
        """Scrape Pinterest pins with improved error handling"""
        try:
            url = f'https://www.pinterest.com/search/pins/?q={search_query}&rs=typed'
            logger.info(f"Accessing URL: {url}")
            self.driver.get(url)
            
            # Initial wait for page load
            time.sleep(5)
            
            # Scroll to load more content
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
            
            # Try different selectors to find pins
            selectors = [
                "div[data-test-id='pin-wrapper']",
                "div[data-test-id='pin']",
                "div[data-test-id='pinrep']",
                "div[class*='Grid__Item']"
            ]
            
            elements = []
            for selector in selectors:
                try:
                    found_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_elements:
                        elements = found_elements
                        logger.info(f"Found {len(elements)} pins using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            if not elements:
                logger.warning("No pins found on the page")
                return []
            
            # Extract data from found elements
            pin_data = []
            for element in elements[:max_pins]:
                data = self.extract_pin_data(element)
                if data:
                    pin_data.append(data)
                    
                if len(pin_data) >= max_pins:
                    break
            
            return pin_data
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []

    def close(self):
        try:
            self.driver.quit()
            logger.info("WebDriver closed successfully")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")

def main():
    scraper = PinterestScraper(headless=False)
    try:
        pins = scraper.scrape_pins("business", max_pins=20)
        print(f"\nFound {len(pins)} pins:")
        
        # Define the CSV file name
        csv_file = 'pins.csv'
        
        # Define the CSV headers
        headers = ['image_url', 'alt_text']
        
        # Write data to CSV file
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for pin in pins:
                if pin:  # Only process if pin data exists
                    writer.writerow(pin)
        
        print(f"\nData saved to {csv_file}")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()