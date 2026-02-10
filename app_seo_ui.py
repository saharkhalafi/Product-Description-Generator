#set this first   setx GEMINI_API_KEY "YOUR_API_KEY_HERE"
import io
import os
from dataclasses import dataclass
from typing import Optional, List

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class ColumnMapping:
    sku: str
    title_hint: str
    type_col: str
    material: str
    color: str
    size_info: str
    target_audience: str
    seasonal_tags: str
    language: str


# -----------------------------
# Helpers
# -----------------------------
def detect_columns(df: pd.DataFrame) -> ColumnMapping:
    """Attempt to detect expected columns by name; fallback to identical names."""
    lower_cols = {c.lower(): c for c in df.columns}

    def pick(name: str) -> str:
        return lower_cols.get(name, name)

    return ColumnMapping(
        sku=pick("sku"),
        title_hint=pick("title_hint"),
        type_col=pick("type"),
        material=pick("material"),
        color=pick("color"),
        size_info=pick("size_info"),
        target_audience=pick("target_audience"),
        seasonal_tags=pick("seasonal_tags"),
        language=pick("language"),
    )


def build_prompt(row: pd.Series, language: str) -> str:
    return f"""
You are an SEO expert and product copywriter.
Generate a {language} product description for an online clothing store.

Product details:
- Title hint: {row['title_hint']}
- Type: {row['type']}
- Material: {row['material']}
- Color: {row['color']}
- Size info: {row['size_info']}
- Target audience: {row['target_audience']}
- Season: {row['seasonal_tags']}

Requirements:
- Write in {language}.
- Maximum 3 sentences.
- Natural and emotional tone suitable for e-commerce.
- Include 2 SEO keywords related to this product.
""".strip()


def try_load_image_bytes(image_path: str) -> Optional[bytes]:
    if not image_path:
        return None
    if not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception:
        return None


def expected_image_path(image_dir: str, sku_value: str) -> str:
    # Matches the original script convention: f"{sku.lower()}_1_.jpg"
    return os.path.join(image_dir, f"{str(sku_value).lower()}_1_.jpg")


def generate_descriptions(
    df: pd.DataFrame,
    mapping: ColumnMapping,
    image_dir: str,
    client: genai.Client,
    model_name: str,
) -> List[str]:
    descriptions: List[str] = []
    progress = st.progress(0, text="Generating descriptions...")
    status_area = st.empty()

    total = len(df)
    for index, row in df.iterrows():
        language_value = str(row[mapping.language])
        prompt = build_prompt(
            row=pd.Series(
                {
                    "title_hint": row[mapping.title_hint],
                    "type": row[mapping.type_col],
                    "material": row[mapping.material],
                    "color": row[mapping.color],
                    "size_info": row[mapping.size_info],
                    "target_audience": row[mapping.target_audience],
                    "seasonal_tags": row[mapping.seasonal_tags],
                }
            ),
            language=language_value,
        )

        parts: List[types.Part] = [types.Part.from_text(text=prompt)]

        sku_value = row[mapping.sku]
        img_path = expected_image_path(image_dir, sku_value) if image_dir else ""
        image_bytes = try_load_image_bytes(img_path)
        if image_bytes:
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        try:
            result = client.models.generate_content(model=model_name, contents=parts)
            text = (result.text or "").strip()
        except Exception as e:
            text = f"[ERROR] {e}"

        descriptions.append(text)

        # UI updates
        progress.progress(min((index + 1) / total, 1.0))
        status_area.write(f"Processed {index + 1} / {total}")

    progress.empty()
    status_area.empty()
    return descriptions


# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="SEO Text Generator", page_icon="📝", layout="wide")

st.title("📝 SEO Product Description Generator")
st.caption("Generate SEO-friendly descriptions from an Excel sheet, optionally using product images.")

with st.sidebar:
    st.header("Settings")

    api_key = st.text_input(
        "Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Your Google Gemini API key. Stored only in-memory while the app runs.",
    )

    model_name = st.selectbox(
        "Model",
        options=["gemini-2.0-flash", "gemini-2.5-flash-image-preview"],
        index=0,
        help="Default matches the original script.",
    )

    image_dir = st.text_input(
        "Image folder (optional)",
        value=os.path.join(os.getcwd()),
        help="Folder containing product images named like {sku}_1_.jpg. Leave blank to skip images.",
    )

    st.markdown("---")
    st.write("Upload your Excel file (.xlsx) containing product rows.")
    uploaded_file = st.file_uploader("Excel file", type=["xlsx"]) 


if uploaded_file is None:
    st.info("Upload an Excel file to begin.")
    st.stop()

# Load dataframe
try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Failed to read Excel: {e}")
    st.stop()

st.subheader("Input Preview")
st.dataframe(df.head(20), use_container_width=True)

# Column mapping
st.markdown("### Column Mapping")
detected = detect_columns(df)
cols = st.columns(3)
with cols[0]:
    sku_col = st.selectbox("SKU column", options=list(df.columns), index=list(df.columns).index(detected.sku) if detected.sku in df.columns else 0)
    title_hint_col = st.selectbox("Title hint column", options=list(df.columns), index=list(df.columns).index(detected.title_hint) if detected.title_hint in df.columns else 0)
    type_col = st.selectbox("Type column", options=list(df.columns), index=list(df.columns).index(detected.type_col) if detected.type_col in df.columns else 0)
with cols[1]:
    material_col = st.selectbox("Material column", options=list(df.columns), index=list(df.columns).index(detected.material) if detected.material in df.columns else 0)
    color_col = st.selectbox("Color column", options=list(df.columns), index=list(df.columns).index(detected.color) if detected.color in df.columns else 0)
    size_info_col = st.selectbox("Size info column", options=list(df.columns), index=list(df.columns).index(detected.size_info) if detected.size_info in df.columns else 0)
with cols[2]:
    target_audience_col = st.selectbox("Target audience column", options=list(df.columns), index=list(df.columns).index(detected.target_audience) if detected.target_audience in df.columns else 0)
    seasonal_tags_col = st.selectbox("Seasonal tags column", options=list(df.columns), index=list(df.columns).index(detected.seasonal_tags) if detected.seasonal_tags in df.columns else 0)
    language_col = st.selectbox("Language column", options=list(df.columns), index=list(df.columns).index(detected.language) if detected.language in df.columns else 0)

mapping = ColumnMapping(
    sku=sku_col,
    title_hint=title_hint_col,
    type_col=type_col,
    material=material_col,
    color=color_col,
    size_info=size_info_col,
    target_audience=target_audience_col,
    seasonal_tags=seasonal_tags_col,
    language=language_col,
)

st.markdown("---")
col_run = st.columns([1, 2])
with col_run[0]:
    run = st.button("Generate Descriptions", type="primary")

if run:
    if not api_key:
        st.error("Please provide a Gemini API key.")
        st.stop()

    client = genai.Client(api_key=api_key)

    results = generate_descriptions(
        df=df,
        mapping=mapping,
        image_dir=image_dir.strip(),
        client=client,
        model_name=model_name,
    )

    df_out = df.copy()
    df_out["seo_description"] = results

    st.success("Generation complete.")

    st.subheader("Results")
    st.dataframe(df_out, use_container_width=True)

    # Prepare download as Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_out.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="Download Excel",
        data=output,
        file_name="products_with_descriptions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


