-- mysql>source db.sql
-- DROP语句慎用，第一次创建数据库的时候请取消注释
DROP DATABASE IF EXISTS news;
CREATE DATABASE news;
USE news;
DROP TABLE IF EXISTS `news_all`;
CREATE TABLE `news_all` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `day` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `site` varchar(255) NOT NULL,
  `keywords` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `url` varchar(255) NOT NULL,
  `article` text,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `urlUnique` (`url`) USING HASH,
  KEY `url` (`url`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=utf8 DELAY_KEY_WRITE=1;
