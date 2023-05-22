DROP TABLE IF EXISTS ekipa;
DROP TABLE IF EXISTS oseba;
DROP TABLE IF EXISTS igralec;
DROP TABLE IF EXISTS poskodba;



CREATE TABLE oseba (
    ime VARCHAR(20) NOT NULL,
    priimek VARCHAR(20) NOT NULL,
    emso INTEGER PRIMARY KEY,
    username VARCHAR(25) NOT NULL,
    geslo VARCHAR(20) NOT NULL,
    najljubsa VARCHAR(20) NOT NULL
);


CREATE TABLE ekipa (
    ime VARCHAR(10),
    kratica VARCHAR(3) PRIMARY KEY
);

CREATE TABLE igralec (
    ime VARCHAR(40)  PRIMARY KEY,
    ekipa VARCHAR REFERENCES  ekipa(kratica),
    pozicija VARCHAR(2),
    tocke FLOAT NOT NULL,
    asistence FLOAT NOT NULL,
    skoki FLOAT NOT NULL,
    odigrane_minute FLOAT  NOT NULL
);

CREATE TABLE poskodba (
    ime VARCHAR(40) PRIMARY KEY,
    cas TIME NOT NULL
);



