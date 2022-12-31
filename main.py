from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

url = 'https://www.stfrancismedicalcenter.com/find-a-provider/'


def get_driver():
  options = Options()
  options.page_load_strategy = 'none'
  options.add_argument('--no-sandbox')
  options.add_argument('--headless')
  options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=options)
  return driver


def convert2list(string):
  li = list(string.split(","))
  return li


def convert2string(s):
  str1 = ""
  for ele in s:
    str1 += ele
    str1 += ','
  return str1


# Driver code


def get_arr(driver):
  tag = 'ProviderCard__Wrapper-sc-161r76h-0'

  driver.get(url)
  time.sleep(2)
  driver.maximize_window()
  time.sleep(2)
  previous_height = driver.execute_script('return document.body.scrollHeight')
  while True:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(2)
    new_height = driver.execute_script('return document.body.scrollHeight')
    if new_height == previous_height:
      break
    previous_height = new_height

  time.sleep(3)
  # driver.close()
  arr = driver.find_elements(By.CLASS_NAME, tag)
  return arr


def parse_arr(arr_item, driver):
  name = arr_item.find_element(By.TAG_NAME, 'b').text
  specialities = arr_item.find_element(By.CLASS_NAME, 'center').find_element(
    By.TAG_NAME, 'b').text
  specialities_arr = convert2list(specialities)
  speciality = specialities_arr[0]
  additional_sp = ''
  if (len(specialities_arr) > 1):
    additional_sp = convert2string(specialities_arr[1:len(specialities_arr)])

  loc = arr_item.find_elements(By.CLASS_NAME,
                               'center')[2].find_element(By.TAG_NAME, 'b').text
  loc_details = convert2list(loc)
  details_url = arr_item.find_element(By.TAG_NAME, 'a').get_attribute('href')

  options = Options()
  options.page_load_strategy = 'none'
  options.add_argument('--no-sandbox')
  options.add_argument('--headless')
  options.add_argument('--disable-dev-shm-usage')
  driver2 = webdriver.Chrome(options=options)

  driver2.get(details_url)
  time.sleep(2)
  address = ''
  phone = ''
  state = ''
  if len(loc_details) > 1:
    state = loc_details[1]

  if (len(
      driver2.find_elements(By.CLASS_NAME,
                            'LocationsDetails__Wrapper-sc-1pryox8-0')) > 0):
    add_tag = driver2.find_element(
      By.CLASS_NAME, 'LocationsDetails__Wrapper-sc-1pryox8-0').find_elements(
        By.TAG_NAME, 'span')
    if len(add_tag) != 0:
      address = add_tag[0].text

  if (len(driver2.find_elements(By.CLASS_NAME, 'inline')) > 0):
    phone_tag = driver2.find_element(By.CLASS_NAME, 'inline').find_elements(
      By.TAG_NAME, 'span')
    if len(phone_tag) != 0:
      phone = phone_tag[0].text

  return {
    'FULL NAME': name,
    'SPECIALITY': speciality,
    'ADDITIONAL-SPECIALITY': additional_sp,
    'ADDRESS': address,
    'CITY': loc_details[0],
    'STATE': state,
    'PHONE': phone,
    'PROFILE_URL': details_url,
  }


if __name__ == "__main__":

  print('Creating driver')
  driver = get_driver()

  print('Fetching data....please wait')
  arr = get_arr(driver)

  print(f'Found {len(arr)} entries')
  print('Storing entries in a CSV File....please wait')
  doctors_data = [parse_arr(item, driver) for item in arr]
  doctors_df = pd.DataFrame(doctors_data)
  # optns = {}
  # optns['strings_to_formulas'] = False
  # optns['strings_to_urls'] = False
  # writer = pd.ExcelWriter('/data.xlsx',engine='xlsxwriter',options=optns)

  doctors_df.to_csv('data.csv', index=False)

  print(len(doctors_data), "entries stored in data.csv file")
