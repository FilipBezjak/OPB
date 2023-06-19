import psycopg2
import sqlite3
from auth_public import *

#s tem smo dodali podatke v bazo php-admin. prijavil se z mojim imenom in geslom
conn_string = "host= '{0}'  dbname='{1}' user='{2}' password='{3}'".format(host,db,user,password)


def uvoziSQL(cur, dat):
    with open(dat, encoding="utf-8") as f:
        skript = f.read()
        cur.execute(skript)

#with psycopg2.connect(conn_string) as con:
with psycopg2.connect(conn_string) as con:
    cur = con.cursor()
    #uvozimo podatke iz datoteke
    #uvoziSQL(cur, "podatki/nba.sql")
    #uvoziSQL(cur, 'podatki/ekipe.sql')
    #uvoziSQL(cur, 'podatki/igralec.sql')
    #uvoziSQL(cur, 'podatki/injury.sql')
    uvoziSQL(cur, 'podatki/proba.sql')
    #cur.execute("insert into oseba (username, geslo, ime, priimek, administrator) values ('filip', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4','Filip','Bezjak', TRUE)")
    con.commit()
#ce nimamo stavka with, moramo na koncu dodati še con.commit()

#namesto ? damo %(datatype) npr s... %(cena)s