--ALLOWED_USERS
INSERT INTO allowed_users (tg_id) VALUES ('714371204');
INSERT INTO allowed_users (tg_id) VALUES ('420551454');
-- USERS
INSERT INTO users (tg_id, tg_username, username, created_at, role, lang, is_active) VALUES ('11111111', 'alejandro_mech', 'Alejandro Fernandes', '2025-05-27 18:29:08.878314', 'mechanic', 'es', true);
INSERT INTO users (tg_id, tg_username, username, created_at, role, lang, is_active) VALUES ('22222222', 'adrian_mech', 'Adrian Lopes', '2025-05-27 18:29:08.878314', 'mechanic', 'es', true);
INSERT INTO users (tg_id, tg_username, username, created_at, role, lang, is_active) VALUES ('33333333', 'david_mech', 'David Martinez', '2025-05-27 18:29:08.878314', 'mechanic', 'es', true);
INSERT INTO users (tg_id, tg_username, username, created_at, role, lang, is_active) VALUES ('44444444', 'dima_mech', 'Dmitry Sobolev', '2025-05-27 18:29:08.878314', 'mechanic', 'ru', true);
INSERT INTO users (tg_id, tg_username, username, created_at, role, lang, is_active) VALUES ('55555555', 'nikolay_mech', 'Nikolay Ivanov', '2025-05-27 18:29:08.878314', 'mechanic', 'en', true);
INSERT INTO users (tg_id, tg_username, username, created_at, role, lang, is_active) VALUES ('66666666', 'diego_mech', 'Diego Sanchez', '2025-05-27 18:29:08.878314', 'mechanic', 'es', false);
-- CATEGORIES
INSERT INTO categories (title, emoji) values ('bicycles', '🚲');
INSERT INTO categories (title, emoji) values ('ebicycles', '⚡');
INSERT INTO categories (title, emoji) values ('segways', '🛴');
-- SUBCATEGORIES
INSERT INTO subcategories (title, category_id) values ('U', 1);
INSERT INTO subcategories (title, category_id) values ('H', 1);
INSERT INTO subcategories (title, category_id) values ('C', 1);
INSERT INTO subcategories (title, category_id) values ('EC', 2);
INSERT INTO subcategories (title, category_id) values ('EH', 2);
INSERT INTO subcategories (title, category_id) values ('EU', 2);
INSERT INTO subcategories (title, category_id) values ('SW', 3);
INSERT INTO subcategories (title, category_id) values ('SS', 3);
-- TRANSPORT
INSERT INTO transports (category_id, subcategory_id, serial_number) values (1, 1, 7);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (1, 1, 12);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (1, 2, 15);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (2, 4, 17);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (2, 4, 33);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (2, 5, 20);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (2, 6, 3);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (3, 7, 10);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (3, 7, 18);
INSERT INTO transports (category_id, subcategory_id, serial_number) values (3, 8, 10);
-- JOBTYPES
INSERT INTO jobtypes (title, emoji) values ('brake_system', '🛑');
INSERT INTO jobtypes (title, emoji) values ('transmission_and_chain', '⚙️');
INSERT INTO jobtypes (title) values ('wheels_and_tires');
INSERT INTO jobtypes (title) values ('steering');
INSERT INTO jobtypes (title) values ('frame_and_suspension');
INSERT INTO jobtypes (title) values ('electrical_and_lighting');
-- CategoryJobtypes
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (1, 1);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (1, 2);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (1, 3);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (1, 4);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (1, 5);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (2, 1);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (2, 2);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (2, 3);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (2, 4);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (2, 5);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (2, 6);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (3, 3);
INSERT INTO categories_jobtypes (category_id, jobtype_id) values (3, 6);
-- JOBS
INSERT INTO jobs (title, jobtype_id) values ('replace_brake_pads', 1);
INSERT INTO jobs (title, jobtype_id) values ('replace_brake_pads', 1);
INSERT INTO jobs (title, jobtype_id) values ('replace_brake_pads', 1);
INSERT INTO jobs (title, jobtype_id) values ('replace_brake_pads', 1);
INSERT INTO jobs (title, jobtype_id) values ('replace_brake_pads', 1);
INSERT INTO jobs (title, jobtype_id) values ('adjust_brakes', 1);
INSERT INTO jobs (title, jobtype_id) values ('adjust_brakes', 1);
INSERT INTO jobs (title, jobtype_id) values ('adjust_brakes', 1);
INSERT INTO jobs (title, jobtype_id) values ('adjust_brakes', 1);
INSERT INTO jobs (title, jobtype_id) values ('check_cables', 1);
INSERT INTO jobs (title, jobtype_id) values ('check_cables', 1);
INSERT INTO jobs (title, jobtype_id) values ('check_cables', 1);
INSERT INTO jobs (title, jobtype_id) values ('check_cables', 1);
INSERT INTO jobs (title, jobtype_id) values ('work with transmission 1', 2);
INSERT INTO jobs (title, jobtype_id) values ('work with transmission 2', 2);
INSERT INTO jobs (title, jobtype_id) values ('work with transmission 3', 2);
INSERT INTO jobs (title, jobtype_id) values ('replace tires 1', 3);
INSERT INTO jobs (title, jobtype_id) values ('replace tires 2', 3);
INSERT INTO jobs (title, jobtype_id) values ('replace tires 3', 3);
INSERT INTO jobs (title, jobtype_id) values ('work with steering 1', 4);
INSERT INTO jobs (title, jobtype_id) values ('work with steering 2', 4);
INSERT INTO jobs (title, jobtype_id) values ('work with steering 3', 4);
INSERT INTO jobs (title, jobtype_id) values ('work with frame and suspension 1', 5);
INSERT INTO jobs (title, jobtype_id) values ('work with frame and suspension 2', 5);
INSERT INTO jobs (title, jobtype_id) values ('work with frame and suspension 3', 5);
INSERT INTO jobs (title, jobtype_id) values ('work with electric 1', 6);
INSERT INTO jobs (title, jobtype_id) values ('work with electric 2', 6);
INSERT INTO jobs (title, jobtype_id) values ('work with electric 3', 6);
-- LOCATIONS
INSERT INTO locations (name) values ('first location');
INSERT INTO locations (name) values ('second location');
-- OPERATIONS
INSERT INTO operations(tg_id, transport_id, duration, location_id, comment, created_at, updated_at) values('420551454', 1, 45, 2, 'some comment', '2025-05-13 20:00:10', '2025-05-13 20:00:10');
INSERT INTO operations(tg_id, transport_id, duration, location_id, comment, created_at, updated_at) values('420551454', 1, 30, 1, 'some comment', '2025-05-14 20:00:10', '2025-05-14 20:00:10');
INSERT INTO operations(tg_id, transport_id, duration, location_id, comment, created_at, updated_at) values('420551454', 3, 30, 1, 'new comment', '2025-05-17 20:00:10', '2025-05-17 20:00:10');
INSERT INTO operations(tg_id, transport_id, duration, location_id, comment, created_at, updated_at) values('420551454', 3, 30, 1, 'new comment2', '2025-05-12 20:00:10', '2025-05-12 20:00:10');
INSERT INTO operations(tg_id, transport_id, duration, location_id, comment, created_at, updated_at) values('420551454', 3, 30, 1, 'some comment 34', '2025-05-10 20:00:10', '2025-05-10 20:00:10');
-- OPERATIONS_JOBS
INSERT INTO operations_jobs(operation_id, job_id) VALUES(1, 1);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(1, 2);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(1, 3);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(2, 4);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(3, 1);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(4, 2);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(4, 4);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(4, 5);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(4, 7);
INSERT INTO operations_jobs(operation_id, job_id) VALUES(5, 3);