import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server

# Path to your browsermob-proxy binary
BROWSERMOB_PATH = "browsermob-proxy/bin/browsermob-proxy"  # Adjust as needed

server = Server(BROWSERMOB_PATH)
server.start()
proxy = server.create_proxy()

chrome_options = Options()
chrome_options.add_argument(f"--proxy-server={proxy.proxy}")

driver = webdriver.Chrome(options=chrome_options)

try:
    proxy.new_har("meetup", options={"captureContent": True})
    driver.get("https://www.meetup.com/find/events/")

    # Wait for page to load
    time.sleep(5)

    # Try to find and click the search button (adjust selector as needed)
    try:
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_btn.click()
        print("Clicked search button.")
    except Exception as e:
        print("Could not find or click search button:", e)

    # Wait for network requests to complete
    time.sleep(10)

    # Parse HAR for gql2 requests
    entries = proxy.har["log"]["entries"]
    hashes = set()
    for entry in entries:
        url = entry["request"]["url"]
        if "/gql2" in url:
            try:
                post_data = entry["request"]["postData"]["text"]
                body = json.loads(post_data)
                op_name = body.get("operationName", "unknown")
                hash_val = (
                    body.get("extensions", {})
                    .get("persistedQuery", {})
                    .get("sha256Hash")
                )
                if hash_val:
                    hashes.add((op_name, hash_val))
            except Exception:
                continue

    print("Captured operationName and sha256Hash values:")
    for op, h in hashes:
        print(f"Operation: {op} | sha256Hash: {h}")

finally:
    driver.quit()
    proxy.close()
    server.stop()