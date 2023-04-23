import json

#ocitno je treba spremeniti tipe v float, drugace so pa string, pri f
#insert pa dodamo stvari v narekovaje, ker sicer ocitno ne da stringa, 
# nevem zakaj
def sql(i,s):
    s=eval(s)
    q=s[0]
    ime=q.get(("ime"))
    minute=float(q.get(("minute")))
    pozicija=q.get(("pozicija"))
    rebounds=float(q.get(("rebounds")))
    tocke=float(q.get(("tocke")))
    asistence=float(q.get(("asistence")))
    ekipa=q.get(("ekipa"))
    s=f"insert into statistika (id, ime, ekipa, pozicija, tocke, asistence, skoki, odigrane_minute) values ({i}, '{ime}', '{ekipa}', '{pozicija}', {tocke}, {asistence}, {rebounds}, {minute});" + "\n"
    return s

#obrni slashe, ko kopiras relative path
with open("letalski-promet/podatki/test2.html",'r',encoding='utf-8') as f:
    with open("letalski-promet/podatki/stat.sql","w",encoding='utf-8') as ap:
        i=0
        for vr in f:
            i+=1
            ap.write(sql(i,vr))
                