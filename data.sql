--ALLOWED_USERS
INSERT INTO allowed_users (tg_id) VALUES ('714371204');
INSERT INTO allowed_users (tg_id) VALUES ('420551454');
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
