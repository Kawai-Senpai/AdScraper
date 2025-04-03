from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

def scrape_page_details(url):
    
    # Load the URL
    driver.get(url)

    page_name_element = driver.find_element(By.XPATH, "//a[contains(@href, 'https://facebook.com/')]")
    page_link = page_name_element.get_attribute("href")
    page_name = page_name_element.text
    print(page_name)
    print(page_link)

    #open page
    driver.get(page_link)

    try:
        #get close button with aria-label="Close"
        close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Close']"))
        )
        close_button.click()
    except Exception as e:
        print(f"Error closing pop-up: {e}")

    try:
        #likes (https://www.facebook.com/fascatcoaching/friends_likes/)
        likes_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/friends_likes/')]"))
        )
        likes_text = likes_button.text
        print(likes_text)
    except Exception as e:
        print(f"Error getting likes: {e}")
        likes_text = None

    try:
        #followers (https://www.facebook.com/fascatcoaching/followers/)
        followers_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers/')]"))
        )
        followers_text = followers_button.text
        print(followers_text)
    except Exception as e:
        print(f"Error getting followers: {e}")
        followers_text = None

    try:
        #Review (https://www.facebook.com/fascatcoaching/reviews)
        reviews_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/reviews')]"))
        )
        reviews_text = reviews_button.text
        print(reviews_text)
    except Exception as e:
        print(f"Error getting reviews: {e}")
        reviews_text = None

    try:
        # get description
        description_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[1]/div/div/span")
        description = description_element.text
        print(description)
    except Exception as e:
        print(f"Error getting description: {e}")
        description = None

    try:
        # Person resonsible for the page
        person_responsible = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[2]/div[2]/div/div[1]/span")
        person_responsible_text = person_responsible.text
        print(person_responsible_text)
    except Exception as e:
        print(f"Error getting person responsible: {e}")
        person_responsible_text = None

    try:
        # get mobile number
        mobile_number = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[3]/div[2]/div/div/span")
        mobile_number_text = mobile_number.text
        print(mobile_number_text)
    except Exception as e:
        print(f"Error getting mobile number: {e}")
        mobile_number_text = None

    try: 
        # get email
        email = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[4]/div[2]/div/div/span")
        email_text = email.text
        print(email_text)
    except Exception as e:
        print(f"Error getting email: {e}")
        email_text = None

    try:
        # get website
        website = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/ul/div[5]/div[2]/div/a/div/div/span")
        website_text = website.text
        print(website_text)
    except Exception as e:
        print(f"Error getting website: {e}")
        website_text = None

    return {
        "page_name": page_name,
        "page_link": page_link,
        "likes": likes_text,
        "followers": followers_text,
        "reviews": reviews_text,
        "description": description,
        "person_responsible": person_responsible_text,
        "mobile_number": mobile_number_text,
        "email": email_text,
        "website": website_text
    }

def download_video(url, path="video.mp4"):

    # Load the URL
    driver.get(url)

    video_elements = driver.find_elements(By.TAG_NAME, "video")
    src = video_elements[0].get_attribute("src")
    print(src)

    # Download the video from the link
    response = requests.get(src, stream=True)
    with open(path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

    print(f"Video downloaded to {path}")
    return {
        "video_url": src,
        "download_path": path
    }

