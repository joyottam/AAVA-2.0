import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Fixtures for common preconditions ---

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login_and_cart(driver):
    # Step 1: Navigate to login page
    driver.get("https://your-ecommerce-app.com/login")
    # Step 2: Perform login (replace selectors and credentials as needed)
    driver.find_element(By.CSS_SELECTOR, "#username").send_keys("testuser")
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys("securePass123")
    driver.find_element(By.CSS_SELECTOR, "#loginBtn").click()
    # Step 3: Add items to cart
    driver.get("https://your-ecommerce-app.com/products")
    driver.find_element(By.CSS_SELECTOR, ".add-to-cart-btn").click()
    # Step 4: Ensure cart has items
    driver.get("https://your-ecommerce-app.com/cart")
    assert len(driver.find_elements(By.CSS_SELECTOR, ".cart-item")) > 0, "Cart is empty after adding item"
    return driver

@pytest.fixture(scope="function")
def valid_payment_method(driver):
    # Step 1: Navigate to payment methods
    driver.get("https://your-ecommerce-app.com/account/payment-methods")
    # Step 2: Ensure at least one valid payment method is configured
    if not driver.find_elements(By.CSS_SELECTOR, ".payment-method"):
        # Add a payment method if none exists (replace with actual steps)
        driver.find_element(By.CSS_SELECTOR, "#add-payment-method").click()
        driver.find_element(By.CSS_SELECTOR, "#card-number").send_keys("4111111111111111")
        driver.find_element(By.CSS_SELECTOR, "#expiry").send_keys("12/26")
        driver.find_element(By.CSS_SELECTOR, "#cvv").send_keys("123")
        driver.find_element(By.CSS_SELECTOR, "#save-method").click()
    assert driver.find_elements(By.CSS_SELECTOR, ".payment-method"), "No valid payment method configured"
    return driver

# --- Test Cases ---

def test_verify_payment_authorization_timeout(login_and_cart):
    """
    TC-001: Verify Payment Authorization Timeout
    Preconditions: User is logged in and has items in cart
    Steps:
        1. Navigate to the payment page
        2. Initiate a payment
        3. Do not complete authorization within the specified timeout period
    Expected Result: Payment process is cancelled and user is notified of timeout
    """
    driver = login_and_cart
    try:
        # Step 1: Navigate to payment page
        driver.get("https://your-ecommerce-app.com/checkout/payment")
        # Step 2: Initiate payment (simulate click)
        driver.find_element(By.CSS_SELECTOR, "#pay-now-btn").click()
        # Step 3: Wait for timeout (simulate inactivity)
        TIMEOUT_SECONDS = 35  # Replace with actual system timeout
        WebDriverWait(driver, TIMEOUT_SECONDS + 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#timeout-message"))
        )
        # Assert: Payment cancelled and timeout message shown
        timeout_msg = driver.find_element(By.CSS_SELECTOR, "#timeout-message").text
        assert "timeout" in timeout_msg.lower() or "session expired" in timeout_msg.lower(), \
            f"Expected timeout notification, got: '{timeout_msg}'"
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Test failed due to missing element or timeout: {e}")

def test_check_system_response_after_timeout(valid_payment_method, driver):
    """
    TC-002: Check System Response After Timeout
    Preconditions: Valid payment method configured
    Steps:
        1. Start payment authorization
        2. Wait for system-defined timeout to elapse
        3. Observe system behavior
    Expected Result: System displays timeout message and returns user to payment page
    """
    # Step 1: Start payment authorization
    driver.get("https://your-ecommerce-app.com/checkout/payment")
    driver.find_element(By.CSS_SELECTOR, "#pay-now-btn").click()
    # Step 2: Wait for timeout
    TIMEOUT_SECONDS = 35  # Replace with actual system timeout
    try:
        WebDriverWait(driver, TIMEOUT_SECONDS + 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#timeout-message"))
        )
        # Step 3: Assert timeout message and redirection
        timeout_msg = driver.find_element(By.CSS_SELECTOR, "#timeout-message").text
        assert "timeout" in timeout_msg.lower() or "session expired" in timeout_msg.lower(), \
            f"Expected timeout message, got: '{timeout_msg}'"
        # Check if user is redirected to payment page
        assert "payment" in driver.current_url, \
            f"User was not returned to payment page after timeout, current URL: {driver.current_url}"
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Test failed due to missing element or timeout: {e}")

def test_ensure_no_double_charge_on_timeout(login_and_cart):
    """
    TC-003: Ensure No Double Charge On Timeout
    Preconditions: User has valid account and payment method
    Steps:
        1. Initiate payment
        2. Allow timeout to occur
        3. Check transaction records
    Expected Result: No payment is processed and no double charge occurs
    """
    driver = login_and_cart
    # Step 1: Initiate payment
    driver.get("https://your-ecommerce-app.com/checkout/payment")
    driver.find_element(By.CSS_SELECTOR, "#pay-now-btn").click()
    # Step 2: Wait for timeout
    TIMEOUT_SECONDS = 35  # Replace with actual system timeout
    try:
        WebDriverWait(driver, TIMEOUT_SECONDS + 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#timeout-message"))
        )
        # Step 3: Check transaction records
        driver.get("https://your-ecommerce-app.com/account/transactions")
        transactions = driver.find_elements(By.CSS_SELECTOR, ".transaction-row")
        # Check for no new payment with today's date or duplicate charges
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        today_payments = [
            txn for txn in transactions
            if today in txn.text and "payment" in txn.text.lower()
        ]
        assert len(today_payments) == 0, \
            f"Unexpected payment(s) found after timeout: {[txn.text for txn in today_payments]}"
    except (NoSuchElementException, TimeoutException) as e:
        pytest.fail(f"Test failed due to missing element or timeout: {e}")
