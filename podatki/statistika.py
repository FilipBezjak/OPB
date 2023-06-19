import json
from datetime import datetime
datumi=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
#slovar, ki ga uporabimo, ko delamo tabelo ekipe
ekipe={
'ATL': 'Atlanta Hawks',
'BOS': 'Boston Celtics',
'BRK': 'Brooklyn Nets',
'CHO': 'Charlotte Hornets',
'CHI': 'Chicago Bulls',
'CLE': 'Cleveland Cavaliers',
'DAL': 'Dallas Mavericks',
'DEN': 'Denver Nuggets',
'DET': 'Detroit Pistons',
'GSW': 'Golden State Warriors',
'HOU': 'Houston Rockets',
'IND': 'Indiana Pacers',
'LAC': 'LA Clippers',
'LAL': 'Los Angeles Lakers',
'MEM': 'Memphis Grizzlies',
'MIA': 'Miami Heat',
'MIL': 'Milwaukee Bucks',
'MIN': 'Minnesota Timberwolves',
'NOP': 'New Orleans Pelicans',
'NYK': 'New York Knicks',
'OKC': 'Oklahoma City Thunder',
'ORL': 'Orlando Magic',
'PHI': 'Philadelphia 76ers',
'PHO': 'Phoenix Suns',
'POR': 'Portland Trail Blazers',
'SAC': 'Sacramento Kings',
'SAS': 'San Antonio Spurs',
'TOR': 'Toronto Raptors',
'UTA': 'Utah Jazz',
'WAS': 'Washington Wizards'}


# pri videu spletne aplikacije se poglej video do konca pri 20.min, da dodaš uporabniku fav ekipo
# prožilci gledajo fav ekipe seštevajo itd i guess
#dodajaj poškodbe


#ocitno je treba spremeniti tipe v float, drugace so pa string, pri f
#insert pa dodamo stvari v narekovaje, ker sicer ocitno ne da stringa, 
# nevem zakaj
def igralec(s):
    s=eval(s)
    q=s[0]
    ime=q.get(("ime"))
    ime=ime.replace("'", "''")
    minute=float(q.get(("minute")))
    pozicija=q.get(("pozicija"))
    rebounds=float(q.get(("rebounds")))
    tocke=float(q.get(("tocke")))
    asistence=float(q.get(("asistence")))
    ekipa=q.get(("ekipa"))
    #damo replace, zaradi prestopov, ce je 2x isto ime, pomeni, da je igralec prestopil, zato vzamemo
    # njegove zadnje vrednosti, saj je to statistika pri ekipi, v kateri trenutno igra. Id ne rabimo, primary key
    # bo kar ime
    s=f"""insert into igralec (ime, ekipa, pozicija, tocke, asistence, skoki, odigrane_minute) values ('{ime}', '{ekipa}', '{pozicija}', {tocke}, {asistence}, {rebounds}, {minute})
    ON CONFLICT (ime) DO UPDATE 
    set ekipa=excluded.ekipa, tocke=excluded.tocke, asistence=excluded.asistence, skoki=excluded.skoki, odigrane_minute=excluded.odigrane_minute;""" + "\n"
    return s

def injury(s):
    now=datetime.now()
    leto=now.year
    if s== 'GTD':
        s=now.strftime('%Y-%m-%d')
    elif s=="Probable for start of season":
        l=leto+1
        s=f'{l}-09-01'
    else:
        mesec=datumi.index(s[10:13])+1
        try:
            dan=int(s[14:16])
        except:
            dan=int(s[-1])
        s=f'{leto}-{mesec}-{dan}'
    return s




#del za POŠKODBE
def poskodbe2():
    with open("podatki/injury.sql","w",encoding='utf-8') as fsql, open("podatki/injury.json","r",encoding='utf-8') as fjson:
        celo=fjson.read()
        slov=eval(celo)
        s=''
        for ime in slov:
            #vsako poškodbo pogleda, kaj je in vrne pravilen datum okrevanja v sql obliki
            cas=injury(slov[ime])
            s+=f"""insert into poskodba (ime, cas) values ('{ime}', '{cas}');""" + "\n"
        fsql.write(s)


#del za EKIPE
#dodamo vse v tabelo ekipe, iz slovarja, ki ga mamo spodaj
def ekipe2():
    with open("podatki/ekipe.sql","w",encoding='utf-8') as ap:
        #vzamemo global slovar
        st=''
        for k, v in ekipe.items():
            s=f"insert into ekipa (ime, kratica) values ('{v}', '{k}');" + "\n"
            st+=s
        ap.write(st)



#nam da tabelo IGRALEC
#obrni slashe, ko kopiras relative path
def igralec2():
    with open("podatki/test.html",'r',encoding='utf-8') as f,open("podatki/igralec.sql","w",encoding='utf-8') as ap:
        for vr in f:
            ap.write(igralec(vr))
