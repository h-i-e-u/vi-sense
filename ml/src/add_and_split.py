#lay 20%  them vao data .

import pandas as pd
from sklearn.model_selection import train_test_split

# 1. Đọc tập dữ liệu gốc 
df_original = pd.read_csv("dataset_cleaned_drop.csv")  # Chứa các cột văn bản và label

# 2. Đọc tập dữ liệu mới 
df_new = pd.read_csv("vlsp_data.csv")

# 3. Chia tập dữ liệu mới thành 2 phần: 
df_new_to_train, df_new_to_test = train_test_split(
    df_new, 
    test_size=0.8, 
    random_state=42, 
    stratify=df_new['label'] # Giữ nguyên tỷ lệ các lớp POS, NEG, NEU
)

# 4. Gộp tập dữ liệu mới (phần mang đi train) vào tập dữ liệu gốc
df_combined_train = pd.concat([df_original, df_new_to_train], ignore_index=True)

# 5. Xáo trộn (shuffle) lại toàn bộ tập train mới để mô hình học đều các domain
df_combined_train = df_combined_train.sample(frac=1, random_state=42).reset_index(drop=True)

# 6. Xuất ra file CSV mới để nạp vào PhoBERT
df_combined_train.to_csv("train_phobert.csv", index=False)
df_new_to_test.to_csv("test_phobert.csv", index=False)

print(f"Số lượng tập train cũ: {len(df_original)}")
print(f"Số lượng lấy từ tập mới đắp vào train: {len(df_new_to_train)}")
print(f"Tổng số lượng tập train MỚI sau khi gộp: {len(df_combined_train)}")
print(f"Số lượng tập test MỚI dùng để đánh giá: {len(df_new_to_test)}")
