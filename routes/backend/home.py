from app import app, render_template

@app.get('/admin')
@app.get('/admin/home')
def admin_home():  # Admin dashboard home

    return render_template('backend/index.html', active_page='home')