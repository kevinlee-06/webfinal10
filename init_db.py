from app import app
from models import db, User, Space, Resource, Permission
from werkzeug.security import generate_password_hash

def initialize_database():
    with app.app_context():
        print("Rebuilding database tables...")
        db.drop_all()
        db.create_all()
        
        print("Creating default users...")
        users = [
            User(
                username='admin', 
                password_hash=generate_password_hash('admin123'), 
                permission_mask=7  # 1(Admin) + 2(Book) + 4(Read) = Full Access
            ),
            User(
                username='student', 
                password_hash=generate_password_hash('student123'), 
                permission_mask=6  # 2(Book) + 4(Read) = View & Book
            ),
            User(
                username='guest', 
                password_hash=generate_password_hash('guest123'), 
                permission_mask=4  # 4(Read) = View Only
            )
        ]
        db.session.add_all(users)
        
        print("Creating sample spaces...")
        lib = Space(
            name="Main Library", 
            description="A quiet study environment with power outlets and Wi-Fi.",
            image_url="https://lib.ntut.edu.tw/public/data/8531652371.JPG"
        )
        office = Space(
            name="Programming Club Office", 
            description="Equipped with 3 PCs and 7 Raspberry Pi units available for borrow.",
            image_url="https://i.imgur.com/pMSmPA8.webp"
        )
        room313 = Space(
            name="Room 313 (Lab)", 
            description="Computer lab, reservations only accepted for club course hours.",
            image_url="https://mapsys.oga.ntut.edu.tw/gisweb/public/uploadfiles.htm?action=listImg&q=40"
        )
        db.session.add_all([lib, office, room313])
        db.session.flush()
        
        print("Creating sample resources...")
        # Resource Types: "Seat", "Computer", "Meeting Room", "Other Equipment"
        resources = [
            # Library Resources
            Resource(name="Seat A1", resource_type="Seat", space_id=lib.id, description=""),
            Resource(name="Seat A2", resource_type="Seat", space_id=lib.id, description=""),
            Resource(name="Seat A3", resource_type="Seat", space_id=lib.id, description=""),
            Resource(name="Seat B1", resource_type="Seat", space_id=lib.id, description=""),
            Resource(name="Seat B2", resource_type="Seat", space_id=lib.id, description=""),
            Resource(name="Seat B3", resource_type="Seat", space_id=lib.id, description=""),
            Resource(name="Discussion Room 1", resource_type="Meeting Room", space_id=lib.id, description="3-6 People"),
            Resource(name="Discussion Room 2", resource_type="Meeting Room", space_id=lib.id, description="3-6 People"),
            Resource(name="Discussion Room 3", resource_type="Meeting Room", space_id=lib.id, description="3-6 People"),
            Resource(name="iPad 10 [01]", resource_type="Computer", space_id=lib.id, description="14-day loan period"),
            Resource(name="iPad 10 [02]", resource_type="Computer", space_id=lib.id, description="14-day loan period"),
            Resource(name="iPad 10 [03]", resource_type="Computer", space_id=lib.id, description="14-day loan period"),
            
            # Office Resources
            Resource(name="Raspberry Pi 01", resource_type="Computer", space_id=office.id, description="Debian 13"),
            Resource(name="Raspberry Pi 02", resource_type="Computer", space_id=office.id, description="Debian 13"),
            Resource(name="Raspberry Pi 03", resource_type="Computer", space_id=office.id, description="Debian 13"),
            Resource(name="Bed", resource_type="Seat", space_id=office.id, description="Kevin's spot"),
            Resource(name="Seat 01", resource_type="Seat", space_id=office.id, description="Folding Chair"),
            Resource(name="Seat 02", resource_type="Seat", space_id=office.id, description="Folding Chair"),
            Resource(name="Seat 05", resource_type="Seat", space_id=office.id, description="Recliner"),
            Resource(name="Seat 06", resource_type="Seat", space_id=office.id, description="Recliner"),
            Resource(name="Workstation 01", resource_type="Computer", space_id=office.id, description="Ubuntu 24.04 LTS"),
            Resource(name="Workstation 02", resource_type="Computer", space_id=office.id, description="Windows 11"),
            Resource(name="Workstation 03", resource_type="Computer", space_id=office.id, is_hidden=True, description="Ubuntu 23.10"),
            
            # Room 313 Resources
            Resource(name="313-01", resource_type="Seat", space_id=room313.id, description="Windows 11"),
            Resource(name="313-02", resource_type="Seat", space_id=room313.id, description="Windows 11"),
            Resource(name="313-03", resource_type="Seat", space_id=room313.id, description="Windows 11"),
            Resource(name="313-04", resource_type="Seat", space_id=room313.id, description="Windows 11"),
        ]
        db.session.add_all(resources)
        db.session.commit()
        
        print("--- Database Initialization Complete! ---")
        print("Admin account: admin / admin123 (Mask: 7)")
        print("Student account: student / student123 (Mask: 6)")

if __name__ == "__main__":
    initialize_database()