 
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
├── app/ # FastAPI backend application
│ ├── api/ # API routes and endpoints
│ ├── models/ # Pydantic data models for validation
│ ├── services/ # Business logic (database, embeddings, similarity)
init.py
├── scripts/ # Utility scripts (seeding, embedding, checks)
├── venv/ # Python virtual environment
├── images/ # Product images (categorized)
│ ├── cars/
│ ├── fruits/
│ ├── phone/
│ ├── softdrink/
│ └── tshirts/
├── config.py # Environment/settings configuration
├── main.py # FastAPI app entrypoint
├── streamlit_app.py # Streamlit interactive frontend app
├── requirements.txt # Python dependencies
├── runtime.txt # Python runtime version (for deployment)
├── .env # Environment variables (not committed)
├── Procfile # Deployment start command (for Render/Heroku)
├── .gitignore

for database 

---

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new project and a free cluster.
3. Create a database user with read/write privileges.
4. Whitelist your IP address or allow access from anywhere (0.0.0.0/0) for demo purposes.
5. Create a database called `visual_product_matcher` and a collection called `products`.
6. Use the provided connection string in your `.env` file as `MONGO_URI`. Include the parameter `&tlsAllowInvalidCertificates=true` for local development on Windows:
   
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true
MONGO_DB=visual_product_matcher
MONGO_COL=products

---

## Installation and Setup

### Prerequisites

- Python 3.10+
- Git
- [pip](https://pip.pypa.io/en/stable/installation/)
- MongoDB Atlas account
- Jina AI API key (free quota available)

### Local Setup

1. Clone the repo:

 ```
 git clone https://github.com/<your-username>/visual-product-matcher.git
 cd visual-product-matcher
 ```

2. Create and activate a virtual environment:

 ```
 python -m venv venv
 source venv/bin/activate  # Linux/macOS
 .\venv\Scripts\activate   # Windows
 ```

3. Install dependencies:

 ```
 pip install -r requirements.txt
 ```

4. Create `.env` file (based on `.env.example`) with your MongoDB and Jina API credentials.

5. Seed product metadata and embeddings:

 ```
 python scripts/seed_from_json.py
 python scripts/embed_products_jina.py
 ```

6. Run FastAPI backend:

 ```
 uvicorn main:app --reload
 ```

7. Run Streamlit frontend:

 ```
 streamlit run streamlit_app.py
 ```

---

## Usage

- Access Streamlit frontend at [http://localhost:8501](http://localhost:8501)
- Browse products or upload/search images for similar products
- Use sidebar to filter categories and adjust similarity thresholds
- The backend API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Deployment

### Backend (FastAPI) on Render

- Push code to GitHub
- Create new Web Service on Render connected to GitHub repo
- Set runtime to Python 3.10 (see `runtime.txt`)
- Set start command to:



- Add environment variables (`MONGO_URI`, `JINA_API_KEY`, etc.) in Render dashboard
- Deploy and test API URL `/docs`

### Frontend (Streamlit) on Streamlit Cloud

- Change `API_BASE` in `streamlit_app.py` to backend URL from Render, e.g.:


## Troubleshooting

- **MongoDB SSL issues on Windows**: Ensure your connection string appends `&tlsAllowInvalidCertificates=true`
- **Slow initial loads**: Free tiers may sleep; wait 30-60 seconds after inactivity
- **Jina API errors**: Check API key limits, image size, and encoding
- **Streamlit UI warnings about `use_container_width`**: Replace with `width="stretch"` or `width="content"`
- **Embedding dimension mismatch**: Ensure Jina model version matches backend embeddings (default: `jina-clip-v2` 768 dims)

---


## Contributing

Contributions and feedback are welcome! Please open issues or submit pull requests.

---

## License

MIT License © 2024

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Jina AI](https://jina.ai/)