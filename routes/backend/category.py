from app import app, render_template, db
from model.Category import Category
from flask import request,redirect,url_for
@app.get('/admin/category')
def category():  # put application's code here
    module = 'category'
    rows = Category.query.all()
    # assert False, rows
    return render_template('backend/category.html', active_page='category', module=module, categorys=rows,page_title='Category Management')


@app.get('/admin/addCategory')
def addCategory_page():  # put application's code here
    return render_template('backend/Category/addCategory.html', active_page='addCategory')

@app.post('/admin/addCategory')
def addCategory():  # put application's code here
    name = request.form["name"]
    description = request.form["description"]

    category= Category(
        name=name,
        description=description
    )
    db.session.add(category)
    db.session.commit()

    return redirect(url_for('category'))

@app.get('/admin/editCategory')
def editCategory_page():  # put application's code here
    module = 'category'
    category_id = request.args.get('category_id')
    category = Category.query.get(int(category_id))
    return render_template('backend/Category/editCategory.html', active_page='category', module=module, category=category)


@app.post('/admin/editCategory')
def editCategory():
    category_id = request.form["category_id"]
    name = request.form["name"]
    description = request.form["description"]

    category = db.session.get(Category, int(category_id))
    if not category:
        return "Category not found", 404

    category.name = name
    category.description = description

    db.session.commit()

    return redirect(url_for('category'))


@app.post('/admin/deleteCategory')
def deleteCategory():
    category_id = request.form["category_id"]
    category = db.session.get(Category, int(category_id))
    if category:
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for('category'))