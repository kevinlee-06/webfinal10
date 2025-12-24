from app import app
from models import db, User, Space, Resource, Permission
from werkzeug.security import generate_password_hash

def initialize_database():
    with app.app_context():
        print("正在重建資料表...")
        db.drop_all()
        db.create_all()
        print("正在建立預設使用者...")
        users = [
            User(
                username='admin', 
                password_hash=generate_password_hash('admin123'), 
                permission_mask=7  # 1(Admin) + 2(Book) + 4(Read) = 全開
            ),
            User(
                username='student', 
                password_hash=generate_password_hash('student123'), 
                permission_mask=6  # 2(Book) + 4(Read) = 可看可訂，不能管理
            ),
            User(
                username='guest', 
                password_hash=generate_password_hash('guest123'), 
                permission_mask=4  # 4(Read) = 只能看
            )
        ]
        db.session.add_all(users)
        print("正在建立範例空間...")
        lib = Space(
            name="圖書館", 
            description="安靜的學習空間，提供插座與 Wi-Fi",
            image_url="https://lib.ntut.edu.tw/public/data/8531652371.JPG"
        )
        office = Space(
            name="程式設計研究社辦公室", 
            description="電腦 3 台、樹莓派 7 片可供借用",
            image_url="https://i.imgur.com/pMSmPA8.webp"
        )
        room313 = Space(
            name="共科 313", 
            description="電腦教室，僅受理社課時段預約",
            image_url="https://mapsys.oga.ntut.edu.tw/gisweb/public/uploadfiles.htm?action=listImg&q=40"
        )
        db.session.add_all([lib, office, room313])
        db.session.flush()
        print("正在建立範例資源...")
        resources = [
            Resource(name="座位 A1", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="座位 A2", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="座位 A3", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="座位 B1", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="座位 B2", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="座位 B3", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="座位 C1", resource_type="座位", space_id=lib.id, description=""),
            Resource(name="討論室 1", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 2", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 3", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 4", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 5", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 6", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 7", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="討論室 8", resource_type="會議室", space_id=lib.id, description="3-6 人"),
            Resource(name="iPad 10 [01]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [02]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [03]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [04]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [05]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [06]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [07]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="iPad 10 [08]", resource_type="電腦", space_id=lib.id, description="使用期限 14 天"),
            Resource(name="樹莓派 01", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="樹莓派 02", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="樹莓派 03", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="樹莓派 04", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="樹莓派 05", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="樹莓派 06", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="樹莓派 07", resource_type="電腦", space_id=office.id, description="Debian 13"),
            Resource(name="床", resource_type="座位", space_id=office.id, description="Kevin 的"),
            Resource(name="座位 01", resource_type="座位", space_id=office.id, description="折疊椅"),
            Resource(name="座位 02", resource_type="座位", space_id=office.id, description="折疊椅"),
            Resource(name="座位 03", resource_type="座位", space_id=office.id, description="折疊椅"),
            Resource(name="座位 04", resource_type="座位", space_id=office.id, description="折疊椅"),
            Resource(name="座位 05", resource_type="座位", space_id=office.id, description="躺椅"),
            Resource(name="座位 06", resource_type="座位", space_id=office.id, description="躺椅"),
            Resource(name="座位 07", resource_type="座位", space_id=office.id, description="躺椅"),
            Resource(name="座位 08", resource_type="座位", space_id=office.id, description="躺椅"),
            Resource(name="電腦 01", resource_type="電腦", space_id=office.id, description="Ubuntu 24.04 LTS"),
            Resource(name="電腦 02", resource_type="電腦", space_id=office.id, description="Windows 11"),
            Resource(name="電腦 03", resource_type="電腦", space_id=office.id, is_hidden=True, description="Ubuntu 23.10"),
            Resource(name="313-01", resource_type="座位", space_id=room313.id, description="Windows 11"),
            Resource(name="313-02", resource_type="座位", space_id=room313.id, description="Windows 11"),
            Resource(name="313-03", resource_type="座位", space_id=room313.id, description="Windows 11"),
            Resource(name="313-04", resource_type="座位", space_id=room313.id, description="Windows 11"),
            Resource(name="313-05", resource_type="座位", space_id=room313.id, description="Windows 11"),
            Resource(name="313-06", resource_type="座位", space_id=room313.id, description="Windows 11"),

        ]
        db.session.add_all(resources)
        db.session.commit()
        print("--- 資料庫初始化完成！ ---")
        print("測試帳號: admin / admin123 (Mask: 7)")
        print("測試帳號: student / student123 (Mask: 6)")

if __name__ == "__main__":
    initialize_database()