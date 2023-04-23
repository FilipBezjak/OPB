import sqlite3

#priklopimo se na testno bazo, ki jo hranimo na disku

baza = "test.db"
def uvoziSQL(cur, dat):
    with open(dat,'r',encoding='utf-8') as f:
        skript = f.read()
        cur.executescript(skript)

with sqlite3.connect(baza) as b:
    cur = b.cursor()
    #uvozimo podatke iz datoteke
    uvoziSQL(cur, "podatki/nba.sql")
    uvoziSQL(cur, 'podatki/stat.sql')
    cur.execute("""insert into oseba (emso,geslo,username) values (123456789,"gesloo","krompir");""")
    cur.execute("""insert into oseba (emso,geslo,username) values (1234,"geslo",'krompir');""")
    cur.execute("""insert into oseba (emso,geslo,username) values (12345,"geslo","dd");""")

with sqlite3.connect(baza) as b:
    cur = b.cursor()
    c=cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        #fetchall klice kurzor kot iterator dokler se ne sprazni
    print(c.fetchall())
    
with sqlite3.connect(baza) as b:
    cur = b.cursor()
    #c=cur.execute("SELECT * FROM statistika")
    print(c.fetchall())
    #PAZI MORE BITI VEJICA ZA INP
    c=cur.execute("SELECT geslo FROM oseba WHERE username = ?",('krompir',))
    print(c.fetchall())

