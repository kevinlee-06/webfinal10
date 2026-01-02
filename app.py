from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Space, Resource, Booking, Permission
from functools import wraps
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-fallback')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Permission Decorator
def require_perm(mask):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash("Please log in first.", "danger")
                return redirect(url_for('login'))
            user = User.query.get(user_id)
            if not user or not (user.permission_mask & mask):
                flash("Access Denied: You do not have sufficient permissions.", "danger")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.template_filter('has_perm')
def has_perm(mask, bit):
    if mask is None: return False
    return bool(int(mask) & int(bit))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_perm_mask'] = user.permission_mask
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('admin_dashboard' if user.permission_mask & Permission.ADMIN else 'home'))
        flash("Invalid username or password.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Successfully logged out.", "info")
    return redirect(url_for('home'))

@app.route('/admin/add_user', methods=['GET', 'POST'])
@require_perm(Permission.ADMIN)
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        perm_mask = int(request.form.get('perm_mask', 6))
        
        if not username or not password:
            flash("Username and password cannot be empty.", "error")
            return redirect(url_for('add_user'))
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('add_user'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for('add_user'))
            
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            permission_mask=perm_mask
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f"User {username} created successfully.", "success")
            return redirect(url_for('manage_assets'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
    return render_template('admin/add_user.html')

@app.route('/')
def home():
    spaces = Space.query.filter_by(is_hidden=False).all()
    return render_template('user/index.html', spaces=spaces)

@app.route('/space/<int:space_id>')
def view_space(space_id):
    space = Space.query.get_or_404(space_id)
    resources = Resource.query.filter_by(space_id=space_id, is_hidden=False).all()
    return render_template('user/space_detail.html', space=space, resources=resources)

@app.route('/api/bookings')
def get_bookings_json():
    user_perm = session.get('user_perm_mask', 0)
    is_admin = (user_perm & 1) == 1
    if is_admin:
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(status='Approved').all()
    
    events = []
    status_colors = {
        'Approved': '#c3edc0', 'Pending': '#fdf2b3', 'Rejected': '#fbc7d4',
        'Cancelled': '#e9ecef', 'Draft': '#f3f0ff'
    }
    
    for b in bookings:
        color = status_colors.get(b.status, '#ff8fa3')
        events.append({
            'id': b.id,
            'title': f"{b.resource.name} ({b.user.username})" if is_admin else f"{b.resource.name} (Reserved)",
            'start': b.start_time.isoformat(),
            'end': b.end_time.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#594d5b',
            'extendedProps': {'status': b.status}
        })
    return jsonify(events)

@app.route('/book/<int:resource_id>', methods=['GET', 'POST'])
@require_perm(Permission.BOOK)
def create_booking(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if request.method == 'POST':
        start_dt = datetime.fromisoformat(request.form['start_time'])
        end_dt = datetime.fromisoformat(request.form['end_time'])
        
        if end_dt <= start_dt:
            flash("End time must be later than start time.", "danger")
            return render_template('user/booking_form.html', resource=resource)
            
        conflict = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.status == 'Approved',
            Booking.start_time < end_dt,
            Booking.end_time > start_dt
        ).first()
        
        if conflict:
            flash("This time slot is already occupied.", "danger")
            return render_template('user/booking_form.html', resource=resource)
            
        new_booking = Booking(
            user_id=session['user_id'], resource_id=resource_id,
            start_time=start_dt, end_time=end_dt,
            attendees=int(request.form['attendees']), status='Pending'
        )
        db.session.add(new_booking)
        db.session.commit()
        flash("Booking request submitted and awaiting approval.", "success")
        return redirect(url_for('my_bookings'))
    return render_template('user/booking_form.html', resource=resource)

@app.route('/my-bookings')
@require_perm(Permission.VIEW)
def my_bookings():
    user_id = session.get('user_id')
    user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    return render_template('user/my_bookings.html', bookings=user_bookings, now=datetime.now())

@app.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@require_perm(Permission.VIEW)
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session.get('user_id'):
        flash("Unauthorized action.", "danger")
    elif booking.status in ['Pending', 'Approved', 'Draft']:
        booking.status = 'Cancelled'
        db.session.commit()
        flash("Booking successfully cancelled.", "success")
    return redirect(url_for('my_bookings'))

@app.route('/booking/end_early/<int:booking_id>', methods=['POST'])
@require_perm(Permission.VIEW)
def end_early(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    now = datetime.now()
    if booking.user_id != session.get('user_id'):
        flash("Unauthorized action.", "danger")
    elif booking.status == 'Approved' and booking.start_time <= now <= booking.end_time:
        booking.end_time = now
        db.session.commit()
        flash("Resource released early.", "success")
    return redirect(url_for('my_bookings'))

@app.route('/admin/dashboard')
@require_perm(Permission.ADMIN)
def admin_dashboard():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/dashboard.html', bookings=bookings)

@app.route('/admin/approve/<int:booking_id>/<string:action>')
@require_perm(Permission.ADMIN)
def review_booking(booking_id, action):
    booking = Booking.query.get_or_404(booking_id)
    status_map = {'approve': 'Approved', 'reject': 'Rejected', 'draft': 'Draft'}
    booking.status = status_map.get(action, 'Pending')
    db.session.commit()
    flash(f"Status updated: {booking.status}", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/assets')
@require_perm(Permission.ADMIN)
def manage_assets():
    spaces = Space.query.all()
    return render_template('admin/manage_assets.html', spaces=spaces)

@app.route('/admin/space/add', methods=['POST'])
@require_perm(Permission.ADMIN)
def add_space():
    new_space = Space(
        name=request.form.get('name'), description=request.form.get('description'),
        image_url=request.form.get('image_url')
    )
    db.session.add(new_space)
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/edit_space/<int:space_id>', methods=['POST'])
@require_perm(Permission.ADMIN)
def edit_space(space_id):
    space = Space.query.get_or_404(space_id)
    space.name = request.form.get('name')
    space.description = request.form.get('description')
    space.image_url = request.form.get('image_url')
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/delete_space/<int:space_id>', methods=['POST'])
@require_perm(Permission.ADMIN)
def delete_space(space_id):
    space = Space.query.get_or_404(space_id)
    db.session.delete(space)
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/resource/add', methods=['POST'])
@require_perm(Permission.ADMIN)
def add_resource():
    new_res = Resource(
        space_id=request.form.get('space_id'), name=request.form.get('name'),
        resource_type=request.form.get('resource_type'), description=request.form.get('description')
    )
    db.session.add(new_res)
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/edit_resource/<int:res_id>', methods=['POST'])
@require_perm(Permission.ADMIN)
def edit_resource(res_id):
    res = Resource.query.get_or_404(res_id)
    res.name = request.form.get('name')
    res.resource_type = request.form.get('resource_type')
    res.description = request.form.get('description')
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/resource/delete/<int:res_id>', methods=['POST'])
@require_perm(Permission.ADMIN)
def delete_resource(res_id):
    res = Resource.query.get_or_404(res_id)
    if res.bookings:
        flash("Deletion failed: Booking records associated with this resource exist.", "danger")
    else:
        db.session.delete(res)
        db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/space/toggle/<int:space_id>')
@require_perm(Permission.ADMIN)
def toggle_space_visibility(space_id):
    space = Space.query.get_or_404(space_id)
    space.is_hidden = not space.is_hidden
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/resource/toggle/<int:res_id>')
@require_perm(Permission.ADMIN)
def toggle_resource(res_id):
    res = Resource.query.get_or_404(res_id)
    res.is_hidden = not res.is_hidden
    db.session.commit()
    return redirect(url_for('manage_assets'))

@app.route('/admin/user/<int:user_id>/permissions', methods=['GET', 'POST'])
@require_perm(Permission.ADMIN)
def manage_user_permissions(user_id):
    target_user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        target_user.permission_mask = int(request.form.get('mask_value'))
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_user.html', target_user=target_user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('404.html', error_type="403", message="Access Forbidden: Insufficient Permissions"), 403

@app.context_processor
def inject_site_info():
    return {
        'site_name': os.getenv('SITE_NAME', 'Space Booking System'),
        'site_description': os.getenv('SITE_DESCRIPTION', '')
    }

if __name__ == '__main__':
    app.run(debug=True, port=5080)