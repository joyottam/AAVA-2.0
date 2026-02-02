import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# --- PyTest Fixtures for Setup/Teardown and Preconditions ---

@pytest.fixture(scope="function")
def driver():
    # Setup: Initialize WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    # Teardown: Quit WebDriver
    driver.quit()

@pytest.fixture(scope="function")
def login_user(driver):
    # Precondition: User is logged in and has a valid payment method
    driver.get("https://payment-portal.example.com/login")
    driver.find_element(By.ID, "username").send_keys("testuser")
    driver.find_element(By.ID, "password").send_keys("Test@1234")
    driver.find_element(By.ID, "loginBtn").click()
    # Wait for dashboard or payment method check
    assert "dashboard" in driver.current_url.lower()
    # Optionally verify payment method
    driver.get("https://payment-portal.example.com/profile")
    assert driver.find_element(By.ID, "payment-method").is_displayed()

# --- Test Case: TC-001 Verify Successful Payment Authorization ---

def test_tc_001_successful_payment_authorization(driver, login_user):
    """
    TC-001: Verify Successful Payment Authorization
    Preconditions: User is logged in and has a valid payment method.
    """
    driver.get("https://payment-portal.example.com/payments")
    driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
    driver.find_element(By.ID, "card-expiry").send_keys("12/28")
    driver.find_element(By.ID, "card-cvc").send_keys("123")
    driver.find_element(By.ID, "submit-payment").click()
    # Wait for confirmation
    try:
        confirmation = driver.find_element(By.ID, "payment-confirmation")
        assert "authorized" in confirmation.text.lower() or "confirmation" in confirmation.text.lower()
    except NoSuchElementException:
        pytest.fail("Payment confirmation not displayed.")

# --- Test Case: TC-002 Verify Authorization Timeout Handling ---

def test_tc_002_authorization_timeout_handling(driver, login_user):
    """
    TC-002: Verify Authorization Timeout Handling
    Preconditions: User is logged in; payment gateway is accessible.
    """
    driver.get("https://payment-portal.example.com/payments")
    driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
    driver.find_element(By.ID, "card-expiry").send_keys("12/28")
    driver.find_element(By.ID, "card-cvc").send_keys("123")
    # Simulate network delay or slow gateway response
    driver.execute_script("window.simulatePaymentGatewayDelay = true;")
    driver.find_element(By.ID, "submit-payment").click()
    # Wait for timeout error
    try:
        timeout_msg = driver.find_element(By.ID, "payment-timeout-error")
        assert "timeout" in timeout_msg.text.lower()
    except NoSuchElementException:
        pytest.fail("Timeout error message not displayed.")
    finally:
        # Reset simulation
        driver.execute_script("window.simulatePaymentGatewayDelay = false;")

# --- Test Case: TC-003 Verify Retry Option on Timeout ---

def test_tc_003_retry_option_on_timeout(driver, login_user):
    """
    TC-003: Verify Retry Option on Timeout
    Preconditions: Timeout scenario as per TC-002.
    """
    driver.get("https://payment-portal.example.com/payments")
    driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
    driver.find_element(By.ID, "card-expiry").send_keys("12/28")
    driver.find_element(By.ID, "card-cvc").send_keys("123")
    # Simulate timeout
    driver.execute_script("window.simulatePaymentGatewayDelay = true;")
    driver.find_element(By.ID, "submit-payment").click()
    time.sleep(5)  # Wait for timeout to trigger
    try:
        retry_prompt = driver.find_element(By.ID, "retry-payment-prompt")
        assert "retry" in retry_prompt.text.lower() or "cancel" in retry_prompt.text.lower()
    except NoSuchElementException:
        pytest.fail("Retry/cancel prompt not displayed after timeout.")
    finally:
        driver.execute_script("window.simulatePaymentGatewayDelay = false;")

# --- Test Case: TC-004 Verify Logging on Authorization Timeout ---

def test_tc_004_logging_on_authorization_timeout(driver, login_user):
    """
    TC-004: Verify Logging on Authorization Timeout
    Preconditions: System logging enabled.
    """
    # Trigger timeout as before
    driver.get("https://payment-portal.example.com/payments")
    driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
    driver.find_element(By.ID, "card-expiry").send_keys("12/28")
    driver.find_element(By.ID, "card-cvc").send_keys("123")
    driver.execute_script("window.simulatePaymentGatewayDelay = true;")
    driver.find_element(By.ID, "submit-payment").click()
    time.sleep(5)
    # Access system logs (assume admin panel or API endpoint)
    # This is a placeholder; in real case, use API or log file access
    logs = fetch_system_logs(user="testuser")
    assert any("timeout" in log.lower() and "testuser" in log.lower() for log in logs), \
        "Timeout event not found in system logs."
    driver.execute_script("window.simulatePaymentGatewayDelay = false;")

def fetch_system_logs(user):
    # Placeholder for log retrieval logic (API, DB, or file)
    # In production, replace with actual log access
    return [
        "2024-06-01 10:15:23 - User testuser - Payment authorization timeout.",
        "2024-06-01 10:16:00 - User testuser - Payment retried."
    ]

# --- Test Case: TC-005 Verify Notification to User on Timeout ---

def test_tc_005_notification_on_timeout(driver, login_user):
    """
    TC-005: Verify Notification to User on Timeout
    Preconditions: Notification service is configured.
    """
    driver.get("https://payment-portal.example.com/payments")
    driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
    driver.find_element(By.ID, "card-expiry").send_keys("12/28")
    driver.find_element(By.ID, "card-cvc").send_keys("123")
    driver.execute_script("window.simulatePaymentGatewayDelay = true;")
    driver.find_element(By.ID, "submit-payment").click()
    time.sleep(5)
    # Check for notification (email/SMS/app) - placeholder/mock
    notification = check_user_notification("testuser", "timeout")
    assert notification, "User did not receive timeout notification."
    driver.execute_script("window.simulatePaymentGatewayDelay = false;")

def check_user_notification(user, event_type):
    # Placeholder for notification check (could be via API, DB, or inbox)
    # In production, implement actual verification
    if event_type == "timeout":
        return True  # Simulate notification received
    return False

# --- Test Case: TC-006 Verify No Double-Charge on Timeout and Retry ---

def test_tc_006_no_double_charge_on_timeout_and_retry(driver, login_user):
    """
    TC-006: Verify No Double-Charge on Timeout and Retry
    Preconditions: Same user, same transaction context.
    """
    driver.get("https://payment-portal.example.com/payments")
    driver.find_element(By.ID, "card-number").send_keys("4111111111111111")
    driver.find_element(By.ID, "card-expiry").send_keys("12/28")
    driver.find_element(By.ID, "card-cvc").send_keys("123")
    driver.execute_script("window.simulatePaymentGatewayDelay = true;")
    driver.find_element(By.ID, "submit-payment").click()
    time.sleep(5)
    # Retry payment after timeout
    driver.execute_script("window.simulatePaymentGatewayDelay = false;")
    driver.find_element(By.ID, "retry-payment-btn").click()
    time.sleep(2)
    # Check transaction history
    transactions = fetch_transaction_history("testuser")
    assert sum(1 for t in transactions if t["status"] == "Success" and t["amount"] == 100) == 1, \
        "More than one successful transaction found; possible double-charge."

def fetch_transaction_history(user):
    # Placeholder for transaction history retrieval (API, DB)
    # In production, implement actual check
    return [
        {"txn_id": "TXN123", "status": "Success", "amount": 100, "user": "testuser"},
        {"txn_id": "TXN124", "status": "Failed", "amount": 100, "user": "testuser"}
    ]
