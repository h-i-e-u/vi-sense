"""
script automation crawl url of item  sold more than 100 in first page on tiki.
item url are use for comment crawling.
"""
import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH ---
tiki_catalog = {
    "sach" : "https://tiki.vn/nha-sach-tiki/c8322",
    "nha_cua" : "https://tiki.vn/nha-cua-doi-song/c1883",
    "dien_thoai" : "https://tiki.vn/dien-thoai-may-tinh-bang/c1789",
    "do_choi" : "https://tiki.vn/do-choi-me-be/c2549",
    "thiet_bi_so" : "https://tiki.vn/thiet-bi-kts-phu-kien-so/c1815",
    "dien_gia_dung" : "https://tiki.vn/dien-gia-dung/c1882",
    "lam_dep" : "https://tiki.vn/lam-dep-suc-khoe/c1520",
    "oto_xe_may" : "http://tiki.vn/o-to-xe-may-xe-dap/c8594",
    "thoi_trang_nu" : "https://tiki.vn/thoi-trang-nu/c931",
    "bach_hoa" : "https://tiki.vn/bach-hoa-online/c4384",
    "the_thao" : "https://tiki.vn/the-thao-da-ngoai/c1975",
    "thoi_trang_nam" : "https://tiki.vn/thoi-trang-nam/c915",
    "laptop" : "https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846",
    "giay_dep_nam" : "https://tiki.vn/giay-dep-nam/c1686",
    "giay_dep_nu" : "https://tiki.vn/giay-dep-nu/c1703"
}

def get_sold_number(text):
    """Trích xuất số từ chuỗi 'Đã bán 117' hoặc 'Đã bán 1.2k'"""
    try:
        # Tìm số và đơn vị (nếu có k)
        match = re.search(r'(\d+(\.\d+)?)\s*([kK]?)', text)
        if match:
            num = float(match.group(1))
            unit = match.group(3).lower()
            return int(num * 1000) if unit == 'k' else int(num)
    except:
        return 0
    return 0

options = Options()
# options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

final_links = []

try:
    for cat_name, url in tiki_catalog.items():
        print(f"Đang quét: {cat_name}...")
        driver.get(url)

        # scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.2);")
        time.sleep(2)
        
        # Đợi tối đa 5s cho các sản phẩm (thẻ a.product-item) xuất hiện
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-item"))
            )
        except:
            print(f"Danh mục {cat_name} load quá lâu hoặc không có hàng.")
            continue

        # Lấy tất cả các item đang hiển thị trên trang đầu
        items = driver.find_elements(By.CSS_SELECTOR, "a.product-item")
        
        for item in items:
            try:
                # Tìm thẻ chứa thông tin 'Đã bán'
                sold_info = item.find_element(By.CLASS_NAME, "quantity").text
                count = get_sold_number(sold_info)
                
                if count >= 100:
                    link = item.get_attribute("href")
                    final_links.append([cat_name, count, link])
            except:
                # Bỏ qua item nếu không có thông tin 'Đã bán' hoặc bị lỗi
                continue

finally:
    driver.quit()

# --- XUẤT CSV ---
with open('tiki_top_links.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Catalog', 'Sold Count', 'Product Link'])
    writer.writerows(final_links)

print(f"\n--- Xong! ---")
print(f"Tổng cộng lấy được {len(final_links)} link sản phẩm đạt yêu cầu.")