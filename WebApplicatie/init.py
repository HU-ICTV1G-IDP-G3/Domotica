from flask import Flask, render_template, request, url_for, redirect, session, g, flash, blueprints, jsonify
import pymysql, re, redis, gc, datetime
from pymysql import escape_string as escape
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from flask_wtf import Form

from wtforms import PasswordField, validators, HiddenField, StringField, SelectField
from wtforms import TextAreaField, BooleanField
from wtforms.validators import EqualTo, Optional, data_required
from wtforms.validators import Length, Email

from passlib.handlers.sha2_crypt import sha256_crypt as hash

#Importeert de redis functies voor later gebruik.
store = RedisStore(redis.StrictRedis())

app = Flask(__name__, static_url_path='/static')
app.config.update(
    SESSION_COOKIE_NAME='DSS',
    SESSION_KEY_BITS=128
)

#Een form gegenereert voor de pagina admin.html
#Hiermee kan een admin een nieuwe user toevoegen.
class NieuweGebruikerForm(Form):
     gebruikersnaam = StringField('Gebruikersnaam', validators=[
           data_required('Voer een gebruikersnaam in.')])
     password = PasswordField('Voer een veilig wachtwoord in.', validators=[
           data_required('Voer een geldig wachtwoord in.')])
     voornaam = StringField('Voornaam', validators=[
           data_required('Dit veld is verplicht.'),
           Length(min=2, max=30, message=(u'Uw voornaam moet minimaal 2 en mag maximaal 30 tekens bevatten.'))])
     achternaam = StringField('Achternaam', validators=[
           data_required('Dit veld is verplicht.'),
           Length(min=2, max=30, message=(u'Uw achternaam moet minimaal 2 en mag maximaal 30 tekens bevatten.'))])
     rang = SelectField('Rang', choices=[("1", "Bewoner"), ("2", "Meldkamer medewerker"), ("3", "Admin")], default="1")

#Voor serverside sessions, maakt gebruik van redis. (Vergeet dus niet dat redis een vereiste is op de locatie waar je deze applicatie wilt draaien.)
KVSessionExtension(store, app)

# @app.before_request
# def db_connect():
#     g.db_conn = pymysql.connect(host='213.233.237.7',
#                                  user='domotica',
#                                  password='Secret so secret',
#                                  db='domotica_db',
#                                  charset='utf8',
#                                  port=3306)
#     global cur
#     cur = g.db_conn.cursor()


#De index pagina, met de login staat hieronder vermeld:
@app.route('/', methods=["GET", "POST"])
def login():
    return render_template("login.html")


#De bewoner pagina, met de verlichting functies staan hieronder vermeld:
@app.route('/bewoner/', methods=["GET", "POST"])
def bewoner():
    return render_template("bewoner.html")


#De meldkamer pagina, staat hieronder vermeld:
@app.route('/meldkamer/', methods=["GET", "POST"])
def meldkamer():
    return render_template("meldkamer.html")


#De admin pagina, met de funcites om een nieuw account aan te maken en te beheren staat hieronder vermeld:
@app.route('/admin/', methods=["GET", "POST"])
def admin():
    #Vraagt het eerder gemaakte 'NieuweGebruikerForm' form aan.
    form = NieuweGebruikerForm()

    #Zodra de post op de pagina langs de vallidators van WTForm zijn gegaan kan de rest plaatsvinden.
    if form.validate_on_submit():
        #Nodig voor de request die we hierna gaan maken.
        admin = NieuweGebruikerForm(request.form)

        #Alle velden worden binnengehaald en aan een variabele gekoppelt.
        username = admin.gebruikersnaam.data
        password = admin.password.data
        voornaam = admin.voornaam.data
        achternaam = admin.achternaam.data
        rang = admin.rang.data

        #Een laatste check of de username wel beschikbaar is (Deze moet uniek zijn):
        cur.execute("SELECT username FROM User WHERE username =%s", (escape(username)))
        beschikbaar = cur.fetchall()

        if beschikbaar == ():
            #Het wachtwoord wordt met een random salt gehashed en beide worden in één variabele gestopt.
            versleutelde_password = hash.encrypt(escape(password))

            #De gegevens worden naar de database verstuurd:
            cur.execute("INSERT INTO User (username, forename, lastname, password, rank) VALUES (%s, %s, %s, %s, %s)", (escape(username), escape(voornaam), escape(achternaam), versleutelde_password, int(rang)))



    return render_template("admin.html", NieuweGebruikerForm=form)

if __name__ == '__main__':
    app.secret_key = '*87gas6&*(73()fa98Nla&$62Nv%#{az' #Secret key for sessions | This key HAS TO BE CHANGED IN THE FINAL VERSION (and not being published on GitHub)
    app.run(debug=True)