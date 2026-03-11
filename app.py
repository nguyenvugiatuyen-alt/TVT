import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# KẾT NỐI DATABASE
# Thay 'URL_DATABASE_CUA_BAN' bằng cái bạn đã copy ở Bước 1
# Nếu chạy ở máy cá nhân thì dùng tạm sqlite để test
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgresql://quanlyphim_db_user:4F3947ei2Rf7WFMml7ACMYqBbDrekRA7@dpg-d6ns0rnkijhs739rk800-a/quanlyphim_db')
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
    
@app.route('/import-excel')
def import_excel():
    import pandas as pd
    import os
    
    file_path = 'RẠP PHIM TVT.xlsx'
    if not os.path.exists(file_path):
        return "Không tìm thấy file Excel trên hệ thống!"
        
    try:
        df = pd.read_excel(file_path).fillna('')
        count = 0
        for index, row in df.iterrows():
            # Bỏ qua nếu tên phim bị trống
            if not str(row.get('TÊN', '')).strip():
                continue
                
            # Kiểm tra xem phim đã có trong DB chưa (tránh bị nhân đôi nếu lỡ bấm 2 lần)
            exist = Movie.query.filter_by(name=str(row['TÊN'])).first()
            if not exist:
                # Xử lý ngày tháng
                date_val = row.get('NGÀY CHIẾU', '')
                if pd.notnull(date_val) and isinstance(date_val, pd.Timestamp):
                    date_val = date_val.strftime('%d/%m/%Y')
                else:
                    date_val = str(date_val)

                new_movie = Movie(
                    name=str(row['TÊN']),
                    genre=str(row.get('THỂ LOẠI', '')),
                    date=date_val,
                    duration=str(row.get('THỜI LƯỢNG', '')),
                    rated=str(row.get('RATED', '')),
                    director=str(row.get('ĐẠO DIỄN', '')),
                    poster=str(row.get('POSTER', ''))
                )
                db.session.add(new_movie)
                count += 1
        
        db.session.commit()
        return f"<h1>Tuyệt vời! Đã copy thành công {count} phim từ Excel sang Database vĩnh viễn.</h1> <a href='/'>Quay lại trang chủ</a>"
    except Exception as e:
        return f"<h1>Bị lỗi rồi: {str(e)}</h1>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
