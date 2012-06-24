-- phpMyAdmin SQL Dump
-- version 2.11.8.1deb5+lenny9
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 24, 2012 at 11:08 PM
-- Server version: 5.0.51
-- PHP Version: 5.2.6-1+lenny16

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `otjobs`
--

-- --------------------------------------------------------

--
-- Table structure for table `band5Summary`
--

CREATE TABLE IF NOT EXISTS `band5Summary` (
  `id` int(11) unsigned NOT NULL auto_increment,
  `pDate` datetime default NULL,
  `tstamp` int(11) default NULL,
  `number` int(11) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1449 ;

-- --------------------------------------------------------

--
-- Table structure for table `otjobs`
--

CREATE TABLE IF NOT EXISTS `otjobs` (
  `tstamp` int(11) NOT NULL default '0',
  `pDate` datetime default NULL,
  `uname` text character set latin1 NOT NULL,
  `title` text character set latin1 NOT NULL,
  `band` text character set latin1,
  `location` text character set latin1 NOT NULL,
  `salary` text character set latin1 NOT NULL,
  `salary_lower` int(11) default NULL,
  `salary_higher` int(11) default NULL,
  `pro_rata` int(11) default NULL,
  `stDate` text character set latin1 NOT NULL,
  `duration` text character set latin1 NOT NULL,
  `descr` text character set latin1 NOT NULL,
  `lat` text character set latin1 NOT NULL,
  `lon` text character set latin1 NOT NULL,
  `city` text character set latin1 NOT NULL,
  `status` varchar(4) character set latin1 default NULL,
  `url` varchar(255) collate utf8_unicode_ci default NULL,
  `repostedcnt` int(11) default '0',
  `uniqurlid` int(11) default NULL,
  `fixedband` int(11) default NULL,
  `source` varchar(11) collate utf8_unicode_ci default NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `otjobssummary`
--

CREATE TABLE IF NOT EXISTS `otjobssummary` (
  `id` int(11) unsigned NOT NULL auto_increment,
  `tstamp` int(11) default NULL,
  `number` int(11) default NULL,
  `numberTemp` int(11) default NULL,
  `numberPerm` int(11) default NULL,
  `numberbandf` int(11) default NULL,
  `numberbands` int(11) default NULL,
  `numberbandse` int(11) default NULL,
  `numberbande` int(11) default NULL,
  `pDate` datetime default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1449 ;

-- --------------------------------------------------------

--
-- Table structure for table `otjobs_errors`
--

CREATE TABLE IF NOT EXISTS `otjobs_errors` (
  `id` int(11) NOT NULL auto_increment,
  `error` varchar(255) default NULL,
  `more` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
