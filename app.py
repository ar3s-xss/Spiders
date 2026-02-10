from flask import Flask, render_template, url_for, request, redirect, abort
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

UPLOAD_FOLDER = 'static/images/spiders'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heif'}

DB_PATH = "/data/database.db"

def init_db():
    os.makedirs("/data", exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS species (id INTEGER PRIMARY KEY AUTOINCREMENT, science_name TEXT, common_name TEXT, world TEXT, world_type TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS spiders (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, gender TEXT, species_id INTEGER, FOREIGN KEY(species_id) REFERENCES species(id) ON DELETE SET NULL)')
    cur.execute('CREATE TABLE IF NOT EXISTS feeding (id INTEGER PRIMARY KEY AUTOINCREMENT, spiders_id INTEGER NOT NULL, date DATE, food TEXT, count INTEGER, FOREIGN KEY(spiders_id) REFERENCES spiders(id) ON DELETE CASCADE)')
    cur.execute('CREATE TABLE IF NOT EXISTS molts (id INTEGER PRIMARY KEY AUTOINCREMENT, spiders_id INTEGER NOT NULL, date DATE, note TEXT, FOREIGN KEY(spiders_id) REFERENCES spiders(id) ON DELETE CASCADE)')
    cur.execute('CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY AUTOINCREMENT, spiders_id INTEGER NOT NULL, image_path TEXT, note TEXT, upload_date DATE, FOREIGN KEY(spiders_id) REFERENCES spiders(id) ON DELETE CASCADE)')
    con.commit()
    con.close()

def con_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


app = Flask(__name__)

with app.app_context():
    init_db()
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


def date_file_name():
    return datetime.now().strftime("%Y_%m_%d")

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Home route


@app.route('/')
@app.route('/home')
def index():
    con = con_db()
    cur = con.cursor()
    cur.execute("SELECT s.id, s.name, s.gender, sp.science_name FROM spiders s LEFT JOIN species sp ON s.species_id = sp.id")
    spiders = cur.fetchall()
    return render_template('index.html', spiders=spiders)

# Edit spider route

@app.route('/edit/<int:spider_id>', methods=['GET', 'POST'])
def edit(spider_id):
    con = con_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if request.method == 'POST':
        s_name = request.form['name']
        s_species_id = request.form['species_id']
        s_gender = request.form['gender']

        cur.execute("""
            UPDATE spiders
            SET name = ?, species_id = ?, gender = ?
            WHERE id = ?
        """, (s_name, s_species_id, s_gender, spider_id))

        con.commit()
        return redirect(url_for('index'))

    
    cur.execute("""
        SELECT s.id, s.name, s.gender, s.species_id
        FROM spiders s
        WHERE s.id = ?
    """, (spider_id,))
    spider = cur.fetchone()

    # load species list for dropdown
    cur.execute("SELECT id, science_name FROM species")
    species_list = cur.fetchall()

    return render_template(
        'edit.html',
        spider=spider,
        species_list=species_list
    )

# Add spider route

@app.route('/add', methods=['GET', 'POST'])
def add():
    con = con_db()
    cur = con.cursor()
    if request.method == 'POST':
        
        s_name = request.form['name']
        s_spec_id = request.form['species_id']
        s_gender = request.form['gender']

        cur.execute("INSERT INTO spiders (name, species_id, gender) VALUES (?, ?, ?)", (s_name, s_spec_id, s_gender))
        con.commit()
        return redirect(url_for('index'))

    cur.execute("SELECT DISTINCT id, science_name FROM species")
    species = cur.fetchall()
    return render_template('add.html', species_list=species)

# Species routes

@app.route('/species', methods=['GET', 'POST'])
def species():
    error = None
    edit_species = None
    con = con_db()
    cur = con.cursor()
    if request.method == 'POST':
        s_sciname = request.form['science_name']
        s_comname = request.form['common_name']
        s_world = request.form['world']
        s_world_type = request.form['world_type']
        cur.execute("SELECT 1 FROM species WHERE science_name=?", (s_sciname,))
        if cur.fetchone():
            error = f"Species \"{s_sciname}\" already exists!"
        else:
            cur.execute("INSERT INTO species (science_name, common_name, world, world_type) VALUES (?, ?, ?, ?)", (s_sciname, s_comname, s_world, s_world_type))
            con.commit()

        return redirect(url_for('species'))
  
    cur.execute("SELECT * FROM species")
    species = cur.fetchall()
    return render_template('species.html', species=species, error=error, edit_species=edit_species)


@app.route('/species/edit/<int:specie_id>',)
def edit_specie(specie_id):
    con = con_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM species WHERE id=?", (specie_id,))
    edit_species = cur.fetchone()
    cur.execute("SELECT * FROM species")
    species = cur.fetchall()
    return render_template('species.html', species=species, edit_species=edit_species)

@app.route('/update_specie/<int:specie_id>', methods=['POST'])
def update_specie(specie_id):
    con = con_db()
    cur = con.cursor()
    s_sciname = request.form['science_name']
    s_comname = request.form['common_name']
    s_world = request.form['world']
    s_world_type = request.form['world_type']
    cur.execute("UPDATE species SET science_name=?, common_name=?, world=?, world_type=? WHERE id=?", (s_sciname, s_comname, s_world, s_world_type, specie_id))
    con.commit()
    return redirect(url_for('species'))

@app.route('/delete_specie/<int:specie_id>', methods=['POST'])
def delete_specie(specie_id):
    con = con_db()
    cur = con.cursor()
    # sqlite3 requires a sequence for parameters; make sure to pass a tuple
    cur.execute("DELETE FROM species WHERE id=?", (specie_id,))
    con.commit()
    return redirect(url_for('species'))

@app.route('/delete_spider/<int:spider_id>', methods=['POST'])
def delete_spider(spider_id):
    con = con_db()
    cur = con.cursor()
    cur.execute("DELETE FROM spiders WHERE id=?", (spider_id,))
    con.commit()
    return redirect(url_for('index'))

@app.route('/spider/<int:spider_id>')
def spider_detail(spider_id):
    con = con_db()
    cur = con.cursor()

    cur.execute("""
        SELECT s.id, s.name, sp.science_name
        FROM spiders s
        LEFT JOIN species sp ON s.species_id = sp.id
        WHERE s.id = ?
    """, (spider_id,))
    spider = cur.fetchone()

    if spider is None:
        abort(404)

    cur.execute("SELECT id, date, food, count FROM feeding WHERE spiders_id=?", (spider_id,))
    food_history = cur.fetchall()

    cur.execute("SELECT id, date, note FROM molts WHERE spiders_id=?", (spider_id,))
    molts = cur.fetchall()

    cur.execute("SELECT id, image_path, note FROM images WHERE spiders_id=?", (spider_id,))
    images = cur.fetchall()

    return render_template(
        'details.html',
        spider=spider,
        food_history=food_history,
        molts=molts,
        images=images
    )

# Food routes

@app.route('/spider/<int:spider_id>/edit_food/<int:food_id>', methods=['GET', 'POST'])
def edit_food(spider_id, food_id):
    con = con_db()
    cur = con.cursor()

    if request.method == 'GET':
        cur.execute(
            "SELECT * FROM feeding WHERE id=? AND spiders_id=?",
            (food_id, spider_id)
        )
        food = cur.fetchone()
        if not food:
            abort(404)

        return render_template('food.html', spider_id=spider_id, food=food)

    cur.execute(
        "UPDATE feeding SET date=?, food=?, count=? WHERE id=? AND spiders_id=?",
        (request.form['date'], request.form['food_type'],
         request.form['food_count'], food_id, spider_id)
    )
    con.commit()
    return redirect(url_for('spider_detail', spider_id=spider_id))

@app.route('/spider/<int:spider_id>/delete_food/<int:food_id>', methods=['POST'])
def delete_food(spider_id, food_id):
    con = con_db()
    cur = con.cursor()
    cur.execute(
        "DELETE FROM feeding WHERE id=? AND spiders_id=?",
        (food_id, spider_id)
    )
    con.commit()
    return redirect(url_for('spider_detail', spider_id=spider_id))


@app.route('/spider/<int:spider_id>/add_food', methods=['GET', 'POST'])
def add_food(spider_id):
    con = con_db()
    cur = con.cursor()

    if request.method == 'POST':
        cur.execute("""
            INSERT INTO feeding (spiders_id, date, food, count)
            VALUES (?, ?, ?, ?)
        """, (
            spider_id,
            request.form['date'],
            request.form['food_type'],
            request.form['food_count']
        ))
        con.commit()
        return redirect(url_for('spider_detail', spider_id=spider_id))

    return render_template('food.html', spider_id=spider_id, food=None)


# Molt routes

@app.route('/spider/<int:spider_id>/add_molt', methods=['GET', 'POST'])
def add_molt(spider_id):
    con = con_db()
    cur = con.cursor()

    if request.method == 'POST':
        cur.execute(
            "INSERT INTO molts (spiders_id, date, note) VALUES (?, ?, ?)",
            (spider_id, request.form['date'], request.form['note'])
        )
        con.commit()
        return redirect(url_for('spider_detail', spider_id=spider_id))

    return render_template('molt.html', spider_id=spider_id, molt=None)


@app.route('/spider/<int:spider_id>/edit_molt/<int:molt_id>', methods=['GET', 'POST'])
def edit_molt(spider_id, molt_id):
    con = con_db()
    cur = con.cursor()

    if request.method == 'GET':
        cur.execute(
            "SELECT * FROM molts WHERE id=? AND spiders_id=?",
            (molt_id, spider_id)
        )
        molt = cur.fetchone()

        if molt is None:
            abort(404)

        return render_template(
            'molt.html',
            spider_id=spider_id,
            molt=molt
        )

    # POST (update)
    cur.execute(
        "UPDATE molts SET date=?, note=? WHERE id=? AND spiders_id=?",
        (
            request.form['date'],
            request.form['note'],
            molt_id,
            spider_id
        )
    )
    con.commit()

    return redirect(url_for('spider_detail', spider_id=spider_id))


@app.route('/spider/<int:spider_id>/delete_molt/<int:molt_id>', methods=['POST'])
def delete_molt(spider_id, molt_id):
    con = con_db()
    cur = con.cursor()

    cur.execute(
        "DELETE FROM molts WHERE id=? AND spiders_id=?",
        (molt_id, spider_id)
    )
    con.commit()

    return redirect(url_for('spider_detail', spider_id=spider_id))

# Image routes

@app.route('/spider/<int:spider_id>/upload_image', methods=['GET', 'POST'])
def upload_image(spider_id):
    con = con_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if request.method == 'POST':

        if 'image_path' not in request.files:
            abort(400)
        file = request.files['image_path']
        if file.filename == '':
            abort(400)
        if not allowed_files(file.filename):
            abort(400)
        filename = secure_filename(file.filename)
        file_final_name = f'{date_file_name()}_{filename}'

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_final_name)
        file.save(file_path)
        note = request.form['note']
        cur.execute('INSERT INTO images (spiders_id, image_path, note) VALUES (?, ?, ?)', (spider_id, file_final_name, note))
        con.commit()
        return redirect(url_for('spider_detail', spider_id=spider_id))
    return render_template('image.html', spider_id=spider_id, image=None)

@app.route('/spider/<int:spider_id>/edit_image/<int:image_id>', methods=['GET', 'POST'])
def edit_image(spider_id, image_id):
    con = con_db()
    cur = con.cursor()

    cur.execute(
        "SELECT * FROM images WHERE id=? AND spiders_id=?",
        (image_id, spider_id)
    )
    image = cur.fetchone()

    if image is None:
        abort(404)

    if request.method == 'POST':
        note = request.form['note']

        file = request.files.get('image_path')

        if file and file.filename != '':
            if not allowed_files(file.filename):
                abort(400)

            filename = secure_filename(file.filename)
            final_name = f"{date_file_name()}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_name))

            # optional: delete old file
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], image['image_path'])
            if os.path.exists(old_path):
                os.remove(old_path)

            cur.execute(
                "UPDATE images SET image_path=?, note=? WHERE id=?",
                (final_name, note, image_id)
            )
        else:
            # only update note
            cur.execute(
                "UPDATE images SET note=? WHERE id=?",
                (note, image_id)
            )

        con.commit()
        return redirect(url_for('spider_detail', spider_id=spider_id))

    return render_template('image.html', spider_id=spider_id, image=image)


@app.route('/spider/<int:spider_id>/delete_image/<int:image_id>', methods=['POST'])
def delete_image(spider_id, image_id):
    con = con_db()
    cur = con.cursor()
    cur.execute("SELECT image_path FROM images WHERE id=? AND spiders_id=?", (image_id, spider_id))
    image = cur.fetchone()
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image['image_path'])):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image['image_path']))
    cur.execute(
        "DELETE FROM images WHERE id=? AND spiders_id=?",
        (image_id, spider_id)
    )
    con.commit()


    return redirect(url_for('spider_detail', spider_id=spider_id))

