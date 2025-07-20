
import random
from flask import Flask, request, redirect, session, render_template_string, send_file
from datetime import datetime
import os
import csv

app = Flask(__name__)
app.secret_key = '은혜로보물찾기_비밀키'

LOG_FILE = 'logs.csv'
ADMIN_PASSWORD = 'gangking15'

IMAGE_FILES = [
    '/static/image1.jpg',
    '/static/image2.jpg',
    '/static/image3.jpg',
    '/static/image4.jpg',
    '/static/image5.jpg'
]

CORRECT_ANSWER = '아삽'
CORRECT_IMAGE = '/static/correct_answer.jpg'

image_and_form_template = """
<div style='text-align: center;'>
<h2>👉 정답을 한글로 입력해 주세요</h2>
<img src='{{ image_url }}' width='640'><br><br>
<form method='post' action='/submit'>
  <label>🎯정답 : <input type='text' name='answer'><br></label>
  <label>⚙️이름 : <input type='text' name='name'><br></label>
  <label>📱전화번호: <input type='text' name='phone'><br></label>
  <br>
  <input type='submit' value='제출'>
</form>
"""

correct_page = """
<body style="text-align:center;">
<h2> 🎉정답입니다! 축하합니다 🎉</h2>
<img src='{{ correct_image }}' width='640'><br>
<br>
<a href='/'>🏠처음으로 돌아가기</a>
"""

success_page = """
<body style="text-align:center;">
<h2>❌참여해 주셔서 감사합니다!</h2>
<br>
<a href='/'>🏠처음으로 돌아가기</a>
"""

admin_login_page = """
<body style="text-align:center;">
<h2>관리자 로그인</h2>
<form method='post'>
  비밀번호: <input type='password' name='password'>
  <input type='submit' value='로그인'>
</form>
{% if error %}
<p style='color:red;'>{{ error }}</p>
{% endif %}
"""

winner_list_page = """
<h2>당첨자 목록</h2>
<table border='1'>
<tr><th>이름</th><th>전화번호</th><th>정답</th><th>시간</th></tr>
{% for row in rows %}
<tr>
  <td>{{ row[0] }}</td>
  <td>{{ row[1] }}</td>
  <td>{{ row[2] }}</td>
  <td>{{ row[3] }}</td>
</tr>
{% endfor %}
</table>
<a href='/download-logs'>CSV 다운로드</a>
"""

@app.route('/')
def index():
    selected_image = random.choice(IMAGE_FILES)
    session['current_image'] = selected_image
    return render_template_string(image_and_form_template, image_url=selected_image)

@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form.get('answer', '').strip()
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()

    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([name, phone, answer, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    if answer == CORRECT_ANSWER:
        return render_template_string(correct_page, correct_image=CORRECT_IMAGE)
    else:
        return render_template_string(success_page)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/winner-list')
        else:
            error = '비밀번호가 틀렸습니다.'
    return render_template_string(admin_login_page, error=error)

@app.route('/winner-list')
def winner_list():
    if not session.get('admin'):
        return redirect('/admin')

    rows = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
    return render_template_string(winner_list_page, rows=rows)

@app.route('/download-logs')
def download_logs():
    if not session.get('admin'):
        return redirect('/admin')
    return send_file(LOG_FILE, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
