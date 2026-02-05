import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Helper functions for common actions
def login(driver, username, password):
    driver.get("https://your-app-url.com/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "loginBtn").click()
    # Wait for successful login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dashboard"))
    )

def initiate_payment(driver, amount=100):
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    driver.find_element(By.ID, "paymentAmount").send_keys(str(amount))
    driver.find_element(By.ID, "confirmPaymentBtn").click()
    # Wait for payment auth screen
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "paymentAuthorization"))
    )

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.mark.high
def test_TC_001_verify_payment_authorization_timeout(driver):
    """
    TC-001: Verify Payment Authorization Timeout
    Preconditions: User must have a valid payment method configured.
    Priority: High
    """
    login(driver, username="testuser", password="password123")
    initiate_payment(driver)
    # Simulate inactivity for 10 minutes (use a shorter time for automation)
    time.sleep(5)  # Replace with 600 for real scenario; 5s for test/demo
    # Expect timeout warning and cancellation
    try:
        warning = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "timeoutWarning"))
        )
        assert "timeout" in warning.text.lower()
        cancel_msg = driver.find_element(By.ID, "authCancelledMsg")
        assert "authorization cancelled" in cancel_msg.text.lower()
    except Exception as e:
        pytest.fail(f"Timeout warning or cancellation message not found: {e}")

@pytest.mark.medium
def test_TC_002_ensure_no_timeout_for_active_user(driver):
    """
    TC-002: Ensure No Timeout for Active User
    Preconditions: User must have a valid payment method configured.
    Priority: Medium
    """
    login(driver, username="testuser", password="password123")
    initiate_payment(driver)
    # Simulate user activity for 15 minutes (shortened for automation)
    for _ in range(3):  # Replace 3 with 15 for real scenario
        driver.find_element(By.ID, "paymentAmount").click()
        time.sleep(2)
    # Check that timeout warning is NOT present
    elements = driver.find_elements(By.ID, "timeoutWarning")
    assert len(elements) == 0, "Timeout warning appeared despite user activity"

@pytest.mark.medium
def test_TC_003_validate_timeout_warning_message(driver):
    """
    TC-003: Validate Timeout Warning Message
    Preconditions: User must have a valid payment method configured.
    Priority: Medium
    """
    login(driver, username="testuser", password="password123")
    initiate_payment(driver)
    # Simulate inactivity for 9m50s (shortened for automation)
    time.sleep(3)  # Replace with 590 for real scenario
    # Observe warning message 10s before timeout
    try:
        warning = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "timeoutWarning"))
        )
        assert "10 seconds" in warning.text, "Warning does not mention 10 seconds before timeout"
    except Exception as e:
        pytest.fail(f"Timeout warning message not found: {e}")

@pytest.mark.high
def test_TC_004_verify_reauthorization_after_timeout(driver):
    """
    TC-004: Verify Re-authorization After Timeout
    Preconditions: User must have a valid payment method configured.
    Priority: High
    """
    login(driver, username="testuser", password="password123")
    initiate_payment(driver)
    # Wait for timeout (shortened for automation)
    time.sleep(5)  # Replace with actual timeout duration
    try:
        driver.find_element(By.ID, "timeoutWarning")
        driver.find_element(By.ID, "authCancelledMsg")
        # Attempt to re-initiate payment
        initiate_payment(driver)
        reauth_prompt = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "reauthPrompt"))
        )
        assert "re-authorize" in reauth_prompt.text.lower()
    except Exception as e:
        pytest.fail(f"Re-authorization prompt not found after timeout: {e}")

@pytest.mark.low
def test_TC_005_check_audit_log_for_timeout_events(driver):
    """
    TC-005: Check Audit Log for Timeout Events
    Preconditions: Admin access required; test user must be present.
    Priority: Low
    """
    # Login as admin
    login(driver, username="adminuser", password="adminpass")
    # Initiate payment as test user (simulate via admin panel or impersonation)
    driver.get("https://your-app-url.com/admin/impersonate?user=testuser")
    initiate_payment(driver)
    time.sleep(5)  # Wait for timeout (shortened)
    # Access audit log
    driver.get("https://your-app-url.com/admin/audit-log")
    try:
        audit_rows = driver.find_elements(By.XPATH, "//tr[contains(., 'timeout') and contains(., 'testuser')]")
        assert len(audit_rows) > 0, "Timeout event not found in audit log for test user"
    except Exception as e:
        pytest.fail(f"Audit log check failed: {e}")
