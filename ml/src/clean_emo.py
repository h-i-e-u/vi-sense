import pandas as pd
import re
import emoji

# 1. Định nghĩa lại hàm xử lý (đã tích hợp emoji)
def clean_sentiment_text(text):
    # Ép kiểu về string để tránh lỗi nếu dòng đó bị trống (NaN)
    text = str(text) 
    
    text = emoji.demojize(text)
    text = text.lower()
    text = re.sub(r'!+', '!', text)
    text = re.sub(r'\?+', '?', text)
    text = re.sub(r'[^a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵdđ0-9\s!?:_]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 2. Đọc file CSV 
df = pd.read_csv('t.csv')

# 3. Áp dụng hàm clean vào cột 'text' bằng phương thức .apply()
# Kết quả sẽ được ghi đè trực tiếp vào cột 'text'
df['text'] = df['text'].apply(clean_sentiment_text)

# 4. Lưu lại thành file CSV mới sạch sẽ để sẵn sàng train model
df.to_csv('t.csv', index=False, encoding='utf-8-sig')

print("Đã tiền xử lý xong và lưu vào file .csv!")
