CREATE TABLE BOOKS (
isbn varchar(50) primary key,
title varchar(100) not null,
author varchar(50) not null,
year_publish smallint not null
);

CREATE TABLE USER_ACCOUNT (
id SERIAL PRIMARY KEY,
userid varchar(50) not null unique,
password bytea not null,
username varchar(100),
email varchar(100),
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
;
CREATE TABLE USER_REVIEWS (
id SERIAL PRIMARY KEY,
userid varchar(50) references USER_ACCOUNT(userid),
isbn varchar(50)  references BOOKS(isbn),
stars smallint not null,
review_comment varchar(200)
)