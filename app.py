import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. CẤU HÌNH DATABASE
# Ưu tiên lấy từ môi trường Render, nếu không có thì dùng link trực tiếp
db_url = os.environ.get('DATABASE_URL') 
if not db_url:
    db_url = 'postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a.singapore-postgres.render.com/quanlyphim_db'

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. MODEL
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    date = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    rated = db.Column(db.String(20))
    director = db.Column(db.String(100))
    poster = db.Column(db.String(500))

# 3. HÀM ĐỒNG BỘ EXCEL (Mới)
def sync_to_excel():
    try:
        movies = Movie.query.all()
        data = [{
            "Tên phim": m.name, "Đạo diễn": m.director, "Thể loại": m.genre,
            "Ngày chiếu": m.date, "Thời lượng": m.duration, "Rated": m.rated, "Poster": m.poster
        } for m in movies]
        df = pd.DataFrame(data)
        df.to_excel("data.xlsx", index=False)
    except Exception as e:
        print(f"Lỗi đồng bộ Excel: {e}")

with app.app_context():
    db.create_all()

# 4. ROUTES
@app.route('/')
def index():
    movies = Movie.query.all()
    all_genres = set()
    all_rated = set()
    for m in movies:
        if m.genre:
            for g in m.genre.split(','): all_genres.add(g.strip())
        if m.rated: all_rated.add(m.rated.strip())
    return render_template('index.html', movies=movies, genres=sorted(list(all_genres)), rated_list=sorted(list(all_rated)))

@app.route('/add', methods=['POST'])
def add_movie():
    new_movie = Movie(
        name=request.form['name'], director=request.form['director'],
        genre=request.form['genre'], date=request.form['date'],
        duration=request.form['duration'], rated=request.form.get('rated', ''),
        poster=request.form['poster']
    )
    db.session.add(new_movie)
    db.session.commit()
    sync_to_excel() # Đồng bộ sau khi thêm
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_movie(id):
    movie = db.session.get(Movie, id)
    if movie:
        movie.name = request.form['name']
        movie.director = request.form['director']
        movie.genre = request.form['genre']
        movie.date = request.form['date']
        movie.duration = request.form['duration']
        movie.rated = request.form['rated']
        movie.poster = request.form['poster']
        db.session.commit()
        sync_to_excel() # Đồng bộ sau khi sửa
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_movie(id):
    movie = db.session.get(Movie, id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
        sync_to_excel() # Đồng bộ sau khi xóa
    return redirect(url_for('index'))

@app.route('/import-excel')
def import_excel():
    if not os.path.exists("data.xlsx"):
        return "Không tìm thấy file Excel trên hệ thống!"
    try:
        df = pd.read_excel("data.xlsx")
        for _, row in df.iterrows():
            new_movie = Movie(
                name=str(row['Tên phim']), director=str(row['Đạo diễn']),
                genre=str(row['Thể loại']), date=str(row['Ngày chiếu']),
                duration=str(row['Thời lượng']), rated=str(row['Rated']),
                poster=str(row['Poster'])
            )
            db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Lỗi: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
