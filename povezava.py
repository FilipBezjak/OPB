import os
import hashlib
import tracemalloc
import poizvedbe
#poizvedbe v bazo delamo v drugi datoteki


# uvozimo bottle.py
from bottleext import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) 
# se znebimo problemov s šumniki
# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


#tracemalloc.start()
#bazo smo naredili v priklop 
#baza_datoteka = "test.db"
skrivnost = "wct3uifzgciuwrt427364gi237g4"

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
def zacetna():
    cur=baza.cursor()
    tekme= cur.execute(f"""SELECT *  FROM tekme order by cas desc limit 10""")
    return template('html/zacetna.html', napaka=nastaviSporocilo(),uporabnik=preveriUporabnika(), tekme=tekme)

@get('/izbire')
def izbire():
    cur=baza.cursor()
    igralci=cur.execute("SELECT * from igralec")
    return template('html/izbire.html',poskodovan=None, igralci=igralci, igralci_izbire=None ,napaka = "", uporabnik=None, )



@get('/izbire/<poskodovan>')
def izbire_igralec(poskodovan):
    cur=baza.cursor()
    odprej=False
    try:
        cur.execute(f"""SELECT * from poskodba where ime='{poskodovan}'""").fetchall()[0]
        odprej=True
    except:
        odprej=False
    print(odprej)
    #poiščemo pri kateri ekipi igra in izberemo prve 3 po točkah v tej ekipi, ki niso poškodovani. Če je naš igralec med prvmi tremi, vrnemo druga dva, če ga ni, ni zanimiv. Isto ponovimo še za asistence in skoke
    igralci=cur.execute("SELECT * from igralec").fetchall()
    ekipa=cur.execute(f"""SELECT ekipa from igralec where ime = '{poskodovan}'""").fetchone()[0]
    igralciT=poizvedbe.izbire(ekipa, cur,poskodovan, 'tocke')
    igralciA=poizvedbe.izbire(ekipa, cur,poskodovan, 'asistence')
    igralciS=poizvedbe.izbire(ekipa, cur,poskodovan, 'skoki')
    igralci_izbire=[igralciT,igralciA,igralciS]
    #potem še vrnemo vse ki igrajo na isti poziciji.
    return template('html/izbire.html', poskodovan=poskodovan ,igralci=igralci,igralci_izbire=igralci_izbire, napaka = "", uporabnik=preveriUporabnika(), odprej=odprej)

def neki():
    print("hej")

@get('/igralci/<sort>')
def igralci(sort):
    ekipe, poskodbe=sort[0],sort[1]
    url=request.url
    if poskodbe=="f":
        poskodbe=None
    cur=baza.cursor()
    if ekipe=='t':
        igralci = poizvedbe.igralci(cur,True)
        return template('html/igralci_ekipe.html',poekipah=True,url=url,igralci=igralci, poskodbe=poskodbe,uporabnik=preveriUporabnika(), napaka="")
    else:
        igralci = poizvedbe.igralci(cur,False)
        return template('html/igralci.html',poekipah=False,url=url,igralci=igralci, poskodbe=poskodbe, napaka=nastaviSporocilo(),uporabnik=preveriUporabnika())


@get('/poskodba')
def poskodba():
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    poskodba = cur.execute(f"""SELECT igralec.ime, ekipa.ime, cas  FROM poskodba JOIN igralec ON igralec.ime = poskodba.ime JOIN ekipa on ekipa.kratica=igralec.ekipa""")
    return template('html/poskodba.html',poskodba=poskodba, napaka=nastaviSporocilo(), uporabnik=uporabnik)

@get('/uporabnik')
def uporabnik():
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    ekipe= cur.execute(f"""SELECT ime,kratica from ekipa left join najljubse on najljubse.ekipa=ekipa.kratica where clovek!='{uporabnik}' or clovek is null""").fetchall()
    najljubse = cur.execute(f"""SELECT ekipa.ime, ekipa FROM najljubse JOIN oseba ON najljubse.clovek = oseba.username JOIN ekipa on ekipa.kratica=najljubse.ekipa WHERE username='{uporabnik}'""").fetchall()
    top3TAS=poizvedbe.top3tas(cur,uporabnik)
    # nam da top 3 pri pike asistence, skoki pri najljubsih, kot [[brooklyn nets,[[[igralec1, #pik],[igralec2, #pik],[igralec3, #pik]][igralec1, #ast],[...],]
    #na koncu nujno fetchall, sicer ga html ne zna prebrati
    return template('html/uporabnik.html',top3TAS=top3TAS, najljubse=najljubse, napaka=nastaviSporocilo(), uporabnik=uporabnik, ekipe=ekipe, cur=cur)

    
@get('/uporabnik/<ekipa>/dodaj')
def dodaj_ekipo(ekipa):
    #na zacetku nastavimo sporocilo na none
    nastaviSporocilo()
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    try:
        cur.execute(f"""insert into najljubse (clovek, ekipa) values ('{uporabnik}', '{ekipa}')""")
    except:
        #nastavimo sporocilo
        nastaviSporocilo(f"{ekipa} ni ime ekipe")
    redirect(url('/uporabnik'))


@get('/adminstrator')
def admin():
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    priljubljenost = poizvedbe.pril(cur)
    osebe=cur.execute("SELECT * from oseba").fetchall()
    return template('html/adminstrator.html', uporabnik=uporabnik,osebe=osebe, priljubljenost=priljubljenost, napaka=None)

@post('/adminstrator')
def admin():
    domaci = request.forms.domaci
    gosti = request.forms.gosti
    datum = request.forms.datum
    cur=baza.cursor()
    cur.execute(f"""INSERT into tekme (ekipa1, ekipa2, cas) values ('{domaci}', '{gosti}', '{datum}')""")
    redirect(url('/adminstrator'))
    
    
@post('/adminstrator/<uporabnik>')
def admin(uporabnik):
    cur=baza.cursor()
    cur.execute(f"""DELETE from oseba where username='{uporabnik}'""")
    redirect(url('/adminstrator'))
    #dodaj se trigerje
    
#<ekipa> nam da vrednost ekipe pri brisi
@post('/uporabnik/<ekipa>')
def brisi(ekipa):
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    cur.execute(f"""delete from najljubse where clovek='{uporabnik}' and ekipa='{ekipa}'""")
    redirect(url('/uporabnik'))

###registracija in prijava.

@get('/prijava')
def prijava_get():
    uporabnik=preveriUporabnika()
    napaka=nastaviSporocilo()
    return template('html/prijava.html', napaka=napaka, uporabnik=uporabnik)

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    print(password)
    if username is None or password is None:
        nastaviSporocilo("nekaj si pustli prazno")
        redirect(url('/prijava'))
    c = baza.cursor()
    gesloHash = None
    #pazi, vejica za username in cursor vrne tuple, zato 
    # je treba izbrati prvega
    # pogledamo, ce je uporabnik v bazi
    try:
        gesloHash = c.execute(f"""SELECT geslo FROM oseba WHERE username =  '{username}'""").fetchone()[0]
        print(gesloHash)
    except:
        print("geslohashnon")
        gesloHash = None
    if gesloHash==None:
        nastaviSporocilo("Uporabnik ne obstaja")
        redirect(url('/prijava'))
        #pogledamo, ali je geslo pravilno
    if hashGesla(password) != gesloHash:
        nastaviSporocilo("Napačno geslo")
        redirect(url("/prijava"))
    response.set_cookie('username', username, secret=skrivnost)
    redirect(url('/uporabnik'))
    
@get('/odjava')
def odjava_get():
    response.delete_cookie('username')
    redirect(url('/prijava'))


@get('/registracija')
def registracija_get():
    #prvo nastavimo napako na None
    napaka = nastaviSporocilo()
    response.delete_cookie('username')
    return template('html/registracija.html', napaka = napaka, uporabnik=None)


@post('/registracija')
def registracija_post():
    password = request.forms.password
    password2 = request.forms.password2
    ime = request.forms.ime
    priimek = request.forms.priimek
    username = request.forms.username
    c = baza.cursor()
    if len(password)<4:
        nastaviSporocilo("Geslo mora vsebovati vsaj 4 znake")
        redirect(url('/registracija'))
    if password != password2:
        nastaviSporocilo("Gesli se ne ujemata")
        redirect(url('/registracija'))
    #zakodira geslo in ga vstavi v bazo
    zg = hashGesla(password)
    #dodamo osebo v bazo
    try:
        c.execute("insert into oseba (username, geslo, ime, priimek) values (?, ?,?,?)",(username, zg, ime, priimek))
        print("hej1")
    #if uporabnik is None:
        napaka = nastaviSporocilo("Uspešno")
        print("hej12")
    #ko se nekdo registrira mu damo cookie
        response.set_cookie('username', username, secret = skrivnost)
    except:
        # če je uporabniško ime zasedeno
        napaka = nastaviSporocilo("Uporabniško ime že obstaja")
        redirect(url('/registracija'))
    redirect(url('/uporabnik'))


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
            uporabnik = c.execute(f"""SELECT * from oseba WHERE username = '{username}'""").fetchone()[0]
        except:
            uporabnik = None
        #ce ga najde, vrne username
        if uporabnik:
            return username
    return None




######################################################################
# Glavni program

# priklopimo se na bazo
baza = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

#conn_string = "host= '{0}'  dbname='{1}' user='{2}' password='{3}'".format(host,dbname,user,password)
#se povezemo z bazo s tem 
#baza = psycopg2.connect(conn_string)
#baza = sqlite3.connect(baza_datoteka, isolation_level= None)
#izpise kere sql stavke posilja. Izpise v terminal
#baza.set_trace_callback(print)
#cur = baza.cursor()
#da uposteva foreign keye. Privzeto jih ne, ce tega eksplicitno ne poves
#cur.execute("PRAGMA foreign_keys = ON;")
#vzpostavi streznik
#run(host='localhost', port = 8080, reloader=True, debug=True)