/*
CS4400: Introduction to Database Systems
Fall 2020
Phase III Template

Team 10
Roy Makkar Gabriel (rmg7)
Quynh Trinh (qtrinh6)
Gavin Lo (glo30) -- not participate in phase 4
Hymee Huang (cfang49)

Directions:
Please follow all instructions from the Phase III assignment PDF.
This file must run without error for credit.

In case you need them:
select * from appointment;
select * from working_at;
select * from location;
select * from user;
select * from student;
select * from administrator;
select * from employee;
select * from labtech;
select * from pool;
select * from site;
select * from sitetester;
select * from test;

*/


-- ID: 2a
-- Author: lvossler3
-- Name: register_student
DROP PROCEDURE IF EXISTS register_student;
DELIMITER //
CREATE PROCEDURE register_student(
		IN i_username VARCHAR(40),
        IN i_email VARCHAR(40),
        IN i_fname VARCHAR(40),
        IN i_lname VARCHAR(40),
        IN i_location VARCHAR(40),
        IN i_housing_type VARCHAR(20),
        IN i_password VARCHAR(40)
)
BEGIN
	INSERT INTO USER
		VALUES (i_username, MD5(i_password), i_email, i_fname, i_lname);
	INSERT INTO STUDENT
		VALUES (i_username, i_housing_type, i_location);
-- End of solution
END //
DELIMITER ;


-- ID: 2b
-- Author: lvossler3
-- Name: register_employee
DROP PROCEDURE IF EXISTS register_employee;
DELIMITER //
CREATE PROCEDURE register_employee(
		IN i_username VARCHAR(40),
        IN i_email VARCHAR(40),
        IN i_fname VARCHAR(40),
        IN i_lname VARCHAR(40),
        IN i_phone VARCHAR(10),
        IN i_labtech BOOLEAN,
        IN i_sitetester BOOLEAN,
        IN i_password VARCHAR(40)
)
BEGIN
-- Type solution below
	IF NOT EXISTS
    (select * from USER
    where username = i_username
    or email = i_email
    or fname = i_fname)
	THEN
		INSERT INTO USER
        VALUES (i_username, MD5(i_password), i_email, i_fname, i_lname);
		INSERT INTO employee
		VALUES (i_username, i_phone);
        IF (i_labtech) THEN
			INSERT INTO LABTECH VALUES(i_username);
		END IF;
        IF (i_sitetester) THEN
			INSERT INTO SITETESTER VALUES (i_username);
		END IF;
	END IF;
-- End of solution
END //
DELIMITER ;

-- ID: 4a
-- Author: Aviva Smith
-- Name: student_view_results
DROP PROCEDURE IF EXISTS `student_view_results`;
DELIMITER //
CREATE PROCEDURE `student_view_results`(
    IN i_student_username VARCHAR(50),
	IN i_test_status VARCHAR(50),
	IN i_start_date DATE,
    IN i_end_date DATE
)
BEGIN
	DROP TABLE IF EXISTS student_view_results_result;
    CREATE TABLE student_view_results_result(
        test_id VARCHAR(7),
        timeslot_date date,
        date_processed date,
        pool_status VARCHAR(40),
        test_status VARCHAR(40)
    );
    INSERT INTO student_view_results_result

    -- Type solution below

		SELECT t.test_id, t.appt_date, p.process_date, p.pool_status, t.test_status
        FROM test AS t
		JOIN pool AS p ON p.pool_id = t.pool_id
        JOIN appointment AS a ON a.appt_date = t.appt_date
			AND a.appt_time = t.appt_time
            AND a.site_name = t.appt_site
        WHERE a.username = i_student_username
			AND IF(i_test_status IS NOT NULL, t.test_status = i_test_status, 1 = 1)
            AND IF(i_start_date IS NOT NULL, t.appt_date >= i_start_date, 1 = 1)
            AND IF(i_end_date IS NOT NULL, t.appt_date <= i_end_date, 1 = 1);

    -- End of solution
END //
DELIMITER ;

-- ID: 5a
-- Author: asmith457
-- Name: explore_results
DROP PROCEDURE IF EXISTS explore_results;
DELIMITER $$
CREATE PROCEDURE explore_results (
    IN i_test_id VARCHAR(7))
BEGIN
    DROP TABLE IF EXISTS explore_results_result;
    CREATE TABLE explore_results_result(
        test_id VARCHAR(7),
        test_date date,
        timeslot time,
        testing_location VARCHAR(40),
        date_processed date,
        pooled_result VARCHAR(40),
        individual_result VARCHAR(40),
        processed_by VARCHAR(80)
    );
    INSERT INTO explore_results_result

    -- Type solution below
	
        SELECT test.test_id AS test_id, test.appt_date AS test_date, test.appt_time AS timeslot, 
                test.appt_site AS testing_location, pool.process_date AS date_processed, pool.pool_status AS pooled_result, 
                test.test_status AS individual_result, CONCAT(user.fname, " ", user.lname) AS processed_by
		FROM pool
        LEFT JOIN test ON pool.pool_id = test.pool_id
        JOIN user ON user.username = pool.processed_by
        WHERE IF((SELECT test_id FROM test WHERE test_id = i_test_id) IS NOT NULL, test.test_id = i_test_id, 1 = 0);
        
    -- End of solution
END$$
DELIMITER ;

-- ID: 6a
-- Author: asmith457
-- Name: aggregate_results
DROP PROCEDURE IF EXISTS aggregate_results;
DELIMITER $$
CREATE PROCEDURE aggregate_results(
    IN i_location VARCHAR(50),
    IN i_housing VARCHAR(50),
    IN i_testing_site VARCHAR(50),
    IN i_start_date DATE,
    IN i_end_date DATE)
BEGIN
    DROP TABLE IF EXISTS aggregate_results_result;
    CREATE TABLE aggregate_results_result(
        test_status VARCHAR(40),
        num_of_test INT,
        percentage DECIMAL(6,2)
    );
    INSERT INTO aggregate_results_result

    -- Type solution below
    SELECT t.test_status, COUNT(t.test_status) AS num_of_test,
		ROUND(COUNT(t.test_status) * 100.0 / (
			SELECT COUNT(*)
            FROM test AS t
			JOIN pool ON pool.pool_id = t.pool_id
            JOIN appointment AS appt ON t.appt_date = appt.appt_date AND t.appt_time = appt.appt_time AND t.appt_site = appt.site_name
			JOIN student ON appt.username = student.student_username
			WHERE IF(i_location IS NOT NULL, student.location = i_location, 1 = 1)
				AND IF(i_housing IS NOT NULL, student.housing_type = i_housing, 1 = 1)
				AND IF(i_testing_site IS NOT NULL, appt.site_name = i_testing_site, 1 = 1)
				AND IF(i_start_date IS NOT NULL, pool.process_date >= i_start_date, 1 = 1)
				AND IF(i_end_date IS NOT NULL, pool.process_date <= i_end_date AND pool.pool_status <> 'pending', 1 = 1)
            ), 2) AS percentage
    FROM test AS t
	JOIN pool ON pool.pool_id = t.pool_id
    JOIN appointment AS appt ON t.appt_date = appt.appt_date AND t.appt_time = appt.appt_time AND t.appt_site = appt.site_name
	JOIN student ON appt.username = student.student_username
	WHERE IF(i_location IS NOT NULL, student.location = i_location, 1 = 1)
		AND IF(i_housing IS NOT NULL, student.housing_type = i_housing, 1 = 1)
		AND IF(i_testing_site IS NOT NULL, appt.site_name = i_testing_site, 1 = 1)
		AND IF(i_start_date IS NOT NULL, pool.process_date >= i_start_date, 1 = 1)
		AND IF(i_end_date IS NOT NULL, pool.process_date <= i_end_date AND pool.pool_status <> 'pending', 1 = 1)
    GROUP BY t.test_status;

    -- End of solution
END$$
DELIMITER ;


-- ID: 7a
-- Author: lvossler3
-- Name: test_sign_up_filter
DROP PROCEDURE IF EXISTS test_sign_up_filter;
DELIMITER //
CREATE PROCEDURE test_sign_up_filter(
    IN i_username VARCHAR(40),
    IN i_testing_site VARCHAR(40),
    IN i_start_date date,
    IN i_end_date date,
    IN i_start_time time,
    IN i_end_time time)
BEGIN
    DROP TABLE IF EXISTS test_sign_up_filter_result;
    CREATE TABLE test_sign_up_filter_result(
        appt_date date,
        appt_time time,
        street VARCHAR (40),
        city VARCHAR(40),
        state VARCHAR(2),
        zip VARCHAR(5),
        site_name VARCHAR(40));
    INSERT INTO test_sign_up_filter_result

    -- Type solution below
    SELECT appt.appt_date, appt.appt_time, site.street, site.city, site.state, site.zip, site.site_name
	FROM appointment AS appt
	JOIN site ON appt.site_name = site.site_name
	WHERE appt.username IS NULL
		AND site.location = (SELECT location FROM student WHERE student_username = i_username)
        AND IF(i_testing_site IS NOT NULL, site.site_name = i_testing_site, 1 = 1)
		AND IF(i_start_date IS NOT NULL, appt.appt_date >= i_start_date, 1 = 1)
		AND IF(i_end_date IS NOT NULL, appt.appt_date <= i_end_date, 1 = 1)
		AND IF(i_start_time IS NOT NULL, appt.appt_time >= i_start_time, 1 = 1)
		AND IF(i_end_time IS NOT NULL, appt.appt_time <= i_end_time, 1 = 1)
	;
    -- End of solution
    END //
    DELIMITER ;

-- ID: 7b
-- Author: lvossler3 (completed by qtrinh6)
-- Name: test_sign_up
DROP PROCEDURE IF EXISTS test_sign_up;
DELIMITER //
CREATE PROCEDURE test_sign_up(
		IN i_username VARCHAR(40),
        IN i_site_name VARCHAR(40),
        IN i_appt_date date,
        IN i_appt_time time,
        IN i_test_id VARCHAR(7)
)
BEGIN
-- Type solution below

	IF i_username IS NOT NULL AND i_site_name IS NOT NULL AND i_appt_date IS NOT NULL AND i_appt_time IS NOT NULL AND i_test_id IS NOT NULL
    AND (SELECT appointment.username
		FROM appointment
        WHERE
			site_name = i_site_name AND
			appt_date = i_appt_date AND
			appt_time = i_appt_time) IS NULL
	AND (SELECT test.test_status
        FROM test
        JOIN appointment AS appt ON test.appt_site = appt.site_name AND test.appt_date = appt.appt_date AND test.appt_time = appt.appt_time
        WHERE appt.username = i_username AND test.test_status = 'pending') IS NULL
	THEN 
		UPDATE appointment AS appt
		SET
			appt.username = i_username
		WHERE
			appt.site_name = i_site_name AND
			appt.appt_date = i_appt_date AND
			appt.appt_time = i_appt_time;
		
        INSERT INTO test VALUES (i_test_id, 'pending', NULL, i_site_name, i_appt_date, i_appt_time);
    END IF;
    
-- End of solution
END //
DELIMITER ;

-- Number: 8a
-- Author: lvossler3  (completed by qtrinh6)
-- Name: tests_processed
DROP PROCEDURE IF EXISTS tests_processed;
DELIMITER //
CREATE PROCEDURE tests_processed(
    IN i_start_date date,
    IN i_end_date date,
    IN i_test_status VARCHAR(10),
    IN i_lab_tech_username VARCHAR(40))
BEGIN
    DROP TABLE IF EXISTS tests_processed_result;
    CREATE TABLE tests_processed_result(
        test_id VARCHAR(7),
        pool_id VARCHAR(10),
        test_date date,
        process_date date,
        test_status VARCHAR(10) );
    INSERT INTO tests_processed_result
    -- Type solution below
    
		SELECT test.test_id, test.pool_id, test.appt_date as test_date, pool.process_date, test.test_status
		FROM pool
        JOIN test ON pool.pool_id = test.pool_id
        WHERE IF(i_start_date IS NOT NULL, test.appt_date >= i_start_date, 1 = 1)
			  AND IF(i_end_date IS NOT NULL, test.appt_date <= i_end_date, 1 = 1)
              AND IF(i_test_status IS NOT NULL, test.test_status = i_test_status, 1 = 1)
              AND IF(i_lab_tech_username IS NOT NULL, pool.processed_by = i_lab_tech_username, 1 = 1)
        ;    
        
    -- End of solution
    END //
    DELIMITER ;

-- ID: 9a
-- Author: ahatcher8@ (completed by qtrinh6)
-- Name: view_pools
DROP PROCEDURE IF EXISTS view_pools;
DELIMITER //
CREATE PROCEDURE view_pools(
    IN i_begin_process_date DATE,
    IN i_end_process_date DATE,
    IN i_pool_status VARCHAR(20),
    IN i_processed_by VARCHAR(40)
)
BEGIN
    DROP TABLE IF EXISTS view_pools_result;
    CREATE TABLE view_pools_result(
        pool_id VARCHAR(10),
        test_ids VARCHAR(100),
        date_processed DATE,
        processed_by VARCHAR(40),
        pool_status VARCHAR(20));

    INSERT INTO view_pools_result
-- Type solution below
	
		SELECT pool.pool_id,
			   GROUP_CONCAT(test.test_id ORDER BY test.test_id) AS test_ids,
               pool.process_date as date_processed, pool.processed_by, pool.pool_status
		FROM pool
        LEFT JOIN test ON pool.pool_id = test.pool_id
        WHERE 1 = 1 AND
			CASE
				-- all arguments are NULL
				WHEN i_begin_process_date IS NULL AND i_end_process_date IS NULL AND (i_pool_status IS NULL OR LOWER(i_pool_status) = 'all') AND i_processed_by IS NULL THEN 1 = 1
                WHEN i_end_process_date IS NOT NULL THEN pool.process_date <= i_end_process_date AND pool.pool_status <> 'pending'
					AND IF(i_begin_process_date IS NOT NULL, pool.process_date >= i_begin_process_date, 1 = 1)
                    AND IF(i_processed_by IS NOT NULL, pool.processed_by = i_processed_by, 1 = 1)
                    AND IF(LOWER(i_pool_status) = 'positive' OR LOWER(i_pool_status) = 'negative', pool.pool_status = i_pool_status, 1 = 1)
                    AND IF(LOWER(i_pool_status) = 'pending', 1 = 0, 1 = 1)
                WHEN i_begin_process_date IS NOT NULL THEN (pool.process_date >= i_begin_process_date OR pool.pool_status = 'pending')
					AND IF(i_pool_status IS NOT NULL, IF(LOWER(i_pool_status) = 'all', 1 = 1, pool.pool_status = i_pool_status), 1 = 1)
                    AND IF(i_processed_by IS NOT NULL, pool.processed_by = i_processed_by, 1 = 1)
				WHEN i_pool_status IS NOT NULL THEN IF(LOWER(i_pool_status) = 'all', 1 = 1, pool.pool_status = i_pool_status)
					AND IF(i_processed_by IS NOT NULL, pool.processed_by = i_processed_by, 1 = 1)
				WHEN i_processed_by IS NOT NULL THEN pool.processed_by = i_processed_by
			END
		GROUP BY pool.pool_id;

-- End of solution
END //
DELIMITER ;

-- ID: 10a
-- Author: ahatcher8@  (completed by qtrinh6)
-- Name: create_pool
DROP PROCEDURE IF EXISTS create_pool;
DELIMITER //
CREATE PROCEDURE create_pool(
	IN i_pool_id VARCHAR(10),
    IN i_test_id VARCHAR(7)
)
BEGIN
-- Type solution below

	IF i_pool_id IS NOT NULL AND i_test_id IS NOT NULL
    AND i_pool_id NOT IN (SELECT pool.pool_id FROM pool)
    AND (SELECT test.test_id FROM test WHERE test.test_id = i_test_id) IS NOT NULL
    AND (SELECT test.pool_id FROM test WHERE test.test_id = i_test_id) IS NULL
    THEN
		INSERT INTO pool VALUES (i_pool_id, 'pending', NULL, NULL);
		UPDATE test
			SET test.pool_id = i_pool_id
            WHERE test.test_id = i_test_id;
    END IF;
-- End of solution
END //
DELIMITER ;

-- ID: 10b
-- Author: ahatcher8@ (completed by qtrinh6)
-- Name: assign_test_to_pool
DROP PROCEDURE IF EXISTS assign_test_to_pool;
DELIMITER //
CREATE PROCEDURE assign_test_to_pool(
    IN i_pool_id VARCHAR(10),
    IN i_test_id VARCHAR(7)
)
BEGIN
-- Type solution below
	IF i_pool_id IS NOT NULL AND i_test_id IS NOT NULL
    AND (SELECT test.test_id FROM test WHERE test.test_id = i_test_id) IS NOT NULL
    AND (SELECT test.pool_id FROM test WHERE test.test_id = i_test_id) IS NULL
    AND (SELECT COUNT(*) FROM test WHERE test.pool_id = i_pool_id) < 7
    THEN
			UPDATE test
			SET test.pool_id = i_pool_id
			WHERE test.test_id = i_test_id;
    END IF;

-- End of solution
END //
DELIMITER ;

-- ID: 11a
-- Author: ahatcher8@
-- Name: process_pool
DROP PROCEDURE IF EXISTS process_pool;
DELIMITER //
CREATE PROCEDURE process_pool(
    IN i_pool_id VARCHAR(10),
    IN i_pool_status VARCHAR(20),
    IN i_process_date DATE,
    IN i_processed_by VARCHAR(40)
)
BEGIN
-- Type solution below

    SELECT pool_status
    INTO @curr_status
    FROM POOL
    WHERE pool_id = i_pool_id;

    IF
        ((@curr_status = 'pending') AND (i_pool_status = 'positive' OR i_pool_status = 'negative'))
    THEN
        UPDATE POOL
        SET pool_status = i_pool_status, process_date = i_process_date, processed_by = i_processed_by
        WHERE pool_id = i_pool_id;
    END IF;


-- End of solution
END //
DELIMITER ;

-- ID: 11b
-- Author: ahatcher8@
-- Name: process_test
DROP PROCEDURE IF EXISTS process_test;
DELIMITER //
CREATE PROCEDURE process_test(
    IN i_test_id VARCHAR(7),
    IN i_test_status VARCHAR(20)
)
BEGIN

	IF EXISTS 
		(SELECT test_id FROM pool p, test t WHERE p.pool_id = t.pool_id AND pool_status IN ('positive', 'negative') AND test_id = i_test_id AND test_status = 'pending')
    THEN
		IF 'positive' = (SELECT pool_status FROM pool p, test t WHERE p.pool_id = t.pool_id AND test_id = i_test_id) AND i_test_status IN ('positive', 'negative', 'pending')
			THEN
				UPDATE test 
				SET test_status = i_test_status
				WHERE test_id = i_test_id;
		ELSE IF 'negative' = (SELECT pool_status FROM pool p, test t WHERE p.pool_id = t.pool_id AND test_id = i_test_id) AND i_test_status = 'negative'
			THEN
				UPDATE test 
				SET test_status = 'negative'
				WHERE test_id = i_test_id;
			END IF;
		END IF;
	END IF;

-- End of solution
END //
DELIMITER ;




-- ID: 12a
-- Author: dvaidyanathan6
-- Name: create_appointment

DROP PROCEDURE IF EXISTS create_appointment;
DELIMITER //
CREATE PROCEDURE create_appointment(
	IN i_site_name VARCHAR(40),
    IN i_date DATE,
    IN i_time TIME
)
BEGIN
-- Type solution below

    IF (SELECT count(*) FROM appointment
    WHERE site_name = i_site_name
    AND appt_date=i_date) < (SELECT count(username) FROM working_at WHERE site=i_site_name) * 10
    AND (i_site_name, i_date, i_time) NOT IN (SELECT site_name, appt_date, appt_time FROM appointment)
    THEN
    INSERT INTO appointment VALUE (NULL, i_site_name, i_date, i_time);
    END IF;

END //
DELIMITER ;


-- ID: 13a
-- Author: dvaidyanathan6@
-- Name: view_appointments
DROP PROCEDURE IF EXISTS view_appointments;
DELIMITER //
CREATE PROCEDURE view_appointments(
    IN i_site_name VARCHAR(40),
    IN i_begin_appt_date DATE,
    IN i_end_appt_date DATE,
    IN i_begin_appt_time TIME,
    IN i_end_appt_time TIME,
    IN i_is_available INT  -- 0 for "booked only", 1 for "available only", NULL for "all"
)
BEGIN
    DROP TABLE IF EXISTS view_appointments_result;
    CREATE TABLE view_appointments_result(

        appt_date DATE,
        appt_time TIME,
        site_name VARCHAR(40),
        location VARCHAR(40),
        username VARCHAR(40));

    
-- Type solution below

	IF (i_is_available IS NULL) # all values
    THEN
		IF (i_site_name IS NULL AND i_begin_appt_date IS NULL AND i_end_appt_date IS NULL AND i_begin_appt_time IS NULL AND i_end_appt_time IS NULL)
		THEN
            INSERT INTO view_appointments_result
			SELECT appt_date, appt_time, appointment.site_name, location, username
			FROM appointment
			LEFT OUTER JOIN site
			ON appointment.site_name = site.site_name;

        ELSE
			INSERT INTO view_appointments_result
			SELECT appt_date, appt_time, appointment.site_name, location, username
			FROM appointment
			LEFT OUTER JOIN site
			ON appointment.site_name = site.site_name
			WHERE IF(i_site_name is not null, appointment.site_name = i_site_name, 1=1)
            AND IF((i_begin_appt_date IS NOT NULL AND i_end_appt_date IS NOT NULL), (appt_date BETWEEN i_begin_appt_date AND i_end_appt_date),
				IF((i_begin_appt_date IS NOT NULL AND i_end_appt_date IS NULL), (appt_date >= i_begin_appt_date),
                IF((i_begin_appt_date IS NULL and i_end_appt_date IS NOT NULL), (appt_date <= i_end_appt_date), 1=1)))
            AND IF((i_begin_appt_time IS NOT NULL AND i_end_appt_time IS NOT NULL), (appt_time BETWEEN i_begin_appt_time AND i_end_appt_time),
				IF((i_begin_appt_time IS NOT NULL AND i_end_appt_time IS NULL), (appt_time >= i_begin_appt_time),
                IF((i_begin_appt_time IS NULL AND i_end_appt_time IS NOT NULL), (appt_time <= i_end_appt_time), 1=1)));
		END if;
        
    ELSE IF 
		(i_is_available = 1) # not booked only
	then
		INSERT INTO view_appointments_result
		SELECT appt_date, appt_time, appointment.site_name, location, username
		FROM appointment
        LEFT OUTER JOIN site ON appointment.site_name = site.site_name
		WHERE username is null
		AND IF(i_site_name is not null, appointment.site_name = i_site_name, 1=1)
		AND IF((i_begin_appt_date IS NOT NULL AND i_end_appt_date IS NOT NULL), (appt_date BETWEEN i_begin_appt_date AND i_end_appt_date),
			IF((i_begin_appt_date IS NOT NULL AND i_end_appt_date IS NULL), (appt_date >= i_begin_appt_date),
			IF((i_begin_appt_date IS NULL and i_end_appt_date IS NOT NULL), (appt_date <= i_end_appt_date), 1=1)))
		AND IF((i_begin_appt_time IS NOT NULL AND i_end_appt_time IS NOT NULL), (appt_time BETWEEN i_begin_appt_time AND i_end_appt_time),
			IF((i_begin_appt_time IS NOT NULL AND i_end_appt_time IS NULL), (appt_time >= i_begin_appt_time),
			IF((i_begin_appt_time IS NULL AND i_end_appt_time IS NOT NULL), (appt_time <= i_end_appt_time), 1=1)));
            
	ELSE IF (i_is_available = 0) # booked only
    THEN
		INSERT INTO view_appointments_result
		SELECT appt_date, appt_time, appointment.site_name, location, username
		FROM appointment LEFT OUTER JOIN site ON appointment.site_name = site.site_name
		WHERE username is not null
		AND IF(i_site_name is not null, appointment.site_name = i_site_name, 1=1)
		AND IF((i_begin_appt_date IS NOT NULL AND i_end_appt_date IS NOT NULL), (appt_date BETWEEN i_begin_appt_date AND i_end_appt_date),
			IF((i_begin_appt_date IS NOT NULL AND i_end_appt_date IS NULL), (appt_date >= i_begin_appt_date),
			IF((i_begin_appt_date IS NULL and i_end_appt_date IS NOT NULL), (appt_date <= i_end_appt_date), 1=1)))
		AND IF((i_begin_appt_time IS NOT NULL AND i_end_appt_time IS NOT NULL), (appt_time BETWEEN i_begin_appt_time AND i_end_appt_time),
			IF((i_begin_appt_time IS NOT NULL AND i_end_appt_time IS NULL), (appt_time >= i_begin_appt_time),
			IF((i_begin_appt_time IS NULL AND i_end_appt_time IS NOT NULL), (appt_time <= i_end_appt_time), 1=1)));

    END IF;
    END IF;
    END IF;
     
    
-- End of solution
END //
DELIMITER ;


-- ID: 14a
-- Author: kachtani3@
-- Name: view_testers
DROP PROCEDURE IF EXISTS view_testers;
DELIMITER //
CREATE PROCEDURE view_testers()
BEGIN
    DROP TABLE IF EXISTS view_testers_result;
    CREATE TABLE view_testers_result(

        username VARCHAR(40),
        name VARCHAR(80),
        phone_number VARCHAR(10),
        assigned_sites VARCHAR(255));

    INSERT INTO view_testers_result
-- Type solution below

	SELECT sitetester_username as username, concat(fname, " ", lname), phone_num, GROUP_CONCAT(site order by site SEPARATOR ',') as assigned_sites
    FROM working_at
    RIGHT OUTER JOIN 
		(SELECT sitetester_username, fname, lname, phone_num
        FROM sitetester, employee, user
        WHERE sitetester_username = emp_username AND sitetester_username = username) AS temp
	ON working_at.username = sitetester_username
	GROUP BY sitetester_username; 


-- End of solution
END //
DELIMITER ;


-- ID: 15a
-- Author: kachtani3@
-- Name: create_testing_site
DROP PROCEDURE IF EXISTS create_testing_site;
DELIMITER //
CREATE PROCEDURE create_testing_site(
	IN i_site_name VARCHAR(40),
    IN i_street varchar(40),
    IN i_city varchar(40),
    IN i_state char(2),
    IN i_zip char(5),
    IN i_location varchar(40),
    IN i_first_tester_username varchar(40)
)
BEGIN
-- Type solution below
	IF NOT EXISTS 
    (SELECT * FROM site
    WHERE site_name = i_site_name and i_street = street and i_city = city and i_state = state and i_zip = zip and i_location = location)
	THEN
		IF (SELECT distinct username FROM working_at WHERE i_first_tester_username = username) IS NOT NULL #username must exist in the system
        THEN
		INSERT INTO site
		VALUES (i_site_name, i_street, i_city, i_state, i_zip, i_location); # ONLY INSERT IF IT DOES NOT ALREADY EXIST IN DB

        INSERT INTO working_at VALUES (i_first_tester_username, i_site_name); 
        END IF;
        
	END IF;
-- End of solution
END //
DELIMITER ;

-- ID: 16a
-- Author: kachtani3@
-- Name: pool_metadata
DROP PROCEDURE IF EXISTS pool_metadata;
DELIMITER //
CREATE PROCEDURE pool_metadata(
    IN i_pool_id VARCHAR(10))
BEGIN
    DROP TABLE IF EXISTS pool_metadata_result;
    CREATE TABLE pool_metadata_result(
        pool_id VARCHAR(10),
        date_processed DATE,
        pooled_result VARCHAR(20),
        processed_by VARCHAR(100));

    INSERT INTO pool_metadata_result
-- Type solution below

	SELECT pool_id, process_date AS date_processed, pool_status AS pooled_result, concat(fname, " ", lname) AS processed_by
    FROM pool, user
    WHERE pool_id = i_pool_id AND username = processed_by;

-- End of solution
END //
DELIMITER ;


-- ID: 16b
-- Author: glo30
-- Name: tests_in_pool
DROP PROCEDURE IF EXISTS tests_in_pool;
DELIMITER //
CREATE PROCEDURE tests_in_pool(
    IN i_pool_id VARCHAR(10))
BEGIN
    DROP TABLE IF EXISTS tests_in_pool_result;
    CREATE TABLE tests_in_pool_result(
        test_id varchar(7),
        date_tested DATE,
        testing_site VARCHAR(40),
        test_result VARCHAR(20));

    INSERT INTO tests_in_pool_result
-- Type solution below

    SELECT test_id, appt_date, appt_site, test_status FROM TEST WHERE pool_id = i_pool_id;

-- End of solution
END //
DELIMITER ;

-- ID: 17a
-- Author: glo30
-- Name: tester_assigned_sites
DROP PROCEDURE IF EXISTS tester_assigned_sites;
DELIMITER //
CREATE PROCEDURE tester_assigned_sites(
    IN i_tester_username VARCHAR(40))
BEGIN
    DROP TABLE IF EXISTS tester_assigned_sites_result;
    CREATE TABLE tester_assigned_sites_result(
        site_name VARCHAR(40));

    INSERT INTO tester_assigned_sites_result
-- Type solution below

    SELECT site FROM WORKING_AT WHERE username = i_tester_username;

-- End of solution
END //
DELIMITER ;

-- ID: 17b
-- Author: glo30
-- Name: assign_tester
DROP PROCEDURE IF EXISTS assign_tester;
DELIMITER //
CREATE PROCEDURE assign_tester(
	IN i_tester_username VARCHAR(40),
    IN i_site_name VARCHAR(40)
)
BEGIN
-- Type solution below

INSERT INTO WORKING_AT (username, site) VALUES (i_tester_username, i_site_name);

-- End of solution
END //
DELIMITER ;


-- ID: 17c
-- Author: glo30
-- Name: unassign_tester
DROP PROCEDURE IF EXISTS unassign_tester;
DELIMITER //
CREATE PROCEDURE unassign_tester(
	IN i_tester_username VARCHAR(40),
    IN i_site_name VARCHAR(40)
)
BEGIN
-- Type solution below

IF (SELECT COUNT(username) FROM WORKING_AT WHERE site = i_site_name) > 1 THEN
	DELETE FROM WORKING_AT WHERE username = i_tester_username AND site = i_site_name;
END IF;

-- End of solution
END //
DELIMITER ;


-- ID: 18a
-- Author: glo30
-- Name: daily_results
DROP PROCEDURE IF EXISTS daily_results;
DELIMITER //
CREATE PROCEDURE daily_results()
BEGIN
	DROP TABLE IF EXISTS daily_results_result;
    CREATE TABLE daily_results_result(
		process_date date,
        num_tests int,
        pos_tests int,
        pos_percent DECIMAL(6,2));
	INSERT INTO daily_results_result
    -- Type solution below

    SELECT process_date, COUNT(*) AS num_tests, SUM(IF(test_status = 'positive', 1, 0)) AS pos_tests, ROUND(100 * SUM(IF(test_status = 'positive', 1, 0)) / COUNT(*), 2) AS pos_percent FROM TEST NATURAL JOIN POOL WHERE process_date IS NOT NULL GROUP BY process_date;

    -- End of solution
    END //
    DELIMITER ;
    
    
-- Additional procedures for phase 4

DROP PROCEDURE IF EXISTS has_pending_test;
DELIMITER //
CREATE PROCEDURE has_pending_test(
		IN i_username VARCHAR(40)
)
BEGIN
	DROP TABLE IF EXISTS has_pending_test_result;
    CREATE TABLE has_pending_test_result(
        pending_test VARCHAR(40));

    INSERT INTO has_pending_test_result

	SELECT test.test_id
	FROM test
	JOIN appointment AS appt ON test.appt_site = appt.site_name AND test.appt_date = appt.appt_date AND test.appt_time = appt.appt_time
	WHERE appt.username = i_username AND test.test_status = 'pending';
    
END //
DELIMITER ;













