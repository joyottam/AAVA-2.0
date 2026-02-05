import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

# TC-001: Verify Payment Authorization Timeout
def test_tc_001_verify_payment_authorization_timeout(driver):
    """
    Preconditions: User has valid payment method
    Priority: High | Created by: Joy Choudhury | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")  # Placeholder URL
    # Step 1: Navigate to Payment Portal
    # Already navigated above
    # Step 2: Initiate Payment
    driver.find_element(By.ID, "initiatePaymentBtn").click()  # Placeholder selector
    # Step 3: Wait for authorization response for 35 seconds
    try:
        WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
        )
        error_msg = driver.find_element(By.CSS_SELECTOR, ".timeout-error-msg").text
        assert "timeout" in error_msg.lower(), "Timeout error message not displayed"
    except Exception as e:
        pytest.fail(f"Timeout error message was not displayed: {e}")

# TC-002: Check Successful Payment Within Timeout
def test_tc_002_check_successful_payment_within_timeout(driver):
    """
    Preconditions: User has valid payment method
    Priority: Critical | Created by: Joy Choudhury | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Simulate completing authorization within 20 seconds
    # (Assume a modal appears; fill and submit quickly)
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "authModal"))
    )
    driver.find_element(By.ID, "authApproveBtn").click()
    # Assert payment is processed successfully
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".success-msg"))
    )
    success_msg = driver.find_element(By.CSS_SELECTOR, ".success-msg").text
    assert "success" in success_msg.lower(), "Payment was not processed successfully"

# TC-003: Validate Error Message on Timeout
def test_tc_003_validate_error_message_on_timeout(driver):
    """
    Preconditions: User session is active
    Priority: Medium | Created by: Joy Choudhury | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Do not respond to authorization; wait for timeout
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    error_msg = driver.find_element(By.CSS_SELECTOR, ".timeout-error-msg").text
    assert "authorization timeout" in error_msg.lower(), "Expected 'Authorization Timeout' error not shown"

# TC-004: Verify No Double Charge on Timeout
def test_tc_004_verify_no_double_charge_on_timeout(driver):
    """
    Preconditions: User initiates payment
    Priority: High | Created by: QA Analyst | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Let authorization timeout
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    # Check transaction records (navigate to account/transactions)
    driver.find_element(By.ID, "accountMenu").click()
    driver.find_element(By.ID, "transactionsTab").click()
    transactions = driver.find_elements(By.CSS_SELECTOR, ".transaction-row")
    # Assert no new charge posted
    for txn in transactions:
        assert "pending" not in txn.text.lower(), "Pending/double charge found after timeout"

# TC-005: Check Audit Log Entry for Timeout Event
def test_tc_005_check_audit_log_entry_for_timeout_event(driver):
    """
    Preconditions: Audit logging is enabled
    Priority: Medium | Created by: QA Analyst | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Trigger payment timeout
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    # Access audit log (admin panel)
    driver.get("https://payment-portal.example.com/admin/audit-log")
    audit_entries = driver.find_elements(By.CSS_SELECTOR, ".audit-entry")
    assert any("timeout" in entry.text.lower() for entry in audit_entries), "Timeout event not found in audit log"

# TC-006: Validate UI Feedback During Timeout
def test_tc_006_validate_ui_feedback_during_timeout(driver):
    """
    Preconditions: User is logged in
    Priority: Low | Created by: Joy Choudhury | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Progress indicator should be visible
    assert driver.find_element(By.CSS_SELECTOR, ".progress-indicator").is_displayed(), "Progress indicator not visible"
    # Wait for timeout message
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    assert not driver.find_element(By.CSS_SELECTOR, ".progress-indicator").is_displayed(), "Progress indicator still visible after timeout"
    assert driver.find_element(By.CSS_SELECTOR, ".timeout-error-msg").is_displayed(), "Timeout message not shown"

# TC-007: Verify System Recovery Post Timeout
def test_tc_007_verify_system_recovery_post_timeout(driver):
    """
    Preconditions: Previous payment timed out
    Priority: Medium | Created by: QA Analyst | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    # Attempt new payment
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".payment-form"))
    )
    assert driver.find_element(By.CSS_SELECTOR, ".payment-form").is_displayed(), "System did not allow new payment after timeout"

# TC-008: Test Authorization Timeout with Invalid Credentials
def test_tc_008_test_authorization_timeout_with_invalid_credentials(driver):
    """
    Preconditions: User account exists
    Priority: Low | Created by: Joy Choudhury | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Enter invalid credentials
    driver.find_element(By.ID, "authUser").send_keys("invalid_user")
    driver.find_element(By.ID, "authPass").send_keys("wrong_pass")
    driver.find_element(By.ID, "authSubmitBtn").click()
    # Wait for timeout
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    error_msg = driver.find_element(By.CSS_SELECTOR, ".timeout-error-msg").text
    assert "error" in error_msg.lower(), "Appropriate error not displayed for invalid credentials"

# TC-009: Check Timeout Handling for Multiple Concurrent Payments
def test_tc_009_check_timeout_handling_for_multiple_concurrent_payments(driver):
    """
    Preconditions: Multiple payment sessions are supported
    Priority: High | Created by: QA Analyst | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    # Initiate multiple payments (simulate with multiple tabs/windows)
    for i in range(2):
        driver.execute_script("window.open('https://payment-portal.example.com/', '_blank');")
    handles = driver.window_handles
    for handle in handles:
        driver.switch_to.window(handle)
        driver.find_element(By.ID, "initiatePaymentBtn").click()
    # Let all authorizations timeout
    for handle in handles:
        driver.switch_to.window(handle)
        WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
        )
        error_msg = driver.find_element(By.CSS_SELECTOR, ".timeout-error-msg").text
        assert "timeout" in error_msg.lower(), "Timeout not handled independently for each payment"

# TC-010: Verify Notification Sent on Timeout
def test_tc_010_verify_notification_sent_on_timeout(driver):
    """
    Preconditions: Notification service is enabled
    Priority: Medium | Created by: Joy Choudhury | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    # Check user notifications (notification bell or inbox)
    driver.find_element(By.ID, "notificationBell").click()
    notifications = driver.find_elements(By.CSS_SELECTOR, ".notification-item")
    assert any("timeout" in n.text.lower() for n in notifications), "No timeout notification received"

# TC-011: Validate Session Remains Active After Timeout
def test_tc_011_validate_session_remains_active_after_timeout(driver):
    """
    Preconditions: Session timeout is longer than payment timeout
    Priority: Low | Created by: QA Analyst | Created: 2026-01-05
    """
    driver.get("https://payment-portal.example.com/")
    driver.find_element(By.ID, "initiatePaymentBtn").click()
    WebDriverWait(driver, 40).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".timeout-error-msg"))
    )
    # Perform another action (e.g., navigate to dashboard)
    driver.find_element(By.ID, "dashboardMenu").click()
    assert driver.current_url.endswith("/dashboard"), "User session is not active after payment timeout"

# TC-012: Check API Response for Timeout
def test_tc_012_check_api_response_for_timeout():
    """
    Preconditions: API key is valid
    Priority: High | Created by: Joy Choudhury | Created: 2026-01-05
    """
    api_url = "https://api.payment-portal.example.com/payments"
    headers = {"Authorization": "Bearer <API_KEY>"}  # Replace <API_KEY> with valid key
    payload = {
        "amount": 100,
        "method": "card",
        "simulate_delay": True,
        "delay_seconds": 40
    }
    response = requests.post(api_url, json=payload, headers=headers, timeout=60)
    assert response.status_code == 408, f"Expected timeout status code 408, got {response.status_code}"
    assert "timeout" in response.text.lower(), "Timeout error not present in API response"
