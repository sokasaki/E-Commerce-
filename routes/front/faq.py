from app import app,render_template


@app.get('/faq')
def faq():
    return render_template("front/faq.html")