-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: apartment_db
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `apartmentapp_commonnotification`
--

DROP TABLE IF EXISTS `apartmentapp_commonnotification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_commonnotification` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `title` varchar(100) NOT NULL,
  `content` longtext NOT NULL,
  `delivery_method` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_commonnotification`
--

LOCK TABLES `apartmentapp_commonnotification` WRITE;
/*!40000 ALTER TABLE `apartmentapp_commonnotification` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_commonnotification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_fee`
--

DROP TABLE IF EXISTS `apartmentapp_fee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_fee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `name` varchar(50) NOT NULL,
  `unit_price` double NOT NULL,
  `unit` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_fee`
--

LOCK TABLES `apartmentapp_fee` WRITE;
/*!40000 ALTER TABLE `apartmentapp_fee` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_fee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_package`
--

DROP TABLE IF EXISTS `apartmentapp_package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_package` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `sender_name` varchar(50) NOT NULL,
  `recipient_name` varchar(50) NOT NULL,
  `status` varchar(20) NOT NULL,
  `pickup_time` datetime(6) DEFAULT NULL,
  `quantity_items` int NOT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `description` longtext NOT NULL,
  `package_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `apartmentapp_package_package_id_aa92ea45_fk_apartment` (`package_id`),
  CONSTRAINT `apartmentapp_package_package_id_aa92ea45_fk_apartment` FOREIGN KEY (`package_id`) REFERENCES `apartmentapp_storagelocker` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_package`
--

LOCK TABLES `apartmentapp_package` WRITE;
/*!40000 ALTER TABLE `apartmentapp_package` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_package` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_privatenotification`
--

DROP TABLE IF EXISTS `apartmentapp_privatenotification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_privatenotification` (
  `commonnotification_ptr_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`commonnotification_ptr_id`),
  KEY `apartmentapp_private_user_id_0c91ae61_fk_apartment` (`user_id`),
  CONSTRAINT `apartmentapp_private_commonnotification_p_5f41816e_fk_apartment` FOREIGN KEY (`commonnotification_ptr_id`) REFERENCES `apartmentapp_commonnotification` (`id`),
  CONSTRAINT `apartmentapp_private_user_id_0c91ae61_fk_apartment` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_privatenotification`
--

LOCK TABLES `apartmentapp_privatenotification` WRITE;
/*!40000 ALTER TABLE `apartmentapp_privatenotification` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_privatenotification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_reflection`
--

DROP TABLE IF EXISTS `apartmentapp_reflection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_reflection` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `title` varchar(100) NOT NULL,
  `content` longtext NOT NULL,
  `status` varchar(20) NOT NULL,
  `resolution` varchar(255) DEFAULT NULL,
  `resolved_date` datetime(6) DEFAULT NULL,
  `admin_resolved` varchar(255) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `apartmentapp_reflection_user_id_a0c914ba_fk_apartmentapp_user_id` (`user_id`),
  CONSTRAINT `apartmentapp_reflection_user_id_a0c914ba_fk_apartmentapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_reflection`
--

LOCK TABLES `apartmentapp_reflection` WRITE;
/*!40000 ALTER TABLE `apartmentapp_reflection` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_reflection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_room`
--

DROP TABLE IF EXISTS `apartmentapp_room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_room` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `room_number` varchar(20) NOT NULL,
  `area` double NOT NULL,
  `floor` int NOT NULL,
  `status` varchar(20) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `room_number` (`room_number`),
  KEY `apartmentapp_room_user_id_3e4ec9f9_fk_apartmentapp_user_id` (`user_id`),
  CONSTRAINT `apartmentapp_room_user_id_3e4ec9f9_fk_apartmentapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_room`
--

LOCK TABLES `apartmentapp_room` WRITE;
/*!40000 ALTER TABLE `apartmentapp_room` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_room` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_storagelocker`
--

DROP TABLE IF EXISTS `apartmentapp_storagelocker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_storagelocker` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `number` varchar(50) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `apartmentapp_storage_user_id_cdeaf635_fk_apartment` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_storagelocker`
--

LOCK TABLES `apartmentapp_storagelocker` WRITE;
/*!40000 ALTER TABLE `apartmentapp_storagelocker` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_storagelocker` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_transaction`
--

DROP TABLE IF EXISTS `apartmentapp_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_transaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `recipient_account_number` varchar(20) NOT NULL,
  `amount` double NOT NULL,
  `description` varchar(100) NOT NULL,
  `sender_account_number` varchar(100) NOT NULL,
  `payment_gateway` varchar(20) NOT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `apartmentapp_transac_user_id_dc9e6f7b_fk_apartment` (`user_id`),
  CONSTRAINT `apartmentapp_transac_user_id_dc9e6f7b_fk_apartment` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_transaction`
--

LOCK TABLES `apartmentapp_transaction` WRITE;
/*!40000 ALTER TABLE `apartmentapp_transaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_transactionfee`
--

DROP TABLE IF EXISTS `apartmentapp_transactionfee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_transactionfee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `note` varchar(100) NOT NULL,
  `unit_price` double NOT NULL,
  `quantity` int NOT NULL,
  `fee_id` bigint NOT NULL,
  `transaction_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `apartmentapp_transactionfee_fee_id_transaction_id_072641f4_uniq` (`fee_id`,`transaction_id`),
  KEY `apartmentapp_transac_transaction_id_a6187c8b_fk_apartment` (`transaction_id`),
  CONSTRAINT `apartmentapp_transac_fee_id_e212f6c7_fk_apartment` FOREIGN KEY (`fee_id`) REFERENCES `apartmentapp_fee` (`id`),
  CONSTRAINT `apartmentapp_transac_transaction_id_a6187c8b_fk_apartment` FOREIGN KEY (`transaction_id`) REFERENCES `apartmentapp_transaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_transactionfee`
--

LOCK TABLES `apartmentapp_transactionfee` WRITE;
/*!40000 ALTER TABLE `apartmentapp_transactionfee` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_transactionfee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_user`
--

DROP TABLE IF EXISTS `apartmentapp_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `date_of_birth` datetime(6) DEFAULT NULL,
  `gender` tinyint(1) NOT NULL,
  `citizen_card` varchar(15) NOT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `changed_password` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `citizen_card` (`citizen_card`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_user`
--

LOCK TABLES `apartmentapp_user` WRITE;
/*!40000 ALTER TABLE `apartmentapp_user` DISABLE KEYS */;
INSERT INTO `apartmentapp_user` VALUES (1,'pbkdf2_sha256$600000$BByaOS2BTlmJscFJa6Hr5c$dEhBwQb+d8RzIiqDYhWEbRzsJJb4txiJ4LeTXRNn/jA=','2025-01-01 09:19:10.576054',1,'admin','','','',1,1,'2025-01-01 06:57:05.958034','Adminstrators','0111111111',NULL,1,'','https://res.cloudinary.com/dea1l3vvu/image/upload/v1735723302/czy9uxxyf2iw1bevzlaf.png',1);
/*!40000 ALTER TABLE `apartmentapp_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_user_groups`
--

DROP TABLE IF EXISTS `apartmentapp_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `apartmentapp_user_groups_user_id_group_id_504566f7_uniq` (`user_id`,`group_id`),
  KEY `apartmentapp_user_groups_group_id_6d16da7e_fk_auth_group_id` (`group_id`),
  CONSTRAINT `apartmentapp_user_gr_user_id_8b34ea58_fk_apartment` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`),
  CONSTRAINT `apartmentapp_user_groups_group_id_6d16da7e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_user_groups`
--

LOCK TABLES `apartmentapp_user_groups` WRITE;
/*!40000 ALTER TABLE `apartmentapp_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_user_user_permissions`
--

DROP TABLE IF EXISTS `apartmentapp_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `apartmentapp_user_user_p_user_id_permission_id_75250ad3_uniq` (`user_id`,`permission_id`),
  KEY `apartmentapp_user_us_permission_id_b080c6d2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `apartmentapp_user_us_permission_id_b080c6d2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `apartmentapp_user_us_user_id_dccccd32_fk_apartment` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_user_user_permissions`
--

LOCK TABLES `apartmentapp_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `apartmentapp_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `apartmentapp_vehiclecard`
--

DROP TABLE IF EXISTS `apartmentapp_vehiclecard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartmentapp_vehiclecard` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created_date` datetime(6) NOT NULL,
  `updated_date` datetime(6) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `expiration_date` datetime(6) NOT NULL,
  `vehicle_number` varchar(20) NOT NULL,
  `relationship` varchar(30) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vehicle_number` (`vehicle_number`),
  KEY `apartmentapp_vehicle_user_id_aba2fa9f_fk_apartment` (`user_id`),
  CONSTRAINT `apartmentapp_vehicle_user_id_aba2fa9f_fk_apartment` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartmentapp_vehiclecard`
--

LOCK TABLES `apartmentapp_vehiclecard` WRITE;
/*!40000 ALTER TABLE `apartmentapp_vehiclecard` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartmentapp_vehiclecard` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_user'),(22,'Can change user',6,'change_user'),(23,'Can delete user',6,'delete_user'),(24,'Can view user',6,'view_user'),(25,'Can add common notification',7,'add_commonnotification'),(26,'Can change common notification',7,'change_commonnotification'),(27,'Can delete common notification',7,'delete_commonnotification'),(28,'Can view common notification',7,'view_commonnotification'),(29,'Can add fee',8,'add_fee'),(30,'Can change fee',8,'change_fee'),(31,'Can delete fee',8,'delete_fee'),(32,'Can view fee',8,'view_fee'),(33,'Can add transaction',9,'add_transaction'),(34,'Can change transaction',9,'change_transaction'),(35,'Can delete transaction',9,'delete_transaction'),(36,'Can view transaction',9,'view_transaction'),(37,'Can add vehicle card',10,'add_vehiclecard'),(38,'Can change vehicle card',10,'change_vehiclecard'),(39,'Can delete vehicle card',10,'delete_vehiclecard'),(40,'Can view vehicle card',10,'view_vehiclecard'),(41,'Can add transaction fee',11,'add_transactionfee'),(42,'Can change transaction fee',11,'change_transactionfee'),(43,'Can delete transaction fee',11,'delete_transactionfee'),(44,'Can view transaction fee',11,'view_transactionfee'),(45,'Can add storage locker',12,'add_storagelocker'),(46,'Can change storage locker',12,'change_storagelocker'),(47,'Can delete storage locker',12,'delete_storagelocker'),(48,'Can view storage locker',12,'view_storagelocker'),(49,'Can add room',13,'add_room'),(50,'Can change room',13,'change_room'),(51,'Can delete room',13,'delete_room'),(52,'Can view room',13,'view_room'),(53,'Can add reflection',14,'add_reflection'),(54,'Can change reflection',14,'change_reflection'),(55,'Can delete reflection',14,'delete_reflection'),(56,'Can view reflection',14,'view_reflection'),(57,'Can add package',15,'add_package'),(58,'Can change package',15,'change_package'),(59,'Can delete package',15,'delete_package'),(60,'Can view package',15,'view_package'),(61,'Can add private notification',16,'add_privatenotification'),(62,'Can change private notification',16,'change_privatenotification'),(63,'Can delete private notification',16,'delete_privatenotification'),(64,'Can view private notification',16,'view_privatenotification');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_apartmentapp_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_apartmentapp_user_id` FOREIGN KEY (`user_id`) REFERENCES `apartmentapp_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(7,'apartmentapp','commonnotification'),(8,'apartmentapp','fee'),(15,'apartmentapp','package'),(16,'apartmentapp','privatenotification'),(14,'apartmentapp','reflection'),(13,'apartmentapp','room'),(12,'apartmentapp','storagelocker'),(9,'apartmentapp','transaction'),(11,'apartmentapp','transactionfee'),(6,'apartmentapp','user'),(10,'apartmentapp','vehiclecard'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-01-01 06:56:26.266408'),(2,'contenttypes','0002_remove_content_type_name','2025-01-01 06:56:26.323490'),(3,'auth','0001_initial','2025-01-01 06:56:26.605692'),(4,'auth','0002_alter_permission_name_max_length','2025-01-01 06:56:26.655974'),(5,'auth','0003_alter_user_email_max_length','2025-01-01 06:56:26.662828'),(6,'auth','0004_alter_user_username_opts','2025-01-01 06:56:26.668827'),(7,'auth','0005_alter_user_last_login_null','2025-01-01 06:56:26.674782'),(8,'auth','0006_require_contenttypes_0002','2025-01-01 06:56:26.679786'),(9,'auth','0007_alter_validators_add_error_messages','2025-01-01 06:56:26.687278'),(10,'auth','0008_alter_user_username_max_length','2025-01-01 06:56:26.693366'),(11,'auth','0009_alter_user_last_name_max_length','2025-01-01 06:56:26.700801'),(12,'auth','0010_alter_group_name_max_length','2025-01-01 06:56:26.716111'),(13,'auth','0011_update_proxy_permissions','2025-01-01 06:56:26.723726'),(14,'auth','0012_alter_user_first_name_max_length','2025-01-01 06:56:26.743558'),(15,'apartmentapp','0001_initial','2025-01-01 06:56:28.060334'),(16,'admin','0001_initial','2025-01-01 06:56:28.209099'),(17,'admin','0002_logentry_remove_auto_add','2025-01-01 06:56:28.226484'),(18,'admin','0003_logentry_add_action_flag_choices','2025-01-01 06:56:28.240657'),(19,'sessions','0001_initial','2025-01-01 06:56:28.282885'),(20,'apartmentapp','0002_alter_user_thumbnail','2025-01-01 07:52:15.137473'),(21,'apartmentapp','0003_alter_package_thumbnail_alter_transaction_thumbnail','2025-01-01 07:53:27.045591');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('vxceqbudq5juzt8tv80yzzv2cwup833k','.eJxVjEEOwiAQRe_C2hCmMG1x6b5nIDMD2KqhSWlXxrsbki50-997_60CHfscjpq2sER1VaAuvxuTPFNpID6o3Fcta9m3hXVT9EmrntaYXrfT_TuYqc6tzhjJo2MYhjhmwNQZsD1JhwKWLfsexXTMCcVDdEwGTPYkCI5HHNXnC-pjN-o:1tSusg:lGrM5rOmnnFaw8-CyJUzZ5fnCyuhzP3cwE9NrPhWFTs','2025-01-15 09:19:10.580049');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-01 16:35:11
