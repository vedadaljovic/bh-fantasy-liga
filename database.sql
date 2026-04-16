-- MySQL dump 10.13  Distrib 8.0.38, for macos14 (arm64)
--
-- Host: 127.0.0.1    Database: bh_fantasy_liga
-- ------------------------------------------------------
-- Server version	8.4.6

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
-- Table structure for table `fantasy_team_gameweek`
--

DROP TABLE IF EXISTS `fantasy_team_gameweek`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasy_team_gameweek` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fantasy_team_id` int NOT NULL,
  `gameweek_id` int NOT NULL,
  `points` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fantasy_team_id` (`fantasy_team_id`),
  KEY `gameweek_id` (`gameweek_id`),
  CONSTRAINT `fantasy_team_gameweek_ibfk_1` FOREIGN KEY (`fantasy_team_id`) REFERENCES `fantasy_teams` (`id`),
  CONSTRAINT `fantasy_team_gameweek_ibfk_2` FOREIGN KEY (`gameweek_id`) REFERENCES `gameweeks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fantasy_team_gameweek`
--

LOCK TABLES `fantasy_team_gameweek` WRITE;
/*!40000 ALTER TABLE `fantasy_team_gameweek` DISABLE KEYS */;
/*!40000 ALTER TABLE `fantasy_team_gameweek` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fantasy_team_players`
--

DROP TABLE IF EXISTS `fantasy_team_players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasy_team_players` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fantasy_team_id` int NOT NULL,
  `player_id` int NOT NULL,
  `is_starting` tinyint(1) DEFAULT '1',
  `is_captain` tinyint(1) DEFAULT '0',
  `is_vice_captain` tinyint(1) DEFAULT '0',
  `bench_order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fantasy_team_id` (`fantasy_team_id`),
  KEY `player_id` (`player_id`),
  CONSTRAINT `fantasy_team_players_ibfk_1` FOREIGN KEY (`fantasy_team_id`) REFERENCES `fantasy_teams` (`id`),
  CONSTRAINT `fantasy_team_players_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fantasy_team_players`
--

LOCK TABLES `fantasy_team_players` WRITE;
/*!40000 ALTER TABLE `fantasy_team_players` DISABLE KEYS */;
/*!40000 ALTER TABLE `fantasy_team_players` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fantasy_teams`
--

DROP TABLE IF EXISTS `fantasy_teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasy_teams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `team_name` varchar(100) NOT NULL,
  `total_points` int DEFAULT '0',
  `gameweek_points` int DEFAULT '0',
  `budget_remaining` decimal(5,1) DEFAULT '100.0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fantasy_teams_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fantasy_teams`
--

LOCK TABLES `fantasy_teams` WRITE;
/*!40000 ALTER TABLE `fantasy_teams` DISABLE KEYS */;
/*!40000 ALTER TABLE `fantasy_teams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fixtures`
--

DROP TABLE IF EXISTS `fixtures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fixtures` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gameweek_id` int NOT NULL,
  `home_team_id` int NOT NULL,
  `away_team_id` int NOT NULL,
  `home_score` int DEFAULT NULL,
  `away_score` int DEFAULT NULL,
  `is_finished` tinyint(1) DEFAULT '0',
  `match_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `gameweek_id` (`gameweek_id`),
  KEY `home_team_id` (`home_team_id`),
  KEY `away_team_id` (`away_team_id`),
  CONSTRAINT `fixtures_ibfk_1` FOREIGN KEY (`gameweek_id`) REFERENCES `gameweeks` (`id`),
  CONSTRAINT `fixtures_ibfk_2` FOREIGN KEY (`home_team_id`) REFERENCES `teams` (`id`),
  CONSTRAINT `fixtures_ibfk_3` FOREIGN KEY (`away_team_id`) REFERENCES `teams` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fixtures`
--

LOCK TABLES `fixtures` WRITE;
/*!40000 ALTER TABLE `fixtures` DISABLE KEYS */;
/*!40000 ALTER TABLE `fixtures` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gameweeks`
--

DROP TABLE IF EXISTS `gameweeks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gameweeks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `deadline` datetime NOT NULL,
  `is_active` tinyint(1) DEFAULT '0',
  `is_finished` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gameweeks`
--

LOCK TABLES `gameweeks` WRITE;
/*!40000 ALTER TABLE `gameweeks` DISABLE KEYS */;
/*!40000 ALTER TABLE `gameweeks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `news` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `news_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `news`
--

LOCK TABLES `news` WRITE;
/*!40000 ALTER TABLE `news` DISABLE KEYS */;
/*!40000 ALTER TABLE `news` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_gameweek_stats`
--

DROP TABLE IF EXISTS `player_gameweek_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_gameweek_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `player_id` int NOT NULL,
  `gameweek_id` int NOT NULL,
  `fixture_id` int NOT NULL,
  `minutes_played` int DEFAULT '0',
  `goals` int DEFAULT '0',
  `assists` int DEFAULT '0',
  `clean_sheet` tinyint(1) DEFAULT '0',
  `yellow_cards` int DEFAULT '0',
  `red_cards` int DEFAULT '0',
  `saves` int DEFAULT '0',
  `bonus_points` int DEFAULT '0',
  `points_scored` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `player_id` (`player_id`),
  KEY `gameweek_id` (`gameweek_id`),
  KEY `fixture_id` (`fixture_id`),
  CONSTRAINT `player_gameweek_stats_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`),
  CONSTRAINT `player_gameweek_stats_ibfk_2` FOREIGN KEY (`gameweek_id`) REFERENCES `gameweeks` (`id`),
  CONSTRAINT `player_gameweek_stats_ibfk_3` FOREIGN KEY (`fixture_id`) REFERENCES `fixtures` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_gameweek_stats`
--

LOCK TABLES `player_gameweek_stats` WRITE;
/*!40000 ALTER TABLE `player_gameweek_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `player_gameweek_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `players` (
  `id` int NOT NULL AUTO_INCREMENT,
  `team_id` int NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `position` enum('GK','DEF','MID','FWD') NOT NULL,
  `price` decimal(4,1) NOT NULL,
  `total_points` int DEFAULT '0',
  `photo_url` varchar(255) DEFAULT NULL,
  `is_available` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `team_id` (`team_id`),
  CONSTRAINT `players_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=285 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `players`
--

LOCK TABLES `players` WRITE;
/*!40000 ALTER TABLE `players` DISABLE KEYS */;
INSERT INTO `players` VALUES (1,1,'Srđan','Modić','GK',5.0,0,NULL,1,'2026-04-12 15:15:24'),(2,1,'Mladen','Jurkas','GK',5.0,0,NULL,1,'2026-04-12 15:15:24'),(3,1,'Damjan','Šiškovski','GK',5.0,0,NULL,1,'2026-04-12 15:15:24'),(4,1,'Nemanja','Jakšić','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(5,1,'Abel','Paskual','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(6,1,'Dušan','Vrbić','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(7,1,'Domagoj','Čulina','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(8,1,'Jurih','Karolina','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(9,1,'Viktor','Rogan','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(10,1,'Zoran','Kvržić','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(11,1,'Sebastian','Herera','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(12,1,'Siniša','Saničanin','DEF',5.0,0,NULL,1,'2026-04-12 15:15:24'),(13,1,'Omar','Sijarić','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(14,1,'Dino','Skorup','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(15,1,'Ognjen','Radošević','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(16,1,'David','Čavić','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(17,1,'Damir','Hrelja','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(18,1,'Srđan','Grahovac','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(19,1,'Stojan','Vranješ','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(20,1,'Sandi','Ogrinec','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(21,1,'Amer','Hiroš','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(22,1,'Stefan','Savić','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(23,1,'Miloš','Jojić','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(24,1,'David','Vuković','MID',5.0,0,NULL,1,'2026-04-12 15:15:24'),(25,1,'Pavle','Đajić','FWD',5.0,0,NULL,1,'2026-04-12 15:15:24'),(26,1,'Karlo','Perić','FWD',5.0,0,NULL,1,'2026-04-12 15:15:24'),(27,1,'Matej','Deket','FWD',5.0,0,NULL,1,'2026-04-12 15:15:24'),(28,1,'Luka','Juričić','FWD',5.0,0,NULL,1,'2026-04-12 15:15:24'),(29,2,'Antonio','Soldo','GK',5.0,0,NULL,1,'2026-04-12 15:26:06'),(30,2,'Zvonimir','Šubarić','GK',5.0,0,NULL,1,'2026-04-12 15:26:06'),(31,2,'Patrik','Kovač','GK',5.0,0,NULL,1,'2026-04-12 15:26:06'),(32,2,'Tarik','Kapetanović','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(33,2,'Dejan','Kerkez','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(34,2,'Josip','Bešlić','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(35,2,'Mate','Lasić','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(36,2,'Ivan','Novoselec','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(37,2,'Filip','Milović','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(38,2,'Valentino','Majstorović','DEF',5.0,0,NULL,1,'2026-04-12 15:26:06'),(39,2,'Mateo','Andačić','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(40,2,'Mario','Čuić','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(41,2,'Danijel','Širić','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(42,2,'Marko','Domančić','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(43,2,'Ivan','Posavec','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(44,2,'Zvonimir','Begić','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(45,2,'Marko','Hanuljak','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(46,2,'Ivan','Kukavica','MID',5.0,0,NULL,1,'2026-04-12 15:26:06'),(47,2,'Branko','Ćurdo','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(48,2,'Leon','Kreković','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(49,2,'Ante','Živković','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(50,2,'Vinko','Petković','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(51,2,'David','Čamber','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(52,2,'Borna','Filipović','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(53,2,'Denis','Bušnja','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(54,2,'Ante','Rozić','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(55,2,'José','Mulato','FWD',5.0,0,NULL,1,'2026-04-12 15:26:06'),(56,3,'Dušan','Marković','GK',5.0,0,NULL,1,'2026-04-12 15:49:25'),(57,3,'Elvir','Trako','GK',5.0,0,NULL,1,'2026-04-12 15:49:25'),(58,3,'Bartul','Markovina','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(59,3,'Blondon','Meyapya','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(60,3,'Nikola','Đurić','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(61,3,'Đorđe','Ćosić','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(62,3,'Slaviša','Radović','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(63,3,'Marko','Čubrilo','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(64,3,'Andrija','Marković','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(65,3,'Božidar','Dimitrić','DEF',5.0,0,NULL,1,'2026-04-12 15:49:25'),(66,3,'Felix','Agyemang','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(67,3,'Huso','Karjašević','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(68,3,'Emanuel','Črnko','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(69,3,'Tino Blaž','Lauš','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(70,3,'Aldin','Hrvanović','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(71,3,'Ateef','Konate','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(72,3,'Ivan','Nikolov','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(73,3,'Andrej','Krstić','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(74,3,'Mohamed','Ghorzi','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(75,3,'Sami','Faraj','MID',5.0,0,NULL,1,'2026-04-12 15:49:25'),(76,3,'Njegoš','Kupusović','FWD',5.0,0,NULL,1,'2026-04-12 15:49:25'),(77,3,'Ognjen','Klenpić','FWD',5.0,0,NULL,1,'2026-04-12 15:49:25'),(78,3,'Danilo','Teodorović','FWD',5.0,0,NULL,1,'2026-04-12 15:49:25'),(79,3,'Anthony','Ijoma','FWD',5.0,0,NULL,1,'2026-04-12 15:49:25'),(80,4,'Mišo','Dubljanić','GK',5.0,0,NULL,1,'2026-04-12 15:59:52'),(81,4,'Vasilije','Zunić','GK',5.0,0,NULL,1,'2026-04-12 15:59:52'),(82,4,'Camilo','Puentes','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(83,4,'Muharem','Trako','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(84,4,'Fabrizio','Danese','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(85,4,'Nemanja','Pekija','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(86,4,'Roberto','Corral','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(87,4,'Álvaro','Roncal','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(88,4,'Viktor','Grbić','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(89,4,'Đuro Giulio','Đekić','DEF',5.0,0,NULL,1,'2026-04-12 15:59:52'),(90,4,'Tarik','Ramić','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(91,4,'Andrés','Mohedano','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(92,4,'Dani','Molina','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(93,4,'Marcel','Ritzmaier','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(94,4,'Fernán','Ferreiroá','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(95,4,'Nedim','Keranović','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(96,4,'Marko','Šebez','MID',5.0,0,NULL,1,'2026-04-12 15:59:52'),(97,4,'Jorge','Bolivar','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(98,4,'Demetre','Gvasalia','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(99,4,'Jordan','Gutiérrez','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(100,4,'Stefan','Marčetić','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(101,4,'Dani','Romera','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(102,4,'Aleksa','Mrđa','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(103,4,'Max','Galić','FWD',5.0,0,NULL,1,'2026-04-12 15:59:52'),(104,5,'Sanin','Mušija','GK',5.0,0,NULL,1,'2026-04-12 16:07:33'),(105,5,'Ivan','Banić','GK',5.0,0,NULL,1,'2026-04-12 16:07:33'),(106,5,'Faris','Mehić','GK',5.0,0,NULL,1,'2026-04-12 16:07:33'),(107,5,'Shane','Maroodza','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(108,5,'Renato','Gojković','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(109,5,'Nermin','Mujkić','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(110,5,'Luka','Hujber','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(111,5,'Amar','Beganović','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(112,5,'Daris','Dizdarević','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(113,5,'Slavko','Bralić','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(114,5,'Stefan','Ristovski','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(115,5,'Mihael','Kuprešak','DEF',5.0,0,NULL,1,'2026-04-12 16:07:33'),(116,5,'Rijad','Telalović','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(117,5,'Francis','Kyeremeh','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(118,5,'Agon','Elezi','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(119,5,'Anes','Krdžalić','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(120,5,'Muamer','Hamzić','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(121,5,'Sergej','Ignatkov','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(122,5,'Kenan','Vrban','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(123,5,'Gojko','Cimirot','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(124,5,'Rafail','Mamas','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(125,5,'Adem','Ljajić','MID',5.0,0,NULL,1,'2026-04-12 16:07:33'),(126,5,'Aldin','Turkeš','FWD',5.0,0,NULL,1,'2026-04-12 16:07:33'),(127,5,'Renan','Oliviera','FWD',5.0,0,NULL,1,'2026-04-12 16:07:33'),(128,6,'Filip','Erić','GK',5.0,0,NULL,1,'2026-04-12 16:21:26'),(129,6,'Bojan','Pavlović','GK',5.0,0,NULL,1,'2026-04-12 16:21:26'),(130,6,'Boris','Varga','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(131,6,'Bojan','Batar','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(132,6,'Niko','Božičković','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(133,6,'Milan','Milanović','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(134,6,'Minja','Tatić','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(135,6,'Bojan','Letić','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(136,6,'Nikola','Žerjal','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(137,6,'Josip','Kvesić','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(138,6,'Haris','Ovčina','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(139,6,'Vasilije','Perković','DEF',5.0,0,NULL,1,'2026-04-12 16:21:26'),(140,6,'Albin','Omić','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(141,6,'Marko','Đira','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(142,6,'Dino','Hasanović','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(143,6,'Darko','Savić','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(144,6,'Ajdin','Redžić','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(145,6,'Fedor','Predragović','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(146,6,'Latar','Zilčić','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(147,6,'Eldar','Mehmedović','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(148,6,'Sergej','Damjanić','MID',5.0,0,NULL,1,'2026-04-12 16:21:26'),(149,6,'Benjamin','Tatar','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(150,6,'Ognjen','Šešlak','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(151,6,'Alen','Dejanović','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(152,6,'Toni','Jović','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(153,6,'Edvin','Suljanović','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(154,6,'Milan','Savić','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(155,6,'Mladen','Veselinović','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(156,6,'Nikola','Mandić','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(157,6,'Dejan','Vidić','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(158,6,'Petar','Kunić','FWD',5.0,0,NULL,1,'2026-04-12 16:21:26'),(159,7,'Ante','Slišković','GK',5.0,0,NULL,1,'2026-04-12 16:31:10'),(160,7,'Renato','Josipović','GK',5.0,0,NULL,1,'2026-04-12 16:31:10'),(161,7,'Ivan','Puljić','GK',5.0,0,NULL,1,'2026-04-12 16:31:10'),(162,7,'Ivan','Pranjić','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(163,7,'Mateo','Soldo','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(164,7,'Božo','Prusina','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(165,7,'Matej','Senić','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(166,7,'Marko','Šuto','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(167,7,'Ante','Gagula','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(168,7,'Mateo','Bašić','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(169,7,'Božo','Musa','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(170,7,'Luka','Perko','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(171,7,'Matej','Hrkać','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(172,7,'Ivan','Kraljević','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(173,7,'Ivan','Jelić','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(174,7,'Nediljko','Stjepanović','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(175,7,'Patrick','Stanić','DEF',5.0,0,NULL,1,'2026-04-12 16:31:10'),(176,7,'Antoni','Bajkuša','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(177,7,'Damir','Zlomislić','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(178,7,'Filip','Matić','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(179,7,'Mato','Stanić','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(180,7,'Marko','Matić','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(181,7,'Filip','Jelčić','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(182,7,'Ilya','Chernyak','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(183,7,'Márcio Rodrigues','Velasco','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(184,7,'Petar','Petriško','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(185,7,'Tomislav','Tomić','MID',5.0,0,NULL,1,'2026-04-12 16:31:10'),(186,7,'Ivano','Srdoč','FWD',5.0,0,NULL,1,'2026-04-12 16:31:10'),(187,7,'Saydou','Bangura','FWD',5.0,0,NULL,1,'2026-04-12 16:31:10'),(188,7,'Ilija','Bagarić','FWD',5.0,0,NULL,1,'2026-04-12 16:31:10'),(189,7,'Kristian','Sesar','FWD',5.0,0,NULL,1,'2026-04-12 16:31:10'),(190,7,'Hubert','Sobol','FWD',5.0,0,NULL,1,'2026-04-12 16:31:10'),(191,7,'Mihael','Klepač','FWD',5.0,0,NULL,1,'2026-04-12 16:31:10'),(192,8,'Tarik','Karić','GK',5.0,0,NULL,1,'2026-04-12 16:45:20'),(193,8,'Faris','Ribić','GK',5.0,0,NULL,1,'2026-04-12 16:45:20'),(194,8,'Besim','Šerbečić','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(195,8,'Ante','Hrkać','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(196,8,'Adin','Bajrić','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(197,8,'Arman Nur','Turković','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(198,8,'Selmir','Pidro','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(199,8,'Klemen','Sturm','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(200,8,'Ajdin','Nukić','DEF',5.0,0,NULL,1,'2026-04-12 16:45:20'),(201,8,'Andro','Babić','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(202,8,'Rafidine','Abdullah','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(203,8,'Ayham','Shhade','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(204,8,'Demir','Halilović','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(205,8,'Vasilije','Đurić','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(206,8,'Dani','Salčin','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(207,8,'Edo','Vehabović','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(208,8,'Dženan','Puce','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(209,8,'Nino','Stojanović','MID',5.0,0,NULL,1,'2026-04-12 16:45:20'),(210,8,'Aldin','Mešić','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(211,8,'Ivan','Šarić','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(212,8,'Amar','Milak','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(213,8,'Said','Duranović','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(214,8,'Mićo','Kuzmanović','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(215,8,'Leonid','Ignatov','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(216,8,'Dominik','Dogan','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(217,8,'Armin','Spahić','FWD',5.0,0,NULL,1,'2026-04-12 16:45:20'),(218,9,'Goran','Karačić','GK',5.0,0,NULL,1,'2026-04-12 16:55:23'),(219,9,'Marin','Ljubić','GK',5.0,0,NULL,1,'2026-04-12 16:55:23'),(220,9,'Tin','Sajko','GK',5.0,0,NULL,1,'2026-04-12 16:55:23'),(221,9,'Duje','Dujmović','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(222,9,'Darick Kobie','Morris','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(223,9,'Hrvoje','Barišić','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(224,9,'David','Karačić','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(225,9,'Slobodan','Jakovljević','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(226,9,'Petar','Mamić','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(227,9,'Toma','Palić','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(228,9,'Marko','Vranjković','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(229,9,'Kerim','Memija','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(230,9,'Mateo','Sušić','DEF',5.0,0,NULL,1,'2026-04-12 16:55:23'),(231,9,'Igor','Savić','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(232,9,'Stefano','Surdanović','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(233,9,'Dan','Lagumdžija','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(234,9,'Neven','Đurasek','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(235,9,'Marijan','Čavar','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(236,9,'Antonio','Ivančić','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(237,9,'Adi','Nalić','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(238,9,'Antonio','Ilić','MID',5.0,0,NULL,1,'2026-04-12 16:55:23'),(239,9,'Mario','Ćuže','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(240,9,'Karlo','Abramović','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(241,9,'Leo','Mikić','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(242,9,'Matej','Šakota','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(243,9,'Tomislav','Kiš','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(244,9,'Toni','Majić','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(245,9,'Nemanja','Bilbija','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(246,9,'Milan','Šikanjić','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(247,9,'Tomi','Jurić','FWD',5.0,0,NULL,1,'2026-04-12 16:55:23'),(248,10,'Tarik','Abdulahović','GK',5.0,0,NULL,1,'2026-04-12 17:15:28'),(249,10,'Alvin','Ćosić','GK',5.0,0,NULL,1,'2026-04-12 17:15:28'),(250,10,'Vedad','Muftić','GK',5.0,0,NULL,1,'2026-04-12 17:15:28'),(251,10,'Edwin','Odinaka','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(252,10,'Enes','Alić','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(253,10,'Ermin','Bičakčić','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(254,10,'Bojan','Nastić','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(255,10,'Mustafa','Šukilović','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(256,10,'Giovanni','Troupee','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(257,10,'Patrik-Gabriel','Galchev','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(258,10,'Collin','Seedorf','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(259,10,'Amar','Zahirović','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(260,10,'Daris','Kelemendi','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(261,10,'Edin','Osmanović','DEF',5.0,0,NULL,1,'2026-04-12 17:15:28'),(262,10,'Afan','Fočop','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(263,10,'Aleksa','Pejić','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(264,10,'Dominik','Prokop','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(265,10,'Madžid','Šošić','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(266,10,'Vini','Peixoto','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(267,10,'Matej','Cvetanoski','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(268,10,'Dženan','Šabić','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(269,10,'Ibraheem','Adams Olanrewaju','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(270,10,'Joao','Erick','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(271,10,'Admir','Gojak','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(272,10,'Deni','Milošević','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(273,10,'Ismail','Oulad M\'Hand','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(274,10,'Armin','Hodžić','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(275,10,'Aldian','Korora','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(276,10,'Eldar','Dragović','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(277,10,'Jonathan','Freeman','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(278,10,'Samir','Radovac','MID',5.0,0,NULL,1,'2026-04-12 17:15:28'),(279,10,'Sulejman','Krpić','FWD',5.0,0,NULL,1,'2026-04-12 17:15:28'),(280,10,'Hamza','Jaganjac','FWD',5.0,0,NULL,1,'2026-04-12 17:15:28'),(281,10,'Joey','Konings','FWD',5.0,0,NULL,1,'2026-04-12 17:15:28'),(282,10,'Muharem','Husković','FWD',5.0,0,NULL,1,'2026-04-12 17:15:28'),(283,10,'Santiago','Garcia','FWD',5.0,0,NULL,1,'2026-04-12 17:15:28'),(284,10,'Davor','Rakić','FWD',5.0,0,NULL,1,'2026-04-12 17:15:28');
/*!40000 ALTER TABLE `players` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `short_name` varchar(10) NOT NULL,
  `logo_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teams`
--

LOCK TABLES `teams` WRITE;
/*!40000 ALTER TABLE `teams` DISABLE KEYS */;
INSERT INTO `teams` VALUES (1,'FK Borac','BOR',NULL,'2026-04-12 14:57:51'),(2,'HŠK Posušje','POS',NULL,'2026-04-12 14:57:51'),(3,'FK Radnik','RAD',NULL,'2026-04-12 14:57:51'),(4,'FK Rudar Prijedor','RUD',NULL,'2026-04-12 14:57:51'),(5,'FK Sarajevo','SAR',NULL,'2026-04-12 14:57:51'),(6,'FK Sloga Doboj','SLO',NULL,'2026-04-12 14:57:51'),(7,'NK Široki Brijeg','ŠRI',NULL,'2026-04-12 14:57:51'),(8,'FK Velež','VEL',NULL,'2026-04-12 14:57:51'),(9,'HŠK Zrinjski','ZRI',NULL,'2026-04-12 14:57:51'),(10,'FK Željezničar','ŽEL',NULL,'2026-04-12 14:57:51');
/*!40000 ALTER TABLE `teams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transfers`
--

DROP TABLE IF EXISTS `transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transfers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fantasy_team_id` int NOT NULL,
  `gameweek_id` int NOT NULL,
  `player_out_id` int NOT NULL,
  `player_in_id` int NOT NULL,
  `transferred_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fantasy_team_id` (`fantasy_team_id`),
  KEY `gameweek_id` (`gameweek_id`),
  KEY `player_out_id` (`player_out_id`),
  KEY `player_in_id` (`player_in_id`),
  CONSTRAINT `transfers_ibfk_1` FOREIGN KEY (`fantasy_team_id`) REFERENCES `fantasy_teams` (`id`),
  CONSTRAINT `transfers_ibfk_2` FOREIGN KEY (`gameweek_id`) REFERENCES `gameweeks` (`id`),
  CONSTRAINT `transfers_ibfk_3` FOREIGN KEY (`player_out_id`) REFERENCES `players` (`id`),
  CONSTRAINT `transfers_ibfk_4` FOREIGN KEY (`player_in_id`) REFERENCES `players` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transfers`
--

LOCK TABLES `transfers` WRITE;
/*!40000 ALTER TABLE `transfers` DISABLE KEYS */;
/*!40000 ALTER TABLE `transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('user','admin') DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-12 19:21:29
