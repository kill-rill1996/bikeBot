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
