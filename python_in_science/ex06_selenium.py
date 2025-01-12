import argparse
import json
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

parser = argparse.ArgumentParser(description="view top 10 shorts on youtube")
parser.add_argument(
    "file",
    nargs="?",
    default=sys.stdout,
    type=argparse.FileType("w"),
    help="path to file",
)
args = parser.parse_args()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--mute-audio")

driver = webdriver.Chrome(
    service=ChromiumService(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    ),
    options=chrome_options,
)
wait = WebDriverWait(driver, timeout=10)

driver.get("https://youtube.com/shorts")

spans = driver.find_elements(By.TAG_NAME, "span")
for span in spans:
    if span.get_attribute("innerText") == "Reject all":
        span.click()
        break

videos = []

for idx in range(4):
    print(idx)
    try:
        short = wait.until(EC.visibility_of_element_located((By.ID, f"{idx}")))
        driver.execute_script("arguments[0].scrollIntoView();", short)

        time.sleep(4)

        channel = short.find_element(
            By.CLASS_NAME,
            "YtReelChannelBarViewModelChannelName",
        )
        title = short.find_element(
            By.CLASS_NAME,
            "YtShortsVideoTitleViewModelHost",
        )
        music = short.find_element(
            By.CLASS_NAME,
            "ytReelSoundMetadataViewModelMarqueeContainer",
        )

    except StaleElementReferenceException:
        continue
    except NoSuchElementException:
        continue

    videos.append(
        dict(
            channel=channel.get_attribute("textContent"),
            title=title.get_attribute("textContent"),
            music=music.get_attribute("textContent") if music else None,
        )
    )


driver.quit()

json.dump(videos, args.file, ensure_ascii=False)
