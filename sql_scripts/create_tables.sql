CREATE TABLE zoo_keeper (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(20) UNIQUE NOT NULL,
    age INT NOT NULL,
    zoo_name VARCHAR(50),
    favorite_monkey INT,
    dream_monkey INT,
    PRIMARY KEY (id)
);

CREATE INDEX zoo_keeper_name ON zoo_keeper (name);

