import pandas as pd

# 1. Đọc file JSON
df = pd.read_json('t.json')

label_mapping = {-1: 'NEG', 0: 'NEU', 1: 'POS'}
df['label'] = df['label'].map(label_mapping)

# 2. Xuất ra file CSV (utf-8-sig giúp không bị lỗi font tiếng Việt khi mở bằng Excel)
df.to_csv('t.csv', index=False, encoding='utf-8-sig')
