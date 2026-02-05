import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Utility functions for setup and teardown
@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

# TC-001: Verify Payment Authorization Timeout
def test_verify_payment_authorization_timeout(driver):
    """
    Test Case ID: TC-001
    Title: Verify Payment Authorization Timeout
    Priority: High
    Created by: Joy Choudhury on 2026-01-05
    Preconditions: User is logged in and has a valid payment method.
    """
    # Step 1: Navigate to the payment page.
    driver.get("https://yourapp.com/payment")  # Replace with actual URL

    # Step 2: Initiate a payment transaction.
    try:
        driver.find_element(By.ID, "startPaymentBtn").click()
    except Exception as e:
        pytest.fail(f"Payment initiation failed: {e}")

    # Step 3: Wait for user inactivity for more than 5 minutes.
    # For automation, simulate with a shorter wait (e.g., 10 seconds).
    time.sleep(10)  # Replace with 300 for real scenario if feasible

    # Step 4: Observe the system response.
    try:
        timeout_page = driver.find_element(By.ID, "timeoutPage")
        assert timeout_page.is_displayed(), "Timeout page not displayed."
    except Exception as e:
        pytest.fail(f"Timeout not handled as expected: {e}")

# TC-002: Validate Timeout Warning Popup
def test_validate_timeout_warning_popup(driver):
    """
    Test Case ID: TC-002
    Title: Validate Timeout Warning Popup
    Priority: Medium
    Created by: Joy Choudhury on 2026-01-05
    Preconditions: User is on the payment authorization screen.
    """
    # Step 1: Start payment transaction.
    driver.get("https://yourapp.com/payment")  # Replace with actual URL
    try:
        driver.find_element(By.ID, "startPaymentBtn").click()
    except Exception as e:
        pytest.fail(f"Payment initiation failed: {e}")

    # Step 2: Remain inactive for 4 minutes (simulated as 8 seconds).
    time.sleep(8)  # Replace with 240 for real scenario

    # Step 3: Check for warning popup.
    try:
        warning_popup = driver.find_element(By.ID, "timeoutWarningPopup")
        assert warning_popup.is_displayed(), "Timeout warning popup not displayed."
        assert "imminent session timeout" in warning_popup.text.lower(), "Warning message text mismatch."
    except Exception as e:
        pytest.fail(f"Warning popup validation failed: {e}")

# TC-003: Ensure Payment Transaction Aborts After Timeout
def test_ensure_payment_transaction_aborts_after_timeout(driver):
    """
    Test Case ID: TC-003
    Title: Ensure Payment Transaction Aborts After Timeout
    Priority: High
    Created by: Joy Choudhury on 2026-01-05
    Preconditions: Valid user session; payment transaction initiated.
    """
    # Step 1: Start a payment transaction.
    driver.get("https://yourapp.com/payment")  # Replace with actual URL
    try:
        driver.find_element(By.ID, "startPaymentBtn").click()
    except Exception as e:
        pytest.fail(f"Payment initiation failed: {e}")

    # Step 2: Remain inactive for 6 minutes (simulated as 12 seconds).
    time.sleep(12)  # Replace with 360 for real scenario

    # Step 3: Attempt to resume transaction.
    try:
        resume_btn = driver.find_element(By.ID, "resumeTransactionBtn")
        resume_btn.click()
    except Exception as e:
        pytest.fail(f"Resume transaction button not found: {e}")

    # Expected: Transaction is aborted and user is notified of timeout.
    try:
        timeout_notification = driver.find_element(By.ID, "timeoutNotification")
        assert timeout_notification.is_displayed(), "Timeout notification not displayed."
        assert "transaction aborted" in timeout_notification.text.lower(), "Notification text mismatch."
    except Exception as e:
        pytest.fail(f"Timeout notification validation failed: {e}")
