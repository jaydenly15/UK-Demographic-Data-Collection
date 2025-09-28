from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrapeAvailableCensusDatasets(year):
    try:
        # Launch browser
        driver = webdriver.Chrome()
        url = f"https://www.nomisweb.co.uk/census/{year}/data_finder"
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(lambda d: any(ds.is_displayed() for ds in d.find_elements(By.CSS_SELECTOR, "div.datasetItem")))

        # 1. Get baseline count before applying filter
        initial_count = driver.execute_script("return document.querySelectorAll('div.datasetItem').length;")

        # 2. Apply filter on the page (whatever action you do: click, set text, etc.)
        if year == 2011:
            lsoa_filter = driver.find_element(By.ID, "rbtn8")
            driver.execute_script("arguments[0].click();", lsoa_filter)
        elif year == 2021:
            # Click the "LSOA" filter (radio button with value='level3c')
            lsoa_filter = driver.find_element(By.CSS_SELECTOR, "input[name='geoglevel'][value='level3c']")
            driver.execute_script("arguments[0].click();", lsoa_filter)

        # 3. Wait until the number of visible dataset items is less than before
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("""
                return Array.from(document.querySelectorAll('div.datasetItem'))
                    .filter(e => e.style.display !== 'none').length;
            """) < initial_count
        )
        
        # 4. Now scrape only the visible ones
        visible_dataset_ids = driver.execute_script("""
            return Array.from(document.querySelectorAll('div.datasetItem'))
                .filter(e => e.style.display !== 'none')
                .map(e => e.id);
        """)

        # Get all dataset elements (we’ll filter by ID)
        datasets = driver.find_elements(By.CSS_SELECTOR, "div.datasetItem")
        results = []

        for ds in datasets:
            dataset_id = ds.get_attribute("id")

            if dataset_id not in visible_dataset_ids:
                continue  # skip hidden datasets

            try:
                name_elem = ds.find_element(By.CSS_SELECTOR, "div.datasetItemName a")
                dataset_name = name_elem.text.strip()
            except NoSuchElementException:
                dataset_name = None

            try:
                code_elem = ds.find_element(By.CSS_SELECTOR, "div.datasetItemName span.datasetItemSubDescription")
                dataset_code = code_elem.text.strip().strip("[]")
            except NoSuchElementException:
                dataset_code = None

            results.append({
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "dataset_code": dataset_code
            })

        # Convert to pandas DataFrame
        df = pd.DataFrame(results)

        # Export to Parquet
        df.to_csv(f"datasets_lsoa_{year}.csv", index=False)
        print(f"datasets_lsoa_{year}.csv")
    except (NoSuchElementException, TimeoutException, WebDriverException) as e:
        print("Scraping error:", e)
    except Exception as e:
        print("Unexpected error:", e)
    finally:
        if driver:
            driver.quit()
            
scrapeAvailableCensusDatasets(2011)
scrapeAvailableCensusDatasets(2021)