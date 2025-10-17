# Visual Product Matcher

An end-to-end AI-powered application that lets users upload an image or provide an image URL to find the top visually similar products present in database.  
Built with **FastAPI**, **Streamlit**, **MongoDB Atlas**, **Cloudinary**, and **Jina AI (CLIP v2)**. Deployed on **Vercel** (backend) and **Streamlit Cloud** (frontend).

## Live Demo

- **Frontend (Streamlit):** https://visualise-appuct-matcher-jina-ai-6yvussbfby48ctg9bdchz7.streamlit.app/
- **Backend (Vercel):** https://visualise-product-matcher-jina-ai.vercel.app/
  - Swagger Docs: `/docs`
  - Health: `/health`
  - Key endpoints: `/api/products`, `/api/categories`, `/api/search`, `/api/search-upload`

---

## Highlights

- Dual-input search: you can either upload image or paste url
- Image embeddings via **Jina CLIP v2** (768-dim vectors)  
- Cosine similarity ranking of all categories  
- Categories : cars, fruits, phone, softdrink, tshirts  
- Images hosted on  **Cloudinary CDN**  
- Used **FastAPI** and async **MongoDB (Motor)**  
- Frontend **Streamlit UI** with category filter and threshold controls(in sidebar top left)  

---

## Project Structure
```
Visualise-Product-Matcher-JINA-AI/
├── app/
│ ├── api/              # REST routes (search, products, upload)
│ ├── models/           # Pydantic schemas
│ └── services/         # MongoDB, Jina, similarity
├── scripts/            # Seed, embed, and diagnostic scripts
├── images/             # Optional local samples downloaded (by category)
├── main.py             # FastAPI entrypoint
├── streamlit_app.py    # Streamlit UI (frontend)
├── config.py           # pydantic-settings
├── requirements.txt    # contain requirements
├── runtime.txt         # Python version for deployment
└── uploaded_urls.json  # urls hosted on cloudinary 
```

---

## Key API Endpoints

- **GET /api/products** — List products with pagination and optional category  
- **POST /api/search** — Search by image URL `{ image_url, top_k, min_similarity, category? }`  
- **POST /api/search-upload** — Search by uploaded image (form-data file)  
- **GET /api/categories** —  categories  

Swagger Docs: https://visualise-product-matcher-jina-ai.vercel.app/docs

---

## Catalog & Embeddings

- **Total products:** 53  
- **Categories:** 5 (cars, fruits, phone, softdrink, tshirts)  
- **Embeddings:** Jina CLIP v2, 768 dimensions (always re-embed if dimensions mismatch)  
- **Storage:** MongoDB Atlas (products collection)  

**Fields:**  
`name, category, url, embedding, embedding_dim, embedding_source`

---

## Tech Stack

- **Backend:** FastAPI, Motor, NumPy, Pydantic  
- **Frontend:** Streamlit  
- **Vectorization/embedding:** Jina AI (jina-clip-v2)  
- **Infra:** MongoDB Atlas, Cloudinary  
- **Deployment:** Vercel (backend) + Streamlit Cloud (frontend)  
- **CI/CD:** GitHub → Vercel/Streamlit auto-deploy

---

## Environment Setup

`.env` template (for local development):
```bash
MONGO_URI=mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority
MONGO_DB=visual_product_matcher
MONGO_COL=products
JINA_API_KEY=your_jina_api_key
JINA_ENDPOINT=https://api.jina.ai/v1/embeddings
APP_HOST=127.0.0.1
APP_PORT=8000
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run locally:
```bash
# Backend
uvicorn main:app --reload

# Frontend
streamlit run streamlit_app.py
```

## Model Compatibility

- Backend uses Jina CLIP v2 for embeddings (768 dimensions)
- Products must have matching embedding dimensions for similarity search
- If embeddings mismatch, re-run `embed_products_jina.py` to refresh all vectors

---

## How Similarity Works

1. Generate query image embedding via **Jina CLIP v2**  
2. Fetch product vectors from MongoDB  
3. Compute cosine similarity
4. Filter by category, threshold, and return top-k ranked products  

---

## About

Built by **Prakash Singh**
**GitHub:** [@Prakashsingh04](https://github.com/Prakashsingh04)

---

## License

**MIT License** — You are free to use, modify, and share this project.
