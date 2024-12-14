DROP PROCEDURE IF EXISTS add_job;

DELIMITER //
CREATE PROCEDURE add_job(
   IN id_data VARCHAR(255),
   IN v_id_site TINYINT UNSIGNED,
   IN job_url_data TEXT,
   IN job_url_direct_data TEXT,
   IN title_data VARCHAR(255),
   IN name_company_data VARCHAR(255),
   IN location_data TEXT,
   IN job_title_data VARCHAR(255),
   IN date_posted_data DATE,
   IN v_id_salary_source TINYINT UNSIGNED,
   IN v_id_interval TINYINT UNSIGNED,
   IN min_amount_data DECIMAL(10, 2),
   IN max_amount_data DECIMAL(10, 2),
   IN v_id_currency TINYINT UNSIGNED,
   IN is_remote_data BOOLEAN,
   IN job_level_data VARCHAR(255),
   IN job_function_data VARCHAR(255),
   IN v_id_company_industry INT UNSIGNED,
   IN v_id_listing_type INT UNSIGNED,
   IN company_email_data VARCHAR(255),
   IN job_has_description_data BOOLEAN,
   IN company_url_data TEXT,
   IN company_url_direct_data TEXT,
   IN company_addresses_data TEXT,
   IN company_num_employees_data TEXT,
   IN company_revenue_data TEXT,
   IN company_has_description_data BOOLEAN,
   IN logo_photo_url_data TEXT,
   IN banner_photo_url_data TEXT,
   IN ceo_name_data VARCHAR(255),
   IN ceo_photo_data TEXT,
   
   OUT v_id_job INT UNSIGNED,
   OUT v_id_company INT UNSIGNED
)
BEGIN
   DECLARE v_id_office INT UNSIGNED;
   DECLARE v_id_localisation_job INT UNSIGNED;
   DECLARE v_id_localisation_company INT UNSIGNED;

   -- Insérer une localisation job
   IF NOT EXISTS (SELECT id_localisation FROM localisation WHERE localisation_description = location_data) THEN
      INSERT INTO localisation(localisation_description) VALUES (location_data);
   END IF;
   SELECT id_localisation INTO v_id_localisation_job FROM localisation WHERE localisation_description = location_data LIMIT 1;
   
   -- Insérer une localisation company
   IF NOT EXISTS (SELECT id_localisation FROM localisation WHERE localisation_description = company_addresses_data) THEN
      INSERT INTO localisation(localisation_description) VALUES (company_addresses_data);
   END IF;
   SELECT id_localisation INTO v_id_localisation_company FROM localisation WHERE localisation_description = company_addresses_data LIMIT 1;


	-- Vérifier si la société existe déjà dans la table company
	IF NOT EXISTS (
	   SELECT 1 
	   FROM company 
	   WHERE company_name = name_company_data
	) THEN
	   -- Insérer la société si elle n'existe pas
	   INSERT INTO company(
		  company_name, 
		  company_email, 
		  company_has_description, 
		  company_url, 
		  company_url_direct, 
		  id_company_industry, 
		  company_logo_photo_url, 
		  company_banner_photo_url, 
		  company_ceo_name, 
		  company_ceo_photo
	   ) 
	   VALUES (
		  name_company_data, 
		  company_email_data, 
		  company_has_description_data, 
		  company_url_data, 
		  company_url_direct_data, 
		  v_id_company_industry, 
		  logo_photo_url_data, 
		  banner_photo_url_data, 
		  ceo_name_data, 
		  ceo_photo_data
	   );
	END IF;

   -- Vérifier si l'entreprise a été mise à jour ou insérée
   SELECT id_company INTO v_id_company FROM company WHERE company_name = name_company_data LIMIT 1;
   
      -- Insérer une office
   IF NOT EXISTS (SELECT id_company FROM office WHERE id_company = v_id_company AND id_localisation = v_id_localisation_company) THEN
      INSERT INTO office(id_company, id_localisation) VALUES (v_id_company, v_id_localisation_company);
   END IF;
   SELECT id_office INTO v_id_office FROM office WHERE id_company = v_id_company AND id_localisation = v_id_localisation_company  LIMIT 1;


   -- Insérer un historique revenu
   -- IF NOT EXISTS (SELECT id_company FROM history_income WHERE id_company = v_id_company AND history_income_date = date_posted_data) THEN
      -- INSERT INTO history_income(id_company, history_income_date, history_income_value) VALUES (v_id_company, date_posted_data, company_revenue_data);
   -- END IF;

   -- -- Insérer un historique nombre employés
   -- IF NOT EXISTS (SELECT id_office FROM history_number_employees WHERE id_office = v_id_office AND history_number_employees_date = date_posted_data) THEN
      -- INSERT INTO history_number_employees(id_office, history_number_employees_date, history_number_employees_value) VALUES (v_id_office, date_posted_data, company_num_employees_data);
   -- END IF;
   

	-- Vérifier si le job existe déjà dans la table job
	IF NOT EXISTS (
	   SELECT 1 
	   FROM job 
	   WHERE job_identifiant = id_data
		 AND id_site = v_id_site
		 AND id_localisation = v_id_localisation_job
		 AND id_office = v_id_office
	) THEN
	   -- Insérer le job si il n'existe pas encore
	   INSERT INTO job(
		  job_identifiant, 
		  id_site, 
		  job_url, 
		  job_url_direct, 
		  id_listing_type, 
		  id_office, 
		  id_localisation, 
		  title, 
		  job_title, 
		  job_date_posted, 
		  id_interval, 
		  job_min_amount, 
		  job_max_amount, 
		  id_currency, 
		  job_is_remote, 
		  job_level, 
		  job_function, 
		  id_salary_source, 
		  job_has_description
	   ) 
	   VALUES (
		  id_data, 
		  v_id_site, 
		  job_url_data, 
		  job_url_direct_data, 
		  v_id_listing_type, 
		  v_id_office, 
		  v_id_localisation_job, 
		  title_data, 
		  job_title_data, 
		  date_posted_data, 
		  v_id_interval, 
		  min_amount_data, 
		  max_amount_data, 
		  v_id_currency, 
		  is_remote_data, 
		  job_level_data, 
		  job_function_data, 
		  v_id_salary_source, 
		  job_has_description_data
	   );
	END IF;

	 
   SELECT id_job INTO v_id_job FROM job WHERE job_identifiant = id_data AND id_site = v_id_site AND id_localisation = v_id_localisation_job AND id_office = v_id_office;

   SET @v_id_job = v_id_job;
   SET @v_id_company = v_id_company;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS GetLocalisationsWithNullCoords;

DELIMITER //

CREATE PROCEDURE GetLocalisationsWithNullCoords()
BEGIN
    SELECT id_localisation, localisation_description FROM localisation 
    WHERE localisation_longitude IS NULL 
    AND localisation_latitude IS NULL 
    AND localisation_description NOT LIKE '%NULL%' 
    LIMIT 100;
END //

DELIMITER ;

DROP PROCEDURE IF EXISTS UpdateLocalisationCoords;

DELIMITER //

CREATE PROCEDURE UpdateLocalisationCoords(
    IN p_id_localisation INT,
    IN p_longitude DECIMAL(12, 8),
    IN p_latitude DECIMAL(12, 8)
)
BEGIN
    UPDATE localisation 
    SET localisation_longitude = p_longitude, localisation_latitude = p_latitude 
    WHERE id_localisation = p_id_localisation;
END //

DELIMITER ;

DROP PROCEDURE IF EXISTS addLocalisationVille;

DELIMITER //

CREATE PROCEDURE addLocalisationVille(
    IN p_city_insee_code INT UNSIGNED,
    IN p_city_code VARCHAR(255),
    IN p_city_zip_code INT UNSIGNED,
    IN p_city_label VARCHAR(255),
    IN p_localisation_description VARCHAR(255),
    IN p_longitude DECIMAL(12, 8),
    IN p_latitude DECIMAL(12, 8),
    IN p_city_department_name VARCHAR(255),
    IN p_city_department_number INT UNSIGNED,
    IN p_city_region_name VARCHAR(255),
    IN p_city_region_geojson_name VARCHAR(255)
)
BEGIN

   DECLARE v_id_localisation_city INT UNSIGNED;

   -- Insérer une localisation city
   IF NOT EXISTS (SELECT id_localisation FROM localisation WHERE localisation_description = p_localisation_description) THEN
      INSERT INTO localisation(localisation_description, localisation_longitude, localisation_latitude) VALUES (p_localisation_description, p_longitude, p_latitude);
   END IF;
   SELECT id_localisation INTO v_id_localisation_city FROM localisation WHERE localisation_description = p_localisation_description LIMIT 1;
   
   
   	-- Vérifier si la city existe déjà dans la table city
	IF NOT EXISTS (
	   SELECT 1 
	   FROM city 
	   WHERE city_label = p_city_label
		 AND city_department_name = p_city_department_name
	) THEN
	   -- Insérer la city si il n'existe pas encore
	   INSERT INTO city(
		  city_insee_code, 
		  city_code, 
		  city_zip_code, 
		  city_label, 
		  id_localisation, 
		  city_department_name, 
		  city_department_number, 
		  city_region_name, 
		  city_region_geojson_name
	   ) 
	   VALUES (
		  p_city_insee_code, 
		  p_city_code, 
		  p_city_zip_code, 
		  p_city_label, 
		  v_id_localisation_city, 
		  p_city_department_name, 
		  p_city_department_number, 
		  p_city_region_name, 
		  p_city_region_geojson_name
	   );
	END IF;
   

END //

DELIMITER ;