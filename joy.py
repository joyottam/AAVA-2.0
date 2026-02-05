import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def login_and_prepare(driver):
    driver.get(os.environ.get("APP_URL") + "/login")
    driver.find_element(By.ID, "username").send_keys(os.environ.get("TEST_USERNAME"))
    driver.find_element(By.ID, "password").send_keys(os.environ.get("TEST_PASSWORD"))
    driver.find_element(By.ID, "loginBtn").click()
    assert "dashboard" in driver.current_url

@pytest.mark.high
def test_verify_payment_authorization_timeout_trigger(driver):
    login_and_prepare(driver)
    driver.get(os.environ.get("APP_URL") + "/payment")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    time.sleep(5 * 60)  # Simulate timeout (optimize for test speed as needed)
    try:
        timeout_msg = driver.find_element(By.ID, "timeoutMessage")
        assert "timeout" in timeout_msg.text.lower()
        assert driver.find_element(By.ID, "paymentStatus").text.lower() == "cancelled"
    except NoSuchElementException:
        pytest.fail("Timeout message or payment cancellation not displayed.")

@pytest.mark.medium
def test_resume_payment_after_timeout(driver):
    login_and_prepare(driver)
    driver.get(os.environ.get("APP_URL") + "/payment")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    time.sleep(5 * 60)
    driver.refresh()
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    try:
        restart_prompt = driver.find_element(By.ID, "restartPaymentPrompt")
        assert "restart" in restart_prompt.text.lower()
    except NoSuchElementException:
        pytest.fail("Restart payment prompt not displayed after timeout.")

@pytest.mark.critical
def test_verify_no_charges_on_timeout(driver):
    login_and_prepare(driver)
    driver.get(os.environ.get("APP_URL") + "/payment")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    time.sleep(5 * 60)
    driver.get(os.environ.get("APP_URL") + "/transactions")
    try:
        transactions = driver.find_elements(By.CSS_SELECTOR, ".transaction-row")
        for txn in transactions:
            status = txn.find_element(By.CLASS_NAME, "status").text.lower()
            assert status != "completed" and status != "charged"
    except NoSuchElementException:
        pass  # No transactions; test passes
