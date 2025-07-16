/*
SQLyog Community v13.1.1 (64 bit)
MySQL - 5.5.29 : Database - events_management
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`events_management` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `events_management`;

/*Table structure for table `bookings` */

DROP TABLE IF EXISTS `bookings`;

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `booking_date` date NOT NULL,
  `booking_time` time NOT NULL,
  `location` varchar(200) DEFAULT NULL,
  `estimated_cost` decimal(10,2) NOT NULL,
  `deposit_paid` decimal(10,2) NOT NULL,
  `payment_status` enum('Pending','Completed') NOT NULL DEFAULT 'Pending',
  `invoice_generated` tinyint(1) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;

/*Data for the table `bookings` */

insert  into `bookings`(`id`,`user_id`,`event_id`,`booking_date`,`booking_time`,`location`,`estimated_cost`,`deposit_paid`,`payment_status`,`invoice_generated`,`created_at`) values 
(1,1,3,'2025-02-28','00:15:00',NULL,5000.00,3000.00,'Completed',0,'2025-02-08 01:16:43'),
(2,1,3,'2025-02-28','03:26:00',NULL,9000.00,5000.00,'Completed',0,'2025-02-08 01:22:25'),
(3,1,3,'2025-02-27','03:34:00',NULL,20000.00,5000.00,'Completed',0,'2025-02-08 01:31:53'),
(4,1,3,'2027-01-07','03:12:00',NULL,4000.00,2000.00,'Completed',0,'2025-02-08 02:08:10'),
(6,1,3,'2025-03-07','05:22:00',NULL,60000.00,30000.00,'Completed',0,'2025-02-19 23:35:13'),
(7,1,3,'2025-02-28','01:48:00',NULL,90000.00,60000.00,'Completed',0,'2025-02-19 23:42:52'),
(8,1,3,'2025-02-28','05:00:00','hyderabad',60000.00,20000.00,'Completed',0,'2025-02-20 00:03:14'),
(9,1,3,'2025-02-27','02:28:00','hyderabad',80000.00,7000.00,'Completed',0,'2025-02-20 00:26:40'),
(10,1,8,'2025-02-25','01:30:00','Ladakh',7777.00,888.00,'Completed',0,'2025-02-20 00:29:05');

/*Table structure for table `event_customization` */

DROP TABLE IF EXISTS `event_customization`;

CREATE TABLE `event_customization` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `guest_count` int(11) NOT NULL,
  `catering_preferences` varchar(255) NOT NULL,
  `decoration_details` varchar(255) NOT NULL,
  `entertainment_options` varchar(255) NOT NULL,
  `photography_options` varchar(255) NOT NULL,
  `seating_arrangement` varchar(255) DEFAULT NULL,
  `sound_and_lighting` varchar(255) DEFAULT NULL,
  `special_requirements` text,
  `estimated_cost` decimal(10,2) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `event_type` varchar(255) DEFAULT NULL,
  `venue` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `event_customization_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `event_customization` */

/*Table structure for table `events` */

DROP TABLE IF EXISTS `events`;

CREATE TABLE `events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_type` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `price_range` varchar(100) NOT NULL,
  `available_venues` text NOT NULL,
  `service_providers` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;

/*Data for the table `events` */

insert  into `events`(`id`,`event_type`,`description`,`price_range`,`available_venues`,`service_providers`,`created_at`) values 
(3,'Dandiya','Dandiya Events & Parties 2025 in Hyderabad','7000','hyderabad','Ramu','2025-02-08 01:16:07'),
(5,'Marriage','asfd','7000','hyderabad','aravind','2025-02-19 19:29:34'),
(6,'Marriage','asfd','7000','hyderabad','aravind','2025-02-19 19:30:09'),
(7,'Marriage','asfd','7000','hyderabad','aravind','2025-02-19 19:30:28'),
(8,'Marriage','asfd','7000','hyderabad','aravind','2025-02-19 19:30:55');

/*Table structure for table `gallery` */

DROP TABLE IF EXISTS `gallery`;

CREATE TABLE `gallery` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `event_type` varchar(255) NOT NULL DEFAULT 'General',
  `venue` varchar(255) NOT NULL DEFAULT 'Unknown',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `gallery_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `gallery` */

insert  into `gallery`(`id`,`user_id`,`image_path`,`event_type`,`venue`,`created_at`) values 
(1,2,'YouSay_Dandiya-1.jpg','Dandiya','hyderabad','2025-02-08 01:09:14');

/*Table structure for table `payments` */

DROP TABLE IF EXISTS `payments`;

CREATE TABLE `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_method` enum('Credit/Debit Card','Net Banking','UPI/QR Code') NOT NULL DEFAULT 'Credit/Debit Card',
  `status` enum('Pending','Completed') NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;

/*Data for the table `payments` */

insert  into `payments`(`id`,`user_id`,`booking_id`,`amount`,`payment_method`,`status`,`created_at`) values 
(1,1,1,0.00,'Credit/Debit Card','Completed','2025-02-08 01:57:30'),
(2,1,2,0.00,'Credit/Debit Card','Completed','2025-02-08 02:03:45'),
(3,1,3,0.00,'Credit/Debit Card','Completed','2025-02-08 02:18:33'),
(4,1,4,0.00,'Credit/Debit Card','Completed','2025-02-19 23:02:20'),
(5,1,7,0.00,'Credit/Debit Card','Completed','2025-02-19 23:43:54'),
(6,1,9,0.00,'Credit/Debit Card','Completed','2025-02-20 00:27:29'),
(7,1,10,0.00,'Credit/Debit Card','Completed','2025-02-20 00:29:33');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `password` varchar(255) NOT NULL,
  `address` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

/*Data for the table `users` */

insert  into `users`(`id`,`name`,`email`,`phone`,`password`,`address`,`created_at`) values 
(1,'aravind','aravind@gmail.com','7678767898','aravind','ddd','2025-02-03 01:01:11'),
(2,'admin','admin@gmail.com','6789876545','admin','hyderabad','2025-02-03 22:31:13');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
