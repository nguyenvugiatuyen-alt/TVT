import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# CẤU HÌNH DATABASE
db_url = os.environ.get('postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a/quanlyphim_db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
elif not db_url:
    db_url = 'postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a.singapore-postgres.render.com/quanlyphim_db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODEL
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    date = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    rated = db.Column(db.String(20))
    director = db.Column(db.String(100))
    poster = db.Column(db.String(500))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    movies = Movie.query.all()
    all_genres = set()
    for m in movies:
        if m.genre:
            for g in m.genre.split(','):
                all_genres.add(g.strip())
    all_rated = sorted(list(set([m.rated for m in movies if m.rated])))
    return render_template('index.html', movies=movies, genres=sorted(list(all_genres)), rated_list=all_rated)

@app.route('/import-excel')
def import_excel():
    file_path = 'data.xlsx'
    if not os.path.exists(file_path):
        return "Lỗi: Không tìm thấy file data.xlsx trên GitHub!"
    try:
        df = pd.read_excel(file_path).fillna('')
        count = 0
        for _, row in df.iterrows():
            if not str(row.get('TÊN', '')).strip(): continue
            if not Movie.query.filter_by(name=str(row['TÊN'])).first():
                d = row.get('NGÀY CHIẾU', '')
                date_str = d.strftime('%d/%m/%Y') if isinstance(d, pd.Timestamp) else str(d)
                new_movie = Movie(
                    name=str(row['TÊN']), genre=str(row.get('THỂ LOẠI', '')),
                    date=date_str, duration=str(row.get('THỜI LƯỢNG', '')),
                    rated=str(row.get('RATED', '')), director=str(row.get('ĐẠO DIỄN', '')),
                    poster=str(row.get('POSTER', ''))
                )
                db.session.add(new_movie)
                count += 1
        db.session.commit()
        return f"Thành công! Đã nạp {count} phim. <a href='/'>Về trang chủ</a>"
    except Exception as e:
        return f"Lỗi xử lý: {str(e)}"

@app.route('/add', methods=['POST'])
def add_movie():
    new_movie = Movie(
        name=request.form['name'], genre=request.form['genre'],
        date=request.form['date'], duration=request.form['duration'],
        rated=request.form['rated'], director=request.form['director'],
        poster=request.form['poster']
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_movie(id):
    movie = db.session.get(Movie, id)
    if movie:
        movie.name, movie.genre = request.form['name'], request.form['genre']
        movie.date, movie.duration = request.form['date'], request.form['duration']
        movie.rated, movie.director = request.form['rated'], request.form['director']
        movie.poster = request.form['poster']
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_movie(id):
    movie = db.session.get(Movie, id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
