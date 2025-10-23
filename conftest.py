import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
logging.getLogger("WDM").setLevel(logging.WARNING)


@pytest.fixture
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--start-maximized")
    opts.add_argument("--lang=en-US")
    opts.add_experimental_option("prefs", {
        "intl.accept_languages": "en,en_US",
        "translate": {"enabled": False},
    })
    opts.add_argument("--incognito")

    d = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    yield d
    time.sleep(5)
    d.quit()

