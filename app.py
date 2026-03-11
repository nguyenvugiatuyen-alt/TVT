import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình Database
db_url = os.environ.get('postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a/quanlyphim_db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    db_url = 'postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a.singapore-postgres.render.com/quanlyphim_db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    all_rated = set() # Bổ sung set để chứa danh sách Rated
    
    for m in movies:
        if m.genre:
            for g in m.genre.split(','):
                all_genres.add(g.strip())
        if m.rated: # Bổ sung logic lấy các nhãn Rated từ Database
            all_rated.add(m.rated.strip())
            
    # Bổ sung rated_list vào lúc render_template
    return render_template('index.html', movies=movies, genres=sorted(list(all_genres)), rated_list=sorted(list(all_rated)))

@app.route('/add', methods=['POST'])
def add_movie():
    new_movie = Movie(
        name=request.form['name'], genre=request.form['genre'],
        date=request.form['date'], duration=request.form['duration'],
        rated=request.form.get('rated', ''), # Bổ sung thêm lấy dữ liệu Rated khi lưu phim mới
        director=request.form['director'], poster=request.form['poster']
    )
    db.session.add(new_movie)
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
