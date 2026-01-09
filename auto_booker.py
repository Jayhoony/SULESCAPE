from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select 
import requests
import time
from datetime import datetime, timedelta

def get_now():
    return datetime.now().strftime('%H:%M:%S.%f')[:-3]

### 사전 설정
target_theme ="오모테나시"
# 지점 설정 (1: 홍대, 2: 인천, 3: 대구, 4: 부산)
TARGET_BRANCH = "4"
TARGET_DATE = "2026-01-21"
target_time = "12:25"
DIRECT_URL = "https://www.seoul-escape.com/reservation?branch=4&theme=&date=2026-01-14#list"
user_name = "성지훈"
user_phone = "010-2526-8883"
booking_people = "4" 
max_attempts= 2 #최대 시도 횟수
# [직링크 생성 로직] 입력받은 지점과 날짜를 기반으로 URL을 자동 생성합니다.
DIRECT_URL = f"https://www.seoul-escape.com/reservation?branch={TARGET_BRANCH}&theme=&date={TARGET_DATE}#list"
###


# 2. 크롬 디버깅 모드 연결 (로그인 유지용)
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options) 
wait = WebDriverWait(driver, 10)

# 3. 사전 접속
attempt = 1
success = False
print(f"[{get_now()}] 페이지 접속 시도...")
driver.get(DIRECT_URL)
xpath_expression = f"//section[contains(@class, 'res-item') and .//h3[contains(text(), '{target_theme}')]]"
found = False
while attempt <= max_attempts and not success:
    try:
        print(f"\n[{get_now()}] === {attempt}회차 시도 시작 ===")
        driver.get(DIRECT_URL) # 매 시도마다 페이지 새로고침
        
        # 1. 테마 및 시간 버튼 찾기
        theme_section = wait.until(EC.presence_of_element_located((By.XPATH, xpath_expression)))
        time_buttons = theme_section.find_elements(By.CSS_SELECTOR, "button.active1")
        
        found_and_clicked = False
        for btn in time_buttons:
            time_val = btn.find_element(By.CSS_SELECTOR, "span.ff-bhs").get_attribute("textContent").strip()
            print(f"[{get_now()}] 검사 중인 시간: {time_val}")
            
            if time_val == target_time:
                print(f"목표 시간 {time_val} 발견! 클릭합니다.")
                driver.execute_script("arguments[0].click();", btn)
                found_and_clicked = True
                break
        
        if not found_and_clicked:
            # 시간을 못 찾으면 에러를 발생시켜 except 구문(재시도)으로 보냄
            raise Exception(f"'{target_time}' 예약 가능 버튼을 찾을 수 없음")

        # 2. 예약 폼 입력 단계
        # 성함 입력
        name_input = wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        name_input.clear()
        name_input.send_keys(user_name)
        
        # 연락처 입력
        phone_input = driver.find_element(By.NAME, "phone")
        phone_input.clear()
        phone_input.send_keys(user_phone)
        
        # 인원 선택
        people_element = wait.until(EC.element_to_be_clickable((By.ID, "evePeople")))
        people_select = Select(people_element)
        people_select.select_by_value(str(booking_people))
        print(f"인원 {booking_people}명 선택 완료")
        
        # 동의 체크 (자바스크립트 클릭)
        policy_checkbox = driver.find_element(By.NAME, "policy")
        if not policy_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", policy_checkbox)
        
        # 3. 예약 완료 버튼 클릭 
        ## 수동으로 할꺼면 주석 처리 해주세요
        reserve_btn = wait.until(EC.element_to_be_clickable((By.ID, "eveReservationBtn")))
        reserve_btn.click()
        
        # 4. 최종 성공 여부 확인 (예: '예약취소/확인' 버튼이 있는 페이지로 이동했는지 확인)
        print(f"[{get_now()}] 예약 신청 버튼 클릭 완료!")
        success = True 

    except Exception as e:
        print(f"[{get_now()}] ⚠️ {attempt}회차 실패 사유: {e}")
        attempt += 1
        if attempt <= max_attempts:
            print(f"[{get_now()}] 1초 후 재시도합니다...")
            time.sleep(1)
        else:
            print(f"[{get_now()}] 최대 시도 횟수({max_attempts})를 초과했습니다.")

if success:
    print("-" * 30)
    print("매크로가 성공적으로 종료되었습니다.")