-- create user tp access MySQL database
CREATE USER 'auth_user' @'localhost' IDENTIFIED BY 'Aauth123';

-- create auth database
CREATE DATABASE auth;

-- give user access to all tables in the auth database
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user' @'localhost';

-- use the auth database
USE auth;

-- create users table
CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR (255) NOT NULL UNIQUE,
    `password` VARCHAR (255) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT NOW()
);

-- insert into table the admin account
INSERT INTO
    users (email, password)
VALUES
    ('minhtran@admin.com', 'Admin123')