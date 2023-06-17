
def top3tas(cur, uporabnik):
    najljubse = cur.execute(f"""SELECT ekipa, ime from najljubse join ekipa on najljubse.ekipa=ekipa.kratica
                                 where clovek=='{uporabnik}'""").fetchall()
    sez=[]
    for ekipa, ime in najljubse:
        ekipa
        t=cur.execute(f"""SELECT ime, tocke from igralec where ekipa=='{ekipa}'
                            order by tocke desc
                                limit 3 """).fetchall()
        a=cur.execute(f"""SELECT ime, asistence from igralec where ekipa=='{ekipa}'
                            order by asistence desc
                                limit 3 """).fetchall()
        s=cur.execute(f"""SELECT ime, skoki from igralec where ekipa=='{ekipa}'
                            order by skoki desc
                                limit 3 """).fetchall()
        sez.append([ime,t,a,s])
    return sez
        
        
def igralci(cur,ekipetf):
    '''dobimo cursor, ekipe(true false), ki nam pove ali igralce pogrupiramo po ekipah'''
    sez=[]
    ekipe = cur.execute("SELECT ime, kratica from ekipa").fetchall()
    if ekipetf:
        for ime, ekipa in ekipe:
            igralci=cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime where ekipa='{ekipa}'""").fetchall()
            sez.append([ime,igralci])
        return sez
    else:
        igralci=cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime""").fetchall()
        return igralci
    
def pril(c):
    return c.execute("""SELECT ekipa.ime, count(clovek)
                            from najljubse join ekipa 
                                on ekipa.kratica=najljubse.ekipa group by ekipa""").fetchall()
    
def izbire(ekipa,cur,ime,tas):
    cur.execute("DROP view if exists prvi_3")
    cur.execute(f"""CREATE view prvi_3 as select * from igralec left join poskodba on poskodba.ime=igralec.ime
                            where ekipa='{ekipa}'and poskodba.ime IS NULL
                                order by {tas} desc limit 3""")
    igralci=cur.execute(f"""SELECT * from prvi_3
                            where
                                EXISTS( select 1 from prvi_3 where ime='{ime}') 
                                and not 
                                ime='{ime}'""").fetchall()
    cur.execute("DROP view prvi_3")
    return igralci
    
