# 📝 Product Description Generator using Google Gemini API

## 📌 Project Overview
In modern e-commerce platforms, writing **unique product descriptions** for thousands of items is a **time-consuming and repetitive task**. Manual copywriting increases operational costs and often results in **inconsistent tone** and product presentation.

This project automates the process using **Google Gemini AI**, generating **high-quality descriptions** for clothing products directly from **Excel data**. It integrates AI text generation with structured product data to create natural, emotional, and keyword-optimized descriptions ready for online stores.

---

## 🎯 Problem Statement
E-commerce businesses face these challenges:

- Writing **individual product descriptions** for large catalogs.
- Maintaining **SEO optimization** for search engine visibility.
- Ensuring **language localization** (e.g., Persian, English).
- Generating content that matches **product type, material, color, and audience**.

To solve this, we leverage the **Gemini Generative AI API** to automatically generate text that combines structured fields with creative natural language output.

---

## ⚙️ Technical Approach

### Input Data
- Accepts an **Excel file (.xlsx)** containing product details:
  - `sku`, `title_hint`, `type`, `material`, `color`, `size_info`, `target_audience`, `seasonal_tags`, `language`

---
## 🧱 Prompt Engineering Strategy
- **Role-based prompting**: “You are an SEO expert…”  
- **Instruction hierarchy**: context → product details → constraints  
- **Keyword inclusion**: ensures SEO relevance  
- **Language control**: dynamic, per Excel column  
- **Conciseness enforcement**: maximum 3 sentences  

This method guarantees **consistent, SEO-relevant, and emotionally engaging** descriptions for e-commerce products.

**Prompt structure:**
- Context understanding (SEO + e-commerce tone)
- Language consistency
- Keyword optimization
- Short, customer-focused outputs
- 
## 🧩 Key Features
- 🔠 Multi-language SEO descriptions   
- ⚡ Batch generation from Excel  



###  Model Integration
- **Google Gemini API** via `google-genai` Python client.
- Model options:
  - `gemini-2.0-flash` → text-only generation
  - `gemini-2.5-flash-image-preview` → text generation with optional image understanding
- Images are passed as bytes alongside text prompts if available.

---

###  Streamlit Web Interface
- Upload Excel files.
- Specify optional image folder.
- Map Excel columns dynamically.
- Choose the Gemini model.
- Track generation progress visually.
- Download results as Excel.

---
