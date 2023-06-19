import os
import bcrypt
from textwrap import wrap
import tracemalloc
import poizvedbe
from datetime import datetime
from functools import wraps
#poizvedbe v bazo delamo v drugi datoteki
tracemalloc.start()

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
ROOT = os.environ.get('BOTTLE_ROOT', '/')

debug(True)

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


#funkcija, ki sprejme dekorator in vrne dekorator
def aliNekaj(funpreveri):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if funpreveri():
                return func(*args, **kwargs)
            else:
                abort(401, "Dostop prepovedan!")
            return wrapper
        return wrapper
    return decorator




def je_admin():
    username = request.get_cookie("username", secret=skrivnost)
    c = baza.cursor()
    c.execute(f"""SELECT administrator from oseba where username='{username}'""")
    try:
        admin=c.fetchone()[0]
    except:
        return False
    return admin


def je_prijavljen():
    neki= request.get_cookie("username", secret=skrivnost)
    if neki:
        return True
    else:
        return False


########## prva stran ################
@get('/')
def zacetna_get():
    geslo = hashGesla("1234")
    poizvedbe.dodaj_admina(baza,geslo)
    tekme=poizvedbe.tekme(baza)
    baza.commit()
    return template('html/zacetna.html', napaka=nastaviSporocilo(),uporabnik=preveriUporabnika(),admin=je_admin(), tekme=tekme)



####### stran izbire #############3
@get('/izbire')
def izbire_get():
    cur=baza.cursor()
    cur.execute("SELECT * from igralec")
    return template('html/izbire.html',poskodovan=None, igralci=cur, igralci_izbire=None ,napaka = "", uporabnik=None, admin=je_admin())



@get('/izbire/<poskodovan>')
def izbire_igralec(poskodovan):
    cur=baza.cursor()
    #pogledamo, če je poškodovan že od prej,
    odprej=False
    cur.execute(f"""SELECT * from poskodba where ime='{poskodovan}'""")
    if cur.fetchall():
        odprej=True
    #poiščemo pri kateri ekipi igra in izberemo prve 3 po točkah v tej ekipi, ki niso poškodovani. Če je naš igralec med prvmi tremi, vrnemo druga dva, če ga ni, ni zanimiv. Isto ponovimo še za asistence in skoke
    cur=baza.cursor()
    cur.execute("SELECT * from igralec")
    igralci=cur
    cur=baza.cursor()
    cur.execute(f"""SELECT ekipa from igralec where ime = '{poskodovan}'""")
    ekipa=cur
    igralciT=poizvedbe.izbire(ekipa, baza,poskodovan, 'tocke')
    igralciA=poizvedbe.izbire(ekipa, baza,poskodovan, 'asistence')
    igralciS=poizvedbe.izbire(ekipa, baza,poskodovan, 'skoki')
    igralci_izbire=[igralciT,igralciA,igralciS]
    baza.commit()
    #potem še vrnemo vse ki igrajo na isti poziciji.
    return template('html/izbire.html', poskodovan=poskodovan ,igralci=igralci,igralci_izbire=igralci_izbire, napaka = "", uporabnik=preveriUporabnika(),admin=je_admin(), odprej=odprej)

################# stran statistika ################33
@get('/igralci/<sort>')
def igralci(sort):
    #na konec urlja dobimo tf, ki nam pove, če pokažemo poškodovane oziroma razvrstimo po ekipah
    ekipe, poskodbe=sort[0],sort[1]
    if poskodbe=="f":
        poskodbe=False
    else:
        poskodbe=True
    if ekipe=='t':
        igralci = poizvedbe.igralci(baza,True)
        baza.commit()
        return template('html/igralci_ekipe.html',poekipah=True,igralci=igralci, poskodbe=poskodbe,uporabnik=preveriUporabnika(),admin=je_admin(), napaka="")
    else:
        igralci = poizvedbe.igralci(baza,False)
        baza.commit()
        return template('html/igralci.html',poekipah=False,igralci=igralci, poskodbe=poskodbe, napaka=nastaviSporocilo(),uporabnik=preveriUporabnika(),admin=je_admin())


################### stran poskodbe ################3333

@get('/poskodba')
def poskodba_get():
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    cur.execute(f"""SELECT igralec.ime, ekipa.ime, cas  FROM poskodba JOIN igralec ON igralec.ime = poskodba.ime JOIN ekipa on ekipa.kratica=igralec.ekipa""")
    baza.commit()
    return template('html/poskodba.html',poskodba=cur, napaka=nastaviSporocilo(), uporabnik=uporabnik,admin=je_admin())


#########STRAN UPORABNIK
### samo ce si prijavljen
@get('/uporabnik')
@aliNekaj(je_prijavljen)
def uporabnik_get():
    uporabnik=preveriUporabnika()
    if uporabnik:
        cur=baza.cursor()
        cur.execute(f"""SELECT ime,kratica from ekipa left join najljubse on najljubse.ekipa=ekipa.kratica where clovek!='{uporabnik}' or clovek is null""")
        ekipe = cur
        cur=baza.cursor()
        cur.execute(f"""SELECT ekipa.ime, ekipa FROM najljubse JOIN oseba ON najljubse.clovek = oseba.username JOIN ekipa on ekipa.kratica=najljubse.ekipa WHERE username='{uporabnik}'""")
        najljubse = cur
        top3TAS=poizvedbe.top3tas(baza,uporabnik)
        baza.commit()
        # nam da top 3 pri pike asistence, skoki pri najljubsih, kot [[brooklyn nets,[[[igralec1, #pik],[igralec2, #pik],[igralec3, #pik]][igralec1, #ast],[...],]
        #na koncu nujno fetchall, sicer ga html ne zna prebrati
        return template('html/uporabnik.html',top3TAS=top3TAS, najljubse=najljubse, napaka=nastaviSporocilo(), uporabnik=uporabnik,admin=je_admin(), ekipe=ekipe, cur=cur)
    else:
        return "Nisi prijavljen"

    
@get('/uporabnik/<ekipa>/dodaj')
@aliNekaj(je_prijavljen)
def uporabnik_ekipa_dodaj(ekipa):
    #na zacetku nastavimo sporocilo na none
    nastaviSporocilo()
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    try:
        cur.execute(f"""insert into najljubse (clovek, ekipa) values ('{uporabnik}', '{ekipa}')""")
        baza.commit()
    except:
        #nastavimo sporocilo
        nastaviSporocilo(f"{ekipa} ni ime ekipe")
    redirect(url('uporabnik_get'))
    
#<ekipa> nam da vrednost ekipe pri brisi
@post('/uporabnik/<ekipa>')
@aliNekaj(je_prijavljen)
def uporabnik_ekipa(ekipa):
    uporabnik=preveriUporabnika()
    cur=baza.cursor()
    cur.execute(f"""delete from najljubse where clovek='{uporabnik}' and ekipa='{ekipa}'""")
    baza.commit()
    redirect(url('uporabnik_get'))
    
################# ADMINSTRATOR PAGE########33
##dostop samo administratorju

@get('/administrator')
@aliNekaj(je_admin)
def administrator_get():
    uporabnik=preveriUporabnika()
    priljubljenost = poizvedbe.pril(baza)
    cur=baza.cursor()
    cur.execute("SELECT * from oseba")
    osebe=cur.fetchall()
    cur=baza.cursor()
    cur.execute(f"SELECT * from ekipa")
    ekipe=cur.fetchall()
    baza.commit()
    datum=datum=datetime.now().strftime("%Y-%m-%d")
    return template('html/administrator.html', uporabnik=uporabnik,admin=je_admin(),osebe=osebe, ekipe=ekipe, priljubljenost=priljubljenost, napaka=nastaviSporocilo(), datum=datum)


#stran administrator
@post('/administrator')
@aliNekaj(je_admin)
def administrator_post():
    domaci = request.forms.domaci
    gosti = request.forms.gosti
    datum = request.forms.datum
    cur=baza.cursor()
    cur.execute(f"""INSERT into tekme (ekipa1, ekipa2, cas) values ('{domaci}', '{gosti}', '{datum}')""")
    nastaviSporocilo("Uspešno dodana tekma")
    baza.commit()
    redirect(url('administrator_get'))


#osveži stran za poškodbe
@post('/administrator/refresh')
@aliNekaj(je_admin)
def administrator_refresh():
    poizvedbe.poskodbe(baza)
    redirect(url('poskodba'))
    
#izbriše uporabnika, ki je vpisan
@get('/administrator/<uporabnik>')
@aliNekaj(je_admin)
def administrator_uporabnik(uporabnik):
    cur=baza.cursor()
    cur.execute(f"""DELETE from oseba where username='{uporabnik}'""")
    baza.commit()
    redirect(url('administrator_get'))


####################33###registracija in prijava.
@aliNekaj(not je_prijavljen)
@get('/prijava')
def prijava_get():
    uporabnik=preveriUporabnika()
    napaka=nastaviSporocilo()
    return template('html/prijava.html', napaka=napaka, uporabnik=uporabnik,admin=je_admin())

@aliNekaj(not je_prijavljen)
@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    if username is None or password is None:
        nastaviSporocilo("nekaj si pustli prazno")
        redirect(url('/prijava'))
    gesloHash = None
    #pazi, vejica za username in cursor vrne tuple, zato 
    # je treba izbrati prvega
    # pogledamo, ce je uporabnik v bazi
    try:
        cur=baza.cursor()
        cur.execute(f"""SELECT geslo FROM oseba WHERE username =  '{username}'""")
        gesloHash=cur.fetchone()[0]
        baza.commit()
    except:
        gesloHash = None
    if gesloHash==None:
        nastaviSporocilo("Uporabnik ne obstaja")
        baza.commit()
        redirect(url('/prijava'))
        #pogledamo, ali je geslo pravilno
    if not preveri_geslo(password, gesloHash):
        nastaviSporocilo("Napačno geslo")
        baza.commit()
        redirect(url("/prijava"))
    response.set_cookie('username', username, secret=skrivnost)
    redirect(url('uporabnik_get'))
  #  
@get('/odjava')
@aliNekaj(je_prijavljen)
def odjava_get():
    response.delete_cookie('username')
    redirect(url('/prijava'))


@get('/registracija')
def registracija_get():
    #prvo nastavimo napako na None
    napaka = nastaviSporocilo()
    response.delete_cookie('username')
    return template('html/registracija.html', napaka = napaka, uporabnik=None, admin=je_admin())


@post('/registracija')
def registracija_post():
    password = request.forms.password
    password2 = request.forms.password2
    ime = request.forms.ime
    priimek = request.forms.priimek
    username = request.forms.username
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
        c = baza.cursor()
        c.execute("""insert into oseba (username, geslo, ime, priimek) values (%s, %s,%s,%s)""",(username,zg,ime,priimek))
        baza.commit()
    #if uporabnik is None:
        napaka = nastaviSporocilo("Uspešno")
    #ko se nekdo registrira mu damo cookie
        response.set_cookie('username', username, secret = skrivnost)
    except:
        # če je uporabniško ime zasedeno
        napaka = nastaviSporocilo("Uporabniško ime že obstaja")
        redirect(url('/registracija'))
    redirect(url('uporabnik_get'))


##########################  geslo zakodira

def hashGesla(geslo):
    geslo = geslo.encode("utf-8")
    sol = bcrypt.gensalt()
    return bcrypt.hashpw(geslo, sol).decode("utf-8")


def preveri_geslo(geslo, zgostitev):
    geslo = geslo.encode("utf-8")
    zgostitev=zgostitev.encode("utf-8")
    return bcrypt.checkpw(geslo, zgostitev)



#######################3
def preveriUporabnika():
    #dobi username tistega, ki trenutno uporablja stran
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        c = baza.cursor()
        uporabnik = None
        #poisce username v tabeli oseba
        try:
            c.execute(f"""SELECT * from oseba WHERE username = '{username}'""")
            uporabnik = c
            baza.commit()
        except:
            uporabnik = None
        #ce ga najde, vrne username
        if uporabnik:
            return username
    return None




    



#ko preklopimo na postgres, je treba poizvedbe spremeniti
# cur=baza.cursor()
# cur.execute(nekaj)
# seznam=cur
# in spet cur=baza.cursor()




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
#cur = baza.cursor()
#da uposteva foreign keye. Privzeto jih ne, ce tega eksplicitno ne poves
#cur.execute("PRAGMA foreign_keys = ON;")
#vzpostavi streznik
#run(host='localhost', port = 8080, reloader=True, debug=True)