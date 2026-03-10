import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
EXCEL_FILE = 'RẠP PHIM TVT.xlsx'

def read_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=['TÊN', 'THỂ LOẠI', 'NGÀY CHIẾU', 'THỜI LƯỢNG', 'RATED', 'ĐẠO DIỄN', 'POSTER'])
        df.to_excel(EXCEL_FILE, index=False)
        return df
    
    try:
        df = pd.read_excel(EXCEL_FILE).fillna('')
        if not df.empty and 'NGÀY CHIẾU' in df.columns:
            # Chuyển đổi ngày tháng an toàn
            df['NGÀY CHIẾU'] = pd.to_datetime(df['NGÀY CHIẾU'], errors='coerce')
            df['NGÀY CHIẾU'] = df['NGÀY CHIẾU'].dt.strftime('%d/%m/%Y').fillna('Chưa rõ')
        return df
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return pd.DataFrame(columns=['TÊN', 'THỂ LOẠI', 'NGÀY CHIẾU', 'THỜI LƯỢNG', 'RATED', 'ĐẠO DIỄN', 'POSTER'])

@app.route('/')
def index():
    df = read_data()
    
    # SỬA LỖI TẠI ĐÂY: Kiểm tra nếu df trống thì trả về danh sách rỗng thay vì số 0
    if not df.empty and 'THỂ LOẠI' in df.columns:
        # Lấy danh sách thể loại và lọc bỏ các giá trị rỗng
        genres_series = df['THỂ LOẠI'].astype(str).str.split(', ')
        all_genres = sorted(list(set([item for sublist in genres_series for item in sublist if item.strip()])))
        
        # Lấy danh sách Rated thực tế
        all_rated = sorted([r for r in df['RATED'].unique() if str(r).strip() != ''])
    else:
        all_genres = []
        all_rated = []

    movies = df.to_dict(orient='records')
    for i, m in enumerate(movies): 
        m['id'] = i
        
    return render_template('index.html', movies=movies, genres=all_genres, rated_list=all_rated)

@app.route('/add', methods=['POST'])
def add_movie():
    df = read_data()
    new_movie = {
        'TÊN': request.form['name'], 'THỂ LOẠI': request.form['genre'],
        'NGÀY CHIẾU': request.form['date'], 'THỜI LƯỢNG': request.form['duration'],
        'RATED': request.form['rated'], 'ĐẠO DIỄN': request.form['director'],
        'POSTER': request.form['poster']
    }
    df = pd.concat([df, pd.DataFrame([new_movie])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_movie(id):
    df = read_data()
    if id < len(df):
        df.loc[id, 'TÊN'] = request.form['name']
        df.loc[id, 'ĐẠO DIỄN'] = request.form['director']
        df.loc[id, 'THỂ LOẠI'] = request.form['genre']
        df.loc[id, 'NGÀY CHIẾU'] = request.form['date']
        df.loc[id, 'THỜI LƯỢNG'] = request.form['duration']
        df.loc[id, 'RATED'] = request.form['rated']
        df.loc[id, 'POSTER'] = request.form['poster']
        df.to_excel(EXCEL_FILE, index=False)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_movie(id):
    df = read_data()
    if id < len(df):
        df = df.drop(df.index[id]).reset_index(drop=True)
        df.to_excel(EXCEL_FILE, index=False)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)