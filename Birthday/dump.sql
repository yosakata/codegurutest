BEGIN;
CREATE TABLE Locations (
  id integer PRIMARY KEY NOT NULL,
  location char(128)
);
INSERT INTO Locations VALUES(1,'Seattle');
INSERT INTO Locations VALUES(2,'Tokyo');
INSERT INTO Locations VALUES(3,'Chiba');
INSERT INTO Locations VALUES(4,'Saitama');
INSERT INTO Locations VALUES(5,'Kanagawa');
CREATE TABLE Relations (
  id integer PRIMARY KEY NOT NULL,
  relation char(128)
);
INSERT INTO Relations VALUES(1,'family');
INSERT INTO Relations VALUES(2,'friends');
CREATE TABLE Users (
  id integer PRIMARY KEY NOT NULL,
  firstname char(128),
  lastname char(128),
  birthday char(128),
  relationID integer(128),
  locationID integer(128)
);
INSERT INTO Users VALUES(1,'Chris','Choi','NA',2,1);
INSERT INTO Users VALUES(2,'Yohei','Sakata','1980/5/25',1,1);
INSERT INTO Users VALUES(3,'Mai','Sakata','1985/8/5',1,1);
INSERT INTO Users VALUES(4,'Leo','Sakata','2020/7/14',1,1);
INSERT INTO Users VALUES(5,'Noriyuki','Sakata','1946/12/16',1,4);
INSERT INTO Users VALUES(6,'Kimiko','Sakata','1948/6/16',1,4);
INSERT INTO Users VALUES(7,'Keiko','Sakata','1978/3/5',1,2);
INSERT INTO Users VALUES(8,'Kiyoko','Taniwa','NA',1,2);
INSERT INTO Users VALUES(9,'Makoto','Tanaka','1969/1/9',1,1);
INSERT INTO Users VALUES(10,'Reiko','Tanaka','1960/5/22',1,1);
INSERT INTO Users VALUES(11,'Yuya','Tanaka','1986/12/20',1,1);
INSERT INTO Users VALUES(12,'Yuka','Tanaka','NA',1,1);
INSERT INTO Users VALUES(13,'Shugo','Tanaka','NA',1,1);
INSERT INTO Users VALUES(14,'Mitsuki','Tanaka','NA',1,1);
INSERT INTO Users VALUES(15,'Takehiro','Tanaka','1989/6/21',1,2);
INSERT INTO Users VALUES(16,'Hiroko','Tanaka','1972/5/29',1,2);
INSERT INTO Users VALUES(17,'Takahiro','Sonoda','1982/5/27',2,5);
INSERT INTO Users VALUES(18,'Marie','Sonoda','NA',2,5);
INSERT INTO Users VALUES(19,'Yua','Sonoda','1917/6/1',2,5);
INSERT INTO Users VALUES(20,'Kailu','Jin','2019/12/31',2,1);
INSERT INTO Users VALUES(21,'Sam','Jin','NA',2,1);
INSERT INTO Users VALUES(22,'Hitomi','Jin','1982/10/2',2,1);
INSERT INTO Users VALUES(23,'Shiho','Fuyuki','1987/9/23',2,1);
INSERT INTO Users VALUES(24,'Ayu','Fisher','2019/1/19',2,1);
INSERT INTO Users VALUES(25,'Shinya','Fisher','2020/6/29',2,1);
INSERT INTO Users VALUES(26,'Ben','Fisher','NA',2,1);
INSERT INTO Users VALUES(27,'Junko','Fisher','1983/10/6',2,1);
INSERT INTO Users VALUES(28,'Yoko','Wills','1987/1/17',2,1);
INSERT INTO Users VALUES(29,'Dave','Wills','1981/5/9',2,1);
INSERT INTO Users VALUES(30,'Isla','Wills','2017/9/25',2,1);
INSERT INTO Users VALUES(31,'Maile','Wills','2020/1/10',2,1);
INSERT INTO Users VALUES(32,'Tomoko','Sakamoto','NA',2,1);
INSERT INTO Users VALUES(33,'Garrett','Sakamoto','NA',2,1);
INSERT INTO Users VALUES(34,'Hikari','Sakamoto','NA',2,1);
INSERT INTO Users VALUES(35,'John','Choi','1980/4/15',2,1);
INSERT INTO Users VALUES(36,'JooAe','Choi','1979/11/1',2,1);
INSERT INTO Users VALUES(37,'Aily','Choi','NA',2,1);
INSERT INTO Users VALUES(38,'Issac','Choi','NA',2,1);
COMMIT;
