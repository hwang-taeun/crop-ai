
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
DROP TABLE IF EXISTS `diagnosis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnosis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `member_id` bigint NOT NULL,
  `crop` enum('TOMATO','POTATO','CORN') NOT NULL,
  `image_key` varchar(255) NOT NULL,
  `thumbnail_key` varchar(255) NOT NULL,
  `feedback` enum('CORRECT','INCORRECT') DEFAULT NULL,
  `feedback_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_member_created` (`member_id`,`created_at`),
  CONSTRAINT `fk_diagnosis_member` FOREIGN KEY (`member_id`) REFERENCES `member` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `diagnosis_candidate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnosis_candidate` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `diagnosis_id` bigint NOT NULL,
  `disease_id` bigint NOT NULL,
  `ranking` int NOT NULL,
  `confidence` decimal(5,4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_diagnosis_ranking` (`diagnosis_id`,`ranking`),
  KEY `fk_candidate_disease` (`disease_id`),
  CONSTRAINT `fk_candidate_diagnosis` FOREIGN KEY (`diagnosis_id`) REFERENCES `diagnosis` (`id`),
  CONSTRAINT `fk_candidate_disease` FOREIGN KEY (`disease_id`) REFERENCES `disease` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `disease` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `label` varchar(100) NOT NULL,
  `crop` enum('TOMATO','POTATO','CORN') NOT NULL,
  `name_ko` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `treatment` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `label` (`label`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
DROP TABLE IF EXISTS `member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `login_id` varchar(30) DEFAULT NULL,
  `password_hash` varchar(100) DEFAULT NULL,
  `failed_login_count` int NOT NULL DEFAULT '0',
  `locked_until` datetime(6) DEFAULT NULL,
  `google_sub` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `nickname` varchar(50) NOT NULL,
  `region` varchar(20) DEFAULT NULL,
  `role` enum('USER','ADMIN') NOT NULL DEFAULT 'USER',
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_member_nickname` (`nickname`),
  UNIQUE KEY `google_sub` (`google_sub`),
  UNIQUE KEY `login_id` (`login_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;


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

LOCK TABLES `disease` WRITE;
/*!40000 ALTER TABLE `disease` DISABLE KEYS */;
INSERT INTO `disease` VALUES (1,'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot','CORN','옥수수 잿빛무늬병','[증상]\n병징은 잎에 발생하며, 발병초기는 원형 또는 부정형의 반점이 나타나고, 진전되면 갈색의 원형 또는 갈색의 불규칙한 병반으로 확대된다.\n병반의 크기는 직경이 5∼10 ㎜이다.\n시간이 지나면서 반점은 확대되고, 불규칙한 모양의 병반으로 합쳐진다.\n심한 경우 잎이 마르고, 고사된다.\n병원균을 PDA에서 암배양시 균총은 쥐색으로 벨벳형태이며, 생육이 매우 느리다.','[방제 방법] 저항성 품종을 쓰고, 수확 후 병든 잔재물은 걷어내거나 깊이 갈아엎습니다. 연작을 피하고 통풍과 배수가 잘되게 관리합니다. 약제 사용은 농업기술센터나 농약안전정보시스템에서 등록 약제를 확인한 뒤 제품 라벨에 따라 적용하세요.'),(2,'Corn_(maize)___Common_rust_','CORN','옥수수 녹병','[증상]\n병징은 잎에서 주로 나타나며, 발병된 잎은 얼룩이 형성되고, 잎이 노화 된다.\n잎의 뒷면에는 노랑~주황색의 녹포자퇴가 형성되며, 하부잎의 표면에 작은 황색~황백색의 병반이 형성된다.','[방제 방법] 저항성 품종을 쓰고, 질소 비료를 과하게 주지 않으며 통풍이 잘되게 관리합니다. 발생 초기에 병든 잎을 확인하고, 약제 사용은 농업기술센터나 농약안전정보시스템에서 등록 약제를 확인한 뒤 제품 라벨에 따라 적용하세요.'),(3,'Corn_(maize)___Northern_Leaf_Blight','CORN','옥수수 그을음무늬병','[증상] 잎에 길쭉한 시가(담배) 모양의 회녹색~황갈색 병반이 생깁니다. 보통 아래 잎에서 먼저 나타나 위쪽 잎으로 올라가며, 병반이 합쳐지면 잎 전체가 말라 죽습니다. 서늘하고 습한 날씨에 많이 발생합니다.','[방제 방법] 저항성 품종을 쓰고, 수확 후 병든 잔재물은 걷어내거나 깊이 갈아엎습니다. 연작을 피하고 밀식하지 않아 통풍이 잘되게 합니다. 약제 사용은 농업기술센터나 농약안전정보시스템에서 등록 약제를 확인한 뒤 제품 라벨에 따라 적용하세요.'),(4,'Corn_(maize)___healthy','CORN','옥수수 정상','잎에서 뚜렷한 병징이 발견되지 않았습니다.','별도 방제가 필요하지 않습니다. 통풍·배수·균형 시비 등 기본 관리를 유지하고 주기적으로 잎을 살펴보세요.'),(5,'Potato___Early_blight','POTATO','감자 겹둥근무늬병','[증상]\n주로 잎에 많이 발생한다.\n처음에는 작은 원형의 갈색반점이 나타나고, 진전되면 1∼2㎝ 크기의 대형 흑갈색 병반이 형성된다.\n심할 때에는 잎 전체가 말라죽게 되고 괴사부에는 흑색의 분생포자가 밀생한다.\n토마토 겹둥근무늬병과 같이 뚜렸한 윤문이 형성되지는 않으나, 병반 상에는 다소의 윤문이 형성되는 것을 볼 수 있다.\n\n[발생 환경]\n온도가 높고 비가 자주 오면 병 발생이 많으며, 비료의 부족은 병을 증가 시킨다.\n병원균은 병든 잔사물에서 균사 또는 분생포자 형태로 겨울을 지내고 1차 전염원이 되며, 바람에 의해 분산, 전파 된다.\n전파된 분생포자는 알맞은 습도가 주어지면 발아하여 잎의 표피를 뚫고 침입, 2∼3일후 병반이 형성된다.','[방제 방법]\n저항성 품종을 이용하는 것이 가장 효과적이다.\n약제방제는 병원균이 확산되기 전에 방제 한다.\n배게 심기지 않도록 하고 통풍이 잘 되도록 관리한다.\n생육 후기에 양분이 부족할 때 많이 발생하기 때문에 적절한 양분관리가 필요하다.\n덩이줄기 감염을 방지하기 위하여 병에 걸린 지상부 잎줄기는 수확 전에 미리 제거하며, 감염된 식물체 잔사물은 수확한 밭에서 완전히 제거 한다.\n콩과나 볏과 작물과의 돌려짓기는 병원균의 밀도를 줄이는 데 도움이 된다.\n감자 수확 후 상처치유을 충분히 하여 괴경에 감염되지 않도록 주의 한다.'),(6,'Potato___Late_blight','POTATO','감자 역병','[증상]\n기상 환경과 재배 양식에 따라 병 증상이 다양하게 나타나는데 초기에는 연록색이나 진한 녹색의 부정형 작은 반점이 잎에 나타난다.\n환경이 적당하면 병은 순식간에 번지는데 적갈색의 큰 괴저 병반이 잎에 먼저 생기고 나중에 잎줄기와 줄기로 번져 포기 전체가 결국 말라죽는다.\n병반 주변에는 가끔 연록색 혹은 노란 윤문이 생기며 병원균 포자가 하얗게 형성되기도 한다.\n감염된 종서는 불규칙한 암갈색의 병반이 표면에 나타나는데 안으로 약간 들어가며 속을 갈라보면 적갈색으로 썩어있으나 비교적 단단하다.\n\n[발생 환경]\np. infestans는 전국의 재배지에서 발생되며 괴경과 감자의 모든 지상부위를 침해한다.\np. nicotianae는 제주도, p. erythroseptica는 강원도에서 발생이 확인되었으나 피해는 크지 않다.\np. infestans는 기온이 서늘하고(16~20˚c) 비가 많은 봄, 가을에 대 발생되는데, 공기중 습도와 병 발생은 밀접한 관계가 있다.\n전국의 모든 감자 재배지역에서 발생이 보고되었다.','[방제 방법]\n역병의 저항성 품종을 선택하고 건전한 씨감자를 사용한다 .\n감자를 넓게 심어 바람이 잘 통하게 하고 물 빠짐이 잘되게 관리 한다.\n스프링클러를 이용한 물주기는 병을 확산 시킬 수 있다.\n병에 걸린 식물체는 발견 즉시 제거하고 전염원이 되므로 포장 주변에 버리지 않도록 한다.\n예방 약제의 살포는 포자의 발아와 침입을 예방하므로 상습 발생지에서는 주기적으로 약제를 살포 한다.\n역병 증상이 발견되면 치료 효과가 있는 살균제 약제 살포가 필요하다.\n동일한 약제를 계속 사용면 저항성 균의 출현 등 문제점을 유발할 수 있으므로 계통이 다른 약제를 교대로 사용 한다.\n등록된 약제를 농약안전사용 기준에 맞게 살포하여 방제 한다.'),(7,'Potato___healthy','POTATO','감자 정상','잎에서 뚜렷한 병징이 발견되지 않았습니다.','별도 방제가 필요하지 않습니다. 통풍·배수·균형 시비 등 기본 관리를 유지하고 주기적으로 잎을 살펴보세요.'),(8,'Tomato___Bacterial_spot','TOMATO','토마토 세균점무늬병','[증상]\n병 발생 초기에 잎에 담갈색∼암갈색을 띤 작은 반점이 수침상으로 형성된다.\n병반의 바깥쪽에 노란 테두리가 형성되기도 한다.\n진전되면 반점이 점점 커지고 주변의 반점과 합쳐져서 커지기도 한다.\n심한 경우 잎이 말라 죽으며 낙엽된다\n\n[발생 환경]\n시설에서는 다습한 환경조건에서 주로 발생한다.\n주로 유묘의 잎에서 발생하는 경향이 있다.\n병원균은 종자나 식물의 잔재물에서 살아남아 전염원이 되거나 물을 통해 주변으로 전반된다.','[방제 방법]\n-건전한 종자와 유묘를 사용한다.\n-하우스 내부를 청결하게 관리하고 다습하지 않도록 통풍과 환기를 잘 시킨다.'),(9,'Tomato___Early_blight','TOMATO','토마토 겹둥근무늬병','[증상]\n잎, 줄기, 과실에 발생한다.\n감염 부위에는 처음에 타원형의 갈색 반점으로 나타나고 진전되면 암갈색의 겹무늬 반점으로 확대된다.\n병든 부위는 마른 상태로 썩으며 겹무늬가 생기고, 후에 분생포자가 형성되어 검은 색을 띠게 된다.\n줄기의 감염 부위 위쪽으로는 시들고 말라 죽는다.\n병든 과실은 검게 썩어 상품가치를 잃게 된다.\n\n[발생 환경]\n병원균은 종자 혹은 병든 부위에서 균사나 분생포자의 형태로 겨울을 지낸 후 분생포자를 형성하여 공기전염 한다.\n시설재배나 노지재배 시 온도와 습도가 높을 때 많이 발생한다.\n이 병은 토마토 이외의 다른 가지과 작물에서도 발생한다.','[방제 방법]\n- 병든 식물은 일찍 제거하고, 발생상습지 포장은 돌려짓기한다.\n- 조생종을 재배하고, 종자소독을 한다.\n- 충분히 비료를 주도록 한다.\n- 지주목을 새워 비,바람에 의해 쓰러지지 않도록 해주며, 통풍과 투광이 잘 되도록 한다.'),(10,'Tomato___Late_blight','TOMATO','토마토 역병','[증상]\n잎, 과실, 줄기 등에서 발생한다.\n잎에 발생하는 초기증상은 불명확한 수침상의 부정형 병반으로 나타나고 점점 커져 급속히 넓은 면적으로 번진다.\n병든 잎은 연한 녹색이나 갈색으로 썩고, 과습하면 잎 뒷면에 다량의 흰 균사와 유주자낭을 형성하여 이슬처럼 보인다.\n병든 잎은 갈색으로 썩고 오그라들면서 말라죽는데, 병발생이 심한 포장은 냉해를 입은 것처럼 보이기도 한다.\n어린 가지나 줄기 혹은 잎자루 등의 병든 부위는 갈색으로 썩으며, 저온과습하면 흰 균사와 포자가 수 없이 많이 형성된다.\n과실의 병든 부위는 흑갈색으로 썩고, 비교적 단단하며 과실전체가 심하게 오그라들기도 한다.\n다른 병원균이 이차적으로 침입하게 되면 과실 전체가 물컹하게 썩기도 한다.\n\n[발생 환경]\n노지포장에서도 발생되지만 시설재배에서 피해가 심하다.\n기온이 낮고 비가 잦으면 심하게 발생하여 치명적인 피해를 주는 병해로서 1～2주만에 전 포장을 황폐화시키기도 한다.\n기주작물이 재배되지 않을 때는 주로 병든 식물체의 잔재(殘滓) 등에서 월동하는데 병든 감자 종서가 결정적인 전염원이 될 수 있다.\n밤 기온은 낮고, 낮에는 따뜻하여 일교차가 크고 다습할 때 심하게 발생하며, 습도는 91～100%, 온도는 3～26℃사이에서 발병되나, 발병 최적온도는 18～22℃이고, 28℃이상에서는 거의 발병되지 않는다.\n이 병은 채소작물중 주로 토마토와 감자에서만 발생한다.','[방제 방법]\n- 환기를 철저히 하여 시설내가 과습하지 않도록 한다.\n- 잦은 물주기를 하지 않고 물빠짐을 좋게 한다.\n- 항상 포장을 청결히 하고 병든 잎이나 줄기는 조기에 제거하여 불에 태우거나 땅속 깊이 묻는다.\n- 등록약제를 이용하여 방제한다.'),(11,'Tomato___Leaf_Mold','TOMATO','토마토 잎곰팡이병','[증상]\n잎에 발생한다.\n처음에는 잎의 표면에 흰색 또는 담회색의 반점으로 나타나고 진전되면 황갈색 병반으로 확대된다.\n잎 뒷면에 담갈색의 병반이 형성되는데, 병반상에는 갈색의 곰팡이가 융단처럼 밀생되어 있는 것을 볼 수 있으며, 오래되면 균총이 갈색에서 연한 자색으로 변한다.\n주로 아래 잎에서 피해가 크며, 심하면 아랫잎 전체가 누렇게되고 말라 죽는다.\n\n[발생 환경]\n병원균은 병든 잎이나 종자 등에서 겨울을 지내고 1차 전염원이 되나, 시설재배에서는 병원균이 각종 농자재에 붙어 겨울을 지내기도 한다.\n2차 전염은 병반상에 형성된 포자가 전반되어 잎의 기공을 통하여 침입하여 발병된다.\n20～25℃ 의 온도조건하에서 피해가 크며, 특히 시설재배지에서 심하게 발생한다.','[방제 방법]\n- 병든 잎을 신속히 제거한다.\n- 90%이상의 상대습도가 유지되지 않도록 한다.\n- 통풍이 잘되게 하고 밀식하지 않는다.\n- 건전한 종자를 사용하고, 깨끗한 자재를 사용한다.\n- 질소질 비료의 과용을 피한다.'),(12,'Tomato___Septoria_leaf_spot','TOMATO','토마토 흰무늬병','[증상]\n잎, 잎자루, 줄기, 가지, 과경에 발생한다.\n발생 초기에는 식물체의 아래쪽에서부터 병 증상이 나타나고, 위쪽으로 진전되어 올라간다.\n감염 부위에는 갈색 내지 암갈색의 작은 반점이 형성되고, 진전되면 병반의 내부는 회색으로 변하며, 그 곳에 흑색의 소립점이 보인다.\n심하게 병든 잎은 황색으로 변하여 마르고 일찍 떨어진다.\n심하게 병든 가지는 황색으로 변해 말라 죽는다.\n\n[발생 환경]\n병원균은 병든 부위에서 병자각의 형태로 겨울을 지낸 후, 병포자를 형성하여 공기전염 한다.\n병원균의 감염적온은 20～25℃이고, 습도가 높은 경우에 병 발생이 심하다.\n노지포장에서는 주로 여름철 장마기 이후에 많이 발생한다.','[방제 방법]\n- 종자를 선별하고, 소독하여 파종한다.\n- 재배 시 균형시비를 한다.\n- 병든 잎은 조기에 제거한다.\n- 온실재배 시 내부가 다습하지 않도록 환기를 한다.'),(13,'Tomato___Spider_mites Two-spotted_spider_mite','TOMATO','토마토 점박이응애','잎 앞면에 작고 하얀 점이 촘촘히 생기고 심하면 잎이 누렇게 변하며, 잎 뒷면에 거미줄 같은 실과 작은 응애가 보입니다. 고온·건조할 때 급증합니다.','피해 잎을 제거하고 시설 내 습도와 통풍을 관리하세요. 천적 활용이나 등록된 약제 사용은 농업기술센터나 농약안전정보시스템에서 확인한 뒤 제품 라벨에 따라 적용하세요.'),(14,'Tomato___Target_Spot','TOMATO','토마토 갈색무늬병','[증상]\n주로 잎과 잎자루에 발생하며, 간혹 줄기와 과실에도 발생한다.\n잎에서는 처음 수침상의 둥근 점무늬로 나타나고, 진전되면 갈색의 원형 내지 부정형 병반으로 확대된다.\n심하게 감염된 잎은 누렇게 변하여 말라 죽는다.\n잎자루와 줄기에서는 처음에 작은 점무늬로 나타나고, 진전되면 병반이 감염 부위를 둘러싸게 되고, 그 위쪽은 말라 죽게 된다.\n과실에서는 처음에 갈색의 원형반점이 약간 움푹 들어간 형태로 나타나며, 진전되면 분화구처럼 확대되고, 후에 감염부위가 쪼개지기도 한다.\n\n[발생 환경]\n병원균은 병든 부위에서 균사나 분생포자의 형태로 겨울을 지낸 후, 분생포자를 형성하여 공기전염 한다.\n감염은 16～32℃ 에서 일어나며, 병 발생 적온은 20～28℃이다.\n이 병은 참깨, 콩 등의 다른 작물에서도 발생한다.','[방제 방법]\n- 건전한 종자를 선별하고, 소독하여 파종한다.\n- 퇴비를 시용하여 작물의 초세를 좋게 한다.\n- 재배 시 균형시비를 한다.'),(15,'Tomato___Tomato_Yellow_Leaf_Curl_Virus','TOMATO','토마토 황화잎말림바이러스병','[증상] 담배가루이가 옮기는 바이러스병입니다. 새잎이 작아지고 잎 가장자리가 위로 말리며 노랗게 변하고, 식물체가 위축됩니다. 어린 모종 때 감염되면 피해가 큽니다.','[방제 방법]\n병을 전염시키는 해충의 세대 기간이 짧아 연간 발생횟수가 많고 증식률이 높으므로 발생초기에 방제하고, 육묘 시 철저한 관리로 병의 확산 예방 한다.'),(16,'Tomato___Tomato_mosaic_virus','TOMATO','토마토 모자이크바이러스병','[증상]\n4종류의 바이러스에 의해서 발생된다.\nCMV에 감염된 잎에서는 작고 많은 황색 반점과 모자이크 및 고사리잎으로 나타나고, 간혹 위축과 기형을 동반하기도 한다.\nPepMoV에 의한 증상은 방울토마토의 잎에 황색의 모자이크 및 괴저윤문으로 나타나며, 줄기에서는 괴사증상이 심하게 나타난다.\nTMV에 의한 증상은 잎에 황색의 모자이크로 나타나며, 진전되면 잎이 기형이 되고, 일부가 가늘어진다.\n품종에 따라서는 새싹의 괴사나 줄기 및 과실의 괴저병반으로 나타난다.\nToMV에 의한 증상은 잎에서는 모자이크로, 줄기에서는 얼룩줄무늬로 나타나며 과실의 표면에는 괴저성의 윤문반점으로 나타난다.\n\n[발생 환경]\n전국적으로 발병율은 일반 토마토에서는 3.3%, 방울 토마토에서는 1.7%로 전체적으로는 낮은 편이다.\n그러나, 지역에 따른 차이가 많아 안강지역에서는 63%까지 감염된 경우도 있었다.\n일반 토마토에는 CMV와 TMV 및 ToMV가 주요 바이러스인 것에 반해, 방울 토마토에서는 PepMoV와 ToMV만 감염되는 것으로 보고되었다.\nCMV는 세계 각국에 널리 분포되어 있으며, 특히 온대지역에 발생이 많다.\n우리 나라에서도 전국 각지에 분포되어 각종 작물에 피해를 주고 있다.\nPVX는 즙액전염 또는 접촉에 의해서도 전염이 된다.\n접촉전염은 잎이나 줄기 접촉뿐만 아니라 뿌리 접촉에 의해서도 전염된다.\nPVX는 진딧물에 의하여 매개되지 않으나, 직시목에 속하는 곤충과 진균(Synchyrium endoticum)에 의하여도 전염되기도 한다.\n자연 상태에서 감염이 되는 기주로는 고추, 담배, 감자, 토마토 등이다.\nPepMoV를 자연상태에서 전염시키는 것은 진딧물이다.\nPepMoV는 비영속형전염 바이러스로서 충체내 잠복기간이 없다.\n또한 바이러스를 획득한 보독충도 단기간 안에 바이러스의 전염력을 잃는다.\n자연상태에서 감염되는 것은 담배, 고추, 감자 등이다.\nTMV는 종자전염이 되고, 연작지 토양내 병든 식물의 유체 등도 1차 전염원으로 중요하다.\nTMV는 진딧물에 의하여 전염되는 것이 아니고, 접촉전염이 되는데 자연감염 기주가 전염원으로 주위에 있으면 발병이 잘 된다.\n또한 이 바이러스는 기주범위가 넓어서 가지과, 국화과, 콩과 등 쌍자엽 식물을 주로 하여 22과 200종 이상 침해한다.\n특히 토마토, 피만, 고추, 담배가 주로 발병되는 작물이다.','[방제 방법]\n○ CMV 방제\n- 진딧물이 전염시키므로 진딧물의 기주를 제거한다.\n- 등록된 살충제를 살포하여 진딧물을 방제한다\n- 전 작물의 잔재물을 제거하고, 작물의 파종시기 및 올멱심기 시기를 조절한다.\n- 바이러스의 잠재적인 보존원인 잡초나 중간기주를 제거한다.\n- 전염원이 되는 병든 식물은 발견 즉시 제거한다.\n○ PepMoV 방제\n- 복숭아혹진딧물의 기주식물인 가지과, 배추과 등을 주위에 재배하지 않는다.\n- 자연 발병 기주인 담배, 고추, 감자 등을 연속 재배하지 말아야 한다.\n- 병든 식물체는 일찍 제거한다.\n- 등록된 살충제를 살포하여 진딧물을 방제한다.\n- 병에 잘 걸리지 않는 품종을 재배한다.\n○ TMV 및 ToMV 방제\n- 고추와 토마토를 연속재배하지 말아야 한다.\n- 종자 소독을 철저히 한 후 파종한다.\n- 오염 토양, 옷, 손, 농기구들의 오염물을 제거한다.\n- 옮겨심기, 눈따기, 수확 등 작업 시에 전염이 되므로 주의하여야 하며 작업 전에는 반드시 손을 닦아야 한다\n- 전염원으로부터 격리된 지역에서 재배한다.\n- 전염원이 되는 병든식물은 발견 즉시 제거한다.'),(17,'Tomato___healthy','TOMATO','토마토 정상','잎에서 뚜렷한 병징이 발견되지 않았습니다.','별도 방제가 필요하지 않습니다. 통풍·배수·균형 시비 등 기본 관리를 유지하고 주기적으로 잎을 살펴보세요.');
/*!40000 ALTER TABLE `disease` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

