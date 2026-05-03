import sys
from pathlib import Path

from dotenv import load_dotenv

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

load_dotenv(_root / ".env")

from services.chroma_client import get_or_create_collection  # noqa: E402

LEGAL_CHUNKS = [
    # EU AI Act - High Risk
    {
        "id": "euaia_art5",
        "text": "Article 5 - Prohibited AI Practices: Real-time remote biometric identification systems in publicly accessible spaces for law enforcement purposes are prohibited, except in specific cases.",
        "metadata": {"source": "EU_AI_Act", "article": "Article 5", "category": "prohibited"}
    },
    {
        "id": "euaia_art9",
        "text": "Article 9 - Risk Management System: A risk management system shall be established, implemented, documented and maintained for high-risk AI systems throughout their entire lifecycle.",
        "metadata": {"source": "EU_AI_Act", "article": "Article 9", "category": "high_risk"}
    },
    {
        "id": "euaia_art13",
        "text": "Article 13 - Transparency and Provision of Information: High-risk AI systems shall be designed and developed in such a way to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output.",
        "metadata": {"source": "EU_AI_Act", "article": "Article 13", "category": "transparency"}
    },
    {
        "id": "euaia_art14",
        "text": "Article 14 - Human Oversight: High-risk AI systems shall be designed and developed in such a way, including with appropriate human-machine interface tools, that they can be effectively overseen by natural persons during the period in which the AI system is in use.",
        "metadata": {"source": "EU_AI_Act", "article": "Article 14", "category": "human_oversight"}
    },
    {
        "id": "euaia_art52",
        "text": "Article 52 - Transparency Obligations for Certain AI Systems: Providers shall ensure that AI systems intended to interact with natural persons are designed and developed in such a way that the natural persons are informed that they are interacting with an AI system.",
        "metadata": {"source": "EU_AI_Act", "article": "Article 52", "category": "transparency"}
    },
    {
        "id": "euaia_art10",
        "text": "Article 10 - Data and Data Governance: Training, validation and testing data sets shall be subject to appropriate data governance and management practices. They shall be relevant, sufficiently representative and free of errors.",
        "metadata": {"source": "EU_AI_Act", "article": "Article 10", "category": "data_governance"}
    },
    # GDPR
    {
        "id": "gdpr_art9",
        "text": "GDPR Article 9 - Processing of special categories of personal data: Processing of personal data revealing racial or ethnic origin, political opinions, religious beliefs, biometric data for the purpose of uniquely identifying a natural person is prohibited.",
        "metadata": {"source": "GDPR", "article": "Article 9", "category": "sensitive_data"}
    },
    {
        "id": "gdpr_art22",
        "text": "GDPR Article 22 - Automated individual decision-making: The data subject shall have the right not to be subject to a decision based solely on automated processing, including profiling, which produces legal effects concerning him or her.",
        "metadata": {"source": "GDPR", "article": "Article 22", "category": "automated_decision"}
    },
    {
        "id": "gdpr_art5",
        "text": "GDPR Article 5 - Principles relating to processing: Personal data shall be processed lawfully, fairly and in a transparent manner. Data minimisation principle requires that data is adequate, relevant and limited to what is necessary.",
        "metadata": {"source": "GDPR", "article": "Article 5", "category": "principles"}
    },
    # KVKK
    {
        "id": "kvkk_art6",
        "text": "KVKK Madde 6 - Özel Nitelikli Kişisel Verilerin İşlenmesi: Kişilerin ırkı, etnik kökeni, siyasi düşüncesi, felsefi inancı, dini, mezhebi veya diğer inançları, kılık ve kıyafeti, dernek, vakıf ya da sendika üyeliği, sağlığı, cinsel hayatı, ceza mahkûmiyeti ve güvenlik tedbirleriyle ilgili verileri ile biyometrik ve genetik verileri özel nitelikli kişisel veridir.",
        "metadata": {"source": "KVKK", "article": "Madde 6", "category": "sensitive_data"}
    },
    {
        "id": "kvkk_art12",
        "text": "KVKK Madde 12 - Veri Güvenliğine İlişkin Yükümlülükler: Veri sorumlusu, kişisel verilerin hukuka aykırı olarak işlenmesini önlemek, verilere hukuka aykırı olarak erişilmesini önlemek ve verilerin muhafazasını sağlamak amacıyla uygun güvenlik düzeyini temin etmeye yönelik gerekli teknik ve idari tedbirleri almak zorundadır.",
        "metadata": {"source": "KVKK", "article": "Madde 12", "category": "data_security"}
    },
    # Z-Inspection
    {
        "id": "zinspect_privacy",
        "text": "Z-Inspection Privacy Principle: AI systems must respect privacy and data protection. This includes data minimization, purpose limitation, and ensuring individuals maintain control over their personal data.",
        "metadata": {"source": "Z_Inspection", "article": "Privacy", "category": "ethical_principle"}
    },
    {
        "id": "zinspect_fairness",
        "text": "Z-Inspection Fairness and Non-Discrimination: AI systems must avoid unfair bias and discrimination. Systems should be tested for disparate impact across protected groups including race, gender, age, and disability.",
        "metadata": {"source": "Z_Inspection", "article": "Fairness", "category": "ethical_principle"}
    },
    {
        "id": "zinspect_transparency",
        "text": "Z-Inspection Transparency: AI systems must be sufficiently transparent. Stakeholders should be informed about the AI system's capabilities and limitations. Explainability should be ensured to the degree possible.",
        "metadata": {"source": "Z_Inspection", "article": "Transparency", "category": "ethical_principle"}
    },
    {
        "id": "zinspect_accountability",
        "text": "Z-Inspection Accountability: Mechanisms must be in place to ensure responsibility and accountability for AI systems. This includes audit trails, documentation, and clear assignment of responsibility.",
        "metadata": {"source": "Z_Inspection", "article": "Accountability", "category": "ethical_principle"}
    },
    {
        "id": "zinspect_human_oversight",
        "text": "Z-Inspection Human Agency and Oversight: AI systems should support human autonomy and decision-making. Human oversight mechanisms must be in place, especially for high-stakes decisions affecting individuals.",
        "metadata": {"source": "Z_Inspection", "article": "Human_Oversight", "category": "ethical_principle"}
    },
]


def load_documents():
    collection = get_or_create_collection()
    existing = collection.get()
    existing_ids = set(existing["ids"])

    new_docs = [d for d in LEGAL_CHUNKS if d["id"] not in existing_ids]

    if not new_docs:
        print("All documents already loaded.")
        return

    collection.add(
        ids=[d["id"] for d in new_docs],
        documents=[d["text"] for d in new_docs],
        metadatas=[d["metadata"] for d in new_docs]
    )
    print(f"Loaded {len(new_docs)} documents into ChromaDB")


if __name__ == "__main__":
    load_documents()
