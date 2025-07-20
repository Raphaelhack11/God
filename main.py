from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class GrantRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact = db.Column(db.String(150))
    amount = db.Column(db.Integer)
    approved = db.Column(db.Boolean, default=False)

# Admin credentials (hardcoded for simplicity)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    contact = request.form['contact']
    amount = request.form['amount']

    if not contact or not amount or not (100 <= int(amount) <= 50000):
        flash('Invalid input. Please try again.', 'error')
        return redirect(url_for('index'))

    grant = GrantRequest(contact=contact, amount=int(amount))
    db.session.add(grant)
    db.session.commit()
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    grants = GrantRequest.query.all()
    return render_template('admin.html', grants=grants)

@app.route('/approve/<int:id>')
def approve(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    grant = GrantRequest.query.get_or_404(id)
    grant.approved = True
    db.session.commit()
    flash('Grant approved. Remember to notify the user manually.')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
