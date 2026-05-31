import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

def parse_review_count(text):
    text = text.lower().strip().replace(',', '')
    try:
        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        nums = ''.join(filter(str.isdigit, text))
        return int(nums) if nums else 0
    except:
        return 0

def crawl_foody():
    filename = "foody_reviews_full_text.csv"
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Tên quán', 'Link', 'Nội dung Review'])

    try:
        driver.get("https://www.foody.vn/ho-chi-minh/dia-diem")
        wait = WebDriverWait(driver, 10)
        
        count_item = 0
        limit_item = 40
        reviews_per_item = 100

        while count_item < limit_item:
            items = driver.find_elements(By.CSS_SELECTOR, "div.row-item.filter-result-item")
            
            if count_item >= len(items):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(3)
                continue

            item = items[count_item]
            
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                time.sleep(1)

                stats = item.find_elements(By.CSS_SELECTOR, ".stats a span:not(.fa)")
                if not stats or parse_review_count(stats[0].text) <= 50:
                    count_item += 1
                    continue

                res_name = item.find_element(By.CSS_SELECTOR, ".resname h2 a").text.strip()
                res_link = item.find_element(By.CSS_SELECTOR, ".resname h2 a").get_attribute("href")
                
                print(f"--- Đang xử lý: {res_name} ---")

                # Mở popup
                driver.execute_script("arguments[0].click();", stats[0])
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fd-btn-close")))
                time.sleep(2)

                # 1. Click nút "Xem thêm bình luận" (Load More) cho đủ số lượng
                while True:
                    rev_elements = driver.find_elements(By.CSS_SELECTOR, ".rd-des span.ng-binding")
                    if len(rev_elements) >= reviews_per_item:
                        break
                    
                    load_more_btn = driver.find_elements(By.CSS_SELECTOR, "a.fd-btn-more")
                    if load_more_btn and load_more_btn[0].is_displayed():
                        driver.execute_script("arguments[0].click();", load_more_btn[0])
                        time.sleep(2)
                    else:
                        break

                # 2. Xử lý case "Xem thêm" (Toggle nội dung dài) cho từng review
                # Tìm tất cả các nút "Xem thêm" hiện có trong popup
                view_more_toggles = driver.find_elements(By.CSS_SELECTOR, "a.view-more")
                if view_more_toggles:
                    print(f"   Đang mở rộng {len(view_more_toggles)} review dài...")
                    for toggle in view_more_toggles:
                        try:
                            # Chỉ click nếu nút đang hiển thị
                            if toggle.is_displayed():
                                driver.execute_script("arguments[0].click();", toggle)
                        except:
                            continue
                    time.sleep(1) # Chờ text bung ra hết

                # 3. Thu thập dữ liệu sau khi đã bung hết nội dung
                rev_elements = driver.find_elements(By.CSS_SELECTOR, ".rd-des span.ng-binding")
                reviews_collected = [r.text.strip().replace('\n', ' ') for r in rev_elements if r.text.strip()]

                # Ghi vào CSV
                with open(filename, 'a', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    for r_text in reviews_collected[:reviews_per_item]:
                        writer.writerow([res_name, res_link, r_text])
                
                print(f"   Xong: {len(reviews_collected[:reviews_per_item])} reviews.")

                # Đóng popup
                close_btn = driver.find_element(By.CLASS_NAME, "fd-btn-close")
                driver.execute_script("arguments[0].click();", close_btn)
                time.sleep(1.5)
                
                count_item += 1

            except Exception as e:
                print(f"   Lỗi: {e}")
                try:
                    close_btn = driver.find_elements(By.CLASS_NAME, "fd-btn-close")
                    if close_btn: driver.execute_script("arguments[0].click();", close_btn[0])
                except: pass
                count_item += 1
                time.sleep(2)

    finally:
        driver.quit()

if __name__ == "__main__":
    crawl_foody()