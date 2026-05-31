import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
url = "https://tiki.vn/noi-nau-cham-1l-elmich-sce-8524ol-hang-chinh-hang-p273561794.html?spid=273594901" 
driver.get(url)
time.sleep(2)

limit = 100
data_list = []



try:
    while len(data_list) < limit:
        # Cuộn xuống để thấy phần bình luận và pagination
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
        time.sleep(2)

        try:
            # Đợi bình luận xuất hiện (giảm xuống 5 giây cho nhanh)
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".review-comment"))
            )
        except:
            print("Không tìm thấy thêm bình luận mới (Có thể đã hết trang).")
            break

        # Lấy các block bình luận
        reviews = driver.find_elements(By.CSS_SELECTOR, ".review-comment")
        new_items_found = 0
        for review in reviews:
            if len(data_list) >= limit:
                break
            try:
                name = review.find_element(By.CLASS_NAME, "review-comment__user-name").text
                content = review.find_element(By.CLASS_NAME, "review-comment__content").text
                data_list.append([name, content.replace("\n", " ")])
                new_items_found += 1
            except:
                continue

        print(f"Đã lấy được: {len(data_list)} bình luận")

        # --- PHẦN CẬP NHẬT: Click nút Next dựa trên HTML mới ---
        try:
            # Tìm thẻ a có class 'btn next' nằm trong phân đoạn pagination
            next_button = driver.find_element(By.CSS_SELECTOR, "a.btn.next")
            
            # Kiểm tra nếu nút Next có tồn tại thì click
            if next_button:
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3) # Đợi trang sau load
            # if "disabled" in next_button.get_attribute("class"):
            #     break
            else:
                break
        except Exception as e:
            print("Đã hết trang hoặc không thể chuyển trang tiếp theo.")
            break

finally:
    if data_list:
        # Lưu vào CSV
        with open('tiki_reviews.csv', mode='w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Người bình luận', 'Nội dung'])
            writer.writerows(data_list)
            driver.quit()


print(f"Hoàn thành! Đã lưu tổng cộng {len(data_list)} bình luận.")