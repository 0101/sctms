# --------------------------------------------------------
# Host:                         127.0.0.1
# Server version:               5.5.9
# Server OS:                    Win32
# HeidiSQL version:             6.0.0.3603
# Date/time:                    2011-03-07 20:10:17
# --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

# Dumping structure for table sctms-dev.cms_blogentry
DROP TABLE IF EXISTS `cms_blogentry`;
CREATE TABLE IF NOT EXISTS `cms_blogentry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `date` datetime NOT NULL,
  `title` varchar(100) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `tags` varchar(150) NOT NULL,
  `hits` int(11) NOT NULL,
  `up` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `text` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `author_id` (`author_id`),
  KEY `cms_blogentry_42dc49bc` (`category_id`),
  KEY `cms_blogentry_56ae2a2a` (`slug`),
  CONSTRAINT `category_id_refs_id_4902694e` FOREIGN KEY (`category_id`) REFERENCES `cms_category` (`id`),
  CONSTRAINT `author_id_refs_id_43c89379` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

# Dumping data for table sctms-dev.cms_blogentry: ~2 rows (approximately)
/*!40000 ALTER TABLE `cms_blogentry` DISABLE KEYS */;
INSERT INTO `cms_blogentry` (`id`, `author_id`, `category_id`, `date`, `title`, `slug`, `tags`, `hits`, `up`, `down`, `text`) VALUES
	(1, 168, 1, '2011-03-07 03:10:34', 'Pes nekous', 'pes-nekous', 'a, b, c, tag, fag', 5, 0, 0, '\r\nWelcome to the Komodo User Guide\r\n\r\nWhat\'s new in Komodo Edit\r\n\r\nBetter Support for Django:\r\nbetter syntax highlighting and smarter indentation for templates\r\nsyntax checking for templates\r\nautomatic code completions for Django template tags and filters\r\nhyperlinks to easily jump to template file locations\r\neasier to open files with fast open supporting directory name matching\r\nProjects: By popular demand, file and directory references have been reintroduced. These can be organized in Groups to keep things logical and tidy.\r\nWorkspace Save and Restore: Komodo will now be regularly saving your workspace. In the case of an unexpected shutdown, you can choose to restore your last used workspace the next time it starts up.\r\nPlaces: A new file manager has been added to Komodo\'s left pane. It provides a customized view of your file system (local or remote) and easy file management operations such as file editing, drag/drop copying, creation of new files and folders, and search.\r\nFaster: A number of Komodo components have been made to run faster, such as startup, shutdown, tab-switching and finding text. The underlying Mozilla source code has been updated to version 1.9.1, the same code base as Firefox 3.5, which means improved performance gains for Komodo.\r\nNew Toolbox: The Komodo toolbox and project system are being rewritten. Individual toolbox items (commands, macros, snippets, etc.) are saved in separate JSON files rather than as nodes in a toolbox.kpf file. There is a new "Invoke Tool" command which allows you to easily search and then execute specific tools. In future versions project-specific tools will appear in the Toolbox sidebar instead of the Projects sidebar, which will eventually be removed.\r\nHyperlink Additions: Hyperlinks have been extended and can now...\r\nshow image preview while hovering on an image link,\r\nshow Code Intelligence definitions while hovering on a symbol,\r\njump to an HTML anchor tag to it\'s definition,\r\njump to HREF and SRC locations,\r\nopen files from a path reference,\r\njump to PHP file includes\r\nHTML 5 and CSS3 Support: Autocomplete for HTML 5 and CSS3.\r\nMore Languages: Syntax highlighting for Markdown, MySQL, and others.\r\n(Read the full Release Notes.)\r\n\r\nSupport and Community\r\n\r\nThe ActiveState Community site has resources to help you use Komodo effectively:\r\n\r\nKomodo FAQs\r\nKomodo Forums\r\nSample Project\r\n\r\nGet started fast with Komodo\'s Sample Project.\r\n\r\nFeature Showcase\r\n\r\nQuick Demos showing advanced search functionality, editing, debugging, and more.'),
	(2, 8, 2, '2011-03-07 19:44:50', 'Jak hoří les?', 'jak-hori-les', 'les, ohen, otazky, odpovedi', 3, 0, 0, 'Používáte-li nástroj pro čtení obrazovky, vypněte Dynamické vyhledávání Google kliknutím sem.\r\nGoogle\r\n\r\n	×\r\n\r\nDynamické vyhledávání je zapnuto ▼\r\n\r\nWeb Obrázky Videa Mapy Zprávy Překladač Gmail další ▼\r\ntheNSLcz@gmail.com | Webová historie | Nastavení ▼ | Odhlásit se\r\nRozšířené vyhledávání\r\nPřibližný počet výsledků: 2 040 000 (0,34 s) \r\nVýsledky hledání\r\nPython Database Programming - 15:57 - [ Přeložit tuto stránku ]\r\n10 Nov 2010 ... Talk video and slides: Using the Python Database API ... SQL Relay is a persistent database connection pooling, proxying and load balancing ...\r\nwiki.python.org/moin/DatabaseProgramming/ - Archiv - Podobné\r\n►\r\nUsingDbApiWithPostgres - PythonInfo Wiki - [ Přeložit tuto stránku ]\r\n15 Feb 2010 ... import psycopg2 as dbapi2 db = dbapi2.connect (database ...\r\nwiki.python.org/moin/UsingDbApiWithPostgres - Archiv - Podobné\r\nZobrazit další výsledky z webu python.org\r\nProgramming Python - Python Database Programming - Connecting to ... - 15:57 - [ Přeložit tuto stránku ]\r\nThese tutorials explore the various Python modules available for database administration. Particular emphasis will be laid on MySQL and PostgreSQL database ...\r\npython.about.com/.../pythonanddatabases/Connecting_to_Databases_With_Python.htm - Archiv - Podobné\r\nConnect to Database Using Python « Code Ghar - [ Přeložit tuto stránku ]\r\n8 Dec 2007 ... Although you can connect to databases using Python on many platforms, ... Skills Expected of a Linux Admin · Software in the Public Interest ...\r\ncodeghar.wordpress.com/.../connect-to-database-using-python/ - Archiv - Podobné\r\nBuilding a web-admin around an existing MS SQL table (python ... - [ Přeložit tuto stránku ]\r\nBuilding a web-admin around an existing MS SQL table (python/django problem? ... Connecting to MS SQL Server using python on linux with \'Windows Credentials ...\r\nstackoverflow.com/.../building-a-web-admin-around-an-existing-ms-sql-table-python-django-problem - Archiv\r\nDjango | Databases | Django documentation - [ Přeložit tuto stránku ]\r\n13 Oct 2010 ... In order for the python manage.py syncdb command to work, your Oracle database ... CONNECT WITH ADMIN OPTION; RESOURCE WITH ADMIN OPTION .... Connecting to the database; Creating your tables; Notes on specific fields ...\r\ndocs.djangoproject.com/en/dev/ref/databases/ - Archiv - Podobné\r\nPython for the SQL Server DBA - [ Přeložit tuto stránku ]\r\nCelkem příspěvků: 12 - Počet autorů: 10 - Poslední příspěvek: 27. srpen 2009\r\nSQL Home > Database Administration > Python for the SQL Server DBA ... This is what I primarily use it for in connection with SQL. ... into a SQL Temp Table line by line and then parse it using pure T-SQL it is generally ...\r\nwww.simple-talk.com › ... › Database Administration - Archiv - Podobné\r\nPython for Unix and Linux system administration - Výsledky hledání v Google Books\r\nNoah Gift, Jeremy M. Jones - 2008 - Computers - 433 str.\r\nTables connected with a foreign key relationship can even be accessed as an attribute of ... Storm is a relative newcomer to the database arena for Python, ...\r\nbooks.google.cz/books?isbn=0596515820...\r\n[Python] chCounter <= 3.1.3 SQL Injection Vulnerability - [ Přeložit tuto stránku ]\r\n1 příspěvek - 1 autor - Poslední příspěvek: 19. listopad 2010\r\nAccess to administration site(can be bypassed if magic_quotes off) ... -1: print \'[-] Could not acces table. Acces denied. ...\r\nwww.hackxcrack.es/.../4125-python-chcounter-3-1-3-sql-injection-vulnerability.html?... - Archiv\r\nFree win32 appwizard Python download - Python win32 appwizard ... - [ Přeložit tuto stránku ]\r\nPython. Details · Download. Odbc connection on win32 script implement the features of retrieving dsn and tables list on win32. ...\r\nwww.lastbeatniks.tk/free-win32-appwizard/python/ - Archiv\r\nVše\r\nObrázky\r\nVidea\r\nZprávy\r\nKnihy\r\nVíce\r\nPraha\r\nZměnit místo\r\nMožnosti vyhledávání\r\nProhledat web\r\nStránky pouze česky\r\nPřeložené cizojazyčné stránky\r\nVíce nástrojů\r\n1	\r\n2\r\n3\r\n4\r\n5\r\n6\r\n7\r\n8\r\n9\r\n10\r\nDalší\r\nTipy pro vyhledávání Sdělte nám svůj názor\r\nGoogle HomeInzerujte s GooglemOsobní údajeVše o Googlu');
/*!40000 ALTER TABLE `cms_blogentry` ENABLE KEYS */;


# Dumping structure for table sctms-dev.cms_category
DROP TABLE IF EXISTS `cms_category`;
CREATE TABLE IF NOT EXISTS `cms_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

# Dumping data for table sctms-dev.cms_category: ~2 rows (approximately)
/*!40000 ALTER TABLE `cms_category` DISABLE KEYS */;
INSERT INTO `cms_category` (`id`, `name`) VALUES
	(1, 'pes'),
	(2, 'les');
/*!40000 ALTER TABLE `cms_category` ENABLE KEYS */;


# Dumping structure for table sctms-dev.cms_comment
DROP TABLE IF EXISTS `cms_comment`;
CREATE TABLE IF NOT EXISTS `cms_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author_id` int(11) NOT NULL,
  `topic_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `date` datetime NOT NULL,
  `up` int(11) NOT NULL,
  `down` int(11) NOT NULL,
  `text` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `author_id` (`author_id`),
  KEY `cms_comment_57732028` (`topic_id`),
  CONSTRAINT `author_id_refs_id_154d9dca` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `topic_id_refs_id_57d1b138` FOREIGN KEY (`topic_id`) REFERENCES `cms_blogentry` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# Dumping data for table sctms-dev.cms_comment: ~0 rows (approximately)
/*!40000 ALTER TABLE `cms_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_comment` ENABLE KEYS */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
