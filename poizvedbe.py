import orodja
import re
import requests
from podatki import statistika



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
    cur=baza.cursor()
    cur.execute("SELECT ime, kratica from ekipa")
    ekipe = cur.fetchall()
    if ekipetf:
        for ime, ekipa in ekipe:
            cur=baza.cursor()
            cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime where ekipa='{ekipa}'""")
            igralci=cur.fetchall()
            sez.append([ime,igralci])
        return sez
    else:
        cur=baza.cursor()
        cur.execute(f"""SELECT * from igralec left join poskodba on igralec.ime=poskodba.ime""")
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

def dodaj_admina(baza, geslo):
    cur=baza.cursor()
    #geslo je 1234
    username='filip'
    priimek='Bezjak'
    ime='Filip'
    admin=True
    cur.execute(f"""insert into oseba (username, geslo, ime, priimek, administrator) values (%s, %s,%s,%s,%s)
    ON CONFLICT (username) DO NOTHING""", (username, geslo, ime, priimek, admin))

def tekme(baza):
    cur=baza.cursor()
    cur.execute(f"""SELECT domaci.ime as domaci, gosti.ime as gosti, cas from tekme
                join ekipa as domaci on domaci.kratica=tekme.ekipa1 
                join ekipa as gosti on gosti.kratica=tekme.ekipa2
                        order by cas desc limit 10""")
    return cur





def slovar_poskodb(s):
    '''Expected to... spremeni v out until datum
    GTD v GTD out for season pusti'''
    for ig in s:
        if s[ig]=='Probable for start of season':
            s[ig]="Out until Sep 1"
        try:
            d,m = s[ig].split()[-1:-3:-1]
            int(d)
            s[ig] = "Out until" + ' ' + m + " " + d
        except:
            if s[ig]=="Game Time Decision":
                s[ig] = "GTD"
    return s




##### pobere poskodbe iz spletne strani

vzorec = (r'class="">(?P<ime>.{0,40})<.a><.span><.span><.td><td.class="TableBase-bodyTd.*?width: 40%;">.\s*(?P<stanje>.*?\S)\s*<')
    # r'players.+?">(?P<ime>.+?)<.*?'
    # r' data-stat="pos" >(?P<pozicija>.*?)<.*?'
    # r'stat="age" >(?P<starost>.*?)<.*?'
    # r'href="/teams.*?">(?P<ekipa>.*?)<.*?'
    # r'stat="g" >(?P<odigrane>.*?)<.*?'
    # r'data-stat="gs" >(?P<zacete>.*?)<.*?'
    # r'data-stat="mp_per_g" >(?P<minute>.*?)<.*?'
    # r'stat="trb_per_g" >(?P<rebounds>.*?)<.*?'
    # r'data-stat="ast_per_g" >(?P<asistence>.*?)<.*?'
    # r'data-stat="stl_per_g" >(?P<steals>.*?)<.*?'
    # r'data-stat="blk_per_g" >(?P<blokade>.*?)<.*?'
    # r'data-stat="tov_per_g" >(?P<turnovers>.*?)<.*?'
    # r'data-stat="pts_per_g" >(?P<tocke>.*?)<'



def poskodbe(baza):
    for stran in range(1):
        stran += 1
        url = "https://www.cbssports.com/nba/injuries/"
        datoteka = "injuryreport.html"
        vsebina = orodja.shrani_spletno_injury(url, datoteka)
        slovar={}
        for zadetek in re.finditer(vzorec, vsebina, flags=re.DOTALL):
            slovar[zadetek.groupdict()['ime']]=zadetek.groupdict()['stanje']
        slovar = slovar_poskodb(slovar)
        cur=baza.cursor()
        cur.execute("DROP TABLE IF EXISTS poskodbe")
        for ime in slovar:
            #vsako poškodbo pogleda, kaj je in vrne pravilen datum okrevanja v sql obliki
            cas=statistika.injury(slovar[ime])
            cur.execute(f"""insert into poskodba (ime, cas) values ('{ime}', '{cas}');""")
        baza.commit()
            

