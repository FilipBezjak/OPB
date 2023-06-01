DROP TABLE IF EXISTS ekipa;
DROP TABLE IF EXISTS oseba;
DROP TABLE IF EXISTS igralec;
DROP TABLE IF EXISTS poskodba;
DROP TABLE IF EXISTS najljubse;
DROP TABLE IF EXISTS tekme;



CREATE TABLE oseba (
    ime VARCHAR(20) NOT NULL,
    priimek VARCHAR(20) NOT NULL,
    username VARCHAR(25) PRIMARY KEY,
    geslo VARCHAR(20) NOT NULL
);

CREATE TABLE najljubse (
    clovek INTEGER REFERENCES oseba(username),
    ekipa VARCHAR(3) REFERENCES ekipa(kratica)
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

CREATE TABLE tekme (
    ekipa1 VARCHAR REFERENCES  ekipa(kratica),
    ekipa2 VARCHAR REFERENCES  ekipa(kratica),
    cas TIME NOT NULL
)



