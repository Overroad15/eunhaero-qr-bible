
import random
from flask import Flask, request, redirect, session, render_template_string, send_file
from datetime import datetime
import os
import csv

app = Flask(__name__)
app.secret_key = '은혜로보물찾기_비밀키'

LOG_FILE = 'logs.csv'
ADMIN_PASSWORD = 'gangking15'

VIDEO_FILES = [
    '/static/video1.mp4',
    '/static/video2.mp4',
    '/static/video3.mp4',
    '/static/video4.mp4',
    '/static/video5.mp4'
]

CORRECT_ANSWER = '아삽'
CORRECT_VIDEO = '/static/correct_answer.mp4'

watch_and_answer_template = """
<h2>정답을 맞춰주세요!</h2>
<video width='640' height='360' controls autoplay onended="document.getElementById('answer-form').style.display='block';">
  <source src='{{ video_url }}' type='video/mp4'>
  Your browser does not support the video tag.
</video>

<div id='answer-form' style='display:none;'>
  <h3>정답과 정보를 한글로 입력해 주세요</h3>
  <form method='post' action='/submit'>
    정답: <input type='text' name='answer'><br>
    이름: <input type='text' name='name'><br>
    전화번호: <input type='text' name='phone'><br>
    <input type='submit' value='제출'>
  </form>
</div>
"""

correct_page = """
<h2>정답입니다! 축하합니다 🎉</h2>
<video width='640' height='360' controls autoplay>
  <source src='{{ correct_video }}' type='video/mp4'>
  Your browser does not support the video tag.
</video>
<a href='/'>처음으로 돌아가기</a>
"""

success_page = """
<h2>참여해 주셔서 감사합니다!</h2>
<a href='/'>처음으로 돌아가기</a>
"""

admin_login_page = """
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
    selected_video = random.choice(VIDEO_FILES)
    return render_template_string(watch_and_answer_template, video_url=selected_video)

@app.route('/submit', methods=['POST'])
def submit():
    answer = request.form.get('answer', '').strip()
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()

    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([name, phone, answer, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    if answer == CORRECT_ANSWER:
        return render_template_string(correct_page, correct_video=CORRECT_VIDEO)
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
    app.run(debug=True)
