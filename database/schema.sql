CREATE TABLE IF NOT EXISTS `blacklist` (
  `user_id` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

<<<<<<< HEAD
CREATE TABLE IF NOT EXISTS `shares` (
  `share_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `url` varchar(255),
  `tag` varchar(20) NOT NULL,
=======
CREATE TABLE IF NOT EXISTS `dayoff` (
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `time` varchar(20) NOT NULL,
  `description` varchar(255) NOT NULL,
>>>>>>> main
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);