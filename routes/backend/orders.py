from app import app, render_template

@app.get('/admin/orders')
def orders():  # put application's code here
    return render_template('backend/orders.html', active_page='orders',page_title='Orders Management')