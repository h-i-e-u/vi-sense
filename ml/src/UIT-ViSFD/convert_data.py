import pandas as pd
import re
import json

def transform_csv(input_csv_path):
    try:
        # CHỈ ĐỌC dữ liệu từ file của bạn
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file '{input_csv_path}' ở thư mục này. Hãy chắc chắn bạn đã để file Train.csv chung thư mục với file code này.")
        return

    # Chuẩn hóa tên cột về chữ thường để tránh lỗi
    df.columns = df.columns.str.strip().str.lower()
    
    if 'comment' not in df.columns or 'label' not in df.columns:
        print(f"❌ Cột trong file của bạn đang là: {list(df.columns)}")
        print(f"Lỗi: Hãy chắc chắn file CSV có cột tên là 'comment' và 'label'.")
        return

    print(f"📊 Đã đọc thành công. Tìm thấy {len(df)} dòng dữ liệu gốc.")
    
    dl_data = [] 
    ml_rows = [] 
    
    for _, row in df.iterrows():
        comment_text = str(row['comment']).strip()
        label_raw = str(row['label']).strip()
        
        if pd.isna(row['label']) or not label_raw or label_raw == 'nan':
            continue
            
        pairs = re.findall(r'\{(.*?)\}', label_raw)
        aspect_list = []
        for pair in pairs:
            if '#' in pair:
                aspect, sentiment = pair.split('#')
                aspect_list.append({
                    "aspect": aspect.strip(),
                    "sentiment": sentiment.strip()
                })
                
        if not aspect_list:
            continue
            
        # FORMAT DEEP LEARNING
        target_parts = [f"{item['aspect']}: {item['sentiment']}" for item in aspect_list]
        target_str = ", ".join(target_parts)
        dl_data.append({
            "input": comment_text,
            "target": target_str
        })
        
        # FORMAT MACHINE LEARNING
        for item in aspect_list:
            text_with_aspect = f"{comment_text} [ASPECT] {item['aspect']}"
            ml_rows.append({
                "text_with_aspect": text_with_aspect,
                "sentiment": item['sentiment']
            })
            
    # Ghi ra 2 file hoàn toàn mới, không ảnh hưởng đến Train.csv
    if dl_data:
        with open('data_deep_learning.jsonl', 'w', encoding='utf-8') as f_dl:
            for item in dl_data:
                f_dl.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"💾 Đã xuất {len(dl_data)} dòng sang file 'data_deep_learning.jsonl'")

    if ml_rows:
        df_ml = pd.DataFrame(ml_rows)
        df_ml.to_csv('data_machine_learning.csv', index=False, encoding='utf-8')
        print(f"💾 Đã xuất {len(df_ml)} dòng sang file 'data_machine_learning.csv'")

# Chạy trực tiếp (Hãy chắc chắn file Train.csv của bạn đã có lại đủ dữ liệu)
transform_csv('Train.csv')
