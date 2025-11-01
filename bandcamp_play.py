# ------------------------------------------------------------
# 🧩 필수 설치 안내
# ------------------------------------------------------------
# 1️⃣ Python 패키지 설치
#     pip install selenium
#
# 2️⃣ Chrome 브라우저 설치
#     - Windows/macOS: https://www.google.com/chrome
#     - Ubuntu: sudo apt install google-chrome-stable
#
# 3️⃣ ChromeDriver 설치 (브라우저 제어용 드라이버)
#     - macOS: brew install chromedriver
#     - Ubuntu: sudo apt install chromium-chromedriver
#     - Windows:
#         https://googlechromelabs.github.io/chrome-for-testing/
#         (설치된 Chrome 버전과 동일한 chromedriver.exe 다운로드 후 PATH 등록)
#
# ⚠️ 위 3개가 준비되어야 아래 코드가 정상 동작합니다!
# ------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

# ------------------------------------------------------------
# 쿠키창 닫기 함수 (다양한 지역/언어 버전 대응)
# ------------------------------------------------------------
def close_cookie_popup(driver):
    """Bandcamp 쿠키 동의 팝업 닫기 (모든 버전 대응)"""
    try:
        # 1️⃣ 기본 '필수 쿠키만 허용' 버튼
        cookie_btn = driver.find_element(By.CSS_SELECTOR, "#cookie-control-dialog button.g-button.outline")
        driver.execute_script("arguments[0].click();", cookie_btn)
        print("✅ 쿠키창 닫음 (필수 쿠키만 허용)")
        return
    except NoSuchElementException:
        pass

    try:
        # 2️⃣ 영어권 버전 (Accept All)
        accept_all = driver.find_element(By.XPATH, "//button[contains(., 'Accept')]")
        driver.execute_script("arguments[0].click();", accept_all)
        print("✅ 쿠키창 닫음 (Accept All)")
        return
    except NoSuchElementException:
        pass

    try:
        # 3️⃣ 여전히 안 닫히면 숨기기
        overlay = driver.find_element(By.ID, "cookie-control-dialog")
        driver.execute_script("arguments[0].style.display='none';", overlay)
        print("⚙️ 팝업이 안 닫혀서 강제 숨김 처리")
    except Exception:
        print("ℹ️ 쿠키 팝업 없음 또는 이미 닫힘")

# ------------------------------------------------------------
# Chrome 옵션 설정
# ------------------------------------------------------------
BANDCAMP_DISCOVER_URL = "https://bandcamp.com/discover/"

options = Options()
# options.add_argument("--headless")   # GUI 숨기려면 주석 해제
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)

# ------------------------------------------------------------
# 사이트 접속 및 쿠키창 닫기
# ------------------------------------------------------------
driver.get(BANDCAMP_DISCOVER_URL)
time.sleep(2)
close_cookie_popup(driver)

# ------------------------------------------------------------
# 트랙 목록 수집
# ------------------------------------------------------------
tracks = driver.find_elements(By.CLASS_NAME, "results-grid-item")
if not tracks:
    print("❌ 트랙을 찾지 못했습니다. 페이지 로딩 실패.")
    driver.quit()
    exit()

first_track = tracks[0]

# ------------------------------------------------------------
# 트랙 정보 추출
# ------------------------------------------------------------
album = first_track.find_element(By.CSS_SELECTOR, "div.meta a strong").text
artist = first_track.find_element(By.CSS_SELECTOR, "div.meta a span").text
genre = first_track.find_element(By.CSS_SELECTOR, "div.meta p.genre").text if len(first_track.find_elements(By.CSS_SELECTOR, "div.meta p.genre")) else "Unknown"
url = first_track.find_element(By.CSS_SELECTOR, "div.meta a").get_attribute("href")

print("\n🎧 재생할 트랙 정보:")
print(f"  앨범: {album}")
print(f"  아티스트: {artist}")
print(f"  장르: {genre}")
print(f"  URL: {url}\n")

# ------------------------------------------------------------
# Play 버튼 강제 클릭 (투명 오버레이 방지 + 상태 확인)
# ------------------------------------------------------------
try:
    play_button = first_track.find_element(By.CSS_SELECTOR, "button.play-pause-button")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", play_button)
    time.sleep(0.5)

    # 1️⃣ 기본 클릭 시도
    try:
        play_button.click()
        print("▶️ 일반 클릭으로 재생 시도")
    except Exception:
        # 2️⃣ 실패 시 JS 강제 클릭
        driver.execute_script("arguments[0].click();", play_button)
        print("⚙️ JS 강제 클릭으로 재생 시도")

    # 3️⃣ aria-label 확인으로 재생 상태 체크
    time.sleep(2)
    label = play_button.get_attribute("aria-label")
    if "Pause" in label:
        print("✅ 재생 성공: 음악이 플레이 중입니다!")
    else:
        print(f"❌ 재생 실패 (현재 상태: {label})")

except Exception as e:
    print("❌ Play 버튼 클릭 실패:", e)

# ------------------------------------------------------------
# 30초 동안 재생 유지
# ------------------------------------------------------------
play_time = 30
for i in range(play_time):
    print(f"🎶 재생 중... {i+1}/{play_time}초", end="\r")
    time.sleep(1)

# ------------------------------------------------------------
# 재생 정지
# ------------------------------------------------------------
try:
    driver.execute_script("arguments[0].click();", play_button)
    print(f"\n⏸️ '{album}' 재생 정지 완료.")
except Exception:
    print("\n⚠️ 정지 클릭 실패.")

# ------------------------------------------------------------
# ‘View more’ 버튼 강제 클릭
# ------------------------------------------------------------
try:
    wait = WebDriverWait(driver, 20)
    button = wait.until(EC.presence_of_element_located((By.ID, "view-more")))
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    driver.execute_script("arguments[0].removeAttribute('disabled');", button)
    driver.execute_script("arguments[0].click();", button)
    print("✅ '더 보기(View more)' 버튼 강제 클릭 완료")
    time.sleep(5)
except Exception as e:
    print("❌ 더 보기 클릭 실패:", e)

# ------------------------------------------------------------
# 트랙 개수 확인 후 종료
# ------------------------------------------------------------
tracks_after = driver.find_elements(By.CLASS_NAME, "results-grid-item")
print(f"🎵 클릭 후 트랙 수: {len(tracks_after)}")

driver.quit()
print("🧹 브라우저 종료 완료")
