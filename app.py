import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình Database
# Ưu tiên lấy link từ biến môi trường DATABASE_URL trên Render
db_url = os.environ.get('postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a/quanlyphim_db')

if db_url:
    # Tự động sửa postgres:// thành postgresql:// nếu Render cấp link cũ
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    # Nếu không tìm thấy link trên Render, dùng cái link trực tiếp của ông ở đây
    db_url = 'postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a.singapore-postgres.render.com/quanlyphim_db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ĐỊNH NGHĨA BẢNG DỮ LIỆU
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    date = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    rated = db.Column(db.String(20))
    director = db.Column(db.String(100))
    poster = db.Column(db.String(500))

# Tạo database nếu chưa có
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    movies = Movie.query.all()
    # Lấy danh sách thể loại để lọc
    all_genres = set()
    for m in movies:
        if m.genre:
            for g in m.genre.split(','):
                all_genres.add(g.strip())
    
    all_rated = sorted(list(set([m.rated for m in movies if m.rated])))
    return render_template('index.html', movies=movies, genres=sorted(list(all_genres)), rated_list=all_rated)

@app.route('/add', methods=['POST'])
def add_movie():
    new_movie = Movie(
        name=request.form['name'],
        genre=request.form['genre'],
        date=request.form['date'],
        duration=request.form['duration'],
        rated=request.form['rated'],
        director=request.form['director'],
        poster=request.form['poster']
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_movie(id):
    movie = Movie.query.get(id)
    if movie:
        movie.name = request.form['name']
        movie.genre = request.form['genre']
        movie.date = request.form['date']
        movie.duration = request.form['duration']
        movie.rated = request.form['rated']
        movie.director = request.form['director']
        movie.poster = request.form['poster']
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_movie(id):
    movie = Movie.query.get(id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
