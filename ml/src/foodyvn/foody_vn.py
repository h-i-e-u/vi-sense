import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Khởi tạo driver (Tự động tải driver phù hợp trong Selenium 4.6+)
driver = webdriver.Chrome()

# Truy cập URL
url = "https://foody.vn/ho-chi-minh/viet-huong-ga-nuong-lu/binh-luan"
driver.get(url)
time.sleep(5) # Đợi trang tải lần đầu

data_list = []
limit = 50

print("Đang lấy dữ liệu...")

while len(data_list) < limit:
    # Lấy danh sách các thẻ review hiện có trên trang
    reviews = driver.find_elements(By.CSS_SELECTOR, "li.review-item")
    
    # Chỉ xử lý các review mới (vượt quá số lượng đã lưu trong data_list)
    for review in reviews[len(data_list):]:
        if len(data_list) >= limit:
            break
        
        try:
            # Lấy các thông tin cơ bản
            username = review.find_element(By.CSS_SELECTOR, "a.ru-username").text.strip()
            rating = review.find_element(By.CSS_SELECTOR, ".review-points").text.strip()
            
            # Tiêu đề (có thể không có)
            try:
                title = review.find_element(By.CSS_SELECTOR, "a.rd-title").text.strip()
            except:
                title = ""
            
            # Nội dung bình luận
            description = review.find_element(By.CSS_SELECTOR, ".rd-des span").text.strip()
            
            data_list.append([username, rating, title, description])
            print(f"Đã lấy: {len(data_list)}/{limit}")
            
        except Exception:
            continue

    # Nếu chưa đủ 50, cuộn xuống để kích hoạt tải thêm (Lazy Load)
    if len(data_list) < limit:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Đợi dữ liệu mới được tải lên

# Lưu vào file CSV với utf-8-sig để tránh lỗi font khi mở bằng Excel
header = ['Người dùng', 'Điểm', 'Tiêu đề', 'Bình luận']
with open('foody_reviews_50.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data_list)

print(f"\nHoàn tất! Đã lưu {len(data_list)} đánh giá vào file 'foody_reviews_50.csv'.")
driver.quit()
