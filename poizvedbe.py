


def igralci(cur,ekipetf):
    '''dobimo cursor, ekipe(true false), ki nam pove ali igralce pogrupiramo po ekipah in nacin na katerega jih razvrstimo (pozicija,tocke,asistence,skoki,odigrane)'''
    sez=[]
    ekipe = cur.execute("SELECT kratica from ekipa").fetchall()
    if ekipetf:
        for ekipa in ekipe:
            ekipa=ekipa[0]
            igralci=cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime where ekipa='{ekipa}'""").fetchall()
            sez.append([ekipa,igralci])
        return sez
    else:
        igralci=cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime""").fetchall()
        return igralci
    
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
    
