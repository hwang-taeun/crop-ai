"""17개 라벨의 한글명 / NCPMS 검색어 / 종류.

kind: disease(NCPMS 병 API로 조회) | pest(해충이라 병 API 대상 아님) | healthy(정상 잎)
name_ko·search·eng 는 추정값이다(eng = NCPMS 영문 병명에 들어갈 말, 대소문자 무시). NCPMS 실제 병명과 다르면 여기만 고치면 된다. (검수 필요)
"""

LABELS_KO = {
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": dict(crop="CORN", crop_kor="옥수수", name_ko="옥수수 잿빛무늬병", search="잿빛무늬병", kind="disease", eng="Gray leaf spot"),
    "Corn_(maize)___Common_rust_": dict(crop="CORN", crop_kor="옥수수", name_ko="옥수수 녹병", search="녹병", kind="disease", eng="Common rust"),
    "Corn_(maize)___Northern_Leaf_Blight": dict(crop="CORN", crop_kor="옥수수", name_ko="옥수수 그을음무늬병", search="그을음무늬병", kind="disease", eng="Northern"),
    "Corn_(maize)___healthy": dict(crop="CORN", crop_kor="옥수수", name_ko="옥수수 정상", search="", kind="healthy"),
    "Potato___Early_blight": dict(crop="POTATO", crop_kor="감자", name_ko="감자 겹둥근무늬병", search="겹둥근무늬병", kind="disease", eng="Early blight"),
    "Potato___Late_blight": dict(crop="POTATO", crop_kor="감자", name_ko="감자 역병", search="역병", kind="disease", eng="Late blight"),
    "Potato___healthy": dict(crop="POTATO", crop_kor="감자", name_ko="감자 정상", search="", kind="healthy"),
    "Tomato___Bacterial_spot": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 세균점무늬병", search="세균점무늬병", kind="disease", eng="Bacterial spot"),
    "Tomato___Early_blight": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 겹둥근무늬병", search="겹둥근무늬병", kind="disease", eng="Early blight"),
    "Tomato___Late_blight": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 역병", search="역병", kind="disease", eng="Late blight"),
    "Tomato___Leaf_Mold": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 잎곰팡이병", search="잎곰팡이병", kind="disease", eng="Leaf mold"),
    "Tomato___Septoria_leaf_spot": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 흰무늬병", search="흰무늬병", kind="disease", eng="Septoria leaf spot"),
    "Tomato___Spider_mites Two-spotted_spider_mite": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 점박이응애", search="", kind="pest"),
    "Tomato___Target_Spot": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 갈색무늬병", search="갈색무늬병", kind="disease", eng="Target spot"),
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 황화잎말림바이러스병", search="황화잎말림바이러스", kind="disease", eng="Yellow leaf curl"),
    "Tomato___Tomato_mosaic_virus": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 모자이크바이러스병", search="모자이크병", kind="disease", eng="Tomato mosaic"),
    "Tomato___healthy": dict(crop="TOMATO", crop_kor="토마토", name_ko="토마토 정상", search="", kind="healthy"),
}

# NCPMS 병 API로 가져올 수 없는 라벨의 고정 문구 (정상 잎 / 해충). 필요하면 팀에서 고쳐 쓴다.
_HEALTHY = ("잎에서 뚜렷한 병징이 발견되지 않았습니다.",
            "별도 방제가 필요하지 않습니다. 통풍·배수·균형 시비 등 기본 관리를 유지하고 주기적으로 잎을 살펴보세요.")
STATIC_TEXT = {
    label: _HEALTHY for label, m in LABELS_KO.items() if m["kind"] == "healthy"
}
STATIC_TEXT["Tomato___Spider_mites Two-spotted_spider_mite"] = (
    "잎 앞면에 작고 하얀 점이 촘촘히 생기고 심하면 잎이 누렇게 변하며, 잎 뒷면에 거미줄 같은 실과 작은 응애가 보입니다. 고온·건조할 때 급증합니다.",
    "피해 잎을 제거하고 시설 내 습도와 통풍을 관리하세요. 천적 활용이나 등록된 약제 사용은 농업기술센터나 농약안전정보시스템에서 확인한 뒤 제품 라벨에 따라 적용하세요.",
)
