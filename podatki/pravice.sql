GRANT CONNECT ON DATABASE sem2022_filipb TO javnost;
GRANT USAGE ON SCHEMA public TO javnost;

GRANT ALL ON DATABASE sem2022_filipb TO filipb WITH GRANT OPTION;
GRANT ALL ON SCHEMA public TO filipb WITH GRANT OPTION;

GRANT ALL ON ALL TABLES IN SCHEMA public TO filipb WITH GRANT OPTION;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO filipb WITH GRANT OPTION;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;

GRANT INSERT ON oseba TO javnost;
GRANT INSERT ON najljubse TO javnost;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO javnost;
GRANT CREATE VIEW ON SCHEMA public TO javnost