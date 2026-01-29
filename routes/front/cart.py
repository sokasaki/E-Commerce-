from app import app,render_template



@app.get('/cart')
def cart():
    return render_template("front/cart.html")