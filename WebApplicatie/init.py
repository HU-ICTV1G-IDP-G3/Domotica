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
from functools import wraps

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

class LoginForm(Form):
     gebruikersnaam = StringField('Gebruikersnaam', validators=[
           data_required('Voer een gebruikersnaam in.')])
     password = PasswordField('Voer een veilig wachtwoord in.', validators=[
           data_required('Voer een geldig wachtwoord in.')])


#Voor serverside sessions, maakt gebruik van redis. (Vergeet dus niet dat redis een vereiste is op de locatie waar je deze applicatie wilt draaien.)
KVSessionExtension(store, app)

@app.before_request
def db_connect():
    g.db_conn = pymysql.connect(host='213.233.237.7',
                                 user='domotica',
                                 password='This password is quantum computer proof.',
                                 db='domotica_db',
                                 charset='utf8',
                                 port=3306)
    global cur
    cur = g.db_conn.cursor()

@app.teardown_request
def db_disconnect(exception=None):
    g.db_conn.close()

#Check of de gebruiker is ingelogd.
def login_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'ingelogd' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

#Check of de gebruiker een bewoner is of niet:
#Indien niet kan de gebruiker NIET naar /bewoner/
def bewoner_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if int(session['login'][0][2]) == 1:
            return f(*args, **kwargs)
        elif int(session['login'][0][2]) == 2:
            return redirect(url_for('meldkamer'))
        elif int(session['login'][0][2]) >= 3:
            return redirect(url_for('admin'))
        else:
            #Indien geen van de bovenstaande optie van toepassing zijn word de persoon uitgelogd.
            session.clear()
            gc.collect()
            return redirect(url_for('login'))
    return wrap

#Check of de gebruiker wel een status heeft als meldkamer of hoger (admin).
def meldkamer_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        #Voor toegang van de meldkamer pagina is een status van 2 of hoger nodig.
        if int(session['login'][0][2]) >= 2:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('bewoner'))
    return wrap

#Check of de gebruiker wel een admin status heeft.
def admin_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        #Voor toegang van de admin pagina heb je de status 3 nodig.
        if int(session['login'][0][2]) == 3:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('bewoner'))
    return wrap

#De sessie wordt gecleared en memory gedumpt, daarna word de user doorgeschakelt naar de homepage (login).
@app.route('/logout/')
@login_req
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('login'))


#De index pagina, met de login staat hieronder vermeld:
@app.route('/', methods=["GET", "POST"])
def login():
    #Vraagt het eerder gemaakte 'NieuweGebruikerForm' form aan.
    form = LoginForm()

    #Zodra de post op de pagina langs de vallidators van WTForm zijn gegaan kan de rest plaatsvinden.
    if form.validate_on_submit():
        #Nodig voor de request die we hierna gaan maken.
        inloggen = LoginForm(request.form)

        #Alle velden worden binnengehaald en aan een variabele gekoppelt.
        username = inloggen.gebruikersnaam.data
        password = inloggen.password.data

        #Haal username en wachtwoord op uit de database.
        cur.execute("SELECT username, password, rank, forename, lastname, idUser, idWoning FROM User WHERE username =%s", (escape(username)))
        login_info = cur.fetchall()

        #Bestaat deze username wel? Anders een error...:
        if not login_info == ():

            #Wachtwoord vergelijken met hash:
            if hash.verify(password, login_info[0][1]):
                session['ingelogd'] = True
                session['login'] = login_info
                if int(login_info[0][2]) == 3:
                    return redirect(url_for('admin'))
                elif int(login_info[0][2]) == 2:
                    return redirect(url_for('meldkamer'))
                else:
                    return redirect(url_for('bewoner'))

            else:
                form.password.errors.append('')

        else:
            form.gebruikersnaam.errors.append('')


    return render_template("login.html", LoginForm=form)


#De bewoner pagina, met de verlichting functies staan hieronder vermeld:
@app.route('/bewoner/', methods=["GET", "POST"])
@login_req
@bewoner_req
def bewoner():
    idWoning = int(session['login'][0][6])
    cur.execute("SELECT idLight, idWoning, name, turnedon FROM domotica_db.Light WHERE idWoning =%s", (idWoning))
    light_info = cur.fetchall()

    return render_template("bewoner.html", light_info=light_info)


#De meldkamer pagina, staat hieronder vermeld:
@app.route('/meldkamer/', methods=["GET", "POST"])
@login_req
@meldkamer_req
def meldkamer():
    return render_template("meldkamer.html")


#De admin pagina, met de funcites om een nieuw account aan te maken en te beheren staat hieronder vermeld:
@app.route('/admin/', methods=["GET", "POST"])
@login_req
@admin_req
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
            g.db_conn.commit()

            #Redirect naar dezelfde pagina voor een refresh, later misschien naar de net aangemaakte user?
            return redirect(url_for('admin'))

    return render_template("admin.html", NieuweGebruikerForm=form)

if __name__ == '__main__':
    app.secret_key = '*87gas6&*(73()fa98Nla&$62Nv%#{az' #Secret key for sessions | This key HAS TO BE CHANGED IN THE FINAL VERSION (and not being published on GitHub)
    app.run(debug=True)