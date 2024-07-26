import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

driver = webdriver.Chrome()

driver.get("https://tickets.paris2024.org/en/event/football-stade-de-lyon-18205097/?affiliate=24R")
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

event = driver.find_element(By.CLASS_NAME, "p-stage-headline").text
sessionInfo = driver.find_element(By.ID, "eventDescription").find_element(By.TAG_NAME, "p").text
dateTime = driver.find_elements(By.CLASS_NAME, "p-stage-list-item")[0].text
venue = driver.find_elements(By.CLASS_NAME, "p-stage-list-item")[1].text
ticketInfo = driver.find_element(By.CLASS_NAME, "js-p24-ctt-description-box").text
categories = driver.find_element(By.ID, "tickets").find_elements(By.CLASS_NAME, "p-card")


# print("Event:", event)
# print("Tickets session information:\n", sessionInfo)
# print("Date:", dateTime.split("|")[0].strip())
# print("Start Time:", dateTime.split("|")[1].strip().split("‒")[0].strip())
# print("End Time:", dateTime.split("|")[1].strip().split("‒")[1].strip())
# print("Stadium:", venue.split("|")[0].strip() )
# print("City:", venue.split("|")[1].strip() )
# print("Tickets selection information:", ticketInfo)



print("Categories:\n")
categories_list = []
for category in categories:
    category_form = category.find_element(By.TAG_NAME, "form")
    category_head = category_form.find_element(By.CLASS_NAME, "event-list-head").text

    try:
        show_button = category_form.find_element(By.CLASS_NAME, "ticket-type-link-show")
        show_button.click()
    except Exception:
        pass

    time.sleep(1)
    ticket_types = category_form.find_elements(By.CLASS_NAME, "ticket-type-item")
    ticket_types_list = []
    for ticket_type in ticket_types:
        ticket_type_title = ticket_type.find_element(By.CLASS_NAME, "ticket-type-title").text
        ticket_type_detail = ticket_type.find_element(By.CLASS_NAME, "ticket-type-detail").text
        ticket_type_availability = ticket_type.find_element(By.CLASS_NAME, "p-ticket-type-stepper").text
        availability = ""

        # print(ticket_type_availability)
        if ticket_type_availability == "0" and ticket_type.find_element(By.CLASS_NAME, "btn-stepper-right").is_enabled():
            availability = "Available"
        else:
            availability = "Currently not available"


        len(ticket_type_title) and ticket_types_list.append({"ticket_type_title":ticket_type_title, "ticket_type_detail":ticket_type_detail, "availability": availability})
    # time.sleep(4)
    categories_list.append(
        {
            "category_name": category_head,
            "ticket_types": ticket_types_list
        }
    )



   
print(json.dumps(categories_list))
# venue = WebDriverWait(driver, 2).until(
#             EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/main/section[2]/div/div/div[2]/div[3]/address/span/span"))).text
# tickets_cat = driver.find_element(By.CLASS_NAME, "js-cat-check").text


# print("Tickets Category information:", tickets_cat)



# time.sleep(15)
driver.quit()
