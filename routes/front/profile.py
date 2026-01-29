from app import app,render_template


@app.get('/profile')
def profile():
    return render_template("front/profile.html")