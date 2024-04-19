-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: cooking
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `asignaciones_rol_usuario`
--

DROP TABLE IF EXISTS `asignaciones_rol_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `asignaciones_rol_usuario` (
  `idUsuario` int DEFAULT NULL,
  `idRol` int DEFAULT NULL,
  KEY `idUsuario` (`idUsuario`),
  KEY `idRol` (`idRol`),
  CONSTRAINT `asignaciones_rol_usuario_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `asignaciones_rol_usuario_ibfk_2` FOREIGN KEY (`idRol`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asignaciones_rol_usuario`
--

LOCK TABLES `asignaciones_rol_usuario` WRITE;
/*!40000 ALTER TABLE `asignaciones_rol_usuario` DISABLE KEYS */;
INSERT INTO `asignaciones_rol_usuario` VALUES (1,1),(1,2),(1,3),(1,3);
/*!40000 ALTER TABLE `asignaciones_rol_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pago_proveedor` float NOT NULL,
  `estatus` tinyint(1) NOT NULL,
  `fecha_compra` date NOT NULL,
  `idUsuario` int NOT NULL,
  `idTransaccionCaja` int DEFAULT NULL,
  `idProveedores` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idTransaccionCaja` (`idTransaccionCaja`),
  KEY `idProveedores` (`idProveedores`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `compras_ibfk_2` FOREIGN KEY (`idTransaccionCaja`) REFERENCES `transacciones_caja` (`id`),
  CONSTRAINT `compras_ibfk_3` FOREIGN KEY (`idProveedores`) REFERENCES `proveedores` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
INSERT INTO `compras` VALUES (1,15400,1,'2024-04-16',1,NULL,1),(2,28505,1,'2024-04-16',1,NULL,3),(3,12958,1,'2024-04-16',1,NULL,10),(4,67180,1,'2024-04-16',1,NULL,11);
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cortes_caja`
--

DROP TABLE IF EXISTS `cortes_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cortes_caja` (
  `id` int NOT NULL AUTO_INCREMENT,
  `monto_final` float DEFAULT NULL,
  `monto_inicial` float DEFAULT NULL,
  `fecha_corte` date DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cortes_caja`
--

LOCK TABLES `cortes_caja` WRITE;
/*!40000 ALTER TABLE `cortes_caja` DISABLE KEYS */;
INSERT INTO `cortes_caja` VALUES (1,NULL,1000,'2024-04-16');
/*!40000 ALTER TABLE `cortes_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalles_venta`
--

DROP TABLE IF EXISTS `detalles_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `precio` float NOT NULL,
  `cantidad` int DEFAULT NULL,
  `idVenta` int DEFAULT NULL,
  `idStock` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idVenta` (`idVenta`),
  KEY `idStock` (`idStock`),
  CONSTRAINT `detalles_venta_ibfk_1` FOREIGN KEY (`idVenta`) REFERENCES `ventas` (`id`),
  CONSTRAINT `detalles_venta_ibfk_2` FOREIGN KEY (`idStock`) REFERENCES `lotes_galletas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_venta`
--

LOCK TABLES `detalles_venta` WRITE;
/*!40000 ALTER TABLE `detalles_venta` DISABLE KEYS */;
INSERT INTO `detalles_venta` VALUES (1,15,50,2,1),(2,15,1,3,1),(3,25,1,3,2),(4,3,1,3,3),(5,17,1,3,4),(6,30,1,3,5);
/*!40000 ALTER TABLE `detalles_venta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos`
--

DROP TABLE IF EXISTS `insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `descripcion` varchar(45) NOT NULL,
  `unidad_medida` enum('Kilos','Litros') NOT NULL,
  `cantidad_maxima` float NOT NULL,
  `cantidad_minima` float NOT NULL,
  `merma` float NOT NULL,
  `estatus` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos`
--

LOCK TABLES `insumos` WRITE;
/*!40000 ALTER TABLE `insumos` DISABLE KEYS */;
INSERT INTO `insumos` VALUES (1,'Harina de Trigo','Harina de trigo para galletas','Kilos',100,50,0,1),(2,'Azúcar','Azúcar refinada para galletas','Kilos',50,10,0,1),(3,'Huevos','Huevos para galletas','Kilos',100,6,0,1),(4,'Leche','Leche para galletas','Litros',100,10,0,1),(5,'Mantequilla','Mantequilla para galletas','Kilos',50,2,0,1),(6,'Sal','Sal para galletas','Kilos',500,5,0,1),(7,'Vainilla','Extracto de vainilla para galletas','Litros',500,100,0,1),(8,'Chocolate','Chocolate para galletas','Kilos',60,10,0,1),(9,'Cacao','Cacao en polvo para galletas','Kilos',15,5,0,1),(10,'Mermelada','Mermelada para galletas','Litros',10,2,0,1),(11,'Polvo de Hornear','Polvo de hornear para galletas','Kilos',20,5,0,1),(12,'Canela','Canela en polvo para galletas','Kilos',100,20,0,1),(13,'Nuez Moscada','Nuez moscada para galletas','Kilos',50,10,0,1),(14,'Avena','Avena en hojuelas para galletas','Kilos',45,1,0,1),(15,'Maní','Maní triturado para galletas','Kilos',18,2,0,1),(16,'Almendras','Almendras picadas para galletas','Kilos',27,1,0,1),(17,'Nuez','Nuez picada para galletas','Kilos',36,1,0,1),(18,'Coco Rallado','Coco rallado para galletas','Kilos',5,1,0,1),(19,'Chips de Chocolate','Chips de chocolate para galletas','Kilos',15,5,0,1),(20,'Dulce de Leche','Dulce de leche para relleno de galletas','Kilos',19,2,0,1);
/*!40000 ALTER TABLE `insumos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos_receta`
--

DROP TABLE IF EXISTS `insumos_receta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos_receta` (
  `idReceta` int NOT NULL,
  `idInsumo` int NOT NULL,
  `cantidad` float NOT NULL,
  PRIMARY KEY (`idReceta`,`idInsumo`),
  KEY `idInsumo` (`idInsumo`),
  CONSTRAINT `insumos_receta_ibfk_1` FOREIGN KEY (`idReceta`) REFERENCES `recetas` (`id`),
  CONSTRAINT `insumos_receta_ibfk_2` FOREIGN KEY (`idInsumo`) REFERENCES `insumos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos_receta`
--

LOCK TABLES `insumos_receta` WRITE;
/*!40000 ALTER TABLE `insumos_receta` DISABLE KEYS */;
INSERT INTO `insumos_receta` VALUES (1,1,1),(1,2,0.2),(1,4,1),(1,17,0.5),(2,1,2),(2,2,0.4),(2,4,2),(2,5,0.1),(3,1,0.7),(3,4,0.89),(3,15,0.6),(3,20,0.15),(4,1,0.9),(4,4,0.5),(4,5,0.09),(4,6,0.015),(4,11,0.1),(4,16,0.4),(5,1,0.6),(5,2,0.1),(5,4,0.4),(5,7,0.2),(5,20,0.2),(6,1,2),(6,4,1),(6,12,0.2),(7,1,0.6),(7,2,0.05),(7,4,0.3),(7,10,0.04);
/*!40000 ALTER TABLE `insumos_receta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs_acciones`
--

DROP TABLE IF EXISTS `logs_acciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs_acciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `modulo` varchar(45) NOT NULL,
  `detalles` varchar(200) NOT NULL,
  `idUsuario` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `logs_acciones_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs_acciones`
--

LOCK TABLES `logs_acciones` WRITE;
/*!40000 ALTER TABLE `logs_acciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `logs_acciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs_login`
--

DROP TABLE IF EXISTS `logs_login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `logs_login` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL,
  `exito` tinyint(1) NOT NULL,
  `idUsuario` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `logs_login_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs_login`
--

LOCK TABLES `logs_login` WRITE;
/*!40000 ALTER TABLE `logs_login` DISABLE KEYS */;
INSERT INTO `logs_login` VALUES (1,'2024-04-16 14:31:26',1,1);
/*!40000 ALTER TABLE `logs_login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lotes_galletas`
--

DROP TABLE IF EXISTS `lotes_galletas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lotes_galletas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha_entrada` date DEFAULT NULL,
  `cantidad` int NOT NULL,
  `merma` int NOT NULL,
  `tipo_venta` int NOT NULL,
  `idProduccion` int NOT NULL,
  `idReceta` int NOT NULL,
  `idUsuarios` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idProduccion` (`idProduccion`),
  KEY `idReceta` (`idReceta`),
  KEY `idUsuarios` (`idUsuarios`),
  CONSTRAINT `lotes_galletas_ibfk_1` FOREIGN KEY (`idProduccion`) REFERENCES `solicitudes_produccion` (`id`),
  CONSTRAINT `lotes_galletas_ibfk_2` FOREIGN KEY (`idReceta`) REFERENCES `recetas` (`id`),
  CONSTRAINT `lotes_galletas_ibfk_3` FOREIGN KEY (`idUsuarios`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lotes_galletas`
--

LOCK TABLES `lotes_galletas` WRITE;
/*!40000 ALTER TABLE `lotes_galletas` DISABLE KEYS */;
INSERT INTO `lotes_galletas` VALUES (1,'2023-04-01',49,5,1,1,1,1),(2,'2023-04-02',199,10,2,1,2,1),(3,'2023-04-03',299,15,3,1,3,1),(4,'2023-04-04',399,20,1,1,4,1),(5,'2023-04-05',499,25,1,1,5,1),(6,'2023-04-06',50,5,1,1,1,1);
/*!40000 ALTER TABLE `lotes_galletas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lotes_insumo`
--

DROP TABLE IF EXISTS `lotes_insumo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lotes_insumo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha_caducidad` date NOT NULL,
  `cantidad` float NOT NULL,
  `fecha_compra` date NOT NULL,
  `precio_unidad` float NOT NULL,
  `merma` float NOT NULL,
  `idInsumo` int NOT NULL,
  `idCompra` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idInsumo` (`idInsumo`),
  KEY `idCompra` (`idCompra`),
  CONSTRAINT `lotes_insumo_ibfk_1` FOREIGN KEY (`idInsumo`) REFERENCES `insumos` (`id`),
  CONSTRAINT `lotes_insumo_ibfk_2` FOREIGN KEY (`idCompra`) REFERENCES `compras` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lotes_insumo`
--

LOCK TABLES `lotes_insumo` WRITE;
/*!40000 ALTER TABLE `lotes_insumo` DISABLE KEYS */;
INSERT INTO `lotes_insumo` VALUES (1,'2024-05-11',100,'2024-04-16',30,0,1,1),(2,'2024-05-11',100,'2024-04-16',50,0,2,1),(3,'2024-05-10',100,'2024-04-16',45,0,3,1),(4,'2024-05-04',100,'2024-04-16',29,0,4,1),(5,'2024-05-03',100,'2024-04-16',65.41,0,5,2),(6,'2024-07-05',100,'2024-04-16',35.45,0,6,2),(7,'2024-05-10',100,'2024-04-16',98.74,0,7,2),(8,'2024-05-08',100,'2024-04-16',85.45,0,8,2),(9,'2024-04-18',26,'2024-04-16',21.1154,0,8,3),(10,'2024-05-02',69,'2024-04-16',127.899,0,9,3),(11,'2024-05-11',60,'2024-04-16',59.7333,0,10,3),(12,'2024-06-21',100,'2024-04-16',65.15,0,11,4),(13,'2024-06-14',100,'2024-04-16',56.52,0,12,4),(14,'2024-08-14',100,'2024-04-16',84.24,0,13,4),(15,'2024-10-25',94,'2024-04-16',21.7447,0,14,4),(16,'2024-05-11',80,'2024-04-16',15,0,15,4),(17,'2024-07-13',100,'2024-04-16',30,0,16,4),(18,'2024-09-14',100,'2024-04-16',105,0,17,4),(19,'2024-05-11',50,'2024-04-16',180,0,18,4),(20,'2024-07-19',100,'2024-04-16',150,0,19,4),(21,'2024-05-11',60,'2024-04-16',97.4167,0,20,4);
/*!40000 ALTER TABLE `lotes_insumo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa` varchar(45) NOT NULL,
  `direccion` varchar(45) NOT NULL,
  `nombre_contacto` varchar(45) NOT NULL,
  `contacto` varchar(45) DEFAULT NULL,
  `estatus` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `empresa` (`empresa`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'Bodega Aurrera','Calle Falsa 123','Juan Perez','1234567890',1),(2,'Walmart','Avenida Principal 456','Maria Lopez','0987654321',1),(3,'Nestle','Boulevard 789','Carlos Gomez','1122334455',1),(4,'Unilever','Calle Central 012','Ana Martinez','5566778899',1),(5,'Coca Cola','Avenida del Sol 345','Pedro Fernandez','9988776655',1),(6,'Pepsi','Boulevard de la Luna 678','Laura Garcia','4455667788',1),(7,'Kellogg','Calle de los Sueños 901','Ricardo Rodriguez','2233445566',1),(8,'General Mills','Avenida de los Sueños 234','Sofia Morales','6677889900',1),(9,'Mars','Boulevard de los Sueños 567','Carmen Sanchez','8899001122',1),(10,'Hershey','Calle de los Sueños 890','Luis Torres','0011223344',1),(11,'Mondelez International','Avenida de los Sueños 123','Patricia Ramirez','4455667788',1),(12,'Nabisco','Boulevard de los Sueños 456','Juanita Perez','2233445566',1),(13,'Kraft Heinz','Calle de los Sueños 789','Miguel Garcia','6677889900',1),(14,'Heinz','Avenida de los Sueños 012','Carmen Sanchez','8899001122',1),(15,'Campbell Soup','Boulevard de los Sueños 345','Luis Torres','0011223344',1);
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `peso_estimado` float NOT NULL,
  `utilidad` float DEFAULT NULL,
  `piezas` int NOT NULL,
  `descripcion` varchar(800) DEFAULT NULL,
  `nombre` varchar(50) NOT NULL,
  `imagen` varchar(2550) DEFAULT NULL,
  `estatus` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES (1,0.027,15,100,'','Galleta de nuez','nuez.jpg',1),(2,0.045,25,100,'','Galleta de chocolate','chocolate.png',1),(3,0.0468,3,50,'','Galleta de mani','mani.jpg',1),(4,0.0267333,17,75,'','Galleta de almendra','almendras.jpg',1),(5,0.05,30,30,'','Galleta de vainilla','vainilla.jpg',1),(6,0.04,21,80,'','Galleta de canela','canela.jpg',1),(7,0.0396,14,25,'','Galleta de mermelada','mermelada-casera.jpg',1);
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin',NULL),(2,'vendedor',NULL),(3,'cocinero',NULL);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes_produccion`
--

DROP TABLE IF EXISTS `solicitudes_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes_produccion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha_produccion` date DEFAULT NULL,
  `mensaje` varchar(50) DEFAULT NULL,
  `estatus` int NOT NULL,
  `tandas` int DEFAULT NULL,
  `merma` int DEFAULT NULL,
  `fecha_solicitud` datetime DEFAULT NULL,
  `posicion` int DEFAULT NULL,
  `idReceta` int NOT NULL,
  `idUsuarioSolicitud` int NOT NULL,
  `idUsuarioProduccion` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idReceta` (`idReceta`),
  KEY `idUsuarioSolicitud` (`idUsuarioSolicitud`),
  KEY `idUsuarioProduccion` (`idUsuarioProduccion`),
  CONSTRAINT `solicitudes_produccion_ibfk_1` FOREIGN KEY (`idReceta`) REFERENCES `recetas` (`id`),
  CONSTRAINT `solicitudes_produccion_ibfk_2` FOREIGN KEY (`idUsuarioSolicitud`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `solicitudes_produccion_ibfk_3` FOREIGN KEY (`idUsuarioProduccion`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes_produccion`
--

LOCK TABLES `solicitudes_produccion` WRITE;
/*!40000 ALTER TABLE `solicitudes_produccion` DISABLE KEYS */;
INSERT INTO `solicitudes_produccion` VALUES (1,'2024-04-16',NULL,4,2,0,'2024-04-16 00:00:00',1,1,1,1);
/*!40000 ALTER TABLE `solicitudes_produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transacciones_caja`
--

DROP TABLE IF EXISTS `transacciones_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transacciones_caja` (
  `id` int NOT NULL AUTO_INCREMENT,
  `monto_egreso` float DEFAULT NULL,
  `monto_ingreso` float DEFAULT NULL,
  `fecha_transaccion` date DEFAULT NULL,
  `idCorteCaja` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idCorteCaja` (`idCorteCaja`),
  CONSTRAINT `transacciones_caja_ibfk_1` FOREIGN KEY (`idCorteCaja`) REFERENCES `cortes_caja` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transacciones_caja`
--

LOCK TABLES `transacciones_caja` WRITE;
/*!40000 ALTER TABLE `transacciones_caja` DISABLE KEYS */;
INSERT INTO `transacciones_caja` VALUES (1,NULL,0,NULL,1),(2,NULL,750,'2024-04-16',1),(3,NULL,90,'2024-04-16',1);
/*!40000 ALTER TABLE `transacciones_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `correo` varchar(255) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `contrasenia` varchar(255) NOT NULL,
  `token` varchar(255) DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `current_login_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_authenticated` tinyint(1) DEFAULT NULL,
  `is_anonymous` tinyint(1) DEFAULT NULL,
  `estatus` tinyint(1) NOT NULL,
  `confirmed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin@correo.com','admin','scrypt:32768:8:1$5eLEnxCeiot2GuHd$8b506093b601d50165a20cfd6a1971afde4d60d1b1e1f72f87d63472c893af4a243a2a3135a90db59ce9b82b1d6636acbe5514d5c4e56a10453d4b75deaaf3a7',NULL,NULL,'2024-04-16 14:31:26',1,1,0,1,NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha_venta` datetime NOT NULL,
  `total_venta` float NOT NULL,
  `idUsuario` int NOT NULL,
  `idTransaccionCaja` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idTransaccionCaja` (`idTransaccionCaja`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`idTransaccionCaja`) REFERENCES `transacciones_caja` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,'2024-04-16 16:23:38',0,1,1),(2,'2024-04-16 16:29:34',750,1,2),(3,'2024-04-16 16:30:29',90,1,3);
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-16 18:03:18
