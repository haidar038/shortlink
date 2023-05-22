from flask import Flask, render_template, redirect, request, abort, flash, url_for, send_from_directory
import string, random, secrets
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_limiter import Limiter
from urllib.parse import urlparse
from flask_mail import Mail, Message
from flask_toastr import Toastr
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, url, Email
from flask_compress import Compress
from flask_assets import Environment, Bundle
from flask_caching import Cache

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["RATELIMIT_DEFAULT"] = "100 per day"
app.config["SECRET_KEY"] = secrets.token_hex(16)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'logging_name': 'sqlalchemy'}
app.config['MAIL_SERVER'] = 'smtp-relay.sendinblue.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'etercode30@gmail.com'
app.config['MAIL_PASSWORD'] = 'p8fdMwC39bac2POy'

compress = Compress()
assets = Environment(app)
toastr = Toastr(app)
db = SQLAlchemy()
mail = Mail(app)
migrate = Migrate(app, db)
db.init_app(app)
compress.init_app(app)
limiter = Limiter(
    app,
    default_limits=["100 per day"]
)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Define SASS Bundle
scss = Bundle('scss/main.scss', filters='pyscss', output='gen/style.css')
assets.register('scss', scss)

css = Bundle('css/style.css', filters='cssmin', output='gen/all.css')
assets.register('css', css)

# Define the JS bundle
js = Bundle('js/main.js', filters='jsmin', output='gen/all.js')
assets.register('js', js)

# Models
class ShortenedUrl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_url = db.Column(db.String(10), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<ShortenedUrl {self.short_url}>"

# Create a form for URL input
class UrlForm(FlaskForm):
    url = StringField('Long URL', validators=[DataRequired(), url()])
    
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])

with app.app_context():
    db.create_all()

@app.route('/')
@cache.cached(timeout=300)
def index():
    form = UrlForm()
    urls = ShortenedUrl.query.all()
    return render_template('index.html', urls=urls, form=form, page="home")

def sanitize_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        return None
    else:
        return parsed_url.geturl()
    
@app.route('/', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=300)
def shorten():
    def shorten():
    form = UrlForm()
    if form.validate_on_submit():
        original_url = form.url.data
        original_url = sanitize_url(original_url)
        if not original_url:
            # Handle invalid URL input
            flash('Invalid URL')
            return render_template('index.html')

        short_url = ''.join(random.choices(
            string.ascii_letters + string.digits, k=5))

        # Check if the ShortenedUrl object already exists in the database
        shortened_url_object = ShortenedUrl.query.filter_by(original_url=original_url).first()
        if shortened_url_object is None:
            # The ShortenedUrl object does not exist in the database, so add it
            shortened_url_object = ShortenedUrl(
                original_url=original_url, short_url=short_url, created_at=datetime.utcnow())
            db.session.add(shortened_url_object)
            db.session.commit()
        else:
            # The ShortenedUrl object already exists in the database, so do nothing
            pass

        # Render the shortened URL page with the new short URL
        return redirect(url_for('shorten_success', short_url=short_url))

    return render_template('index.html', form=form)

@app.route('/googledb6605d07a2ef7ce.html')
def google_verification():
    return render_template('googledb6605d07a2ef7ce.html')


@app.route('/robots.xml')
def robots():
    return render_template('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.route('/<short_url>')
def redirect_to_original_url(short_url):
    # Retrieve the original URL from the database
    shortened_url = ShortenedUrl.query.filter_by(short_url=short_url).first()
    if shortened_url:
        # Increment the clicks count of the ShortenedUrl object
        shortened_url.clicks += 1
        db.session.commit()
        original_url = shortened_url.original_url
        # Redirect the user to the original URL
        return redirect(original_url)
    else:
        # If the shortened URL is not found, return a 404 error
        return abort(404)

@app.route('/shorten-success/<short_url>')
@cache.cached(timeout=300)
def shorten_success(short_url):
    # Retrieve the original URL from the database
    shortened_url = ShortenedUrl.query.filter_by(short_url=short_url).first()
    clicked = shortened_url.clicks
    if shortened_url:
        original_url = shortened_url.original_url
        # Render the "shorten_success" page with the short URL and original URL
        
        # host_url = urlparse(request.host_url).netloc
        
        return render_template('shorten.html', short_url= host_url + '/' + short_url, original_url=original_url, clicked=clicked, page="shorten")
    else:
        # If the shortened URL is not found, return a 404 error
        return abort(404)

@app.route('/about')
def about():
    return render_template('about.html', page="about")

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # Send email to support email address
        msg = Message('Contact Form Submission', sender=email, recipients=['etercode30@gmail.com'])
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)

        flash('Thank you for contacting us! We will get back to you shortly.')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form, page="contact")

@app.route('/privacy')
def privacy():
    return render_template('privacy_policy.html', page="privacy")

@app.route('/tou')
def tou():
    return render_template('tou.html', page="tou")

if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
    app.run(port=5000)
    # app.run(debug=True)
