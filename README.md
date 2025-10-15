# Visual Product Matcher with Jina AI, FastAPI, and Streamlit

## Overview

This project is a **Visual Product Matcher** web application that allows users to search for visually similar products by uploading images or providing image URLs. It leverages:

- **FastAPI**: Backend REST API for product metadata and similarity search
- **MongoDB Atlas**: Cloud NoSQL database to store product metadata and embeddings
- **Jina AI**: State-of-the-art image embedding service through their API
- **Streamlit**: Interactive Python frontend for easy UI and image upload/search

The system extracts image embeddings using Jina AI, stores them in MongoDB, and performs cosine similarity matching to find visually similar products.

---

## Directory Structure

product-matcher/
├── app/                          # FastAPI backend application
│   ├── api/                      # API routes and endpoints
│   ├── models/                   # Pydantic data models for validation
│   ├── services/                 # Business logic (database, embeddings, similarity)
│   └── __init__.py
│
├── scripts/                      # Utility scripts (seeding, embedding, checks)
│
├── venv/                         # Python virtual environment
│
├── images/                       # Product images (categorized)
│   ├── cars/
│   ├── fruits/
│   ├── phone/
│   ├── softdrink/
│   └── tshirts/
│
├── config.py                     # Environment/settings configuration
├── main.py                       # FastAPI app entrypoint
├── streamlit_app.py              # Streamlit interactive frontend app
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python runtime version (for deployment)
├── .env                          # Environment variables (not committed)
├── Procfile                      # Deployment start command (for Render/Heroku)
└── .gitignore                    # Git ignore file



---

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new project and a free cluster.
3. Create a database user with read/write privileges.
4. Whitelist your IP address or allow access from anywhere (0.0.0.0/0) for demo purposes.
5. Create a database called `visual_product_matcher` and a collection called `products`.
6. Use the provided connection string in your `.env` file as `MONGO_URI`. Include the parameter `&tlsAllowInvalidCertificates=true` for local development on Windows:
   

---

##  Quickstart

### 1. Clone Repository


git clone https://github.com/Prakashsingh04/Visualise-Product-Matcher-JINA-AI.git
cd Visualise-Product-Matcher-JINA-AI


### 2. Environment Setup

Create a `.env` file in the project root:

MongoDB Atlas
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true
MONGO_DB=visual_product_matcher
MONGO_COL=products

Jina AI
JINA_API_KEY=your_jina_api_key
JINA_ENDPOINT=https://api.jina.ai/v1/embeddings


### 3. Install Dependencies

Create virtual environment
python -m venv venv

Activate virtual environment
Windows:
.\venv\Scripts\activate

Linux/macOS:
source venv/bin/activate

Install packages
pip install -r requirements.txt

---

##  Building the Database

1. Place your images in `images/` subfolders named for their category (e.g., `fruits`, `cars`, `phone`)
2. Upload images to Cloudinary and save URLs in `uploaded_urls.json`
3. Run the seeding and embedding scripts:

Seed product metadata
python scripts/seed_from_json.py

Generate embeddings with Jina AI
python scripts/embed_products_jina.py


This will:

 Import product metadata (name, category, URL) into MongoDB  
 Generate 768-dimensional embeddings using Jina CLIP v2  
 Store embeddings alongside products for fast similarity search

---

##  Running the App

### 1. Start the Backend

uvicorn main:app --reload

Backend will run on `http://localhost:8000`  
API docs available at `http://localhost:8000/docs`

### 2. Start the Frontend

streamlit run streamlit_app.py

Frontend will open on `http://localhost:8501`

---

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API health check |
| `/health` | GET | Service health status |
| `/api/products` | GET | List all products (with pagination & filters) |
| `/api/products/{id}` | GET | Get single product by ID |
| `/api/search` | POST | Search by image URL (JSON: `{ image_url, top_k, min_similarity }`) |
| `/api/search-upload` | POST | Search by uploading image (form-data) |
| `/api/categories` | GET | Get all product categories |

---

## 🖼️ Core Components

### Frontend (Streamlit)

- **Upload Image Tab** - Select and preview local images before searching
- **Search by URL Tab** - Paste image URLs for instant search
- **Browse Products Tab** - View all products with category filters
- **Category Filter** - Sidebar filtering for cars, fruits, phones, softdrinks, tshirts
- **Similarity Slider** - Adjustable minimum similarity threshold (0.0 - 1.0)

### Backend (FastAPI)

- **Jina AI Service** - Generate 768-dim image embeddings using CLIP v2 model
- **MongoDB Service** - Async database operations with Motor driver
- **Similarity Service** - Cosine similarity calculations with NumPy
- **Product Models** - Pydantic validation for requests/responses

---

## 🛠️ Tech Stack

### Frontend

- **Streamlit** - Interactive Python web framework
- **Requests** - HTTP client for API calls
- **Pillow** - Image processing and resizing

### Backend

- **FastAPI** - Modern async Python web framework
- **Motor** - Async MongoDB driver
- **MongoDB Atlas** - Cloud NoSQL database
- **Jina AI** - Image embeddings (jina-clip-v2, 768 dimensions)
- **NumPy** - Efficient cosine similarity computation
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server

### Infrastructure

- **Cloudinary** - Image CDN and storage
- **Render** - Backend deployment (free tier)
- **Streamlit Cloud** - Frontend deployment (free tier)

---

##  Deployment

### Backend on Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Configure:
   - **Runtime**: Python 3.10 (see `runtime.txt`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard
5. Deploy and get your API URL

### Frontend on Streamlit Cloud

1. Update `API_BASE` in `streamlit_app.py` to your Render backend URL
2. Push changes to GitHub
3. Create new app in Streamlit Cloud
4. Set **Main file**: `streamlit_app.py`
5. Add secrets:
## Dataset

The project includes **54 products** across **5 categories**:

- Cars (12 items)
- Fruits (10 items)
- Phones (10 items)
- Soft Drinks (11 items)
- T-Shirts (11 items)

All images hosted on Cloudinary CDN for fast global delivery.

---## License

MIT License. Feel free to use, modify, and share!


## Contact

**Prakash Singh**  

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - Interactive Python apps
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Cloud database
- [Jina AI](https://jina.ai/) - State-of-the-art image embeddings
- [Cloudinary](https://cloudinary.com/) - Image CDN and management