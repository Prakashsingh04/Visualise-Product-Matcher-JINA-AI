# Visual Product Matcher

An end-to-end AI-powered application that lets users upload an image or provide an image URL to find the top visually similar products from a curated catalog.  
Built with **FastAPI**, **Streamlit**, **MongoDB Atlas**, **Cloudinary**, and **Jina AI (CLIP v2)**.

---

## What this shows

- Production-grade Python full stack with clean API design and async I/O  
- Practical use of vector embeddings for similarity search at scale  
- Robust data pipeline: seed → embed → serve → search  
- Cloud-ready architecture with clear separation of concerns and deploy scripts  

---

## Highlights

- Dual-input search: Upload image or paste image URL  
- Image embeddings via **Jina CLIP v2** (768-dim vectors)  
- Cosine similarity ranking across categories  
- Categories supported: cars, fruits, phone, softdrink, tshirts  
- Images served via **Cloudinary CDN**  
- Minimal-latency API with **FastAPI** and async **MongoDB (Motor)**  
- Clean **Streamlit UI** with category filter and threshold controls  

---

## Project Structure

Visualise-Product-Matcher-JINA-AI/
├── app/
│ ├── api/ # REST routes (search, products, upload)
│ ├── models/ # Pydantic schemas
│ └── services/ # MongoDB, Jina, similarity
├── scripts/ # Seed, embed, and diagnostic scripts
├── images/ # Optional local samples (by category)
├── main.py # FastAPI entrypoint
├── streamlit_app.py # Streamlit UI (upload + URL search + browse)
├── config.py # Settings via pydantic-settings
├── requirements.txt # Locked, deploy-tested deps
├── Procfile # Render start command
├── runtime.txt # Python version for deployment
└── uploaded_urls.json # 54 Cloudinary URLs (cars/fruits/phone/softdrink/tshirts)


---

## Key API Endpoints

- **GET /api/products** — List products with pagination and optional category  
- **POST /api/search** — Search by image URL `{ image_url, top_k, min_similarity, category? }`  
- **POST /api/search-upload** — Search by uploaded image (form-data file)  
- **GET /api/categories** — Supported categories  

Swagger Docs: `http://<backend-host>/docs`

---

## Catalog & Embeddings

- **Total products:** 54  
- **Categories:** 5 (cars, fruits, phone, softdrink, tshirts)  
- **Embeddings:** Jina CLIP v2, 768 dimensions  
- **Storage:** MongoDB Atlas (products collection)  

**Fields:**  
`name, category, url, embedding, embedding_dim, embedding_source`

---

## Tech Stack

- **Backend:** FastAPI, Motor, NumPy, Pydantic  
- **Frontend:** Streamlit (URL search, upload, browse, filters)  
- **Vectorization:** Jina AI (jina-clip-v2)  
- **Infra:** MongoDB Atlas, Cloudinary  
- **Deployment:** Ready for Render + Streamlit Cloud  

---

## Live

- **Backend (FastAPI):** *(add your Render URL)*  
- **Frontend (Streamlit):** *(add your Streamlit Cloud URL)*  

---

## How Similarity Works

1. Generate query image embedding via **Jina CLIP v2**  
2. Fetch product vectors from MongoDB  
3. Compute cosine similarity:

   \[
   sim(a,b) = \frac{a \cdot b}{\|a\| \|b\|}
   \]

4. Filter by category (optional), threshold, and return top-k ranked products  

---

## Engineering Decisions

- Kept embeddings in MongoDB for simplicity and portability; can be swapped with a vector DB if scale demands  
- Standardized on CLIP v2 (768-dim) to ensure consistent similarity metrics across upload and URL modes  
- Streamlit chosen for rapid iteration and clean UX in Python without a separate JS stack  

---

## What Could Be Next

- Switch to a dedicated vector database (Qdrant, Pinecone) for >100k items  
- Batch embedding refresh pipeline and drift monitoring  
- Reranking with cross-modal models for tighter precision  
- Authentication and per-tenant catalogs  
- Containerized deployment with CI/CD  

---

## About

Built by **Prakash Singh** — Python developer focused on ML systems, API engineering, and cloud-first applications.  
**GitHub:** [@Prakashsingh04](https://github.com/Prakashsingh04)  
**LinkedIn:** *(add your link)*  

---

## License

**MIT License** — You are free to use, modify, and share this project.
