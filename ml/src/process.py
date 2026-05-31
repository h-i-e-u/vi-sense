import pandas as pd

# df = pd.read_csv('d_data.csv')
# print(df['label'].value_counts())
# # # 1. Đọc 2 file CSV lên
df1 = pd.read_csv('c_data.csv')
df2 = pd.read_csv('t.csv')

# # # # 2. Gộp (merge) 2 file thành 1 dataframe chung
# # # Dùng concat nối tiếp các dòng (nối đuôi nhau)
merged_df = pd.concat([df1, df2], ignore_index=True)

# # # # 3. Loại bỏ các dòng trống ở cột "text" để tránh lỗi tính toán
merged_df = merged_df.dropna(subset=['text'])
#MERGED
merged_df.to_csv('d_data.csv', index=False, encoding='utf-8-sig')
# # # # 4. Đếm số từ và lọc các dòng có > 256 từ
# # # # Hàm split() giúp tách các từ dựa trên khoảng trắng
# # # word_counts = merged_df['text'].apply(lambda x: len(str(x).split()))
# # # filtered_df = merged_df[word_counts <= 256]
# # # 4. Lưu kết quả sạch ra file CSV mới

# 5. In kết quả ra màn hình

# (Tùy chọn) Lưu file đã gộp ra một file mới nếu bạn cần
# merged_df.to_csv('merged_output.csv', index=False)


# df = pd.read_csv("vlsp_neu.csv")

# # df["label"] = df["label"].str.upper() #.str[:3]

# df = df[df["label"] == "NEU"]

# print(df["label"].value_counts())
# df[["text", "label"]].to_csv("vlsp_neu.csv", index=False, encoding="utf-8-sig")


# print("ok")



# df = pd.read_csv("data_lite.csv")
# df2 = pd.read_csv("dulieu_3lop.csv")

# # 1. Chuyển toàn bộ chữ trong cột "label" của cả 2 df về chữ thường
# df["label"] = df["label"].str.lower()
# df2["label"] = df2["label"].str.lower()



# df_merge = pd.concat([df, df2])

# print(df_merge["label"].value_counts)







# # 1. Tách riêng nhóm POS và tiến hành lấy mẫu ngẫu nhiên (ví dụ lấy 4698 hoặc số lượng bạn muốn)
# df_pos_down = df[df["label"] == "POS"].sample(n=6669, random_state=42)

# # 2. Lấy toàn bộ các dòng KHÔNG PHẢI là POS (giữ nguyên NEG và NEU)
# df_others = df[df["label"] != "POS"]

# # 3. Gộp hai phần lại với nhau
# df_downsampled = pd.concat([df_pos_down, df_others])

# # Kiểm tra lại kết quả
# print(df_downsampled["label"].value_counts())



# df[["text", "label"]].to_csv("data.csv", index=False, encoding="utf-8-sig")
