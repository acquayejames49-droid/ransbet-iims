-- Ransbet IIMS - MySQL database schema
-- Generated from app/models.py (SQLAlchemy ORM definitions)
-- Engine: MySQL 8.0

CREATE TABLE categories (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(80) NOT NULL, 
	description VARCHAR(200), 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE suppliers (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	contact_person VARCHAR(120), 
	phone VARCHAR(40), 
	email VARCHAR(120), 
	lead_time_days INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	`role` VARCHAR(20) NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE audit_logs (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER, 
	action VARCHAR(50) NOT NULL, 
	description VARCHAR(255), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE products (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	sku VARCHAR(64), 
	category_id INTEGER, 
	supplier_id INTEGER, 
	unit_price FLOAT, 
	cost_price FLOAT, 
	current_stock INTEGER, 
	reorder_point INTEGER, 
	unit VARCHAR(16), 
	is_active BOOL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id)
);

CREATE TABLE anomaly_flags (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	product_id INTEGER NOT NULL, 
	flag_date DATE NOT NULL, 
	quantity INTEGER, 
	expected FLOAT, 
	score FLOAT, 
	reason VARCHAR(40), 
	resolved BOOL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE forecast_metrics (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	product_id INTEGER NOT NULL, 
	mape FLOAT, 
	mae FLOAT, 
	rmse FLOAT, 
	trained_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE forecasts (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	product_id INTEGER NOT NULL, 
	forecast_date DATE NOT NULL, 
	predicted_qty FLOAT NOT NULL, 
	lower FLOAT, 
	upper FLOAT, 
	generated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE sales (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price FLOAT NOT NULL, 
	total FLOAT NOT NULL, 
	sale_date DATE, 
	user_id INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE stock_movements (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	product_id INTEGER NOT NULL, 
	movement_type VARCHAR(20) NOT NULL, 
	quantity INTEGER NOT NULL, 
	stock_after INTEGER NOT NULL, 
	unit_price FLOAT, 
	note VARCHAR(200), 
	user_id INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
