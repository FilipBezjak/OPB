DROP TABLE IF EXISTS statistika;
DROP TABLE IF EXISTS oseba;


CREATE TABLE oseba (
    emso INTEGER,
    username TEXT,
    geslo TEXT);


CREATE TABLE statistika (
    id INTEGER PRIMARY KEY,
    ime TEXT NOT NULL,
    ekipa TEXT NOT NULL,
    odigrane_minute FLOAT(10)  NOT NULL,
    tocke FLOAT(10) NOT NULL,
    asistence FLOAT(10) NOT NULL,
    skoki FLOAT(10) NOT NULL,
    pozicija TEXT NOT NULL);