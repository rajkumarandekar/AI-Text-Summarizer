# import streamlit as st
# import validators
# from urllib.parse import urlparse, parse_qs

# from youtube_transcript_api import YouTubeTranscriptApi

# from langchain_core.documents import Document
# from langchain_core.prompts import PromptTemplate
# from langchain_groq import ChatGroq
# from langchain.chains.summarize import load_summarize_chain
# from langchain_community.document_loaders import UnstructuredURLLoader


# # -------------------- Streamlit UI -------------------- #

# st.set_page_config(
#     page_title="LangChain: Summarize Text From YT or Website",
#     page_icon="🦜"
# )

# st.title("🦜 LangChain: Summarize Text From YT or Website")
# st.subheader("Summarize URL")

# with st.sidebar:
#     groq_api_key = st.text_input(
#         "Groq API Key",
#         type="password"
#     )

# generic_url = st.text_input(
#     "URL",
#     label_visibility="collapsed"
# )

# # -------------------- Prompt -------------------- #

# prompt = PromptTemplate.from_template(
#     """
# Provide a concise summary of the following content in approximately 300 words.

# Content:
# {text}
# """
# )

# # -------------------- Helper Functions -------------------- #


# def extract_video_id(url: str):
#     """Extract YouTube video id."""

#     parsed = urlparse(url)

#     if parsed.hostname == "youtu.be":
#         return parsed.path.lstrip("/")

#     if parsed.hostname and "youtube.com" in parsed.hostname:
#         return parse_qs(parsed.query).get("v", [None])[0]

#     return None


# def load_youtube(url: str):
#     """Load YouTube transcript using youtube-transcript-api 1.2.4"""

#     video_id = extract_video_id(url)

#     if not video_id:
#         raise ValueError("Invalid YouTube URL")

#     api = YouTubeTranscriptApi()

#     transcript = api.fetch(video_id)

#     transcript_text = " ".join(
#         snippet.text
#         for snippet in transcript
#     )

#     return [
#         Document(
#             page_content=transcript_text,
#             metadata={"source": url}
#         )
#     ]


# def load_website(url: str):
#     """Load website content."""

#     loader = UnstructuredURLLoader(
#         urls=[url],
#         ssl_verify=False,
#         headers={
#             "User-Agent":
#             "Mozilla/5.0"
#         }
#     )

#     return loader.load()


# # -------------------- Main -------------------- #

# if st.button("Summarize the Content from YT or Website"):

#     if not groq_api_key.strip():
#         st.error("Please enter your Groq API Key.")
#         st.stop()

#     if not generic_url.strip():
#         st.error("Please enter a URL.")
#         st.stop()

#     if not validators.url(generic_url):
#         st.error("Please enter a valid URL.")
#         st.stop()

#     try:

#         with st.spinner("Loading content..."):

#             if (
#                 "youtube.com" in generic_url
#                 or "youtu.be" in generic_url
#             ):
#                 docs = load_youtube(generic_url)
#             else:
#                 docs = load_website(generic_url)

#         if not docs:
#             st.error("No content found.")
#             st.stop()

#         llm = ChatGroq(
#             groq_api_key=groq_api_key,
#             model="llama-3.3-70b-versatile",
#         )

#         chain = load_summarize_chain(
#             llm=llm,
#             chain_type="stuff",
#             prompt=prompt,
#         )

#         with st.spinner("Generating summary..."):

#             result = chain.invoke(
#                 {"input_documents": docs}
#             )

#         if isinstance(result, dict):
#             summary = (
#                 result.get("output_text")
#                 or result.get("text")
#                 or str(result)
#             )
#         else:
#             summary = result

#         st.success(summary)

#     except Exception as e:
#         st.exception(e)

import streamlit as st
import validators
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader

# -------------------- PAGE CONFIG -------------------- #

st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM CSS -------------------- #

st.markdown("""
<style>

.main{
    padding-top:1rem;
}

.block-container{
    padding-top:2rem;
}

h1,h2,h3{
    color:white;
}
            
.hero{
padding:35px;
border-radius:18px;
text-align:center;
margin-bottom:25px;
box-shadow:0px 8px 20px rgba(0,0,0,.15);
}

.hero h1{
color:black;
font-size:42px;
margin-bottom:10px;
}

.hero p{
color:black;
font-size:18px;
}

.stTextInput>div>div>input{
border-radius:12px;
padding:12px;
}

.stButton>button{
width:100%;
height:55px;
font-size:18px;
font-weight:bold;
border-radius:12px;
background:#43A047;
color:white;
border:none;
}

.stButton>button:hover{
background:#2E7D32;
color:white;
}

.summary-card{

background:#F1FFF3;

padding:25px;

border-radius:15px;

border-left:8px solid #43A047;

box-shadow:0px 6px 15px rgba(0,0,0,.12);

color:#1B5E20;

font-size:17px;

line-height:1.8;

}
.metric-card{

background:#E8F5E9;

padding:18px;

border-radius:12px;

text-align:center;

}

.footer{
text-align:center;
color:gray;
padding-top:30px;
}

.stTextInput>div>div>input{

border:2px solid #81C784;

border-radius:12px;

}
.stProgress > div > div > div > div{

background:#43A047;

}


</style>
""", unsafe_allow_html=True)

# -------------------- HERO -------------------- #

st.markdown("""
<div class='hero'>

<h1>🦜 AI Text Summarizer</h1>

<p>
Summarize YouTube Videos & Website Articles using
<b>LangChain + Groq Llama 3.3 70B</b>
</p>

</div>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR -------------------- #

with st.sidebar:

    st.title("⚙ Settings")

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password"
    )

    st.divider()

    st.markdown("### 🤖 Model")

    st.success("llama-3.3-70b-versatile")

    st.divider()

    st.markdown("### 📌 Supported URLs")

    st.markdown("""
- 🎥 YouTube Videos

- 🌍 Website Articles

- 📰 Blogs

- 📚 Documentation

- 📄 News Articles
""")

    st.divider()

    st.info(
        "Paste a URL and click **Generate Summary**."
    )

# -------------------- URL INPUT -------------------- #

generic_url = st.text_input(
    "🔗 Enter Website or YouTube URL"
)

if generic_url:

    if "youtube.com" in generic_url or "youtu.be" in generic_url:

        st.success("🎥 YouTube Video Detected")

    else:

        st.success("🌍 Website Detected")

# -------------------- PROMPT -------------------- #

prompt = PromptTemplate.from_template(
"""
Provide a detailed summary in approximately 300 words.

Content:

{text}
"""
)

# -------------------- HELPERS -------------------- #

def extract_video_id(url):

    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        return parsed.path[1:]

    if parsed.hostname and "youtube.com" in parsed.hostname:
        return parse_qs(parsed.query).get("v",[None])[0]

    return None


def load_youtube(url):

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
            metadata={"source":url}
        )
    ]


def load_website(url):

    loader = UnstructuredURLLoader(
        urls=[url],
        ssl_verify=False,
        headers={
            "User-Agent":"Mozilla/5.0"
        }
    )

    return loader.load()

# -------------------- MAIN -------------------- #

if st.button("🚀 Generate Summary", use_container_width=True):

    # ---------------- Validation ---------------- #

    if not groq_api_key.strip():
        st.warning("⚠ Please enter your Groq API Key.")
        st.stop()

    if not generic_url.strip():
        st.warning("⚠ Please enter a valid URL.")
        st.stop()

    if not validators.url(generic_url):
        st.error("❌ Invalid URL.")
        st.stop()

    try:

        progress = st.progress(0, text="🚀 Initializing...")

        progress.progress(10, text="🔍 Detecting URL type...")

        # ---------- Load Documents ---------- #

        if (
            "youtube.com" in generic_url
            or "youtu.be" in generic_url
        ):

            progress.progress(30, text="🎥 Fetching YouTube transcript...")

            docs = load_youtube(generic_url)

            source_type = "YouTube Video"

        else:

            progress.progress(30, text="🌍 Reading Website...")

            docs = load_website(generic_url)

            source_type = "Website"

        if not docs:

            st.error("No content found.")
            st.stop()

        progress.progress(55, text="🤖 Loading Llama 3.3 70B...")

        # ---------- LLM ---------- #

        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model="llama-3.3-70b-versatile",
        )

        chain = load_summarize_chain(
            llm=llm,
            chain_type="stuff",
            prompt=prompt,
        )

        progress.progress(80, text="📝 Generating Summary...")

        result = chain.invoke(
            {
                "input_documents": docs
            }
        )

        progress.progress(100, text="✅ Completed")

        # ---------- Output ---------- #

        if isinstance(result, dict):

            summary = (
                result.get("output_text")
                or result.get("text")
                or str(result)
            )

        else:

            summary = result

        st.toast("🎉 Summary Generated Successfully!")

        st.balloons()

        st.divider()

        st.markdown("## 📄 AI Generated Summary")

        st.markdown(
            f"""
<div class="summary-card">

{summary}

</div>
""",
            unsafe_allow_html=True,
        )

        st.divider()

        # ---------- Metrics ---------- #

        st.markdown("## 📊 Summary Statistics")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📝 Words",
            len(summary.split())
        )

        c2.metric(
            "🔤 Characters",
            len(summary)
        )

        c3.metric(
            "📄 Documents",
            len(docs)
        )

        st.divider()

        # ---------- Source Info ---------- #

        with st.expander("📚 Source Information"):

            st.write("### Source Details")

            st.write("**Source Type:**", source_type)

            st.write(
                "**URL:**",
                generic_url
            )

            st.write(
                "**Characters Extracted:**",
                len(docs[0].page_content)
            )

            st.write(
                "**Words Extracted:**",
                len(docs[0].page_content.split())
            )

            st.text_area(
                "Preview",
                docs[0].page_content[:1200],
                height=220
            )

        st.divider()

        # ---------- Download ---------- #

        st.download_button(

            label="📥 Download Summary",

            data=summary,

            file_name="summary.txt",

            mime="text/plain",

            use_container_width=True

        )

        st.divider()

        st.markdown(
            """
<div class='footer'>

Made with ❤️ using Streamlit | LangChain | Groq

</div>
""",
            unsafe_allow_html=True,
        )

    except Exception as e:

        st.error("❌ Something went wrong.")

        st.exception(e)