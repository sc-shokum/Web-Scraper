from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import csv
import time

firefox_options = Options()
# firefox_options.add_argument("--headless")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument("--disable-dev-shm-usage")
firefox_options.add_argument("--disable-gpu")
driver = webdriver.Firefox(options=firefox_options)

def input_entity_name_and_search(entity_name):
    """
    Connects the driver to the URL, then inputs the query into search
    field then clicks the search button. If a captcha is detected, it 
    waits for the user to manually solve it and then again repeats the 
    search process.

    Args:
        entity_name (string): Name of the company
    """
    driver.get("https://icis.corp.delaware.gov/eCorp/EntitySearch/NameSearch.aspx")
    time.sleep(5)
    
    while True:
        try:
            entity_name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_frmEntityName"))
            )
            entity_name_field.clear()
            entity_name_field.send_keys(entity_name)
            
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnSubmit"))
            )
            search_button.click()
            time.sleep(5)
            print("Clicked search")
            
            captcha_present = False
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
                )
                captcha_present = True
                print("Captcha detecte, solve it.")
            except:
                captcha_present = False
            
            if captcha_present:
                while True:
                    try:
                        WebDriverWait(driver, 5).until_not(
                            EC.presence_of_element_located((By.CLASS_NAME, "g-recaptcha"))
                        )
                        print("Captcha solved.")
                        break
                    except:
                        print("Waiting for captcha to be solved...")
                        time.sleep(5)
                continue
            else:
                print("No captcha detected")
                return
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return
        
def check_and_extract_results()->bool:
    """
    Checks if the table after searching is empty or not. If it's
    empty then return false to initiate the searching process again.
    If it's true then one by one it clicks on the entity to find the
    details about the company and append the data to csv file.

    Returns:
        bool: True is the extracting of data was sucessfull, False otherwise.
    """
    print("Inside results")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tblResults")))
        
        rows = driver.find_elements(By.XPATH, "//table[@id='tblResults']/tbody/tr")
        
        if len(rows) <= 1:
            return False
        
        with open('entity_details.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["File Number", "Incorporation Date/Formation Date", "Entity Name", "Entity Kind", "Entity Type", "Residency", "State"])
            
            for i in range(1, len(rows)):
                try:
                    rows = driver.find_elements(By.XPATH, "//table[@id='tblResults']/tbody/tr")
                    columns = rows[i].find_elements(By.TAG_NAME, "td")
                    file_number = columns[0].text
                    entity_link = columns[1].find_element(By.TAG_NAME, "a")
                    entity_name = entity_link.text
                    entity_link.click()
                    time.sleep(3)
                    
                    details = extract_entity_details(file_number, entity_name)
                    writer.writerow(details.values())
                    
                    driver.back()
                    time.sleep(3)
                except Exception as e:
                    print(f"An error occurred while processing row {i}: {e}")
                    continue
        
        return True
    except Exception as e:
        print(f"An error occurred while extracting results: {e}")
        return False

def extract_entity_details(file_number, entity_name):
    """
    Extracts the data about the entity then coverts it to dictionary
    to append to csv file

    Args:
        file_number (int): Number of the entity
        entity_name (string): Name of the entity

    Returns:
        dictionary: Returns all the details about the entity including File Number,
        Formation date, Enitiy name, Entity kind, Entity type, Residency and State.
    """
    try:
        details = {
            "File Number": file_number,
            "Incorporation Date/Formation Date": "",
            "Entity Name": entity_name,
            "Entity Kind": "",
            "Entity Type": "",
            "Residency": "",
            "State": ""
        }
        
        details["Incorporation Date/Formation Date"] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblIncDate").text
        details["Entity Kind"] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblEntityKind").text
        details["Entity Type"] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblEntityType").text
        details["Residency"] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblResidency").text
        details["State"] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblState").text
        
        return details
    except Exception as e:
        print(f"An error occurred while extracting entity details: {e}")
        return {}

def start_scrapping(name):
    """
    Takes the name of the entity to search then calls the 
    input_entity_name_and_search() function to initiate the 
    search process. If the process fails for more than 3 times, 
    it stops the process. Finally, closes the driver.

    Args:
        name (string): name of the entity
    """
    try:
        entity_name = name
        input_entity_name_and_search(entity_name)
        time.sleep(5)
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            if check_and_extract_results():
                break
            else:
                print(f"Attempt {attempts + 1} failed. Retrying...")
                input_entity_name_and_search(entity_name)
                attempts += 1

    finally:
        driver.quit()

# sudo apt install lxde
# vim .bashrc 
# export DISPLAY: <window ip>:0
# source .bashrc 