import csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 1. Cấu hình
API_KEY = 'AIzaSyDsHhNlGAgHpB22uagpSPIC7mgfy13lhnU'  # Thay bằng API Key của bạn
video_ids = ['Th06918VpjA', 'HYXpZ9ApNNk', 'GntJXsOLU10', 'S0vldC2uLfw', 'xtmI9Bb7A2M', 'ao2wv1G2sew', 'N0lI9Tgy0wg', 'ZvsbS4v5n0U', 'dqT91OALNcM', 'tHl9Dl9Co-g', 'i8Ew80mxJYs', 'Pgg1fyAvkX8', 'P1xdsD3Dldc', 'nNLgXgus_Mc', 'jbr4ipGwYxs', 'DLouCHAS8y0', 'edD2jHe_h5E', 'IdVMgwPB_jU', 'Et-fIK4mvtU', '4iLLPcq310I', 'wg4U8yygJBQ', 'KEBv5EJ-d2I', 'bqKWGAAM4sc', 'CIPw0-0CR9Q', 'zyqwAsd7MJI', 'UDP_g12x4cc', 'SXSnRlueUT4', 'Z70P3Hr-GPs', '7AoEig577ik']
MAX_COMMENTS_PER_VIDEO = 200
OUTPUT_FILE = 'youtube_comments.csv'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def crawl_to_csv():
    # Mở file CSV để ghi
    with open(OUTPUT_FILE, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        # Ghi tiêu đề cột
        writer.writerow(['Video ID', 'Author', 'Comment', 'Likes', 'Published At'])

        for v_id in video_ids:
            print(f"--- Đang lấy dữ liệu cho video: {v_id} ---")
            count = 0
            next_page_token = None
            
            try:
                while count < MAX_COMMENTS_PER_VIDEO:
                    # Tính toán số lượng cần lấy cho lần gọi này (tối đa 100)
                    remaining = MAX_COMMENTS_PER_VIDEO - count
                    max_results = min(100, remaining)

                    request = youtube.commentThreads().list(
                        part="snippet",
                        videoId=v_id,
                        maxResults=max_results,
                        pageToken=next_page_token,
                        textFormat="plainText"
                    )
                    response = request.execute()

                    for item in response.get('items', []):
                        comment = item['snippet']['topLevelComment']['snippet']
                        
                        # Ghi trực tiếp vào file CSV
                        writer.writerow([
                            v_id,
                            comment['authorDisplayName'],
                            comment['textDisplay'].replace('\n', ' '), # Bỏ dòng trống trong comment
                            comment['likeCount'],
                            comment['publishedAt']
                        ])
                        count += 1

                    # Kiểm tra trang tiếp theo
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token or count >= MAX_COMMENTS_PER_VIDEO:
                        break
                
                print(f"Hoàn thành: Lấy được {count} comments.")

            except HttpError as e:
                print(f"Lỗi khi truy cập video {v_id}: {e}")
                continue

    print(f"\n=> Đã lưu toàn bộ dữ liệu vào file: {OUTPUT_FILE}")

if __name__ == "__main__":
    crawl_to_csv()