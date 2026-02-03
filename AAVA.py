import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def login(driver, username, password):
    driver.get("https://example.com/login")
    driver.find_element(By.CSS_SELECTOR, "#username").send_keys(username)
    driver.find_element(By.CSS_SELECTOR, "#password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#loginBtn").click()

def open_form_page(driver):
    driver.get("https://example.com/form")

def logout(driver):
    driver.find_element(By.CSS_SELECTOR, "#logoutBtn").click()

def test_TC_01_verify_login_with_valid_credentials(driver):
    """
    TC_01: Verify login with valid credentials
    Preconditions: Valid username/password
    Steps: Open URL; Enter valid username; Enter valid password; Click Login
    """
    login(driver, "valid_user", "valid_pass")
    assert driver.current_url.endswith("/dashboard")
    assert "Dashboard" in driver.title

def test_TC_02_verify_login_with_invalid_password(driver):
    """
    TC_02: Verify login with invalid password
    Preconditions: Invalid password
    Steps: Open URL; Enter valid username; Enter invalid password; Click Login
    """
    login(driver, "valid_user", "invalid_pass")
    error = driver.find_element(By.CSS_SELECTOR, "#errorMsg")
    assert error.is_displayed()
    assert "Error" in error.text

def test_TC_03_verify_login_with_empty_fields(driver):
    """
    TC_03: Verify login with empty fields
    Steps: Open URL; Click Login without entering data
    """
    driver.get("https://example.com/login")
    driver.find_element(By.CSS_SELECTOR, "#loginBtn").click()
    validation = driver.find_element(By.CSS_SELECTOR, "#validationMsg")
    assert validation.is_displayed()
    assert "required" in validation.text.lower()

def test_TC_04_verify_application_url_opens_in_browser(driver):
    """
    TC_04: Verify application URL opens in browser
    Preconditions: Application URL
    Steps: Launch Chrome; Enter application URL
    """
    driver.get("https://example.com/")
    assert "Example Application" in driver.title

def test_TC_05_verify_dashboard_link_navigation(driver):
    """
    TC_05: Verify dashboard link navigation
    Steps: Login; Click Dashboard link
    """
    login(driver, "valid_user", "valid_pass")
    driver.find_element(By.CSS_SELECTOR, "#dashboardLink").click()
    assert driver.current_url.endswith("/dashboard")
    assert "Dashboard" in driver.title

def test_TC_06_verify_broken_link_behavior(driver):
    """
    TC_06: Verify broken link behavior
    Preconditions: Link
    Steps: Click target link
    """
    driver.get("https://example.com/")
    driver.find_element(By.CSS_SELECTOR, "#targetLink").click()
    assert "404" not in driver.page_source
    assert driver.current_url != "about:blank"

def test_TC_07_submit_form_with_valid_data(driver):
    """
    TC_07: Submit form with valid data
    Preconditions: Valid form data
    Steps: Open form page; Enter valid details; Click Submit
    """
    open_form_page(driver)
    driver.find_element(By.CSS_SELECTOR, "#name").send_keys("Test User")
    driver.find_element(By.CSS_SELECTOR, "#email").send_keys("test@example.com")
    driver.find_element(By.CSS_SELECTOR, "#submitBtn").click()
    success = driver.find_element(By.CSS_SELECTOR, "#successMsg")
    assert success.is_displayed()
    assert "submitted successfully" in success.text.lower()

def test_TC_08_submit_form_with_empty_mandatory_fields(driver):
    """
    TC_08: Submit form with empty mandatory fields
    Steps: Open form page; Leave mandatory fields empty; Click Submit
    """
    open_form_page(driver)
    driver.find_element(By.CSS_SELECTOR, "#submitBtn").click()
    errors = driver.find_elements(By.CSS_SELECTOR, ".error")
    assert any(e.is_displayed() for e in errors)

def test_TC_09_verify_page_title(driver):
    """
    TC_09: Verify page title
    Steps: Open application
    """
    driver.get("https://example.com/")
    assert driver.title == "Expected Page Title"

def test_TC_10_verify_logo_visibility(driver):
    """
    TC_10: Verify logo visibility
    Steps: Open application
    """
    driver.get("https://example.com/")
    logo = driver.find_element(By.CSS_SELECTOR, "#logo")
    assert logo.is_displayed()

def test_TC_11_verify_logout_functionality(driver):
    """
    TC_11: Verify logout functionality
    Steps: Login; Click Logout
    """
    login(driver, "valid_user", "valid_pass")
    logout(driver)
    assert driver.current_url.endswith("/login")
    assert "Login" in driver.title
