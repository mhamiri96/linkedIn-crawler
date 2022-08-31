#selenium library for crawling and recieveing data also browser automation
import time
import logging #for committing logs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3 #library for connecting to database and executing sql commands with python
#-------------------------------------------------------------------------------------#
def login(username,pass1):
    "setup of web browser and signing up of linkedin account of user"
    #we use chrome as default web browser for this project
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    #the login page of linkedin
    browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    #This can be useful when certain elements on the webpage are not available immediately and need some time to load
    browser.implicitly_wait(1)
    #Open the webbrowser and use it for autonomous control
    Username=browser.find_element(By.NAME,"session_key")
    #Send username details
    Username.send_keys(username)
    #Find password
    password=browser.find_element(By.NAME,"session_password")
    #Send password details
    password.send_keys(pass1)
    #Submit button
    browser.find_element(By.XPATH,"//button[@type='submit']").click()
    return browser

def find_current_user(browser):
    "finding user's name and occupation"
    temp=[]
    browser.implicitly_wait(10)
    #finding user's name
    temp.append(browser.find_element(By.XPATH, "//div[@class='t-16 t-black t-bold']").text)
    #finding user's occupation
    temp.append(browser.find_element(By.XPATH, "//p[@class='identity-headline t-12 t-black--light t-normal mt1']").text)
    temp.append("")
    return temp

def find_other_users(browser,temp):
    "finding connections of user"
    people_temp = []
    browser.find_element(By.XPATH, "//a[@href='https://www.linkedin.com/mynetwork/?']").click()
    browser.implicitly_wait(5)
    browser.find_element(By.XPATH, "//a[@href='/mynetwork/invite-connect/connections/']").click()
    #finding number of connections which is greater than 40, we must scroll down to find others
    people_temp = browser.find_elements(By.CLASS_NAME, "mn-connection-card__details")
    SCROLL_PAUSE_TIME = 1.5
    last_height = browser.execute_script("return document.body.scrollHeight")
    if len(people_temp)>=40:
        while True:
            #scrolling down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #waiting to load page
            time.sleep(SCROLL_PAUSE_TIME)
            #calculating new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                #waiting for <show more result> button to appear
                el = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH,
                "//button[@class='artdeco-button artdeco-button--muted artdeco-button--1 "
                "artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button']")))
                el.click()
                break
            last_height = new_height
        browser.implicitly_wait(10)
        time.sleep(2)
    #finding all connections
    people_temp = browser.find_elements(By.CLASS_NAME, "mn-connection-card__details")
    people=[]
    #removing unnecessary elements and preparing a list for inserting into databse
    for i in range(len(people_temp)):
        people.append(people_temp[i].text.splitlines())
        people[i].remove("Member’s name")
        people[i].remove("Member’s occupation")
        people[i][2] = people[i][2].replace("Connected ", "")
    people.insert(0,temp)
    return people

def database_connection(list):
    """creates linkedin database (linkedin.db file) which has user info (first row) and info of user's connections which are consist
    of connection's name, occupation and how long they know each other"""
    con = sqlite3.connect('linkedin.db')
    print("Opened database successfully")
    cur = con.cursor()
    cur.execute("CREATE TABLE linkedIn(MemberName, MemberOccupation, ConnectionTime)")
    cur.executemany("INSERT INTO linkedIn VALUES (?,?,?)", list)
    con.commit()
    con.close()

if __name__ == '__main__':
    username=input("username: ")
    password=input("password: ")
    logging.basicConfig(filename="linkedin.log",level=logging.DEBUG,format="%(asctime)s %(message)s")
    logging.debug("Logging test...")
    logging.info("The program is working as expected")
    logging.warning("The program may not function properly")
    logging.error("The program encountered an error")
    logging.critical("The program crashed")
    browser=login(username,password)
    temp=find_current_user(browser)
    list_of_people=find_other_users(browser,temp)
    database_connection(list_of_people)


