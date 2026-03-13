-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 12, 2026 at 02:59 PM
-- Wersja serwera: 8.0.41
-- Wersja PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `komis`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `cars`
--

CREATE TABLE `cars` (
  `id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `price` int NOT NULL,
  `year` int NOT NULL,
  `mileage` int NOT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `fuel` varchar(50) DEFAULT NULL,
  `engine` varchar(50) DEFAULT NULL,
  `description` text,
  `created_at` datetime DEFAULT NULL,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `car_images`
--

CREATE TABLE `car_images` (
  `id` int NOT NULL,
  `car_id` int DEFAULT NULL,
  `filename` varchar(255) NOT NULL,
  `is_main` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `login_attempts`
--

CREATE TABLE `login_attempts` (
  `id` int NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `ip_address` varchar(45) NOT NULL,
  `timestamp` float DEFAULT NULL,
  `success` int DEFAULT NULL,
  `locked_until` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `login_attempts`
--

INSERT INTO `login_attempts` (`id`, `username`, `ip_address`, `timestamp`, `success`, `locked_until`) VALUES
(34, 'admin', '37.47.198.53', 1767860000, 1, 0);

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `login_metadata`
--

CREATE TABLE `login_metadata` (
  `id` int NOT NULL,
  `username` varchar(50) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `region` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `screen_width` int DEFAULT NULL,
  `screen_height` int DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `user_agent` text,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `login_metadata`
--

INSERT INTO `login_metadata` (`id`, `username`, `ip_address`, `city`, `region`, `country`, `screen_width`, `screen_height`, `timezone`, `user_agent`, `created_at`) VALUES
(1, 'jan', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1536, 960, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2025-12-31 19:13:37'),
(2, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1536, 960, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2025-12-31 19:14:57'),
(3, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1536, 960, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2025-12-31 22:08:35'),
(4, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1536, 960, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2025-12-31 22:38:21'),
(5, 'jan2', '37.47.198.53', NULL, NULL, NULL, 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2026-01-01 19:36:55'),
(6, 'jan2', '37.47.198.53', NULL, NULL, NULL, 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2026-01-01 19:37:00'),
(7, 'jan3', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2026-01-01 23:04:57'),
(8, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:00:27'),
(9, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:28:31'),
(10, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:29:20'),
(11, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:42:49'),
(12, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:43:19'),
(13, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:43:34'),
(14, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:44:35'),
(15, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:45:04'),
(16, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 10:52:05'),
(17, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:07:28'),
(18, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:08:21'),
(19, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:23:03'),
(20, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:23:31'),
(21, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:25:23'),
(22, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:25:50'),
(23, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:27:39'),
(24, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:28:03'),
(25, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:29:52'),
(26, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:30:17'),
(27, 'jan3', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:33:40'),
(28, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0', '2026-01-02 11:34:20'),
(29, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2026-01-02 22:02:05'),
(30, 'jan2', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1920, 1080, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2026-01-03 20:17:26'),
(31, 'admin', '37.47.198.53', 'Gdansk', 'Pomerania', 'Poland', 1536, 960, 'Europe/Warsaw', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', '2026-01-08 09:08:58');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','user','seller') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES
(4, 'admin', '$pbkdf2-sha256$29000$zFmLcW7N.b9Xau1dCwHAmA$6g7aTVTpWVaCQiBcbM01zxcQ/lSQSNf6znuA6Mczq6w', 'admin'),
(5, 'jan2', '$pbkdf2-sha256$29000$ipEyhvBey/mfk9Iag/Deew$hJapIHfaIHtXC228MFBkgQMxdwazqk.GgkFqcPG3fPI', 'seller');

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `cars`
--
ALTER TABLE `cars`
  ADD PRIMARY KEY (`id`);

--
-- Indeksy dla tabeli `car_images`
--
ALTER TABLE `car_images`
  ADD PRIMARY KEY (`id`),
  ADD KEY `car_images_ibfk_2` (`car_id`);

--
-- Indeksy dla tabeli `login_attempts`
--
ALTER TABLE `login_attempts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_login_attempts_id` (`id`);

--
-- Indeksy dla tabeli `login_metadata`
--
ALTER TABLE `login_metadata`
  ADD PRIMARY KEY (`id`);

--
-- Indeksy dla tabeli `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `ix_users_id` (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cars`
--
ALTER TABLE `cars`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52;

--
-- AUTO_INCREMENT for table `car_images`
--
ALTER TABLE `car_images`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=96;

--
-- AUTO_INCREMENT for table `login_attempts`
--
ALTER TABLE `login_attempts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `login_metadata`
--
ALTER TABLE `login_metadata`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `car_images`
--
ALTER TABLE `car_images`
  ADD CONSTRAINT `car_images_ibfk_2` FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
