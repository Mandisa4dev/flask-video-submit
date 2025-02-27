import json
import os
import base64
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 🔹 Secure Encryption for Login Credentials
KEY_FILE = "secret.key"
LOGIN_FILE = "logins.json"

# ✅ Generate a key for encryption (run once)
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

# ✅ Load the encryption key
def load_key():
    return open(KEY_FILE, "rb").read()

# ✅ Encrypt Data
def encrypt_data(data):
    key = load_key()
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()

# ✅ Decrypt Data
def decrypt_data(data):
    key = load_key()
    cipher = Fernet(key)
    return cipher.decrypt(data.encode()).decode()

# ✅ Load or create login credentials file
def load_logins():
    if os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, "r") as file:
            return json.load(file)
    return {}

def save_logins(logins):
    with open(LOGIN_FILE, "w") as file:
        json.dump(logins, file, indent=4)

# ✅ Function to get login details (stores them securely)
def get_login_details(site):
    logins = load_logins()
    
    if site in logins:
        return decrypt_data(logins[site]["username"]), decrypt_data(logins[site]["password"])
    
    username = input(f"Enter your username for {site}: ")
    password = input(f"Enter your password for {site}: ")

    logins[site] = {
        "username": encrypt_data(username),
        "password": encrypt_data(password)
    }
    
    save_logins(logins)
    return username, password

# 🔹 Automate Login & Video Submission with Selenium
def submit_video_with_login(site, login_url, video_url, username_field, password_field, submit_field):
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(login_url)

    # Enter Login Details
    username, password = get_login_details(site)
    driver.find_element(By.NAME, username_field).send_keys(username)
    driver.find_element(By.NAME, password_field).send_keys(password, Keys.RETURN)
    time.sleep(3)  # Wait for login

    # Submit Video (Assuming there's a single input field for video URL)
    driver.find_element(By.NAME, submit_field).send_keys(video_url, Keys.RETURN)
    time.sleep(3)  # Wait for submission

    print(f"✅ Video submitted on {site}")
    driver.quit()

# 🔹 Direct Submission Without Login
def submit_video_direct(site, submit_url, video_url):
    import requests

    response = requests.post(submit_url, data={"video": video_url})
    
    if response.status_code == 200:
        print(f"✅ Video submitted successfully on {site}")
    else:
        print(f"❌ Failed to submit on {site}")

# 🔹 Example Websites (Modify These)
websites = [
    {
        "site": "Reddit",
        "login_required": True,
        "login_url": "https://www.reddit.com/login/",
        "username_field": "username",
        "password_field": "password",
        "submit_field": "video_link"
    },
    {
        "site": "Dailymotion",
        "login_required": False,
        "submit_url": "https://www.dailymotion.com/upload"
    }
]

# 🔹 Run Automation
generate_key()  # Ensure encryption key exists
video_url = input("Enter your YouTube video link: ")

for site in websites:
    if site["login_required"]:
        submit_video_with_login(
            site["site"], site["login_url"], video_url, 
            site["username_field"], site["password_field"], site["submit_field"]
        )
    else:
        submit_video_direct(site["site"], site["submit_url"], video_url)
