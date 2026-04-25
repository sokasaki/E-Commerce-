from app import app, render_template


@app.errorhandler(404)
def error_404(e):
    return render_template('error/404.html')


@app.errorhandler(500)
def error_500(e):
    return render_template('error/500.html')