import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import re
import time
import sys


def get_job_post_links_linkedin(job_keyword, location, scrolls):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10) # seconds
    driver.get('https://linkedin.com/jobs/search')

    # Insert search keyword and location
    driver.implicitly_wait(10)
    keyword_find = driver.find_element(By.XPATH, "//input[@name='keywords']")
    location_find = driver.find_element(By.XPATH, "//input[@name='location']")
    keyword_find.send_keys(job_keyword)
    location_find.clear()
    location_find.send_keys(location)
    location_find.send_keys(Keys.RETURN)
    time.sleep(10)
    search_url = driver.current_url
    driver.get(search_url)

    # WebPage scrolling automation
    counter = 0

    while counter < scrolls:
        counter += 1
        html = driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.HOME)
        html.send_keys(Keys.END)
        driver.implicitly_wait(10)
        if counter >= 6:
            try:
                driver.find_element(By.XPATH, '//button[@class="infinite-scroller__show-more-button infinite-scroller__show-more-button--visible"]').click()
            except:
                continue
        time.sleep(3)

    '''all job post links'''
    links = []
    elems = driver.find_elements(By.XPATH, "//a[@class='base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]']")
    for elem in elems:
        links.append(elem.get_attribute("href"))
    original_stdout = sys.stdout
    with open('stack_database_links.txt', mode='a', encoding='utf-8') as my_file:
        for link in links:
            if link not in my_file:
                sys.stdout = my_file
                print(link)
                sys.stdout = original_stdout
    return links


def get_stack(job_keyword, location, scrolls):
    links = get_job_post_links_linkedin(job_keyword, location, scrolls)

    python_counter = 0
    sql_counter = 0
    aws_counter = 0
    git_counter = 0
    r_counter = 0

    job_posts_counter = 0
    for link in links:
        res = requests.get(link)
        soup = BeautifulSoup(res.text, 'html.parser')
        post = soup.find('div', {'class': "show-more-less-html__markup"})
        if post:
            checker = 0
            if re.findall(r'(?i)(?<!\w)Python(?!\w)', post.text):
                python_counter += 1
                checker = 1
            if re.findall(r'(?i)(?<!NO)sql(?!\w)', post.text):
                sql_counter += 1
                checker = 1
            if re.findall(r'(?i)(?<!\w)aws', post.text):
                aws_counter += 1
                checker = 1
            if re.findall(r'(?i)(?<!\w)git(?!\w)', post.text):
                git_counter += 1
                checker = 1
            if re.findall(r'(?i)(?<!\w)r(?!\w)', post.text):
                r_counter += 1
                checker = 1
            if checker == 1:
                job_posts_counter += 1

            # with open('stack.txt', mode='a', encoding='utf-8') as my_file:
            #     my_file.write(post.text)

    stack_counter = {'Python': python_counter,
                     'SQL': sql_counter,
                     'AWS': aws_counter,
                     'Git': git_counter,
                     'R': r_counter
                     }

    return stack_counter, job_posts_counter


# search_link = 'https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=Polen&locationId=&geoId=105072130&f_TPR=&position=1&pageNum=0'

stack_counter, job_posts_counter = get_stack('Data Analyst', 'Poland', scrolls=8)
# print(f'Number of stack mentions in {job_posts_counter} job posts: {stack_counter}')
original_stdout = sys.stdout
with open('stack_database_type.txt', mode='a', encoding='utf-8') as my_file:
    sys.stdout = my_file
    print(f'Number of stack mentions in {job_posts_counter} job posts: {stack_counter}')
    sys.stdout = original_stdout

'''Test of function'''
# with open('stack.txt', mode='w', encoding='utf-8') as my_file:
#     for job_description in stack_counter:
#         my_file.write(job_description)



