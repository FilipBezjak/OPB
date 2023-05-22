from glob import glob
from bottle import * 
import sqlite3
import hashlib
import tracemalloc

tracemalloc.start()
#bazo smo naredili v priklop 
baza_datoteka = "test.db"
skrivnost = "wct3uifzgciuwrt427364gi237g4"
debug(True)

napakaSporocilo=None
#vrne staro napako in jo nastavi na novo, ki jo vrne ob naslednjem klicu.
def nastaviSporocilo(sporocilo = None):
    global napakaSporocilo
    staro = napakaSporocilo
    napakaSporocilo = sporocilo
    return staro

#napaka za staticne vire: slike, css....
static_dir = "./static"

#strezenje staticnih datotek
@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

@get('/')
def prijava():
    napaka = nastaviSporocilo()
    username = request.forms.username
    password = request.forms.password
    c = baza.cursor()
    if username is None or password is None:
        nastaviSporocilo("nekaj si pustli prazno")
        redirect('/prijava/')
    return template('html/prijava.html', napaka = napaka, cur=c)

@post('/prijava/')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    if username is None or password is None:
        nastaviSporocilo("nekaj si pustli prazno")
        redirect('/prijava/')
    c = baza.cursor()
    gesloHash = None
    #pazi, vejica za username in cursor vrne tuple, zato 
    # je treba izbrati prvega
    # pogledamo, ce je uporabnik v bazi
    try:
        gesloHash = hashGesla(c.execute("SELECT geslo FROM oseba WHERE username =  ?",(username,)).fetchone()[0])
    except:
        gesloHash = None
    if gesloHash==None:
        nastaviSporocilo("Uporabnik ne obstaja")
        redirect('/prijava/')
        #pogledamo, ali je geslo pravilno
    if hashGesla(password) != gesloHash:
        nastaviSporocilo("Napačno geslo")
        redirect("/prijava/")
    response.set_cookie('username', username, secret=skrivnost)
    redirect('/')
    
@get('/odjava/')
def odjava_get():
    response.delete_cookie('username')
    redirect('/prijava/')


@get('/registracija/')
def registracija_get():
    #prvo nastavimo napako na None
    napaka = nastaviSporocilo()
    return template('html/registracija.html', napaka = napaka)


@post('/registracija/')
def registracija_post():
    password = request.forms.password
    password2 = request.forms.password2
    emso = request.forms.emso
    username = request.forms.username
    c = baza.cursor()
    if len(password)<4:
        nastaviSporocilo("Geslo mora vsebovati vsaj 4 znake")
        redirect('/registracija/')
    if password != password2:
        nastaviSporocilo("Gesli se ne ujemata")
        redirect('/registracija/')
    #zakodira geslo in ga vstavi v bazo
    zg = hashGesla(password)
    #dodamo osebo v bazo
    print('hej')
    c.execute("insert into oseba (username, geslo, emso) values (?, ?,?)",(username, zg, emso))
    #if uporabnik is None:
    napaka = nastaviSporocilo("uspesno")
    #ko se nekdo registrira mu damo cookie
    response.set_cookie('username', username, secret = skrivnost)
    return template('html/registracija.html', napaka = napaka,cur=c)

@get('/igralci')
def igralci():
    cur=baza.cursor()
    igralci = cur.execute("SELECT * from igralec")
    print(igralci)
    return template('html/igralci.html',igralci=igralci)


@get('/poskodba')
def poskodba():
    cur=baza.cursor()
    poskodba = cur.execute("SELECT * from poskodba")
    return template('html/poskodba.html',poskodba=poskodba)


#geslo zakodira
def hashGesla(geslo):
    m=hashlib.sha256()
    m.update(geslo.encode("utf-8"))
    return m.hexdigest()

def preveriUporabnika():
    #dobi username tistega, ki trenutno uporablja stran
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        c = baza.cursor()
        uporabnik = None
        #poisce username v tabeli oseba
        try:
            uporabnik = c.execute("SELECT * from oseba WHERE username = ?", (username)).fetchone()
        except:
            uporabnik = None
        if uporabnik:
            return uporabnik
    redirect("/login/")



#se povezemo z bazo s tem 
baza = sqlite3.connect(baza_datoteka, isolation_level= None)
#izpise kere sql stavke posilja. Izpise v terminal
baza.set_trace_callback(print)
cur = baza.cursor()
#da uposteva foreign keye. Privzeto jih ne, ce tega eksplicitno ne poves
cur.execute("PRAGMA foreign_keys = ON;")
#vzpostavi streznik
run(host='localhost', port = 8080, reloader=True, debug=True)