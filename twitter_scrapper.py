import os
from time import sleep
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

my_user = os.getenv("TWITTER_USERNAME")
my_pass = os.getenv("TWITTER_PASSWORD")

search_item = "Business"

# Use ChromeDriverManager to automatically manage the ChromeDriver
service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service)
driver.get("https://twitter.com/i/flow/login")

# Wait for the username field to be present
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))

username = driver.find_element(By.NAME, "text")
username.send_keys(my_user)
username.send_keys(Keys.RETURN)

# Wait for the password field to be present
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))

password = driver.find_element(By.NAME, "password")
password.send_keys(my_pass)
password.send_keys(Keys.RETURN)

sleep(3)

# Scrape Tweets mentioning about Business
search_box = driver.find_element(By.XPATH, "//input[@data-testid='SearchBox_Search_Input']")
search_box.send_keys(search_item)
search_box.send_keys(Keys.ENTER)

all_tweets = set()

tweets = driver.find_elements(By.XPATH, "//div[@data-testid='tweetText']")
while True:
    for tweet in tweets:
        all_tweets.add(tweet.text)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    sleep(3)
    tweets = driver.find_elements(By.XPATH, "//div[@data-testid='tweetText']")
    if len(all_tweets) > 100:
        break

all_tweets = list(all_tweets)

# Save tweets to a .txt file
with open('tweets.txt', mode='w', encoding='utf-8') as file:
    for tweet in all_tweets:
        file.write(tweet + "\n")

print(f"Saved {len(all_tweets)} tweets to tweets.txt")
