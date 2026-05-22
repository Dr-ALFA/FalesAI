"""
FelasAI reader experience.
"""

from __future__ import annotations

import json
from html import escape

import mistune
import streamlit as st
from dotenv import load_dotenv

from agents import run_orchestrator
from llm_config import has_chat_credentials

load_dotenv()

TOPIC = "Palestine"
render_markdown = mistune.create_markdown(escape=True)
UI_TEXT = {
    "ar": {
        "deck": "مقالة مصورة عن فلسطين، معدة للقراءة.",
        "panel_title": "مقالة فلسطين",
        "panel_copy": "تنشأ المقالة عبر ثلاث خطوات تحريرية متتابعة.",
        "ui_language": "لغة الواجهة",
        "article_language": "لغة المقالة",
        "article_length": "طول المقالة",
        "images": "عدد الصور",
        "create": "أنشيء المقالة",
        "recreate": "أنشيء نسخة جديدة",
        "step_writer": "1. وكيل كتابة المقالة",
        "step_writer_copy": "يكتب النص الأساسي عن فلسطين.",
        "step_images": "2. وكيل الصور",
        "step_images_copy": "يختار صورا تدعم فقرات المقالة.",
        "step_editor": "3. وكيل تنظيم المحتوى",
        "step_editor_copy": "ينظم النص والصور في عرض مريح للقراءة.",
        "starting": "بدأ إعداد المقالة...",
        "boot": "تهيئة الوكلاء",
        "phase_essay": "كتابة المقالة",
        "phase_images": "اختيار الصور",
        "phase_editor": "تنظيم المحتوى",
        "ready": "المقالة جاهزة.",
        "empty": "ستظهر المقالة المصورة هنا بعد إنشائها.",
        "download": "تحميل المقالة",
        "missing_key": "يلزم إضافة مفتاح Ollama Cloud في إعدادات التطبيق قبل إنشاء المقالة.",
        "done_essay": "اكتملت مسودة المقالة.",
        "done_images": "اكتمل اختيار الصور المناسبة.",
        "done_editor": "اكتملت النسخة النهائية للمقالة.",
        "start_essay": "وكيل كتابة المقالة يكتب النص الأساسي.",
        "start_images": "وكيل الصور يبحث عن صور مناسبة لفقرات المقالة.",
        "start_editor": "وكيل تنظيم المحتوى ينسق النص والصور.",
    },
    "en": {
        "deck": "An illustrated article about Palestine, prepared for reading.",
        "panel_title": "Palestine Article",
        "panel_copy": "The article is prepared in three editorial steps.",
        "ui_language": "Interface language",
        "article_language": "Article language",
        "article_length": "Article length",
        "images": "Images",
        "create": "Create article",
        "recreate": "Create a new version",
        "step_writer": "1. Essay Writer Agent",
        "step_writer_copy": "Writes the core article about Palestine.",
        "step_images": "2. Image Curator Agent",
        "step_images_copy": "Selects images that support the article.",
        "step_editor": "3. Content Organizer Agent",
        "step_editor_copy": "Shapes text and images into a reading experience.",
        "starting": "Article preparation started...",
        "boot": "Preparing agents",
        "phase_essay": "Writing article",
        "phase_images": "Selecting images",
        "phase_editor": "Organizing content",
        "ready": "Article ready.",
        "empty": "The illustrated article will appear here after it is created.",
        "download": "Download article",
        "missing_key": "Add the Ollama Cloud API key to the app settings before creating an article.",
        "done_essay": "The article draft is complete.",
        "done_images": "The image selection is complete.",
        "done_editor": "The final article is ready.",
        "start_essay": "The writing agent is drafting the article.",
        "start_images": "The image agent is finding images for the article.",
        "start_editor": "The editor agent is arranging text and images.",
    },
}
ARTICLE_LANGUAGES = {"العربية": "Arabic", "English": "English"}

st.set_page_config(
    page_title="Palestine | FelasAI",
    page_icon="🇵🇸",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def read_images(raw_images: str) -> list[dict]:
    try:
        parsed = json.loads(raw_images)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def first_image(images: list[dict]) -> dict:
    for image in images:
        if image.get("image_url"):
            return image
    return {}


def render_brand(text: dict[str, str]) -> None:
    st.markdown(
        f"""
        <header class="masthead">
            <div class="flagline"></div>
            <h1>FelasAI</h1>
            <p class="signature">By DrALFA</p>
            <p class="deck">{text["deck"]}</p>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_cover(image: dict) -> None:
    if not image.get("image_url"):
        return
    url = escape(str(image["image_url"]))
    alt = escape(str(image.get("title", "Palestine")))
    caption = escape(str(image.get("title", "Palestine")))
    st.markdown(
        f"""
        <figure class="cover">
            <img src="{url}" alt="{alt}">
            <figcaption>{caption}</figcaption>
        </figure>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    :root {
        --ink: #171411;
        --paper: #f7f1e5;
        --paper-light: #fffaf0;
        --muted: #675d52;
        --line: rgba(23, 20, 17, .15);
        --red: #ad2133;
        --green: #17633d;
    }
    .stApp {
        background:
            linear-gradient(180deg, rgba(255,250,240,.82), rgba(247,241,229,.98)),
            var(--paper);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container {
        max-width: 1280px;
        padding-top: 1.25rem;
        padding-bottom: 4rem;
    }
    .masthead {
        max-width: 860px;
        padding: 1rem 0 1.35rem;
    }
    .flagline {
        background: linear-gradient(90deg, #111 0 25%, #fff 25% 50%, #17633d 50% 75%, #ad2133 75%);
        height: 5px;
        margin-bottom: 2rem;
        width: min(320px, 70vw);
    }
    .masthead h1 {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(3.4rem, 8vw, 7.6rem);
        font-weight: 700;
        letter-spacing: 0;
        line-height: .9;
        margin: 0 0 .9rem;
    }
    .signature {
        color: var(--red);
        font-family: system-ui, sans-serif;
        font-size: .82rem;
        font-weight: 600;
        letter-spacing: 0;
        margin: -.3rem 0 .8rem;
    }
    .deck {
        color: var(--muted);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1.18rem, 2vw, 1.55rem);
        line-height: 1.45;
        margin: 0;
    }
    .cover {
        border-bottom: 1px solid var(--line);
        margin: 0 0 1.4rem;
        padding-bottom: .7rem;
    }
    .cover img, .cover.placeholder {
        aspect-ratio: 16 / 8;
        background: linear-gradient(135deg, #1a1a1a, #17633d 54%, #ad2133);
        display: block;
        max-height: 610px;
        object-fit: cover;
        width: 100%;
    }
    .cover figcaption {
        color: var(--muted);
        font-size: .84rem;
        line-height: 1.4;
        padding-top: .55rem;
    }
    .control-panel {
        background: rgba(255,250,240,.72);
        border-top: 1px solid var(--line);
        padding: 1.2rem 0;
        position: sticky;
        top: 1rem;
    }
    .control-panel h2 {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.7rem;
        letter-spacing: 0;
        line-height: 1.2;
        margin: 0 0 .5rem;
    }
    .control-panel p {
        color: var(--muted);
        line-height: 1.65;
        margin-bottom: 1rem;
    }
    .workflow-step {
        border-top: 1px solid var(--line);
        margin-top: .9rem;
        padding-top: .9rem;
    }
    .workflow-step strong {
        color: var(--green);
        display: block;
        font-size: .92rem;
        margin-bottom: .22rem;
    }
    .workflow-step span {
        color: var(--muted);
        display: block;
        font-size: .92rem;
        line-height: 1.5;
    }
    .article {
        background: var(--paper-light);
        border-top: 1px solid var(--line);
        box-shadow: 0 18px 55px rgba(44, 29, 12, .08);
        margin: 0 auto;
        max-width: 850px;
        padding: clamp(1.2rem, 4vw, 4rem);
    }
    .article.rtl {
        direction: rtl;
        text-align: right;
    }
    .article h1 {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(2rem, 4vw, 3.4rem);
        letter-spacing: 0;
        line-height: 1.08;
        margin-top: 0;
    }
    .article h2 {
        border-top: 1px solid var(--line);
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1.45rem, 2.4vw, 2.1rem);
        letter-spacing: 0;
        line-height: 1.2;
        margin-top: 2.5rem;
        padding-top: 1.7rem;
    }
    .article p, .article li {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.16rem;
        line-height: 1.82;
    }
    .article em:first-child {
        color: var(--muted);
        font-size: 1.24rem;
        line-height: 1.65;
    }
    .article img {
        border-radius: 3px;
        display: block;
        margin: 2rem auto .65rem;
        max-height: 580px;
        object-fit: cover;
        width: 100%;
    }
    .article img + em, .article p:has(img) + p em {
        color: var(--muted);
        display: block;
        font-family: system-ui, sans-serif;
        font-size: .88rem;
        line-height: 1.5;
    }
    .reader-note {
        color: var(--muted);
        border-top: 1px solid var(--line);
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1.2rem, 2vw, 1.65rem);
        line-height: 1.55;
        margin: 0;
        padding-top: 1.5rem;
    }
    .stButton button, .stDownloadButton button {
        border-radius: 4px;
        min-height: 2.75rem;
    }
    @media (max-width: 720px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .control-panel { position: static; }
        .article { padding: 1.25rem; }
        .article p, .article li { font-size: 1.05rem; line-height: 1.72; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

result = st.session_state.get("run_result")
images = read_images(result["images"]) if result else []
ui_language = st.session_state.get("ui_language", "ar")
text = UI_TEXT[ui_language]
render_brand(text)

controls, reader = st.columns([.82, 2.18], gap="large")

with controls:
    ui_choice = st.radio(
        text["ui_language"],
        ["العربية", "English"],
        index=0 if ui_language == "ar" else 1,
        horizontal=True,
    )
    selected_ui_language = "ar" if ui_choice == "العربية" else "en"
    if selected_ui_language != ui_language:
        st.session_state["ui_language"] = selected_ui_language
        st.rerun()
    text = UI_TEXT[selected_ui_language]
    st.markdown(
        f"""
        <section class="control-panel">
            <h2>{text["panel_title"]}</h2>
            <p>{text["panel_copy"]}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    article_options = list(ARTICLE_LANGUAGES)
    article_index = 0 if st.session_state.get("article_language", "Arabic") == "Arabic" else 1
    article_choice = st.radio(text["article_language"], article_options, index=article_index, horizontal=True)
    article_language = ARTICLE_LANGUAGES[article_choice]
    st.session_state["article_language"] = article_language
    word_count = st.slider(text["article_length"], 700, 2400, 1400, 100)
    num_images = st.slider(text["images"], 2, 7, 4)
    button_label = text["create"] if not result else text["recreate"]
    generate = st.button(button_label, type="primary", use_container_width=True)
    if not has_chat_credentials():
        st.warning(text["missing_key"])
    if generate:
        if not has_chat_credentials():
            st.stop()
        progress_labels = {
            "essay_started": text["phase_essay"],
            "images_started": text["phase_images"],
            "organizer_started": text["phase_editor"],
        }
        progress_messages = {
            "essay_started": text["start_essay"],
            "images_started": text["start_images"],
            "organizer_started": text["start_editor"],
            "essay_done": text["done_essay"],
            "images_done": text["done_images"],
            "organizer_done": text["done_editor"],
        }

        with st.status(text["starting"], expanded=True) as status:
            progress_bar = st.progress(0, text=text["boot"])
            completed_steps = {"essay_done": 34, "images_done": 67, "organizer_done": 100}

            def show_progress(phase: str, message: str) -> None:
                display_message = progress_messages.get(phase, message)
                if phase in progress_labels:
                    status.update(label=progress_labels[phase], state="running")
                if phase in completed_steps:
                    progress_bar.progress(completed_steps[phase], text=display_message)
                    st.write(f"✓ {display_message}")
                else:
                    st.write(display_message)

            st.session_state["run_result"] = run_orchestrator(
                TOPIC,
                word_count=word_count,
                num_images=num_images,
                article_language=article_language,
                progress_callback=show_progress,
            )
            status.update(label=text["ready"], state="complete")
        st.rerun()
    st.markdown(
        f"""
        <div class="workflow-step">
            <strong>{text["step_writer"]}</strong>
            <span>{text["step_writer_copy"]}</span>
        </div>
        <div class="workflow-step">
            <strong>{text["step_images"]}</strong>
            <span>{text["step_images_copy"]}</span>
        </div>
        <div class="workflow-step">
            <strong>{text["step_editor"]}</strong>
            <span>{text["step_editor_copy"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with reader:
    if not result:
        st.markdown(
            f'<p class="reader-note">{text["empty"]}</p>',
            unsafe_allow_html=True,
        )
        st.stop()

    render_cover(first_image(images))
    article_class = "article rtl" if result.get("article_language") == "Arabic" else "article"
    st.markdown(
        f'<article class="{article_class}">{render_markdown(result["final_document"])}</article>',
        unsafe_allow_html=True,
    )
    st.download_button(
        text["download"],
        result["final_document"],
        file_name="palestine_article.md",
        mime="text/markdown",
    )
