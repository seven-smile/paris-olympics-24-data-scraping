import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

driver = webdriver.Chrome()

driver.get("https://tickets.paris2024.org/en/search/?affiliate=24R")
driver.maximize_window()

try:
    queue = driver.find_element(By.CLASS_NAME, "progress")
    if queue.is_displayed():
        print("Queue is displayed, waiting for 30 seconds.")
        time.sleep(30)
    else:
        print("Queue is not displayed.")
except NoSuchElementException:
    print("Queue did not appear this time")

try:
    cookies = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "cmpwelcomebtnno"))
    )
    cookies.click()
    print("Cookies button clicked.")
except TimeoutException:
    print("Cookies element not found")

title = driver.title
print("Page title:", title)

#do not remove this sleep command. page maytake a few seconds to load records
time.sleep(5)

summary = []
page = 1

def scrape_page():

    try:
        all_items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "product-item")))

        for index in range(len(all_items)):
            headline = all_items[index].find_element(By.ID, f"listing-headline-{index}").text
            description = all_items[index].find_element(By.CLASS_NAME, f"listing-description").text
            data_Time_venue = all_items[index].find_element(By.CLASS_NAME, f"listing-subheadline").text
            price = all_items[index].find_element(By.TAG_NAME, f"p24-listing-cta").find_element(By.TAG_NAME, 'event-status').text

            print("\n")

            # Print scraped data
            # print("Event:", headline)
            # print("Description:", description)
            # print("Date, Time and Venue:", data_Time_venue )
            # print("Price:", price)
            print("total:",len(summary), "| index:",index, "| page:", page )

            dtv = data_Time_venue.split("|")

            all_items[index].click()
            event = {
                    "index": len(summary),
                    "headline": headline,
                    "description": description,
                    "date": dtv[0].strip(),
                    "start_time": dtv[1].strip().split("-")[0].strip(),
                    "end_time": dtv[1].strip().split("-")[1].strip(),
                    "city": dtv[2].strip(),
                    "venue": dtv[3].strip(),
                    "price": price,
                }
            
            try:
                close_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/serp-modal/div[2]/button")))
                close_button.click()

            except Exception as e:
                details = extract_FullDetail()
                event["details"] = details
                driver.back()

            summary.append(event)
            
            all_items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "product-item")))


    except Exception as e:
        print(e)


def extract_FullDetail():
    details = {}
    event = driver.find_element(By.CLASS_NAME, "p-stage-headline").text
    sessionInfo = driver.find_element(By.ID, "eventDescription").find_element(By.TAG_NAME, "p").text
    dateTime = driver.find_elements(By.CLASS_NAME, "p-stage-list-item")[0].text
    venue = driver.find_elements(By.CLASS_NAME, "p-stage-list-item")[1].text
    ticketInfo = driver.find_element(By.CLASS_NAME, "js-p24-ctt-description-box").text
    categories = driver.find_element(By.ID, "tickets").find_elements(By.CLASS_NAME, "p-card")

    details["event"] = event
    details["ticket_session_info"] = sessionInfo
    details["date"] = dateTime.split("|")[0].strip()
    details["start_time"] = dateTime.split("|")[1].strip().split("‒")[0].strip()
    details["end_time"] = dateTime.split("|")[1].strip().split("‒")[1].strip()
    details["stadium"] = venue.split("|")[0].strip()
    details["city"] = venue.split("|")[1].strip()
    details["ticket_selection_info"] = ticketInfo

    categories_list = []
    for category in categories:
        category_form = category.find_element(By.TAG_NAME, "form")
        category_head = category_form.find_element(By.CLASS_NAME, "event-list-head").text

        try:
            show_button = category_form.find_element(By.CLASS_NAME, "ticket-type-link-show")
            show_button.click()
        except Exception:
            pass

        ticket_types = category_form.find_elements(By.CLASS_NAME, "ticket-type-item")
        ticket_types_list = []
        for ticket_type in ticket_types:
            ticket_type_title = ticket_type.find_element(By.CLASS_NAME, "ticket-type-title").text
            ticket_type_detail = ticket_type.find_element(By.CLASS_NAME, "ticket-type-detail").text
            ticket_type_availability = ticket_type.find_element(By.CLASS_NAME, "p-ticket-type-stepper").text
            availability = ""

            if ticket_type_availability == "0" and ticket_type.find_element(By.CLASS_NAME, "btn-stepper-right").is_enabled():
                availability = "Available"
            else:
                availability = "Currently not available"


            len(ticket_type_title) and ticket_types_list.append({"ticket_type_title":ticket_type_title, "ticket_type_detail":ticket_type_detail, "availability": availability})
        categories_list.append(
            {
                "category_name": category_head,
                "ticket_types": ticket_types_list
            }
        )



     # Print scraped data
    
    details["categories"] = categories_list

    return details
    # print("Event:", event)
    # print("Tickets session information:\n", sessionInfo)
    # print("Date:", dateTime.split("|")[0].strip())
    # print("Start Time:", dateTime.split("|")[1].strip().split("‒")[0].strip())
    # print("End Time:", dateTime.split("|")[1].strip().split("‒")[1].strip())
    # print("Stadium:", venue.split("|")[0].strip() )
    # print("City:", venue.split("|")[1].strip() )
    # print("Tickets selection information:", ticketInfo)

    


    
# detail_click = driver.find_element(By.CLASS_NAME, "p-btn")
# detail_click.click()
while True:
    scrape_page()

    try:
        pagination_block = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagination-block"))
        ).find_elements(By.TAG_NAME, "pagination-item")

        next_button = pagination_block[len(pagination_block) - 1].find_element(By.TAG_NAME, "a")

        next_button.click()
        page+=1
    except Exception as e:
        break

with open("summary.json", "w") as file: 
    json.dump(summary, file, indent=1)


time.sleep(15)
driver.quit()
