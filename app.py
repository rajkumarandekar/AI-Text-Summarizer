import streamlit as st
import validators
from urllib.parse import urlparse, parse_qs
import tempfile
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import RequestBlocked

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from langchain_community.document_loaders import (
    UnstructuredURLLoader,
    PyMuPDFLoader,
)

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="AI Universal Summarizer",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
}

.hero{
background:linear-gradient(135deg,#D8F3DC,#B7EFC5,#95D5B2);
padding:35px;
border-radius:20px;
text-align:center;
margin-bottom:25px;
box-shadow:0px 10px 25px rgba(0,0,0,.15);
}

.hero h1{
color:#1B4332;
font-size:42px;
}

.hero p{
color:#2D6A4F;
font-size:18px;
}

.stButton>button{
width:100%;
height:55px;
border-radius:12px;
background:#2D6A4F;
color:white;
font-size:18px;
font-weight:bold;
}

.stButton>button:hover{
background:#1B4332;
color:white;
}

.summary-card{
background:#F4FFF6;
padding:25px;
border-left:8px solid #2D6A4F;
border-radius:15px;
color:#1B4332;
box-shadow:0px 6px 16px rgba(0,0,0,.15);
}

.stProgress > div > div > div > div{
background:#2D6A4F;
}

section[data-testid="stSidebar"]{
background:#F8FFF8;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #

st.markdown("""
<div class="hero">

<h1>🦜 AI Universal Summarizer</h1>

<p>
Summarize Websites • YouTube • arXiv Papers • PDF Documents
using <b>LangChain + Groq</b>
</p>

</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.header("⚙ Settings")

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password"
    )

    st.divider()

    st.success("Model")

    st.code("llama-3.3-70b-versatile")

    st.divider()

    st.markdown("### Supported Sources")

    st.markdown("""
✅ Website URLs

✅ YouTube Videos

✅ arXiv Papers

✅ PDF URLs
""")

    st.info(
        "Paste any supported URL and click Generate Summary."
    )

# ---------------- URL ---------------- #

generic_url = st.text_input(
    "🔗 Enter URL"
)

if generic_url:

    if "youtube.com" in generic_url or "youtu.be" in generic_url:
        st.success("🎥 YouTube Video")

    elif "arxiv.org" in generic_url:
        st.success("📚 arXiv Paper")

    elif generic_url.lower().endswith(".pdf"):
        st.success("📄 PDF Document")

    else:
        st.success("🌍 Website")

# ---------------- HELPER FUNCTIONS ---------------- #

def extract_video_id(url: str):
    """Extract YouTube Video ID"""

    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    if parsed.hostname and "youtube.com" in parsed.hostname:
        return parse_qs(parsed.query).get("v", [None])[0]

    return None


# -------------------------------------------------- #

def load_youtube(url: str):
    """Load transcript from YouTube"""

    video_id = extract_video_id(url)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    api = YouTubeTranscriptApi()

    transcript = api.fetch(video_id)

    transcript_text = " ".join(
        snippet.text
        for snippet in transcript
    )

    return [
        Document(
            page_content=transcript_text,
            metadata={
                "source": url,
                "type": "YouTube"
            }
        )
    ]


# -------------------------------------------------- #

def load_website(url: str):
    """Load Website"""

    loader = UnstructuredURLLoader(
        urls=[url],
        ssl_verify=False,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )

    docs = loader.load()

    if len(docs) == 0:
        raise ValueError("Unable to extract website content.")

    return docs


# -------------------------------------------------- #

def load_pdf(url: str):
    """Load PDF URL"""

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Unable to download PDF.")

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ) as f:

        f.write(response.content)

        pdf_path = f.name

    loader = PyMuPDFLoader(pdf_path)

    docs = loader.load()

    return docs


# -------------------------------------------------- #

def load_arxiv(url: str):
    """
    Convert
    https://arxiv.org/abs/2506.11020
    →
    https://arxiv.org/pdf/2506.11020.pdf
    """

    paper_id = url.split("/")[-1]

    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"

    return load_pdf(pdf_url)


# -------------------------------------------------- #

def detect_source(url: str):
    """Detect URL Type"""

    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"

    elif "arxiv.org" in url:
        return "arxiv"

    elif url.lower().endswith(".pdf"):
        return "pdf"

    else:
        return "website"


# -------------------------------------------------- #

def load_documents(url: str):
    """Automatically load the correct source."""

    source = detect_source(url)

    if source == "youtube":
        docs = load_youtube(url)
        source_name = "🎥 YouTube Video"

    elif source == "arxiv":
        docs = load_arxiv(url)
        source_name = "📚 arXiv Paper"

    elif source == "pdf":
        docs = load_pdf(url)
        source_name = "📄 PDF Document"

    else:
        docs = load_website(url)
        source_name = "🌍 Website"

    return docs, source_name


# ---------------- MAIN ---------------- #

if st.button("🚀 Generate Summary", use_container_width=True):

    # ---------- Validation ---------- #

    if not groq_api_key.strip():
        st.warning("⚠ Please enter your Groq API Key.")
        st.stop()

    if not generic_url.strip():
        st.warning("⚠ Please enter a URL.")
        st.stop()

    if not validators.url(generic_url):
        st.error("❌ Invalid URL.")
        st.stop()

    # ✅ Progress bar created AFTER validation
    progress = st.progress(0, text="🚀 Initializing...")

    try:

        progress.progress(10, text="🔍 Detecting source...")

        docs, source_type = load_documents(generic_url)

        progress.progress(40, text=f"📚 Loading {source_type}...")

        if not docs:
            st.error("No content found.")
            st.stop()

        progress.progress(60, text="🤖 Loading Groq Model...")

        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model="llama-3.3-70b-versatile"
        )

        progress.progress(80, text="🧠 Generating Summary...")

        # Combine all doc content, truncate to avoid token limits
        full_text = " ".join([doc.page_content for doc in docs])
        full_text = full_text[:12000]  # Safe limit for Groq

        final_prompt = f"""
Provide a concise summary in approximately 300 words.

Content:

{full_text}
"""

        response = llm.invoke(final_prompt)
        summary = response.content

        progress.progress(100, text="✅ Completed!")

        # ---------------- RESULT ---------------- #

        st.toast("🎉 Summary Generated!")
        st.balloons()

        # ---------------- SUMMARY ---------------- #

        st.divider()
        st.markdown("## 📄 AI Generated Summary")
        st.markdown(
            f'<div class="summary-card">{summary}</div>',
            unsafe_allow_html=True
        )
        st.divider()

        # ---------------- STATISTICS ---------------- #

        st.markdown("## 📊 Summary Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📝 Words", len(summary.split()))

        with col2:
            st.metric("🔤 Characters", len(summary))

        with col3:
            st.metric("📄 Documents", len(docs))

        st.divider()

        # ---------------- SOURCE INFO ---------------- #

        with st.expander("📚 Source Information"):

            st.markdown(f"### {source_type}")

            st.write("**URL:**")
            st.code(generic_url)

            st.write(
                "**Characters Extracted:**",
                len(docs[0].page_content)
            )

            st.write(
                "**Words Extracted:**",
                len(docs[0].page_content.split())
            )

            st.markdown("### Preview")

            st.text_area(
                "",
                docs[0].page_content[:1500],
                height=250
            )

        st.divider()

        # ---------------- DOWNLOAD ---------------- #

        st.download_button(
            label="📥 Download Summary",
            data=summary,
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.divider()

        # ---------------- FOOTER ---------------- #

        st.markdown(
            """
<div style="text-align:center;
padding:25px;
color:#2D6A4F;
font-size:16px;">

Made with ❤️ using
<b>Streamlit</b> •
<b>LangChain</b> •
<b>Groq</b>

</div>
""",
            unsafe_allow_html=True
        )

    except RequestBlocked:
        st.error("❌ YouTube blocked transcript access. Try a different video.")

    except ValueError as e:
        st.error(str(e))

    except Exception as e:
        st.exception(e)
