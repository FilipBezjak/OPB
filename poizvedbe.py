
def top3tas(baza, uporabnik):
    cur=baza.cursor()
    cur.execute(f"""SELECT ekipa, ime from najljubse join ekipa on najljubse.ekipa=ekipa.kratica
                                 where clovek='{uporabnik}'""")
    najljubse=cur
    sez=[]
    for ekipa, ime in najljubse:
        cur=baza.cursor()
        cur.execute(f"""SELECT ime, tocke from igralec where ekipa='{ekipa}'
                            order by tocke desc
                                limit 3 """)
        t=cur.fetchall()
        cur=baza.cursor()
        cur.execute(f"""SELECT ime, asistence from igralec where ekipa='{ekipa}'
                            order by asistence desc
                                limit 3 """)
        a=cur.fetchall()
        cur=baza.cursor()
        cur.execute(f"""SELECT ime, skoki from igralec where ekipa='{ekipa}'
                            order by skoki desc
                                limit 3 """)
        s=cur.fetchall()
        sez.append([ime,t,a,s])
    return sez
        
        
def igralci(baza,ekipetf):
    '''dobimo cursor, ekipe(true false), ki nam pove ali igralce pogrupiramo po ekipah'''
    sez=[]
    print("tu1")
    cur=baza.cursor()
    cur.execute("SELECT ime, kratica from ekipa")
    print("tu2")
    ekipe = cur.fetchall()
    if ekipetf:
        for ime, ekipa in ekipe:
            cur=baza.cursor()
            cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime where ekipa='{ekipa}'""")
            igralci=cur.fetchall()
            sez.append([ime,igralci])
        return sez
    else:
        print("tu3")
        cur=baza.cursor()
        cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime""")
        print("tu5")
        return cur.fetchall()
    
def pril(baza):
    c=baza.cursor()
    c.execute("""SELECT ekipa.ime, count(clovek)
                            from najljubse join ekipa 
                                on ekipa.kratica=najljubse.ekipa group by ekipa.ime""")
    return c
    
def izbire(ekipa,baza,ime,tas):
    cur=baza.cursor()
    cur.execute("DROP view if exists prvi_3")
    #mora biti igralec.*, sicer vrne napako, ker bi imela dva stolpca ime "ime"
    cur.execute(f"""CREATE view prvi_3 as select igralec.* from igralec left join poskodba on poskodba.ime=igralec.ime
                            where ekipa='{ekipa}'and poskodba.ime IS NULL
                                order by {tas} desc limit 3""")
    cur.execute(f"""SELECT * from prvi_3
                            where
                                EXISTS( select 1 from prvi_3 where ime='{ime}') 
                                and not 
                                ime='{ime}'""")
    igralci=cur
    cur=baza.cursor()
    cur.execute("DROP view prvi_3")
    return igralci
    
