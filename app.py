from flask import Flask, request, session, redirect, render_template_string, url_for
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# User data
USER = {
    'username': 'admin',
    'password': '1234567890',
    '2fa_secret': pyotp.random_base32()
}

# Load HTML from file in same directory
def load_template(filename):
    with open(filename, 'r') as f:
        return f.read()

@app.route('/')
def index():
    if 'verified' in session:
        return render_template_string(load_template("home.html"))
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER['username'] and request.form['password'] == USER['password']:
            session['authenticated'] = True
            return redirect('/verify')
    return render_template_string(load_template("login.html"))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'authenticated' not in session:
        return redirect('/login')

    totp = pyotp.TOTP(USER['2fa_secret'])
    if request.method == 'POST':
        token = request.form['token']
        if totp.verify(token):
            session['verified'] = True
            return redirect('/')
        return 'Invalid 2FA token', 403

    uri = totp.provisioning_uri(name="admin@example.com", issuer_name="2FA Project")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('ascii')

    html = load_template("verify.html")
    return render_template_string(html, qr_data=img_b64)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
