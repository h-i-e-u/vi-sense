# seed.py
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models import models  
from app.utils.auth import get_password_hash 

def seed_data():
    db: Session = SessionLocal()
    try:
        # 1. Kiểm tra tránh trùng lặp dữ liệu khi container restart
        if db.query(models.User).first() is not None:
            print("🌱 Database đã có dữ liệu, bỏ qua bước seed.")
            return

        print("🌱 Đang khởi tạo dữ liệu mẫu với mã hóa Argon2...")

        # 2. Tạo một User mẫu (Mật khẩu đăng nhập sẽ là: 1234)
        plain_password = "1234"
        hashed_password = get_password_hash(plain_password)

        test_user = models.User(
            id=1,
            email="test@gmail.com",
            username="testuser",
            hashed_password=hashed_password, # Lưu mật khẩu đã băm bằng Argon2
            created_at=datetime.utcnow()
        )
        db.add(test_user)
        db.flush() # Lấy id của user để map sang bảng History
       
        # # 3. Tạo một vài AnalysisJob mẫu cho trang History đúng chuẩn Schema
        # job1 = models.AnalysisJob(
        #     id=str(uuid.uuid4()), # Sinh ID dạng chuỗi giống như thực tế
        #     user_id=test_user.id,
        #     type="text",
        #     status="completed",
        #     created_at=datetime.utcnow(),
        #     # Điền metadata giả lập cấu trúc JSON giống API trả về ở Frontend
        #     job_metadata={
        #         "total_comments": 10,
        #         "positive_ratio": 0.8
        #     }
        # )

        # job2 = models.AnalysisJob(
        #     id=str(uuid.uuid4()),
        #     user_id=test_user.id,
        #     type="link",
        #     source_url="https://example.com",
        #     status="completed",
        #     created_at=datetime.utcnow(),
        #     job_metadata={
        #         "total_comments": 45,
        #         "positive_ratio": 0.45
        #     }
        # )

        # db.add_all([job1, job2])
        db.commit()
        print("✅ Khởi tạo tài khoản mẫu thành công!")
        print("👉 Email: test@gmail.com")
        print("👉 Password: 1234")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi gieo dữ liệu (seed): {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()