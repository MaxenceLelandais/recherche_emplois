USE recherche_entreprise;
-- Création des tables avec des clés étrangères compatibles

-- DROP TABLE IF EXISTS job;
-- DROP TABLE IF EXISTS list_employees;
-- DROP TABLE IF EXISTS history_income;
-- DROP TABLE IF EXISTS history_number_employees;
-- DROP TABLE IF EXISTS employee;
-- DROP TABLE IF EXISTS office;
-- DROP TABLE IF EXISTS company;
-- DROP TABLE IF EXISTS company_industry;
-- DROP TABLE IF EXISTS localisation;
-- DROP TABLE IF EXISTS listing_type;
-- DROP TABLE IF EXISTS salary_source;
-- DROP TABLE IF EXISTS currency;
-- DROP TABLE IF EXISTS interval_salary;
-- DROP TABLE IF EXISTS site;

-- Création de la table site
CREATE TABLE site (
   id_site TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   site_name VARCHAR(255) NOT NULL,
   UNIQUE (site_name)
);

-- Création de la table interval_salary
CREATE TABLE interval_salary (
   id_interval TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   interval_name VARCHAR(255) NOT NULL,
   UNIQUE (interval_name)
);

-- Création de la table currency
CREATE TABLE currency (
   id_currency TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   currency_name VARCHAR(255) NOT NULL,
   UNIQUE (currency_name)
);

-- Création de la table salary_source
CREATE TABLE salary_source (
   id_salary_source TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   salary_source_name VARCHAR(255) NOT NULL,
   UNIQUE (salary_source_name)
);

-- Création de la table listing_type
CREATE TABLE listing_type (
   id_listing_type TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   listing_type_name VARCHAR(255) NOT NULL,
   UNIQUE (listing_type_name)
);

-- Création de la table company_industry
CREATE TABLE company_industry (
   id_company_industry TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   company_industry_name VARCHAR(255) NOT NULL,
   UNIQUE (company_industry_name)
);

-- Création de la table localisation
CREATE TABLE localisation (
   id_localisation INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   localisation_description TEXT NOT NULL,
   localisation_longitude DECIMAL(10, 6),
   localisation_latitude DECIMAL(10, 6),
   UNIQUE (localisation_description)
);

-- Création de la table company avec id_company en INT UNSIGNED
CREATE TABLE company (
   id_company INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   company_name VARCHAR(255) NOT NULL UNIQUE,
   company_email VARCHAR(255),
   company_has_description BOOLEAN,
   company_url TEXT,
   company_url_direct TEXT,
   head_office_id_localisation INT UNSIGNED,   
   id_company_industry TINYINT UNSIGNED,
   company_logo_photo_url TEXT,
   company_banner_photo_url TEXT,
   company_ceo_name VARCHAR(255),
   company_ceo_photo TEXT,
   FOREIGN KEY (head_office_id_localisation) REFERENCES localisation(id_localisation),
   FOREIGN KEY (id_company_industry) REFERENCES company_industry(id_company_industry)
);

-- Création de la table office
CREATE TABLE office (
   id_office INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   id_company INT UNSIGNED,
   id_localisation INT UNSIGNED,
   office_name VARCHAR(255),
   UNIQUE (id_company, id_localisation, office_name),
   FOREIGN KEY (id_company) REFERENCES company(id_company),
   FOREIGN KEY (id_localisation) REFERENCES localisation(id_localisation) 
);

-- Création de la table history_income
CREATE TABLE history_income (
   id_company INT UNSIGNED NOT NULL,
   history_income_date DATE NOT NULL,
   history_income_value TEXT NOT NULL,
   PRIMARY KEY (id_company, history_income_date),
   FOREIGN KEY (id_company) REFERENCES company(id_company)
);

-- Création de la table history_number_employees
CREATE TABLE history_number_employees (
   id_office INT UNSIGNED NOT NULL,
   history_number_employees_date DATE NOT NULL,
   history_number_employees_value TEXT NOT NULL,
   PRIMARY KEY (id_office, history_number_employees_date),
   FOREIGN KEY (id_office) REFERENCES office(id_office) 
);

-- Création de la table employee
CREATE TABLE employee (
   id_employee INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   employee_name VARCHAR(255) NOT NULL,
   employee_last_name VARCHAR(255),
   employee_email VARCHAR(255),
   employee_has_informations BOOLEAN,
   id_localisation INT UNSIGNED,
   FOREIGN KEY (id_localisation) REFERENCES localisation(id_localisation) ON DELETE SET NULL
);

-- Création de la table list_employees
CREATE TABLE list_employees (
   id_office INT UNSIGNED NOT NULL,
   id_employee INT UNSIGNED NOT NULL,
   employee_hire_date DATE,
   employee_fire_date DATE,
   employee_job VARCHAR(255),
   employee_salary DECIMAL(10, 2),
   PRIMARY KEY (id_office, id_employee),
   FOREIGN KEY (id_office) REFERENCES office(id_office) ,
   FOREIGN KEY (id_employee) REFERENCES employee(id_employee)
);

-- Création de la table job
CREATE TABLE job (
   id_job INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   job_identifiant VARCHAR(255) NOT NULL,
   id_site TINYINT UNSIGNED NOT NULL,
   job_url TEXT NOT NULL,
   job_url_direct TEXT,
   id_listing_type TINYINT UNSIGNED,
   id_office INT UNSIGNED NOT NULL,
   id_localisation INT UNSIGNED,
   title VARCHAR(255),
   job_title VARCHAR(255),
   job_date_posted DATE,
   id_interval TINYINT UNSIGNED,
   job_min_amount DECIMAL(10, 2),
   job_max_amount DECIMAL(10, 2),
   id_currency TINYINT UNSIGNED,
   job_is_remote BOOLEAN,
   job_level VARCHAR(255),
   job_function VARCHAR(255),
   id_salary_source TINYINT UNSIGNED,
   job_has_description BOOLEAN,
   UNIQUE (job_identifiant, id_site, id_localisation, id_office),
   FOREIGN KEY (id_site) REFERENCES site(id_site),
   FOREIGN KEY (id_interval) REFERENCES interval_salary(id_interval),
   FOREIGN KEY (id_currency) REFERENCES currency(id_currency),
   FOREIGN KEY (id_salary_source) REFERENCES salary_source(id_salary_source),
   FOREIGN KEY (id_listing_type) REFERENCES listing_type(id_listing_type),
   FOREIGN KEY (id_office) REFERENCES office(id_office),
   FOREIGN KEY (id_localisation) REFERENCES localisation(id_localisation)
);


-- Création de la table city
CREATE TABLE city (
   id_city INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   city_insee_code INT UNSIGNED NOT NULL,
   city_code VARCHAR(255),
   city_zip_code INT UNSIGNED NOT NULL,
   city_label VARCHAR(255),
   id_localisation INT UNSIGNED, 
   city_department_name VARCHAR(255),
   city_department_number INT UNSIGNED NOT NULL,
   city_region_name VARCHAR(255),
   city_region_geojson_name VARCHAR(255),
   
   UNIQUE (city_label, city_department_name),
   FOREIGN KEY (id_localisation) REFERENCES localisation(id_localisation)
);