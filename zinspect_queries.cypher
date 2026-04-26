// ============================================================
// ZInspect Ontoloji — Neo4j Cypher Sorgu Kütüphanesi
// Eskişehir Osmangazi Üniversitesi — Bitirme Projesi
// ============================================================


// ------------------------------------------------------------
// BÖLÜM 1: VERİ BÜTÜNLÜĞÜ KONTROL SORGULARI
// ------------------------------------------------------------

// Q1 — Toplam node sayısı
MATCH (n) 
RETURN count(n) AS toplam_node;

// Q2 — İlişki tipleri ve adetleri
MATCH ()-[r]->() 
RETURN DISTINCT type(r) AS iliski_tipi, count(r) AS adet
ORDER BY adet DESC;

// Q3 — Tüm individual'lar
MATCH (s:Individual) 
RETURN s.name AS individual
ORDER BY s.name;

// Q4 — Tüm individual ilişkileri (ilk 50)
MATCH (s:Individual)-[r]->(o:Individual)
RETURN s.name AS kaynak, type(r) AS iliski, o.name AS hedef
ORDER BY s.name
LIMIT 50;


// ------------------------------------------------------------
// BÖLÜM 2: Z-INSPECTION AŞAMA 1 — KAPSAM BELİRLEME
// ------------------------------------------------------------

// Q5 — Sistem envanteri (tip bazlı)
MATCH (s:Individual)-[:INSTANCE_OF]->(c:OWLClass)
WHERE c.name IN ["AiSystem", "BiometricIdentificationSystem", 
                 "HRRecruitmentSystem", "EducationAISystem"]
RETURN s.name AS YZ_Sistemi, c.name AS Sistem_Tipi
ORDER BY c.name;

// Q6 — Sektör dağılımı
MATCH (s:Individual)-[:HAS_SECTOR]->(sektor:Individual)
RETURN sektor.name AS Sektor, 
       collect(s.name) AS Sistemler, 
       count(s) AS Sistem_Sayisi
ORDER BY Sistem_Sayisi DESC;

// Q7 — Karar tipi analizi
MATCH (s:Individual)-[:HAS_DECISION_TYPE]->(d:Individual)
RETURN s.name AS YZ_Sistemi, d.name AS Karar_Tipi
ORDER BY s.name;


// ------------------------------------------------------------
// BÖLÜM 3: Z-INSPECTION AŞAMA 2 — DEĞERLENDİRME
// ------------------------------------------------------------

// Q8 — Risk seviyeleri (S1, S2 SWRL kural çıktıları)
MATCH (s:Individual)-[:HAS_RISK_LEVEL]->(r:Individual)
RETURN s.name AS YZ_Sistemi, r.name AS Risk_Seviyesi
ORDER BY r.name;

// Q9 — Otomasyon seviyeleri
MATCH (s:Individual)-[:HAS_AUTOMATION_LEVEL]->(a:Individual)
RETURN s.name AS YZ_Sistemi, a.name AS Otomasyon_Seviyesi;

// Q10 — Etik ihlaller (violates ilişkisi)
MATCH (s:Individual)-[:VIOLATES]->(p:Individual)
RETURN s.name AS YZ_Sistemi, p.name AS Ihlal_Edilen_Ilke
ORDER BY s.name;

// Q11 — Etik gerilimler
MATCH (s:Individual)-[:HAS_ETHICAL_TENSION]->(t:Individual)
WITH s, count(t) AS gerilim_sayisi, collect(t.name) AS gerilimler
RETURN s.name AS YZ_Sistemi, 
       gerilim_sayisi AS Gerilim_Sayisi, 
       gerilimler AS Gerilimler
ORDER BY gerilim_sayisi DESC;

// Q12 — İlke çatışmaları (döngü tespiti)
MATCH (a:Individual)-[:CONFLICTS_WITH]->(b:Individual)
RETURN a.name AS Ilke_1, b.name AS Ilke_2;

// Q13 — Yasal dayanak kontrolü (KVKK/GDPR)
MATCH (s:Individual)-[:HAS_LEGAL_BASIS]->(l:Individual)
RETURN s.name AS YZ_Sistemi, l.name AS Yasal_Durum;

// Q14 — Kamuya açık alanda çalışan sistemler
MATCH (s:Individual)-[:HAS_USER_AREA]->(a:Individual)
WHERE a.name = "PublicSpace"
RETURN s.name AS Sistem, a.name AS Alan;


// ------------------------------------------------------------
// BÖLÜM 4: Z-INSPECTION AŞAMA 3 — ÇÖZÜM
// ------------------------------------------------------------

// Q15 — İnsan denetimi zorunlulukları (S3 SWRL kural çıktısı)
MATCH (s:Individual)-[:REQUIRES]->(o:Individual)
RETURN s.name AS YZ_Sistemi, o.name AS Zorunluluk
ORDER BY s.name;

// Q16 — Etkilenen paydaşlar
MATCH (s:Individual)-[:AFFECTS]->(p:Individual)
RETURN s.name AS YZ_Sistemi, collect(p.name) AS Etkilenen_Kisiler;

// Q17 — Risk yayılımı (çok atlamalı)
MATCH path = (s:Individual)-[:AFFECTS*1..3]->(p:Individual)
RETURN s.name AS Kaynak_Sistem, 
       length(path) AS Atlama_Sayisi,
       p.name AS Etkilenen
ORDER BY Atlama_Sayisi;


// ------------------------------------------------------------
// BÖLÜM 5: TAM SİSTEM PROFİLİ (FastAPI /assess endpoint'i)
// ------------------------------------------------------------

// Q18 — Tek sistemin tam Z-Inspection profili
// Kullanım: ClearviewAI_System yerine sorgulanacak sistemi yaz
MATCH (s:Individual {name: "ClearviewAI_System"})
OPTIONAL MATCH (s)-[:HAS_RISK_LEVEL]->(risk)
OPTIONAL MATCH (s)-[:VIOLATES]->(ilke)
OPTIONAL MATCH (s)-[:HAS_ETHICAL_TENSION]->(gerilim)
OPTIONAL MATCH (s)-[:HAS_SECTOR]->(sektor)
OPTIONAL MATCH (s)-[:HAS_DECISION_TYPE]->(karar)
OPTIONAL MATCH (s)-[:REQUIRES]->(zorunluluk)
OPTIONAL MATCH (s)-[:HAS_LEGAL_BASIS]->(yasal)
OPTIONAL MATCH (s)-[:AFFECTS]->(etkilenen)
RETURN s.name AS Sistem,
       collect(DISTINCT risk.name) AS Risk_Seviyeleri,
       collect(DISTINCT ilke.name) AS Ihlaller,
       collect(DISTINCT gerilim.name) AS Etik_Gerilimler,
       collect(DISTINCT sektor.name) AS Sektor,
       collect(DISTINCT karar.name) AS Karar_Tipleri,
       collect(DISTINCT zorunluluk.name) AS Zorunluluklar,
       collect(DISTINCT yasal.name) AS Yasal_Durum,
       collect(DISTINCT etkilenen.name) AS Etkilenen_Kisiler;

// Q19 — Tüm sistemlerin özet tablosu
MATCH (s:Individual)-[:HAS_SECTOR]->(sektor:Individual)
OPTIONAL MATCH (s)-[:HAS_RISK_LEVEL]->(risk)
OPTIONAL MATCH (s)-[:REQUIRES]->(zorunluluk)
OPTIONAL MATCH (s)-[:HAS_DECISION_TYPE]->(karar)
RETURN s.name AS Sistem,
       sektor.name AS Sektor,
       collect(DISTINCT risk.name) AS Risk,
       collect(DISTINCT karar.name) AS Karar_Tipleri,
       collect(DISTINCT zorunluluk.name) AS Zorunluluklar
ORDER BY s.name;


// ------------------------------------------------------------
// BÖLÜM 6: ERC SKORU HESAPLAMA (Risk Katsayısı)
// ------------------------------------------------------------

// Q20 — Bağlantı sayısına göre risk skoru (ham ERC)
MATCH (s:Individual)-[r]->()
WITH s, count(r) AS baglanti_sayisi
WHERE baglanti_sayisi > 1
RETURN s.name AS Sistem, 
       baglanti_sayisi AS ERC_Ham_Skor
ORDER BY ERC_Ham_Skor DESC
LIMIT 10;

// Q21 — Ağırlıklı ERC hesaplama
// (ihlal=3 puan, gerilim=2 puan, diğer=1 puan)
MATCH (s:Individual)
OPTIONAL MATCH (s)-[:VIOLATES]->(v)
OPTIONAL MATCH (s)-[:HAS_ETHICAL_TENSION]->(t)
OPTIONAL MATCH (s)-[:REQUIRES]->(r)
WITH s,
     count(DISTINCT v) * 3 AS ihlal_puani,
     count(DISTINCT t) * 2 AS gerilim_puani,
     count(DISTINCT r) * 1 AS zorunluluk_puani
WHERE (ihlal_puani + gerilim_puani + zorunluluk_puani) > 0
RETURN s.name AS Sistem,
       ihlal_puani AS Ihlal_Puani,
       gerilim_puani AS Gerilim_Puani,
       zorunluluk_puani AS Zorunluluk_Puani,
       (ihlal_puani + gerilim_puani + zorunluluk_puani) AS TOPLAM_ERC
ORDER BY TOPLAM_ERC DESC;


// ------------------------------------------------------------
// BÖLÜM 7: BENCHMARK VAKA ANALİZİ (Tez Bölüm 5)
// ------------------------------------------------------------

// Q22 — COMPAS sistemi analizi
MATCH (s:Individual {name: "COMPAS_RecidivismSystem"})
OPTIONAL MATCH (s)-[r]->(o:Individual)
RETURN s.name AS Sistem, type(r) AS Iliski, o.name AS Hedef;

// Q23 — Amazon HR analizi  
MATCH (s:Individual {name: "AmazonHR_CVFilter"})
OPTIONAL MATCH (s)-[r]->(o:Individual)
RETURN s.name AS Sistem, type(r) AS Iliski, o.name AS Hedef;

// Q24 — ClearviewAI analizi
MATCH (s:Individual {name: "ClearviewAI_System"})
OPTIONAL MATCH (s)-[r]->(o:Individual)
RETURN s.name AS Sistem, type(r) AS Iliski, o.name AS Hedef;

// Q25 — Tüm benchmark vakalarının karşılaştırması
MATCH (s:Individual)
WHERE s.name IN ["ClearviewAI_System", "AmazonHR_CVFilter", 
                 "COMPAS_RecidivismSystem", "AutoHiringSystem",
                 "StudentGradingSystem"]
OPTIONAL MATCH (s)-[:HAS_RISK_LEVEL]->(risk)
OPTIONAL MATCH (s)-[:VIOLATES]->(ilke)
OPTIONAL MATCH (s)-[:REQUIRES]->(zorunluluk)
RETURN s.name AS Sistem,
       collect(DISTINCT risk.name) AS Risk,
       count(DISTINCT ilke) AS Ihlal_Sayisi,
       collect(DISTINCT zorunluluk.name) AS Zorunluluklar
ORDER BY Ihlal_Sayisi DESC;
