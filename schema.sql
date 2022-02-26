CREATE TABLE milestone (
	id INTEGER NOT NULL, 
	description VARCHAR(256) NOT NULL, 
	finished DATETIME, 
	signed_by VARCHAR(99), 
	card_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(card_id) REFERENCES card (id)
);
CREATE TABLE db_user (
	uid VARCHAR (80) NOT NULL, 
	is_admin BOOLEAN DEFAULT (0), 
	PRIMARY KEY (uid));

CREATE TABLE card (
	id INTEGER NOT NULL, 
	project_name VARCHAR (256) NOT NULL, 
	student_name VARCHAR (256) NOT NULL, 
	is_visible BOOLEAN DEFAULT (1), 
	PRIMARY KEY (id));

CREATE TABLE dbuser_card (
	dbuser_uid VARCHAR(80) NOT NULL, 
	card_id INTEGER NOT NULL, 
	PRIMARY KEY (dbuser_uid, card_id), 
	FOREIGN KEY(dbuser_uid) REFERENCES db_user (uid), 
	FOREIGN KEY(card_id) REFERENCES card (id)
);
