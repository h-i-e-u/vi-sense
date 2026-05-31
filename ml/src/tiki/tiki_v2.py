import random
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH ---
INPUT_FILE = 'tiki_top_links.csv'
OUTPUT_FILE = 'tiki_reviews_final.csv'
CHECKPOINT_FILE = 'crawled_links.txt'
LIMIT_PER_PRODUCT = 80 
BREAK_AFTER_LINKS = 8  # Nghỉ sau mỗi 10 link
BREAK_DURATION = random.randint(250, 260)     # Thời gian nghỉ (giây)
# time.sleep(300)

driver = webdriver.Chrome()

def load_crawled_links():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def save_checkpoint(link):
    with open(CHECKPOINT_FILE, 'a') as f:
        f.write(link + '\n')

def crawl_comments(url):
    data_list = []
    driver.get(url)
    time.sleep(5)
    
    while len(data_list) < LIMIT_PER_PRODUCT:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
        time.sleep(2.5)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".review-comment"))
            )
        except:
            break

        reviews = driver.find_elements(By.CSS_SELECTOR, ".review-comment")
        for review in reviews:
            if len(data_list) >= LIMIT_PER_PRODUCT: break
            try:
                # --- XỬ LÝ NÚT "XEM THÊM" TẠI ĐÂY ---
                try:
                    # Tìm nút Xem thêm bên trong cụm bình luận này
                    # Class thường là 'show-more-content' hoặc chứa text 'Xem thêm'
                    show_more = review.find_element(By.CSS_SELECTOR, ".show-more-content")
                    if show_more.is_displayed():
                        driver.execute_script("arguments[0].click();", show_more)
                        time.sleep(0.5) # Đợi một chút để text bung ra
                except:
                    # Nếu không có nút "Xem thêm" thì bỏ qua, chạy tiếp bên dưới
                    pass

                name = review.find_element(By.CLASS_NAME, "review-comment__user-name").text
                content = review.find_element(By.CLASS_NAME, "review-comment__content").text
                
                if content and content.strip() != "":
                    data_list.append([name, content.replace("\n", " ")])
            except:
                continue

        # Chuyển trang
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.btn.next")
            if "disabled" in next_button.get_attribute("class"): break
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2.5)
        except:
            break
    return data_list

# --- CHƯƠNG TRÌNH CHÍNH ---
crawled_links = load_crawled_links()
count = 0  # Bộ đếm số link đã crawl trong phiên này

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Link Sản Phẩm', 'Người bình luận', 'Nội dung'])

try:
    with open(INPUT_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_link = row['Product Link']
            
            if product_link in crawled_links:
                continue

            # Kiểm tra xem đã đến lúc nghỉ chưa
            if count > 0 and count % BREAK_AFTER_LINKS == 0:
                print(f"--- Đã xong {count} link. Nghỉ {BREAK_DURATION} giây cho đỡ mệt... ---")
                time.sleep(BREAK_DURATION)

            print(f"[{count + 1}] Đang crawl: {product_link}")
            comments = crawl_comments(product_link)
            
            if comments:
                with open(OUTPUT_FILE, mode='a', encoding='utf-8-sig', newline='') as f_out:
                    writer = csv.writer(f_out)
                    for c in comments:
                        writer.writerow([product_link, c[0], c[1]])
                
            save_checkpoint(product_link)
            crawled_links.add(product_link)
            count += 1 # Tăng bộ đếm

except KeyboardInterrupt:
    print("\nĐã dừng thủ công. Checkpoint đã được lưu.")
finally:
    driver.quit()
    print(f"Tổng kết: Đã crawl thêm được {count} link mới trong lần này.")