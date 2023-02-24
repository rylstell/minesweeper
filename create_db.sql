DROP DATABASE IF EXISTS minesweeper;
CREATE DATABASE IF NOT EXISTS minesweeper;

USE minesweeper;

CREATE TABLE Score(
    score_id INT NOT NULL AUTO_INCREMENT,
    score INT NOT NULL,
    name VARCHAR(10) NOT NULL,
    diff VARCHAR(10) NOT NULL,
    score_date DATETIME NOT NULL,
    PRIMARY KEY (score_id)
);
