
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
<div style='text-align: center; font-size: 20px;'>
<h2>👉 정답을 한글로 입력해 주세요</h2>
<h2>(힌트는 모두 다섯가지)</h2>
<img src='{{ image_url }}' width='640'><br><br>
<form method='post' action='/submit'>
  <label>🎯정답 : <input type='text' name='answer' style='font-size: 18px; padding: 8px; width: 300px;'><br></label>
  <label>⚙️제출자 이름 : <input type='text' name='name' style='font-size: 18px; padding: 8px; width: 300px;'><br></label>
  <label>📱전화번호: <input type='text' name='phone' style='font-size: 18px; padding: 8px; width: 300px;'><br></label>
  <br>
  <input type='submit' value='제출' style='font-size: 25px; padding: 10px 20px;'>
</form>
</div>
"""

correct_page = """
<body style="text-align:center; font-size: 20px; padding: 20px;">
<h2 style="font-size: 32px;">🎉 정답입니다! 축하합니다 🎉</h2>
<img src='{{ correct_image }}' width='640'><br><br>

<hr style="margin: 40px 0;">
<div style='text-align: left; display: inline-block; text-align: left; max-width: 640px; font-size: 18px; line-height: 1.6;'>
  <p>🎶 <strong>아삽</strong>은 하나님을 찬양하는 일을 맡은 노래하는 선생님이었어요.</p>
  <p>🎺 다윗 왕이 하나님께 예배드릴 때, 아삽은 악기를 연주하고 노래하며 예배를 도왔답니다.</p>
  <p>🤔 그는 "하나님, 왜 나쁜 사람들이 잘 사나요?" 하고 마음의 고민을 솔직히 노래로 표현했어요.</p>
  <p>📖 그의 노래는 <strong>시편 50편, 73편부터 83편</strong>까지에 있어요.</p>

  <p style="margin-top:20px;"><strong>🌟 아삽의 찬양 중 한 구절 (시편 73:26)</strong></p>
  <blockquote style='font-style: italic; color: #444; background: #f9f9f9; padding: 10px; border-left: 5px solid #ccc;'>
    "내 몸과 마음은 약해질 수 있지만,<br>
    하나님은 내 마음의 힘이고, 내가 가지는 가장 큰 복이세요."
  </blockquote>

  <p>🙏 아삽은 언제나 하나님께 가까이 가는 게 가장 좋은 일이라고 믿었어요.</p>
  <p>😊 그래서 우리도 힘들 때 하나님께 솔직하게 말하고, 찬양하며 기도할 수 있답니다. 🎵🙏</p>
</div>

<br><br>
<a href='/' style="font-size: 24px;">🏠 처음으로 돌아가기</a>
</body>
"""

success_page = """
<body style="text-align:center;">
<h2 style="font-size: 32px;">❌참여해 주셔서 감사합니다!</h2>
<h2 style="font-size: 32px;">🧪 다시 시도해주세요 🔁</h2>
<br>
<a href='/'style="font-size: 24px;">🏠처음으로 돌아가기</a>
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
<body style="text-align:center;">
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
