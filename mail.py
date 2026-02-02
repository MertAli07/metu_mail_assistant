import streamlit as st
# import streamlit.components.v1 as components
import requests
import os
from datetime import datetime
import time
 
# --- CONFIG & STYLING ---
st.set_page_config(page_title="Mail Assistant Pro", page_icon="✨", layout="wide")
 
# --- BACKEND FUNCTIONS ---
 
# Goaltech Lambda URL
LAMBDA_URL = "https://ngohy4i3pcv5j36nejdmjbcgpq0egfou.lambda-url.eu-central-1.on.aws/"
 
def get_ai_suggestion(user_text):
    """Fetches AI suggestion from AWS Lambda."""
    payload = {"input": {"query": user_text}}
    try:
        # Real Call to Lambda
        response = requests.post(LAMBDA_URL, json=payload, timeout=500)
        response.raise_for_status()
        return response.json().get("result", "AI Suggestion received, but output key was missing.")
    except Exception as e:
        return f"⚠️ Error connecting to AI Agent: {str(e)}"
 
# --- INITIALIZATION ---
 
# Initialize Session State Variables directly (No Auth needed)
if "outbox" not in st.session_state:
    st.session_state.outbox = []
if "selected_example" not in st.session_state:
    st.session_state.selected_example = None
if "name" not in st.session_state:
    st.session_state.name = "Demo User" # Default name for the UI
 
# --- MAIN APP LAYOUT ---
 
# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/666/666162.png", width=50)
    st.markdown(f"### Hello, {st.session_state['name'].split()[0]}! 👋")
    
    st.markdown("---")
    
    # Navigation
    menu = st.radio("Navigation", ["📥 Incoming", "✍️ Compose", "📊 Diagram", "ℹ️ About"], label_visibility="collapsed")
    
    st.markdown("---")
    st.caption("QUICK TEMPLATES")
    
    # Example Questions
    examples = [
        # --- Orijinal Sorular ---
        {"label": "🎓 Instructor Change", "to": "hotline@metu.edu.tr", "subject": "Instructor Change Request", "body": "Merhaba. Bu Dönem emekli olan bölümümüz hocalarından Prof.Dr. Ali Eryılmazın\nöğrencisi 2599686 numaralı öğrencisi Semra Sıkıra'ın Danışman değişikliği\nyapması gerekmektedir. Ali hocamız sisteme giremediği için öğrenciyi\nbırakamıyor. Nasıl yapabiliriz?\n\n\nKevser Özkan \n\n4049"},
        {"label": "🔒 VPN Issue", "to": "hotline@metu.edu.tr", "subject": "VPN Connection Problem", "body": "Merhaba hocam,\n\nİyi günler, VPN indirdiğim masaüstü bilgisayarımda eklerde belirttiğim gibi bir uyarı alıyorum ve indirmek istediğim lisanslı uygulamaların olduğu “https:\/\/software.cc.metu.edu.tr\/download.php” linke ulaşamıyorum. VPN bağlandığı halde bu linke tıkladığımda güvenli bulunmadığından yine bağlanamıyorum. Yardımcı olursanız çok sevinirim.\n\nTeşekkürler,\nAzra"},
        {"label": "❓ Eduroam", "to": "academic@metu.edu.tr", "subject": "Cannot Connect to Eduroam", "body": "Merhaba hocam,\n\nİyi günler, eduroma nasıl bağlanabilirim? İyi çalışmalar, Mert Ali Yalçın"},
        
        # --- Genel Bilgi Soruları ---
        {"label": "🇬🇧 Eğitim Dili", "to": "tanitim@metu.edu.tr", "subject": "Eğitim Dili Hakkında Bilgi", "body": "Merhaba,\n\nODTÜ'de eğitim dili nedir? Tamamı İngilizce mi yoksa Türkçe bölümler de var mı?\n\nSaygılarımla."},
        {"label": "💰 Burs Olanakları", "to": "bursofisi@metu.edu.tr", "subject": "Burs Olanakları Hakkında", "body": "İyi günler,\n\nÜniversitenizin sunduğu burs olanakları nelerdir? Başarı bursu ve ihtiyaç bursu kriterleri hakkında bilgi alabilir miyim?\n\nTeşekkürler."},
        {"label": "🤝 Mezun Ağı", "to": "mezun@metu.edu.tr", "subject": "Mezun İletişim Ağı", "body": "Merhaba,\n\nODTÜ mezunları arası iletişim ve bilgi ağı ne kadar gelişmiş durumda? Mezunlar Derneği'nin aktif çalışmaları var mı?"},
        {"label": "❓ Genel Sorular", "to": "iletisim@metu.edu.tr", "subject": "İlgili Birim Yönlendirmesi", "body": "Merhaba,\n\nODTÜ ile ilgili genel sorularım var, hangi birim ile görüşmeliyim? Yönlendirebilirseniz sevinirim."},
        
        # --- Öğrenci İşleri (Kayıt/Ders) Soruları ---
        {"label": "📝 Ara Dönem Kayıt", "to": "oidb@metu.edu.tr", "subject": "Hazırlık Atlama ve Ara Dönem", "body": "Sayın Yetkili,\n\nKayıtlardan sonra birinci dönem sonunda İYS-IELTS-TOEFL-PTE belgelerinden herhangi birini vererek ara dönemde (Irregular olarak) birinci sınıf öğrencisi olunabilir mi?\n\nBilgilerinize arz ederim."},
        {"label": "📋 Geç Kayıt/Ekle-Bırak", "to": "oidb@metu.edu.tr", "subject": "Ders Ekleme-Bırakma ve Geç Kayıt Prosedürü", "body": "Sayın Yetkili,\n\nDers ekleme-bırakma süresi bittikten sonra ders ekleme-bırakma işlemleri nasıl yapılmaktadır?\n\nAyrıca, etkileşimli kayıtlarda kayıt yaptırmayan öğrencilerin kayıt işlemleri için izlemesi gereken prosedür nedir?\n\nBilgilerinize arz ederim."},
        {"label": "💼 Staj ve Sigorta", "to": "staj@metu.edu.tr", "subject": "Staj İşlemleri ve Sigorta Hakkında", "body": "Merhaba,\n\nStaj başvurusu ve staj süresince yaptırılan sigorta işlemleri ile ilgili detaylı bilgiyi nereden alabilirim? Başvuru sürecinde hangi belgeler gereklidir?\n\nYardımlarınız için teşekkürler."},
 
        # --- YENİ EKLENENLER (Diploma & Yan Dal) ---
        {"label": "📜 Diploma Kaybı", "to": "oidb@metu.edu.tr", "subject": "Diploma İkinci Nüsha Talebi", "body": "Sayın Yetkili,\n\nDiplomamı kaybettim. İkinci kopya (nüsha) sizden alabilir miyim? Bunun için gerekli prosedür ve belgeler nelerdir?\n\nBilgilerinize arz ederim."},
        {"label": "📚 İkinci Yan Dal", "to": "oidb@metu.edu.tr", "subject": "İkinci Yan Dal Programı Başvurusu", "body": "Merhaba,\n\nŞu anda bir yan dal programına kayıtlıyım. Başka bir program için başvuru yapabilir miyim? Kabul olmam halinde aynı anda iki yan dal programı izleyebilir miyim?\n\nSaygılarımla."}
    ]
    
    for ex in examples:
        if st.button(ex["label"], key=f"btn_{ex['label']}", use_container_width=True):
            st.session_state.selected_example = ex
            st.toast(f"Template loaded: {ex['label']}")
 
# --- PAGE: COMPOSE ---
if menu == "✍️ Compose":
    st.title("✍️ New Message")
    st.markdown("Draft your message below. The AI Agent will analyze replies.")
    
    # Session State'de anlık sonucu tutmak için değişken kontrolü
    if "latest_result" not in st.session_state:
        st.session_state.latest_result = None
 
    # Load template if selected
    if st.session_state.selected_example:
        default_to = st.session_state.selected_example["to"]
        default_sub = st.session_state.selected_example["subject"]
        default_body = st.session_state.selected_example["body"]
        st.session_state.selected_example = None # Reset
        # Yeni şablon yüklendiğinde eski sonucu temizle
        st.session_state.latest_result = None
    else:
        default_to = ""
        default_sub = ""
        default_body = ""
 
    col1, col2 = st.columns([3, 1])
    
    with col1:
        with st.container():
            # Session state keys kullanarak veriyi koruyoruz
            if 'form_to' not in st.session_state: st.session_state.form_to = default_to
            if 'form_sub' not in st.session_state: st.session_state.form_sub = default_sub
            if 'form_body' not in st.session_state: st.session_state.form_body = default_body
 
            if default_to:
                st.session_state.form_to = default_to
                st.session_state.form_sub = default_sub
                st.session_state.form_body = default_body
 
            with st.form("compose_form", clear_on_submit=False): # Formu temizlemiyoruz ki yazı kalsın
                to_addr = st.text_input("To", key="form_to", placeholder="recipient@metu.edu.tr")
                subject = st.text_input("Subject", key="form_sub", placeholder="Brief summary of the issue")
                body = st.text_area("Message Body", key="form_body", height=250)
                
                col_sub1, col_sub2 = st.columns([1, 5])
                with col_sub1:
                    submitted = st.form_submit_button("🚀 Send", use_container_width=True, type="primary")
                
                if submitted:
                    if to_addr and subject and body:
                        # İşlem başladığını göster
                        with st.spinner("AI Agent is analyzing the request..."):
                            # 1. AI'dan cevabı al
                            ai_response = get_ai_suggestion(body)
                            
                            # 2. Hem ekranda göstermek için kaydet
                            st.session_state.latest_result = ai_response
                            
                            # 3. Hem de Inbox'a (Incoming) kaydet
                            new_email = {
                                "id": int(time.time()),
                                "to": to_addr,
                                "subject": subject,
                                "body": body,
                                "time": datetime.now().strftime("%d %b, %H:%M"),
                                "read": False,
                                "ai_hint": ai_response # Cevabı direkt ekliyoruz
                            }
                            st.session_state.outbox.append(new_email)
                        
                        st.success("Message processed and saved!")
                    else:
                        st.warning("Please fill in all fields.")
 
        # --- SONUCU EKRANDA GÖSTERME ALANI ---
        if st.session_state.latest_result:
            st.markdown("---")
            st.subheader("⚡ Instant AI Analysis")
            
            # Sonucu chat balonu içinde göster
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(f"**AI Suggestion:**")
                st.write(st.session_state.latest_result)
                
                # Aksiyon butonları (Görsel amaçlı)
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve Draft", key="fast_approve"):
                    st.toast("Draft approved via Quick Action")
                if c2.button("🛠️ Edit Response", key="fast_edit"):
                    st.toast("Opened in editor mode")
 
    with col2:
        st.info("💡 **Tip:** The result will appear instantly below the form and will also be saved in your 'Incoming' folder.")
 
# --- PAGE: INCOMING ---
elif menu == "📥 Incoming":
    st.title("📥 Inbox")
    
    if not st.session_state.outbox:
        st.container().markdown("""
        <div style="text-align: center; padding: 50px; color: #666;">
            <h3>📭 Nothing here yet</h3>
            <p>Sent messages and their AI analysis will appear here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Reverse list to show newest first
        for email in reversed(st.session_state.outbox):
            
            # Custom HTML Card for the Email Header
            # Not: Renkler CSS içinde tanımlandı, burada class="email-card" yeterli.
            st.markdown(f"""
            <div class="email-card">
                <div style="display:flex; justify-content:space-between; font-size:0.8em;">
                    <span>To: {email['to']}</span>
                    <span>{email['time']}</span>
                </div>
                <h4>{email['subject']}</h4>
            </div>
            """, unsafe_allow_html=True)
 
            with st.expander("📄 View Content & AI Insights", expanded=False):
                st.markdown("**Message Content:**")
                st.text_area("", value=email['body'], height=100, disabled=True, key=f"body_{email['id']}")
                
                st.markdown("---")
                st.markdown("#### ✨ AI Agent Analysis")
                
                # Check if we already have the hint to avoid re-calling Lambda on every render
                if "ai_hint" not in email:
                    if st.button("🧠 Analyze with AI Agent", key=f"analyze_{email['id']}"):
                        with st.status("Connecting to Neural Network...", expanded=True) as status:
                            st.write("Extracting context...")
                            time.sleep(0.5)
                            st.write("Querying Lambda Knowledge Base...")
                            suggestion = get_ai_suggestion(email['body'])
                            email["ai_hint"] = suggestion
                            status.update(label="Analysis Complete!", state="complete", expanded=False)
                        st.rerun()
                
                # If analysis exists, show it nicely
                if "ai_hint" in email:
                    # Using Chat Message UI for the Agent
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(f"**Suggestion:**")
                        st.markdown(email["ai_hint"])
                        
                        st.markdown("---")
                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            st.button("✅ Approve Draft", key=f"app_{email['id']}")
                        with col_act2:
                            st.button("🛠️ Edit Response", key=f"edit_{email['id']}")

# --- PAGE: DIAGRAM ---
elif menu == "📊 Diagram":
    st.title("📊 System Architecture Diagram")
    st.markdown("Visual representation of the METU Mail Assistant system architecture.")
    
    # Read and display the diagram HTML
    diagram_path = os.path.join(os.path.dirname(__file__), "docs", "index.html")
    try:
        with open(diagram_path, "r", encoding="utf-8") as f:
            diagram_html = f.read()
        
        # Inject CSS to make background white
        white_bg_style = """
        <style>
            body {
                background-color: white !important;
                margin: 0;
                padding: 0;
            }
            html {
                background-color: white !important;
            }
            .mxgraph {
                background-color: white !important;
            }
            div[class*="mxgraph"] {
                background-color: white !important;
            }
            iframe {
                background-color: white !important;
            }
        </style>
        """
        # Insert style tag in head section
        if "</head>" in diagram_html:
            diagram_html = diagram_html.replace("</head>", white_bg_style + "</head>")
        elif "<body>" in diagram_html:
            # If no head tag, add style before body
            diagram_html = diagram_html.replace("<body>", white_bg_style + "<body style='background-color: white;'>")
        else:
            # Fallback: prepend style
            diagram_html = white_bg_style + diagram_html
        
        # Also modify body tag directly if it exists
        if "<body>" in diagram_html and 'style=' not in diagram_html.split("<body>")[1].split(">")[0]:
            diagram_html = diagram_html.replace("<body>", "<body style='background-color: white;'>")
        
        # Display the diagram with appropriate height
        components.html(diagram_html, height=1200, scrolling=True)
    except FileNotFoundError:
        st.error(f"Diagram file not found at: {diagram_path}")
    except Exception as e:
        st.error(f"Error loading diagram: {str(e)}")

# --- PAGE: ABOUT ---
elif menu == "ℹ️ About":
    st.title("About Mail Assistant")
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)
    st.markdown("""
    This application is a **Proof of Concept (PoC)** for the METU Mail Assistant project.
    
    **Architecture:**
    * **Frontend:** Streamlit (Python)
    * **Backend Logic:** AWS Lambda
    * **AI Model:** AWS Bedrock / Custom LLM Agent
    
    Built for demonstrating automated email classification and response drafting capabilities.
    """)