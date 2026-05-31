# crawling 1 page on foody.vn

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
url = "https://www.foody.vn/ho-chi-minh/viet-huong-ga-nuong-lu/binh-luan"
driver.get(url)
time.sleep(5)

limit = 100
data_list = []

print("Bắt đầu quá trình tải bình luận...")

while True:
    # Đếm số lượng review hiện có trên trang
    reviews = driver.find_elements(By.CSS_SELECTOR, "li.review-item")
    current_count = len(reviews)
    print(f"Hiện có: {current_count} bình luận trên trang.")

    if current_count >= limit:
        print("Đã load đủ số lượng yêu cầu.")
        break

    try:
        # Tìm nút "Xem thêm"
        btn_more = driver.find_element(By.CSS_SELECTOR, "a.fd-btn-more")
        
        # Kiểm tra nếu nút đang ẩn hoặc đang loading (dựa vào style hoặc class)
        if "ng-hide" in btn_more.get_attribute("class") or not btn_more.is_displayed():
            print("Nút 'Xem thêm' đã bị ẩn (có thể đã hết bình luận).")
            break

        # Sử dụng JavaScript để click trực tiếp (tránh lỗi ElementClickInterceptedException)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_more)
        time.sleep(5)
        driver.execute_script("arguments[0].click();", btn_more)
        
        # Đợi một chút để dữ liệu mới đổ về
        time.sleep(5) 
        
    except Exception as e:
        # Nếu không tìm thấy nút bằng find_element, thử cuộn trang nhẹ để kích hoạt script của trang
        driver.execute_script("window.scrollBy(0, -200);")
        print("Đang đợi thêm dữ liệu hoặc thử tìm lại nút...")
        time.sleep(5)
        # Nếu vẫn không thấy sau khi thử lại, có thể thực sự đã hết
        try:
            btn_more = driver.find_element(By.CSS_SELECTOR, "a.fd-btn-more")
        except:
            print("Kết thúc: Không tìm thấy nút 'Xem thêm'.")
            break

# Tiến hành lấy dữ liệu sau khi đã load đủ
reviews = driver.find_elements(By.CSS_SELECTOR, "li.review-item")
for review in reviews[:limit]:
    try:
        user = review.find_element(By.CSS_SELECTOR, "a.ru-username").text.strip()
        score = review.find_element(By.CSS_SELECTOR, ".review-points").text.strip()
        
        try:
            title = review.find_element(By.CSS_SELECTOR, "a.rd-title").text.strip()
        except:
            title = ""
            
        # Lấy description từ thẻ span ng-bind-html
        desc = review.find_element(By.CSS_SELECTOR, ".rd-des span").text.strip()
        
        data_list.append([user, score, title, desc])
    except:
        continue

# Lưu file
with open('foody_50.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['User', 'Rating', 'Title', 'Comment'])
    writer.writerows(data_list)

print(f"Hoàn thành! Đã lưu {len(data_list)} bình luận.")
driver.quit()
