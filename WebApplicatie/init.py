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
                                 password='Maybe there is no password?',
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


@app.route('/bewoner/verlichting')
@login_req
@bewoner_req
def verlichting():
    a = request.args.get('a', '0', type=str)
    b = request.args.get('b', '0', type=int)

    #Controlle of de gebruiker wel toegang mag hebben tot deze verlichting:
    idWoning = int(session['login'][0][6])
    cur.execute("SELECT idLight FROM domotica_db.Light WHERE idWoning =%s", (idWoning))
    idlight = cur.fetchall()

    #For loop te checken of variabele B voor komt in de variabele idlight (de net gefetchde waarde).
    for i in range(len(idlight)):
        if b in idlight[i]:
            #Hier wordt de verlichting aangepast.
            if a == 'false':
                cur.execute("UPDATE Light SET turnedon=0 WHERE idLight=%s", (b))
                g.db_conn.commit()
            elif a == 'true':
                cur.execute("UPDATE Light SET turnedon=1 WHERE idLight=%s", (b))
                g.db_conn.commit()

    return jsonify(result=a)

@app.route('/bewoner/camera_uitschakelen')
@login_req
@bewoner_req
def camera_uitschakelen():
    a = request.args.get('a', '0', type=str)

    #Woning ID om de cameras uit te schakelen
    idWoning = int(session['login'][0][6])

    #Camera aan of uit...
    if a == 'false':
        cur.execute("UPDATE Woning SET camera=0 WHERE idWoning=%s", (idWoning))
        g.db_conn.commit()
    elif a == 'true':
        cur.execute("UPDATE Woning SET camera=1 WHERE idWoning=%s", (idWoning))
        g.db_conn.commit()

    return jsonify(result=a)


#De bewoner pagina, met de verlichting functies staan hieronder vermeld:
@app.route('/bewoner/', methods=["GET", "POST"])
@login_req
@bewoner_req
def bewoner():
    #Check of er geen woning aan deze user is gekoppeld.
    if not session['login'][0][6] == None or session['login'][0][6] == ():
        heeftwoning = 1

        #Haalt de woning ID op uit de sessie.
        idWoning = int(session['login'][0][6])

        #Doormiddel van de woning ID wordt de informatie voor de verlichting opgehaald (gekoppeld aan de woning)
        cur.execute("SELECT idLight, idWoning, name, turnedon FROM domotica_db.Light WHERE idWoning =%s", (idWoning))
        light_info = cur.fetchall()

        #Doormiddel van de woning ID wordt de informatie over de woning opgehaald.
        cur.execute("SELECT idWoning, adress, camera, helpbutton FROM domotica_db.Woning WHERE idWoning =%s", (idWoning))
        woning_info = cur.fetchall()

        if request.method == "POST":
            alarm = request.form.get('alarm', None)
            if alarm == "alarm":
                cur.execute("UPDATE Woning SET helpbutton=1 WHERE idWoning=%s", (idWoning))
                g.db_conn.commit()

        if not light_info == ():
            # Deze woning heeft verlichting!
            heeftverlichting = 1
        else:
            #Deze woning heeft GEEN verlichting!
            heeftverlichting = 0
            light_info=0

    else:
        heeftwoning=0
        light_info=0
        woning_info=0
        heeftverlichting = 0

    return render_template("bewoner.html", light_info=light_info, woning_info=woning_info, heeftwoning=heeftwoning, heeftverlichting=heeftverlichting)



@app.route('/meldkamer/alarm')
@login_req
@meldkamer_req
def alarm():
    cur.execute("SELECT idWoning, adress FROM domotica_db.Woning WHERE helpbutton = 1;")
    a = cur.fetchall()
    return jsonify(result=a)


#De meldkamer pagina, staat hieronder vermeld:
@app.route('/meldkamer/', methods=["GET", "POST"])
@login_req
@meldkamer_req
def meldkamer():
    cur.execute("SELECT idWoning, adress, camera, helpbutton FROM domotica_db.Woning")
    woning_info = cur.fetchall()
    cur.execute("SELECT idCamera, idWoning, name, url FROM domotica_db.Camera")
    camera_info = cur.fetchall()
    session['camera_url'] = 0
    return render_template("meldkamer.html", woning_info=woning_info, camera_info=camera_info)

@app.route('/meldkamer/<woning>/', methods=["GET", "POST"])
@login_req
@meldkamer_req
def meldkamerstream(woning):
    cur.execute("SELECT idWoning, adress, camera, helpbutton FROM domotica_db.Woning")
    woning_info = cur.fetchall()
    cur.execute("SELECT idCamera, idWoning, name, url FROM domotica_db.Camera")
    camera_info = cur.fetchall()
    session['camera_url'] = int(woning)

    cur.execute("SELECT idCamera, name, url, idWoning FROM domotica_db.Camera WHERE idWoning =%s", (int(woning)))
    camera_id = cur.fetchall()

    return render_template("meldkamer2.html", woning_info=woning_info, camera_info=camera_info, camera_id=camera_id)


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