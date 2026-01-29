from app import app, render_template

@app.get('/admin/inventory')
def inventory():  # put application's code here
    return render_template('backend/inventory.html', active_page='inventory',page_title='Inventory Management')