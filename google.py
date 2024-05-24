from selenium import webdriver
from bs4 import BeautifulSoup
import os
import urllib.request
import time
from PIL import Image


def is_good_image(img_path):
    # Open the image file
    try:
        img = Image.open(img_path)
        width, height = img.size

        # Check image properties
        if width >= 200 and height >= 200 and width / height > 0.5:
            return True
    except Exception as e:
        print(f"Error processing image: {e}")
    return False


def crawl_image_urls(query, max_links_to_fetch):
    api_url = "https://search.naver.com/search.naver?ssc=tab.image.all&where=image&sm=tab_jum&query="
    url = api_url + '+'.join(query.split())

    # Initialize WebDriver with Chrome
    driver = webdriver.Chrome()
    driver.get(url)

    image_urls = set()
    image_count = 0

    # Scroll down to load more images
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust sleep time as needed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Parse HTML content after scrolling
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract image URLs
    for img in soup.find_all('img'):
        try:
            img_url = img['src']
            if img_url.startswith('http'):
                # Replace 'thumb' in the URL with 'full' to get high-resolution image
                img_url = img_url.replace('thumb', 'full')
                image_urls.add(img_url)
                image_count += 1
                if image_count >= max_links_to_fetch:
                    break
        except KeyError:
            pass

    driver.quit()  # Close the WebDriver

    return list(image_urls)


def download_images(folder_path, image_urls):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for i, url in enumerate(image_urls):
        try:
            img_path = os.path.join(folder_path, f"image_{i+1}.jpg")
            urllib.request.urlretrieve(url, img_path)

            # Check if the downloaded image is of good quality
            if is_good_image(img_path):
                print(f"Saved image image_{i+1}.jpg at {img_path}")
            else:
                os.remove(img_path)  # Delete low-quality image
                print(f"Deleted low-quality image: image_{i+1}.jpg")
        except Exception as e:
            print(f"Failed to save image image_{i+1}. Error: {e}")

# Main function to fetch and download images


def fetch_and_download_images(query, folder_path, max_images=50):
    image_urls = crawl_image_urls(query, max_images)
    download_images(folder_path, image_urls)
    print(
        f"Downloaded {len(image_urls)} images to the directory: {os.path.abspath(folder_path)}")


# Usage
query = "키워드"
folder_path = "키워드_images"
fetch_and_download_images(query, folder_path, max_images=150)

print("hi jeesu")
