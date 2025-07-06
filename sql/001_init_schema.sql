
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'rootpass';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;


USE cctvdb;
CREATE TABLE IF NOT EXISTS `users` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL,
	`email` varchar(255) NOT NULL,
	`hashed_password` varchar(1000) NOT NULL,
	`created_on` date NOT NULL,
	`created_by` varchar(255) NOT NULL,
	`updated_on` date NOT NULL,
	`updated_by` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `roles` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(255) NOT NULL,
	`rank` int NOT NULL,
	`created_on` date NOT NULL,
	`created_by` varchar(255) NOT NULL,
	`updated_on` date NOT NULL,
	`updated_by` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `user_role_map` (
	`role_id` int NOT NULL,
	`user_id` int NOT NULL,
	`created_on` date NOT NULL,
	`created_by` varchar(255) NOT NULL,
	`updated_on` date NOT NULL,
	`updated_by` varchar(255) NOT NULL,
	PRIMARY KEY (`role_id`, `user_id`)
);

CREATE TABLE IF NOT EXISTS `permissions` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`permission_name` varchar(255) NOT NULL,
	`created_by` varchar(255) NOT NULL,
	`created_on` date NOT NULL,
	`updated_by` varchar(255) NOT NULL,
	`updated_on` date NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `role_permission_map` (
	`role_id` int NOT NULL,
	`permission_id` int NOT NULL,
	`created_by` varchar(255) NOT NULL,
	`created_on` date NOT NULL,
	`updated_by` varchar(255) NOT NULL,
	`updated_on` date NOT NULL,
	PRIMARY KEY (`role_id`, `permission_id`)
);

CREATE TABLE IF NOT EXISTS `cameras` (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`device_name` varchar(255) NOT NULL,
	`device_ip` varchar(255) NOT NULL,
	`device_location` varchar(255) NOT NULL,
	`created_by` varchar(255) NOT NULL,
	`created_on` date NOT NULL,
	`updated_by` varchar(255) NOT NULL,
	`updated_on` varchar(255) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE audit_logs (
    `id` INTEGER AUTO_INCREMENT UNIQUE,
    `user_id` INTEGER NOT NULL,
    `action` VARCHAR(50) NOT NULL,
    `entity_type` VARCHAR(100) NOT NULL,
    `entity_id` INTEGER,
    `details` TEXT,
    `timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    PRIMARY KEY(`id`)
);

CREATE TABLE  camera_assignment_map (
	`id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`camera_id` int NOT NULL,
	`user_id` int NOT NULL,
	`assigned_by` int NOT NULL,
	`CREATED_BY` varchar(255) NOT NULL,
	`CREATED_ON` date NOT NULL,
	`UPDATED_BY` varchar(255) NOT NULL,
	`UPDATED_ON` date NOT NULL,
	PRIMARY KEY (`id`)
);

ALTER TABLE `user_role_map` ADD CONSTRAINT `user_role_map_fk0` FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`);

ALTER TABLE `user_role_map` ADD CONSTRAINT `user_role_map_fk1` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`);

ALTER TABLE `role_permission_map` ADD CONSTRAINT `role_permission_map_fk0` FOREIGN KEY (`role_id`) REFERENCES `roles`(`id`);

ALTER TABLE `role_permission_map` ADD CONSTRAINT `role_permission_map_fk1` FOREIGN KEY (`permission_id`) REFERENCES `permissions`(`id`);

ALTER TABLE `camera_assignment_map` ADD CONSTRAINT `camera_assignment_map_fk0` FOREIGN KEY (`camera_id`) REFERENCES `cameras`(`id`);

ALTER TABLE `camera_assignment_map` ADD CONSTRAINT `camera_assignment_map_fk1` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`);

ALTER TABLE `camera_assignment_map` ADD CONSTRAINT `camera_assignment_map_fk2` FOREIGN KEY (`assigned_by`) REFERENCES `users`(`id`);


/* Perm entries */ 
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'CREATE_CAMERA', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'EDIT_CAMERA', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'DELETE_CAMERA', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'VIEW_CAMERA', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'ASSIGN_CAMERA', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');


INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'VIEW_ALL_USERS', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'CREATE_USER', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'EDIT_USER', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'DELETE_USER', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `permissions` (`id`, `permission_name`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES (NULL, 'VIEW_ACTIVITY_LOGS', 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');





/* Role entries */ 
INSERT INTO `roles` (`id`, `name`, `rank`, `created_on`, `created_by`, `updated_on`, `updated_by`) VALUES (NULL, 'superadmin', '1', '2025-07-05', 'ADMIN', '2025-07-05', 'ADMIN');

INSERT INTO `roles` (`id`, `name`, `rank`, `created_on`, `created_by`, `updated_on`, `updated_by`) VALUES (NULL, 'branchadmin', '2', '2025-07-05', 'ADMIN', '2025-07-05', 'ADMIN');

INSERT INTO `roles` (`id`, `name`, `rank`, `created_on`, `created_by`, `updated_on`, `updated_by`) VALUES (NULL, 'supervisor', '3', '2025-07-05', 'ADMIN', '2025-07-05', 'ADMIN');

/* role perm map entries */ 

INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'CREATE_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'EDIT_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'DELETE_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'VIEW_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'ASSIGN_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');


INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'VIEW_ALL_USERS'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'CREATE_USER'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'EDIT_USER'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'DELETE_USER'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'superadmin'), (select id from permissions where permission_name = 'VIEW_ACTIVITY_LOGS'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');



INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'branchadmin'), (select id from permissions where permission_name = 'CREATE_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'branchadmin'), (select id from permissions where permission_name = 'EDIT_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'branchadmin'), (select id from permissions where permission_name = 'DELETE_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');
INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'branchadmin'), (select id from permissions where permission_name = 'VIEW_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');



INSERT INTO `role_permission_map` (`role_id`, `permission_id`, `created_by`, `created_on`, `updated_by`, `updated_on`) VALUES ((SELECT ID FROM roles WHERE NAME = 'supervisor'), (select id from permissions where permission_name = 'VIEW_CAMERA'), 'ADMIN', '2025-07-05', 'ADMIN', '2025-07-05');



/* user onboarding */ 
INSERT INTO `users` (`name`, `email`, `hashed_password`, `created_on`, `created_by`, `updated_on`, `updated_by`) VALUES ('hritik', 'hritik1509@gmail.com','$2b$12$eJiIgDGZEtIVGt2upeol3eh6l5RC.rMQrcyv9C4P4LG39BbamfoQe', '2025-07-05', 'ADMIN', '2025-07-05', 'ADMIN');





/* user role map onboarding */ 

INSERT INTO `user_role_map` (`role_id`, `user_id`, `created_on`, `created_by`, `updated_on`, `updated_by`) VALUES ((select id from roles where name = 'superadmin'), (select id from users where name = 'hritik'), '2025-07-05', 'ADMIN', '2025-07-05', 'ADMIN');