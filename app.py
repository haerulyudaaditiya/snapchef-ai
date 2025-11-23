import streamlit as st
from google import genai
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SnapChef AI",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL UI STYLING (CSS) ---
st.markdown("""
    <style>
    /* 1. Main Background & Text Color - Adaptive for Light/Dark Mode */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* CSS Variables for Theme Adaptation */
    :root {
        --primary-color: #2E8B57;
        --primary-dark: #1F6B45;
        --secondary-color: #4A90E2;
        --background-color: #FFFFFF;
        --surface-color: #F8F9FA;
        --text-color: #212529;
        --text-secondary: #6C757D;
        --border-color: #E9ECEF;
        --card-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0E1117;
            --surface-color: #262730;
            --text-color: #FAFAFA;
            --text-secondary: #A0A4AB;
            --border-color: #424242;
            --card-shadow: 0 2px 12px rgba(0,0,0,0.3);
        }
    }
    
    /* 2. Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    p, div, label, li, span {
        color: var(--text-color) !important;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* 3. Button Styling */
    .stButton>button {
        background-color: var(--primary-color);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-dark);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3);
    }
    
    .stButton>button:focus {
        box-shadow: 0 0 0 2px rgba(46, 139, 87, 0.3);
    }
    
    /* 4. Card Container Styling */
    .main-card {
        background-color: var(--surface-color);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
    }
    
    /* 5. Image Styling */
    .uploaded-image {
        border-radius: 8px;
        border: 1px solid var(--border-color);
        width: 100%;
        height: auto;
    }
    
    /* 6. Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--surface-color);
        border-right: 1px solid var(--border-color);
    }
    
    /* 7. Input Field Styling */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stSlider>div>div>div>div {
        background-color: var(--background-color);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 6px;
    }
    
    /* 8. Success/Error Messages */
    .stSuccess {
        background-color: rgba(46, 139, 87, 0.1);
        border: 1px solid var(--primary-color);
        border-radius: 6px;
    }
    
    .stError {
        background-color: rgba(220, 53, 69, 0.1);
        border: 1px solid #dc3545;
        border-radius: 6px;
    }
    
    /* 9. Custom Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* 10. Result Container */
    .recipe-result {
        background-color: var(--surface-color);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI FUNCTION (BACKEND) ---
def generate_recipe(image, diet_type, difficulty, allergies):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        
    if not api_key:
        return "ERROR_KEY_MISSING"

    try:
        client = genai.Client(api_key=api_key)
        
        # Model yang tersedia berdasarkan test
        model_names = [
            "gemini-2.0-flash",  # Model utama - cepat dan efisien
            "gemini-2.0-flash-lite",  # Alternatif 1
            "gemini-pro-latest",  # Alternatif 2  
            "gemini-flash-latest",  # Alternatif 3
            "gemini-2.0-flash-001"  # Alternatif 4
        ]
        
        prompt_text = f"""
        Anda adalah Chef Profesional 'SnapChef'. 
        Analisis gambar bahan makanan yang diberikan dan buat resep masakan yang sesuai.

        INFORMASI PENGGUNA:
        - Tipe Diet: {diet_type}
        - Level Kemampuan Memasak: {difficulty}
        - Alergi/Pantangan: {allergies if allergies else "Tidak ada"}

        TUGAS:
        1. Identifikasi bahan makanan yang terlihat dalam gambar
        2. Buat resep masakan yang sesuai dengan bahan yang tersedia
        3. Sesuaikan dengan preferensi diet dan hindari bahan alergi
        4. Berikan instruksi yang sesuai dengan level kemampuan pengguna

        FORMAT OUTPUT (gunakan Markdown):

        # [NAMA MASAKAN]

        **Deskripsi:** [Deskripsi singkat 1-2 kalimat tentang masakan ini]

        ## Informasi Nutrisi (Per Porsi)
        | Kalori | Protein | Karbohidrat | Lemak |
        |--------|---------|-------------|-------|
        | [isi] kkal | [isi] g | [isi] g | [isi] g |

        ## Bahan-bahan
        **Bahan Utama:**
        - [daftar bahan utama]

        **Bumbu dan Pelengkap:**
        - [daftar bumbu]

        ## Langkah Pembuatan
        1. **[Langkah 1]** - [penjelasan detail dan jelas]
        2. **[Langkah 2]** - [penjelasan detail dan jelas]
        3. [lanjutkan sesuai kebutuhan]

        **Tips Chef:** [Tips berguna untuk hasil terbaik]
        **Waktu Penyiapan:** [Perkiraan waktu persiapan dan memasak]
        **Tingkat Kesulitan:** {difficulty}
        """

        # Coba model yang tersedia
        for model_name in model_names:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt_text, image]
                )
                return response.text
            except Exception as model_error:
                if "not found" in str(model_error).lower() or "404" in str(model_error):
                    continue  # Coba model berikutnya
                else:
                    # Jika error lain, mungkin model ada tapi error lain
                    continue
        else:
            return "ERROR_MODEL_NOT_FOUND: Tidak ada model Gemini yang berhasil"
            
    except Exception as e:
        return f"ERROR_SYSTEM: {str(e)}"

# --- UI LAYOUT ---

# 1. Header Section
st.markdown("<div>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>SnapChef AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 0;'>Transformasikan bahan makanan menjadi resep masakan berkualitas</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 2. Sidebar Configuration
with st.sidebar:
    st.markdown("<h3>Konfigurasi</h3>", unsafe_allow_html=True)
    
    st.markdown("**Preferensi Diet**")
    diet_type = st.selectbox(
        "Pola Makan:", 
        ["Seimbang", "Sehat & Rendah Kalori", "High Protein", "Vegetarian", "Vegan", "Keto"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("**Tingkat Kemampuan**")
    difficulty = st.select_slider(
        "Kemampuan Memasak:",
        options=["Pemula", "Menengah", "Lanjutan"],
        value="Menengah",
        label_visibility="collapsed"
    )
    
    st.markdown("**Pantangan Makanan**")
    allergies = st.text_input(
        "Alergi atau Pantangan:",
        placeholder="Contoh: kacang, seafood, gluten",
        label_visibility="collapsed"
    )
    
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    
    st.markdown("**Panduan Penggunaan**")
    st.markdown("<small style='color: var(--text-secondary);'>• Gunakan foto dengan pencahayaan baik</small>", unsafe_allow_html=True)
    st.markdown("<small style='color: var(--text-secondary);'>• Pastikan bahan makanan terlihat jelas</small>", unsafe_allow_html=True)
    st.markdown("<small style='color: var(--text-secondary);'>• Foto dari berbagai angle untuk hasil optimal</small>", unsafe_allow_html=True)

# 3. Main Content Area
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<div>", unsafe_allow_html=True)
    st.markdown("### Input Bahan Makanan")
    
    image = None

    uploaded_file = st.file_uploader(
        "Unggah gambar bahan makanan",
        type=["jpg", "jpeg", "png"],
        help="Pilih gambar berisi bahan makanan yang ingin diolah"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Pratinjau Gambar", use_container_width=True)
        st.success("Gambar berhasil dimuat dan siap diproses")
    else:
        st.info("Silakan unggah gambar bahan makanan untuk memulai")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div>", unsafe_allow_html=True)
    st.markdown("### Hasil Resep")
    
    if uploaded_file:
        if st.button("Buat Resep", type="primary", use_container_width=True):
            with st.spinner("Menganalisis bahan dan membuat resep..."):
                result = generate_recipe(image, diet_type, difficulty, allergies)
                
                if result == "ERROR_KEY_MISSING":
                    st.error("API Key tidak ditemukan. Harap periksa konfigurasi environment variables.")
                elif isinstance(result, str) and "ERROR_MODEL_NOT_FOUND" in result:
                    st.error("Model AI tidak tersedia. Periksa dokumentasi untuk model yang didukung.")
                elif isinstance(result, str) and result.startswith("ERROR_SYSTEM"):
                    st.error("Terjadi kesalahan sistem. Periksa koneksi internet dan coba lagi.")
                    with st.expander("Detail Error"):
                        st.code(result)
                else:
                    st.markdown("<div>", unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Success indicator
                    st.toast("Resep berhasil dibuat!", icon="✅")
    else:
        st.info("Unggah gambar di kolom sebelah kiri untuk menghasilkan resep")
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Footer
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: var(--text-secondary); font-size: 0.9rem;'>"
    "SnapChef AI • Powered by Google Gemini • Final Project AI Tools"
    "</div>", 
    unsafe_allow_html=True
)