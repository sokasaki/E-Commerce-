from app import app, render_template

@app.get('/admin/reports')
def reports():  # put application's code here
    return render_template('backend/reports.html', active_page='reports',page_tittle='Report Mangement')    