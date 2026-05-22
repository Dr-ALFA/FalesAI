"""
🇵🇸 FalesAI — Palestine AI Content System
==========================================
Palestine-focused multi-agent system. Bilingual EN/AR with RTL support.
"""

import streamlit as st
import os
import json
from dotenv import load_dotenv
from translations import t

load_dotenv()

TOPIC = "Palestine"

st.set_page_config(
    page_title="FalesAI — Palestine",
    page_icon="🇵🇸",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
lang = st.session_state["lang"]
is_rtl = lang == "ar"
direction = "rtl" if is_rtl else "ltr"
font_family = "'Cairo', 'Inter', sans-serif" if is_rtl else "'Inter', sans-serif"
title_font = "'Cairo', serif" if is_rtl else "'Playfair Display', serif"
text_align = "right" if is_rtl else "left"
arrow = "←" if is_rtl else "→"

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&family=Cairo:wght@300;400;500;600;700;800&display=swap');

:root {{
    --bg-card: rgba(255,255,255,0.03);
    --border-subtle: rgba(255,255,255,0.08);
    --text-primary: #f0f0f5;
    --text-secondary: #8b8b9e;
    --pal-green: #009736;
    --pal-red: #ce1126;
    --pal-black: #1a1a2e;
    --gradient-pal: linear-gradient(135deg, #ce1126, #009736);
    --gradient-glass: linear-gradient(135deg, rgba(0,151,54,0.08), rgba(206,17,38,0.05));
    --shadow-glow: 0 0 40px rgba(0,151,54,0.15);
}}

.stApp {{ font-family: {font_family}; direction: {direction}; }}

/* Hero */
.hero-container {{ text-align: center; padding: 2rem 1rem 0.5rem; }}
.hero-flag {{ font-size: 4.5rem; margin-bottom: 0.5rem;
    animation: pulse 2.5s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.08); }} }}
.hero-title {{
    font-family: {title_font}; font-size: 3rem; font-weight: 800;
    background: var(--gradient-pal); -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 0.4rem; line-height: 1.4;
}}
.hero-subtitle {{ font-size: 1.05rem; color: var(--text-secondary); font-weight: 300; line-height: 1.6; }}
.pal-stripe {{
    height: 4px; border-radius: 2px; margin: 1.2rem auto;
    max-width: 400px;
    background: linear-gradient(90deg, #1a1a2e 25%, #009736 25%, #009736 50%, #fff 50%, #fff 75%, #ce1126 75%);
}}

/* Agent cards */
.agent-card {{
    background: var(--gradient-glass); border: 1px solid var(--border-subtle);
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
    backdrop-filter: blur(10px); transition: all 0.3s ease;
    text-align: {text_align};
}}
.agent-card:hover {{ border-color: var(--pal-green); box-shadow: var(--shadow-glow); transform: translateY(-2px); }}
.agent-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
.agent-name {{ font-weight: 700; font-size: 1rem; color: var(--text-primary); margin-bottom: 0.3rem; }}
.agent-desc {{ font-size: 0.85rem; color: var(--text-secondary); line-height: 1.7; }}

/* Pipeline */
.pipeline-flow {{
    display: flex; align-items: center; justify-content: center;
    gap: 8px; padding: 1rem; flex-wrap: wrap; direction: {direction};
}}
.pipeline-step {{
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-radius: 12px; padding: 10px 18px; text-align: center; min-width: 130px;
}}
.pipeline-arrow {{ color: var(--text-secondary); font-size: 1.5rem; }}

/* Image gallery */
.image-card {{
    background: var(--bg-card); border: 1px solid var(--border-subtle);
    border-radius: 16px; overflow: hidden; transition: all 0.3s ease; margin-bottom: 1rem;
}}
.image-card:hover {{ border-color: var(--pal-red); box-shadow: 0 0 30px rgba(206,17,38,0.15); transform: translateY(-3px); }}
.image-card img {{ width: 100%; height: 200px; object-fit: cover; }}
.image-card-body {{ padding: 1rem; text-align: {text_align}; }}
.image-card-title {{ font-weight: 700; color: var(--text-primary); margin-bottom: 0.3rem; font-size: 0.95rem; }}
.image-card-desc {{ font-size: 0.82rem; color: var(--text-secondary); line-height: 1.6; }}
.image-card-category {{
    display: inline-block; padding: 3px 10px; border-radius: 10px;
    font-size: 0.7rem; font-weight: 600; background: rgba(0,151,54,0.15);
    color: var(--pal-green); margin-top: 0.5rem;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0a0f0a 0%, #0d1117 40%, #111827 100%);
    border-right: 1px solid rgba(0,151,54,0.15);
}}

.stDownloadButton > button {{
    background: var(--gradient-pal) !important; color: white !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.6rem 2rem !important; font-weight: 600 !important;
}}
.stDownloadButton > button:hover {{ transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(0,151,54,0.3) !important; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding: 1.2rem 0;">
        <div style="width:60px; height:60px; margin:0 auto 10px; border-radius:16px;
                    background: linear-gradient(135deg, #ce1126, #009736);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.6rem; font-weight:800; color:#fff;
                    box-shadow: 0 4px 20px rgba(0,151,54,0.3);
                    font-family: {title_font};">F</div>
        <div style="font-family:{title_font}; font-size:1.5rem; font-weight:800;
                    background: linear-gradient(135deg, #ce1126, #ff6b6b, #009736);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing: 1px;">
            FalesAI
        </div>
        <div style="font-size:0.75rem; color:#6b7280; margin-top:4px; letter-spacing:0.5px;">
            {t("brand_subtitle", lang)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Language toggle
    lang_options = {"English 🇬🇧": "en", "العربية 🇵🇸": "ar"}
    current_label = [k for k, v in lang_options.items() if v == lang][0]
    selected = st.radio(
        t("lang_label", lang),
        list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_label),
        horizontal=True,
    )
    if lang_options[selected] != lang:
        st.session_state["lang"] = lang_options[selected]
        st.rerun()

    st.markdown("---")

    st.markdown(t("agent_team", lang))
    for icon, name, desc in t("agents", lang):
        st.markdown(f"""
        <div class="agent-card">
            <div class="agent-icon">{icon}</div>
            <div class="agent-name">{name}</div>
            <div class="agent-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(t("settings", lang))
    word_count = st.slider(t("word_count_label", lang), 500, 3000, 1500, 100)
    num_images = st.slider(t("num_images_label", lang), 3, 10, 6)

    st.markdown("---")
    st.markdown(f'<div style="text-align:center; padding:1rem 0; font-size:0.7rem; color:#64748b;">{t("footer", lang)}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-container">
    <div class="hero-flag" style="font-family:{title_font}; font-size:3.5rem; font-weight:800;
        background: var(--gradient-pal); -webkit-background-clip:text;
        -webkit-text-fill-color:transparent; background-clip:text;">FalesAI</div>
    <div class="hero-title">{t("hero_title", lang)}</div>
    <div class="hero-subtitle">{t("hero_subtitle", lang)}</div>
    <div class="pal-stripe"></div>
</div>
""", unsafe_allow_html=True)

# Pipeline
icons = ["✍️", "🖼️", "📐", "📄"]
steps = t("pipeline_steps", lang)
ph = '<div class="pipeline-flow">'
for i, (ic, lb) in enumerate(zip(icons, steps)):
    ph += f'<div class="pipeline-step"><div style="font-size:1.3rem;">{ic}</div><div style="font-size:0.8rem;font-weight:600;">{lb}</div></div>'
    if i < len(steps) - 1:
        ph += f'<div class="pipeline-arrow">{arrow}</div>'
ph += '</div>'
st.markdown(ph, unsafe_allow_html=True)

# Generate button (no topic input — Palestine only)
run_button = st.button(t("generate_btn", lang), use_container_width=True, type="primary")


# ══════════════════════════════════════════════════════════════════════
#  EXECUTION
# ══════════════════════════════════════════════════════════════════════
if run_button:
    st.session_state["running"] = True
    with st.container():
        st.markdown("---")
        st.markdown(t("pipeline_progress", lang))

        with st.status(t("essay_status_running", lang), expanded=True) as s1:
            st.write(t("essay_topic_line", lang))
            st.write(t("essay_target_line", lang).format(wc=word_count))
            from tools.essay_tool import essay_writer_tool
            essay_result = essay_writer_tool.invoke({"topic": TOPIC, "word_count": word_count})
            word_ct = len(essay_result.split())
            st.write(t("essay_complete_line", lang).format(wc=word_ct))
            s1.update(label=t("essay_status_done", lang), state="complete")

        with st.status(t("image_status_running", lang), expanded=True) as s2:
            st.write(t("image_search_line", lang).format(n=num_images))
            from tools.image_tool import image_suggester_tool
            images_result = image_suggester_tool.invoke({"topic": TOPIC, "num_images": num_images})
            try:
                images_list = json.loads(images_result)
                st.write(t("image_found_line", lang).format(n=len(images_list)))
            except json.JSONDecodeError:
                images_list = []
                st.write(t("image_fallback_line", lang))
            s2.update(label=t("image_status_done", lang), state="complete")

        with st.status(t("org_status_running", lang), expanded=True) as s3:
            st.write(t("org_merge_line", lang))
            from tools.organizer_tool import content_organizer_tool
            final_doc = content_organizer_tool.invoke({"essay": essay_result, "image_suggestions": images_result})
            st.write(t("org_done_line", lang))
            s3.update(label=t("org_status_done", lang), state="complete")

    st.session_state.update({
        "essay": essay_result, "images": images_result,
        "images_list": images_list, "final_doc": final_doc,
        "word_count": word_ct, "topic": TOPIC, "running": False,
    })


# ══════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════
if st.session_state.get("final_doc"):
    st.markdown("---")
    essay_text = st.session_state.get("essay", "")
    imgs = st.session_state.get("images_list", [])
    wc = st.session_state.get("word_count", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric(t("metric_words", lang), f"{wc:,}")
    with c2: st.metric(t("metric_images", lang), len(imgs))
    with c3: st.metric(t("metric_paragraphs", lang), essay_text.count("\n\n") + 1 if essay_text else 0)
    with c4: st.metric(t("metric_read_time", lang), t("read_time_unit", lang).format(m=max(1, wc // 200)))

    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([t("tab_final", lang), t("tab_essay", lang), t("tab_gallery", lang), t("tab_logs", lang)])

    with tab1:
        st.markdown(st.session_state["final_doc"])
        st.markdown("---")
        st.download_button(t("download_doc", lang), st.session_state["final_doc"], "palestine_document.md", "text/markdown", use_container_width=True)

    with tab2:
        st.markdown(st.session_state["essay"])
        st.markdown("---")
        st.download_button(t("download_essay", lang), st.session_state["essay"], "palestine_essay.md", "text/markdown", use_container_width=True)

    with tab3:
        if imgs:
            cols = st.columns(3)
            for idx, img in enumerate(imgs):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="image-card">
                        <img src="{img.get('image_url','')}" alt="{img.get('title','')}"
                             onerror="this.src='https://placehold.co/800x500/1a1a2e/009736?text={img.get('title','Image').replace(' ','+')}'">
                        <div class="image-card-body">
                            <div class="image-card-title">{img.get('title','')}</div>
                            <div class="image-card-desc">{img.get('description','')}</div>
                            <div class="image-card-category">{img.get('category','')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(t("no_images", lang))

    with tab4:
        st.markdown(t("logs_title", lang))
        for label, tn, data_key in zip(
            t("log_labels", lang),
            ["essay_writer_tool", "image_suggester_tool", "content_organizer_tool"],
            ["essay", "images", "final_doc"],
        ):
            with st.expander(f"{label} — `{tn}`", expanded=False):
                st.markdown(f"{t('tool_label', lang)} `{tn}`")
                st.markdown(t("output_preview", lang))
                preview = st.session_state.get(data_key, "")[:800]
                st.code(preview + ("..." if len(preview) == 800 else ""), language="markdown")

elif not st.session_state.get("running"):
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center; padding:3rem 2rem;">
        <div style="font-size:1.3rem; font-weight:600; color:#f0f0f5; margin-bottom:0.5rem;">
            {t("empty_title", lang)}
        </div>
        <div style="font-size:0.9rem; color:#8b8b9e; max-width:500px; margin:0 auto; line-height:1.8;">
            {t("empty_desc", lang)}
        </div>
    </div>
    """, unsafe_allow_html=True)
