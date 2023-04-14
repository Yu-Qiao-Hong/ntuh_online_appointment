from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import datetime
import config
import ddddocr
import requests

def CheckConfig():
    begin = datetime.datetime.strptime(config.APPOINTMENT_BEGIN, '%Y/%m/%d')
    end = datetime.datetime.strptime(config.APPOINTMENT_END, '%Y/%m/%d')
    if begin > end:
        print('Appointment begin date is greater than end date')
        return (False, 'Appointment begin date is greater than end date')
    else:
        print('OK')
        return (True,'')

#config_res = CheckConfig()
#if config_res[0] == False:
#    print(config_res[1])

url = f'https://reg.ntuh.gov.tw/webadministration/DoctorServiceQueryByDrName.aspx?HospCode={config.HOSP_CODE}&QueryName={config.DOCTOR_NAME}'

chrome_options = Options()
# chrome_options.add_argument('--headless')  # 啟動無頭模式
chrome_options.add_argument('--disable-gpu')  # 規避google bug

driver = webdriver.Chrome(
    executable_path=config.CHROME_DRIVER_PATH, chrome_options=chrome_options)

driver.get(url)

link = None
while link == None:
    links = driver.find_elements(By.LINK_TEXT, '掛號')
    if (len(links) == 0):
        print(f'目前沒有可掛號的時段，稍後會重新嘗試...')
        time.sleep(config.RETRY_DELAY_SEC)
        driver.get(url)
    else:
        link = links[0]

link.click()

try:
    # 點選用身分證方式登入
    time.sleep(0.3)
    driver.find_element(By.XPATH, '//*[@id="radInputNum_0"]').click()

    # 輸入 ID
    time.sleep(0.3)
    id_text = driver.find_element(By.XPATH, '//*[@id="txtIuputID"]')
    id_text.send_keys(config.ID)

    # 年
    time.sleep(0.3)
    select_year = Select(driver.find_element(By.NAME, 'ddlBirthYear'))
    select_year.select_by_visible_text(config.BIRTH_YEAR)
    
    # 月
    time.sleep(0.3)
    select_month = Select(driver.find_element(By.NAME, 'ddlBirthMonth'))
    select_month.select_by_visible_text(config.BIRTH_MONTH)

    # 日
    time.sleep(0.3)
    select_day = Select(driver.find_element(By.NAME, 'ddlBirthDay'))
    select_day.select_by_visible_text(config.BIRTH_DAY)

    # Get verify code
    ocr = ddddocr.DdddOcr()
    image_url = driver.find_element(By.ID, 'imgVlid').get_attribute('src')
    img_content = requests.get(image_url,'lxml').content
    res = ocr.classification(img_content)

    # 輸入 verify code
    verify_code_text = driver.find_element(By.NAME, 'txtVerifyCode')
    verify_code_text.send_keys(res)

    # click OK
    ok_btn = driver.find_element(By.NAME, 'btnOK')
    ok_btn.click()

    #driver.find_element(By.ID, 'ErrorMessageText')

    print('預約成功')
    ShowTime = driver.find_element(By.ID, 'ShowTime').text
    print(f'時間：{ShowTime}')

    ShowDept = driver.find_element(By.ID, 'ShowDept').text
    print(f'科別：{ShowDept}')

    ShowClinic = driver.find_element(By.ID, 'ShowClinic').text
    print(f'診別：{ShowClinic}')

    ShowDt = driver.find_element(By.ID, 'ShowDt').text
    print(f'醫事人員：{ShowDt}')

    ShowLoc = driver.find_element(By.ID, 'ShowLoc').text
    print(f'看診地點：{ShowLoc}')

except Exception as e:
    print(f"預約失敗，重新進行預約，錯誤訊息: {e.msg}")
    driver.quit()
