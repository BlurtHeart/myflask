from app import create_app, db
import os

app = create_app('development')
# why here push app context
context = app.app_context()
context.push()
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
