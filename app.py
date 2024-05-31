from flask import Flask, render_template, redirect, url_for, request, flash,session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from config import Config
from models import db, Property, PropertyImage, SuperUser
from forms import PropertyForm
import os
from PIL import Image 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.init_app(app)

with app.app_context():
    db.create_all()
@login_manager.user_loader
def load_user(user_id):
    return SuperUser.query.get(int(user_id))

@app.route('/')
def index():
    properties = Property.query.order_by(Property.date_added.desc()).all()
    hero_template='components/home_hero.html'
    title='Home'
    return render_template('index.html', properties=properties, title=title,hero_template=hero_template)

@app.route('/contact')
def contact():
    hero_template='components/default_hero.html'
    title='Contact Us'
    return render_template('/pages/contact.html', title=title, hero_template=hero_template)

@app.route('/about')
def about():
    hero_template='components/default_hero.html'
    title='About'
    return render_template('/pages/about.html', title=title, hero_template=hero_template)

@app.route('/services')
def services():
    categories = [
        "Architectural design and planning",
        "Land investigation",
        "Notary service",
        "Due diligence",
        "Establish building permit",
        "Establish building construction",
        "Land topography measurement",
        "Determination map boundary",
        "Villa management",
        "Establish foreign investment company in Indonesia ( PT. PMA )",
        "Establish Business permit",
        "Land Acquisition",
        "Theodolit format Autocad"
    ]
    hero_template='components/default_hero.html'
    title='About'
    return render_template('/pages/service.html', categories=categories,title=title, hero_template=hero_template)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = SuperUser.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/admin')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Jumlah properti per halaman
    properties = Property.query.order_by(Property.date_added.desc()).paginate(page=page, per_page=per_page)
    return render_template('listview.html', properties=properties)

# @app.route('/admin')
# @login_required
# def admin():
#     return render_template('listview.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '', type=str)
    
    if query:
        # Assuming the Property model has 'title', 'location', 'zip_code', and 'type' fields
        properties = Property.query.filter(
            or_(
                Property.title.ilike(f'%{query}%'),
                Property.location.ilike(f'%{query}%'),
                Property.type.ilike(f'%{query}%')
            )
        ).all()
    else:
        properties = []
    hero_template='components/default_hero.html'
    title='Searching'
    return render_template('/pages/search_results.html', properties=properties,title=title,hero_template=hero_template)


def resize_images(filepaths, output_size=(1080, 1080)):
    for filepath in filepaths:
        with Image.open(filepath) as img:
            img = img.resize(output_size, Image.LANCZOS)
            img.save(filepath)


def save_images(images):
    filenames = []
    for image in images:
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        filenames.append(filepath)  # Menyimpan path file, bukan hanya nama file
    resize_images(filenames, (1080, 1080))  # Memanggil resize_images dengan daftar path file
    return [os.path.basename(filepath) for filepath in filenames]  # Mengembalikan nama file saja, bukan path lengkap

# @app.route('/property')
# def view_property():
#     page = request.args.get('page', 1, type=int)
#     per_page = 16  # Total items per page (5 rows * 4 items per row)
#     pagination = Property.query.order_by(Property.date_added.desc()).paginate(page=page, per_page=per_page, error_out=False)
#     properties = pagination.items
#     next_url = url_for('view_property', page=pagination.next_num) if pagination.has_next else None
#     prev_url = url_for('view_property', page=pagination.prev_num) if pagination.has_prev else None
#     hero_template='components/default_hero.html'
#     title='Properties'
#     return render_template('view_property.html',title=title, properties=properties, pagination=pagination, next_url=next_url, prev_url=prev_url, hero_template=hero_template)
@app.route('/property', methods=['GET'])
def view_property():
    page = request.args.get('page', 1, type=int)
    property_type = request.args.get('type')
    sort_by = request.args.get('sort')

    query = Property.query

    if property_type:
        query = query.filter_by(type=property_type)

    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Property.date_added.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(Property.date_added.desc())
    else:
        query = query.order_by(Property.date_added.desc())

    properties = query.paginate(page=page, per_page=5)
    prev_url = url_for('view_property', page=properties.prev_num) if properties.has_prev else None
    next_url = url_for('view_property', page=properties.next_num) if properties.has_next else None
    hero_template='components/default_hero.html'
    title='Properties'
    return render_template('view_property.html',title=title, properties=properties.items, pagination=properties, prev_url=prev_url, next_url=next_url,hero_template=hero_template)



@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    hero_template='components/default_hero.html'
    title='Detail Property'
    return render_template('property_detail.html',title=title, property=property,hero_template=hero_template)

@app.route('/create', methods=['GET', 'POST'])
def create_property():
    form = PropertyForm()
    if form.validate_on_submit():
        new_property = Property(
            title=form.title.data,
            type=form.type.data,
            price=form.price.data,
            description=form.description.data,
            location=form.location.data
        )
        db.session.add(new_property)
        db.session.commit()

        if form.images.data:
            filenames = save_images(form.images.data)
            for filename in filenames:
                new_image = PropertyImage(filename=filename, property_id=new_property.id)
                db.session.add(new_image)
            db.session.commit()

        flash('Property created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_property.html', form=form)

@app.route('/edit/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    form = PropertyForm(obj=property)
    
    if form.validate_on_submit():
        if form.images.data:
            # Delete existing images
            existing_images = PropertyImage.query.filter_by(property_id=property_id).all()
            for image in existing_images:
                db.session.delete(image)
            
            # Save new images
            filenames = save_images(form.images.data)
            for filename in filenames:
                new_image = PropertyImage(filename=filename, property_id=property_id)
                db.session.add(new_image)
        
        property.title = form.title.data
        property.description = form.description.data
        property.price = form.price.data
        property.location = form.location.data
        db.session.commit()
        
        flash('Property updated successfully!', 'success')
        return redirect(url_for('dashboard', property_id=property.id))
    
    return render_template('edit_property.html', form=form)



@app.route('/delete/<int:property_id>', methods=['POST'])
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    related_images = PropertyImage.query.filter_by(property_id=property_id).all()
    for image in related_images:
        db.session.delete(image)
    db.session.delete(property)
    db.session.commit()
    
    flash('Property and associated images deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
