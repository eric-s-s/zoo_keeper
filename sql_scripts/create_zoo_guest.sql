DROP USER IF EXISTS 'keeper_guest'@'localhost' ;
CREATE USER 'keeper_guest'@'localhost';
GRANT ALL PRIVILEGES ON keeper.* TO 'keeper_guest'@'localhost';
GRANT ALL PRIVILEGES ON test.* TO 'keeper_guest'@'localhost';
