import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

def login_and_navigate(driver):
    """
    Helper to log in the user and navigate to the Payment module.
    Assumes login page and selectors are known.
    """
    driver.get("https://yourapp.example.com/login")
    # Replace with actual selectors and credentials
    driver.find_element(By.ID, "username").send_keys("testuser")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.ID, "loginBtn").click()
    # Wait for login to complete
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "paymentModuleLink"))
    )
    driver.find_element(By.ID, "paymentModuleLink").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "initiatePaymentBtn"))
    )

def trigger_payment_timeout(driver, amount="10000"):
    """
    Helper to initiate a payment that will trigger an authorization timeout.
    Assumes timeout occurs for high amounts or specific conditions.
    """
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    driver.find_element(By.ID, "amountField").clear()
    driver.find_element(By.ID, "amountField").send_keys(amount)
    driver.find_element(By.ID, "submitPaymentBtn").click()
    # Wait for timeout (simulate configured duration, e.g., 30s)
    timeout_duration = 30  # seconds, adjust as per config
    time.sleep(timeout_duration)

def test_verify_payment_authorization_timeout_trigger(driver):
    """
    TC-001: Verify Payment Authorization Timeout Trigger
    Preconditions: User is logged in; Payment module is accessible
    Steps:
      1. Navigate to Payment module
      2. Initiate a payment exceeding the authorization timeout threshold
      3. Wait for the configured timeout duration
    Expected Result: System displays a timeout error and payment is not authorized
    """
    login_and_navigate(driver)
    trigger_payment_timeout(driver)
    # Assert timeout error is displayed
    try:
        error_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "timeoutErrorMsg"))
        )
        assert "timeout" in error_elem.text.lower()
        # Optionally verify payment is not authorized (e.g., status label)
        status_elem = driver.find_element(By.ID, "paymentStatus")
        assert "not authorized" in status_elem.text.lower()
    except Exception as e:
        pytest.fail(f"Timeout error or status not displayed as expected: {e}")

def test_resubmit_payment_after_timeout(driver):
    """
    TC-002: Resubmit Payment After Timeout
    Preconditions: Payment previously timed out
    Steps:
      1. Trigger a payment timeout as per TC-001
      2. Attempt to resubmit the same payment
    Expected Result: System allows resubmission and processes payment if within limits
    """
    login_and_navigate(driver)
    trigger_payment_timeout(driver)
    # Attempt to resubmit payment
    try:
        resubmit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "resubmitPaymentBtn"))
        )
        resubmit_btn.click()
        # Optionally adjust amount to be within allowed limits
        amount_field = driver.find_element(By.ID, "amountField")
        amount_field.clear()
        amount_field.send_keys("500")  # within limit
        driver.find_element(By.ID, "submitPaymentBtn").click()
        # Assert payment processed
        success_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "paymentSuccessMsg"))
        )
        assert "processed" in success_elem.text.lower()
    except Exception as e:
        pytest.fail(f"Resubmission failed or payment not processed: {e}")

def test_verify_audit_logging_for_timeout_event(driver):
    """
    TC-003: Verify Audit Logging for Timeout Event
    Preconditions: Audit logging enabled
    Steps:
      1. Cause a payment authorization timeout
      2. Access the audit log/report
    Expected Result: Timeout event is logged with timestamp and user details
    """
    login_and_navigate(driver)
    trigger_payment_timeout(driver)
    # Access audit log
    try:
        driver.find_element(By.ID, "auditLogLink").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "auditLogTable"))
        )
        log_rows = driver.find_elements(By.CSS_SELECTOR, "#auditLogTable tr")
        found = False
        for row in log_rows:
            if "timeout" in row.text.lower() and "testuser" in row.text.lower():
                found = True
                # Optionally check for timestamp pattern
                assert any(char.isdigit() for char in row.text)
                break
        assert found, "Timeout event not found in audit log."
    except Exception as e:
        pytest.fail(f"Audit log verification failed: {e}")

def test_check_notification_on_payment_timeout(driver):
    """
    TC-004: Check Notification on Payment Timeout
    Preconditions: Notification service active
    Steps:
      1. Trigger a payment authorization timeout
      2. Check user notifications/messages
    Expected Result: User receives notification about the timeout event
    """
    login_and_navigate(driver)
    trigger_payment_timeout(driver)
    # Check notifications
    try:
        driver.find_element(By.ID, "notificationIcon").click()
        notif_items = driver.find_elements(By.CLASS_NAME, "notificationItem")
        found = False
        for item in notif_items:
            if "timeout" in item.text.lower():
                found = True
                break
        assert found, "Timeout notification not found."
    except Exception as e:
        pytest.fail(f"Notification check failed: {e}")

def test_verify_system_recovery_after_timeout(driver):
    """
    TC-005: Verify System Recovery After Timeout
    Preconditions: System reset after timeout
    Steps:
      1. Simulate a payment timeout
      2. Attempt a new payment transaction
    Expected Result: System processes new payment normally without residual timeout errors
    """
    login_and_navigate(driver)
    trigger_payment_timeout(driver)
    # Simulate system reset if required (e.g., logout/login)
    driver.refresh()
    login_and_navigate(driver)
    # Attempt a new payment
    try:
        driver.find_element(By.ID, "initiatePaymentBtn").click()
        driver.find_element(By.ID, "amountField").clear()
        driver.find_element(By.ID, "amountField").send_keys("250")
        driver.find_element(By.ID, "submitPaymentBtn").click()
        success_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "paymentSuccessMsg"))
        )
        assert "processed" in success_elem.text.lower()
    except Exception as e:
        pytest.fail(f"System did not recover properly: {e}")
