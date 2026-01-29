from app import app,render_template



@app.get('/check')
def check():
    return render_template("front/check-out.html")