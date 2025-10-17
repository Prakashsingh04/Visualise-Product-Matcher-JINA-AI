import streamlit as st
import requests
import base64
from io import BytesIO
import os
import requests
import streamlit as st

# API Base URL (configurable)
# Prefer Streamlit secrets, then environment variable, then default to deployed /api base
API_BASE = (
    st.secrets.get("API_BASE")
    if hasattr(st, "secrets") and "API_BASE" in st.secrets
    else os.getenv("API_BASE", "https://visualise-product-matcher-jina-ai.vercel.app/api")
).rstrip("/")

# Page config
st.set_page_config(
    page_title="Visual Product Matcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .product-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .similarity-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .high-similarity { background: #dcfce7; color: #166534; }
    .med-similarity { background: #fef9c3; color: #854d0e; }
    .low-similarity { background: #f3f4f6; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

# API functions
@st.cache_data(ttl=300)
def get_categories():
    try:
        response = requests.get(f"{API_BASE}/categories", timeout=5)
        if response.status_code == 200:
            return response.json().get("categories", [])
        else:
            try:
                detail = response.json().get('detail')
            except Exception:
                detail = response.text
            st.error(f"Categories fetch failed: {response.status_code} {detail}")
            return []
    except Exception as e:
        st.error(f"Cannot reach backend at {API_BASE}. Error: {e}")
        return []

def get_products(category=None, limit=20, skip=0):
    try:
        params = {"limit": limit, "skip": skip}
        if category:
            params["category"] = category
        response = requests.get(f"{API_BASE}/products", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                detail = response.json().get('detail')
            except Exception:
                detail = response.text
            st.warning(f"Products fetch failed: {response.status_code} {detail}")
            return []
    except Exception as e:
        st.warning(f"Products fetch error: {e}")
        return []

def search_similar_url(image_url, top_k=10, min_similarity=0.25, category=None):
    try:
        payload = {
            "image_url": image_url,
            "top_k": top_k,
            "min_similarity": min_similarity
        }
        if category:
            payload["category"] = category
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                detail = response.json().get('detail')
            except Exception:
                detail = response.text
            st.error(f"Search failed: {response.status_code} {detail}")
            return None
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return None

def search_similar_upload(image_file, top_k=10, min_similarity=0.25, category=None):
    try:
        # Ensure we're at the start and read bytes
        try:
            image_file.seek(0)
        except Exception:
            pass
        file_bytes = image_file.getvalue() if hasattr(image_file, "getvalue") else image_file.read()
        filename = getattr(image_file, "name", "upload.jpg")
        content_type = getattr(image_file, "type", None) or "application/octet-stream"

        files = {
            "file": (filename, file_bytes, content_type)
        }
        params = {
            "top_k": top_k,
            "min_similarity": min_similarity
        }
        if category:
            params["category"] = category
        response = requests.post(
            f"{API_BASE}/search-upload",
            files=files,
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            try:
                detail = response.json().get('detail')
            except Exception:
                detail = response.text
            st.error(f"Upload search failed: {response.status_code} {detail}")
            return None
    except Exception as e:
        st.error(f"Upload search failed: {str(e)}")
        return None

# Main App
st.markdown('<h1 class="main-header">Visual Product Matcher</h1>', unsafe_allow_html=True)
st.markdown("**Find visually similar products using AI-powered image embeddings**")

# Check backend
categories = get_categories()
if not categories:
    st.warning(
        "Cannot connect to backend. Verify your API is reachable at: "
        f"{API_BASE} (try opening {API_BASE}/health and {API_BASE}/categories)"
    )
    st.stop()

# Sidebar
st.sidebar.header("⚙️Search Settings")
st.sidebar.markdown("---")

selected_category = st.sidebar.selectbox(
    "Filter by Category",
    options=["All"] + categories,
    index=0,
    format_func=lambda x: x.capitalize() if x != "All" else "All Categories"
)
category_filter = None if selected_category == "All" else selected_category

st.sidebar.markdown("---")
top_k = st.sidebar.slider("🔢 Number of Results", 1, 20, 10)
min_similarity = st.sidebar.slider("Min Similarity", 0.0, 1.0, 0.3, 0.05, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.info(f"**Current Filter:** {selected_category if selected_category != 'All' else 'All Categories'}")

# Main Content
tab1, tab2, tab3 = st.tabs(["Upload Image", "Search by URL", "Browse Products"])

with tab1:
    st.header("Upload Image File")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        # Avoid AVIF because Pillow on Streamlit Cloud can't decode it by default
        type=[
            'png', 'jpg', 'jpeg', 'webp'
        ],
        help="Upload a local image file to find similar products (PNG, JPG, JPEG, WEBP)"
    )
    
    if uploaded_file:
        col_preview, col_info = st.columns([1, 2])
        
        with col_preview:
            # Try to preview; if PIL can't decode, show a friendly message instead of crashing
            try:
                st.image(uploaded_file, caption="Uploaded Image", width="stretch")
            except Exception:
                st.warning("Preview not available for this file type. The search will still attempt to process it.")
        
        with col_info:
            st.info(f"**File:** {uploaded_file.name}\n\n**Size:** {uploaded_file.size / 1024:.1f} KB\n\n**Type:** {uploaded_file.type}")
            
            if st.button("Find Similar Products", type="primary", key="upload_search"):
                with st.spinner("Processing image and searching..."):
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    
                    # Call search function
                    results = search_similar_upload(
                        uploaded_file,
                        top_k,
                        min_similarity,
                        category_filter
                    )
                    
                    if results and results.get('results'):
                        st.success(f"Found {results['total_results']} similar products!")
                        
                        st.markdown("---")
                        st.subheader("Search Results")
                        
                        cols = st.columns(3)
                        for idx, result in enumerate(results['results']):
                            product = result['product']
                            score = result['similarity_score']
                            
                            with cols[idx % 3]:
                                st.image(product['url'],width="stretch")
                                
                                if score >= 0.8:
                                    badge_class = "high-similarity"
                                elif score >= 0.5:
                                    badge_class = "med-similarity"
                                else:
                                    badge_class = "low-similarity"
                                
                                st.markdown(f"""
                                <div class="product-card">
                                    <h4>{product['name']}</h4>
                                    <p><strong>Category:</strong> {product['category'].title()}</p>
                                    <span class="similarity-badge {badge_class}">
                                        {score:.1%} Match
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                    elif results is not None:
                        st.warning(
                            "No similar products found. Try:\n"
                            "- Lowering the similarity threshold\n"
                            "- Uploading a different image\n"
                            "- Checking if the image category matches your filter"
                        )
                    else:
                        st.error("Search failed. If you uploaded an AVIF image, please convert it to PNG/JPG/WEBP and try again.")

with tab2:
    st.header("Search by Image URL")
    
    col_input, col_preview = st.columns([2, 1])
    
    with col_input:
        image_url = st.text_input(
            "Paste Image URL",
            placeholder="https://res.cloudinary.com/.../image.jpg",
            help="Enter a direct image URL"
        )
        
        search_button = st.button("Find Similar Products", type="primary", key="url_search")
    
    with col_preview:
        if image_url:
            try:
                st.image(image_url, caption="Query Image", width="stretch")
            except:
                st.warning("Invalid image URL")
    
    if search_button:
        if not image_url:
            st.warning("Please enter an image URL")
        else:
            with st.spinner("Generating embedding and searching..."):
                results = search_similar_url(image_url, top_k, min_similarity, category_filter)
                
                if results and results.get('results'):
                    st.success(f"Found {results['total_results']} similar products!")
                    
                    st.markdown("---")
                    st.subheader("Search Results")
                    
                    cols = st.columns(3)
                    for idx, result in enumerate(results['results']):
                        product = result['product']
                        score = result['similarity_score']
                        
                        with cols[idx % 3]:
                            st.image(product['url'], width="stretch")
                            
                            if score >= 0.8:
                                badge_class = "high-similarity"
                            elif score >= 0.5:
                                badge_class = "med-similarity"
                            else:
                                badge_class = "low-similarity"
                            
                            st.markdown(f"""
                            <div class="product-card">
                                <h4>{product['name']}</h4>
                                <p><strong>Category:</strong> {product['category'].title()}</p>
                                <span class="similarity-badge {badge_class}">
                                    {score:.1%} Match
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error("No similar products found.")

with tab3:
    st.header("Browse All Products")
    
    if category_filter:
        st.info(f"Showing: **{category_filter.title()}**")
    
    # Fetch ALL products (no limit)
    with st.spinner("Loading products..."):
        products = get_products(category_filter, 100, 0)  # Increase limit to 100
    
    if products:
        st.write(f"**Total: {len(products)} products**")
        
        # Display in grid (5 columns)
        cols = st.columns(5)
        for idx, product in enumerate(products):
            with cols[idx % 5]:
                st.image(product['url'], width="stretch")
                st.caption(f"**{product['name']}**")
                st.markdown(f"<small> {product['category'].title()}</small>", unsafe_allow_html=True)
    else:
        st.info("No products available.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
    Built with <strong>Streamlit</strong> + <strong>FastAPI</strong> + <strong>MongoDB Atlas</strong> + <strong>Jina AI</strong>
</div>
""", unsafe_allow_html=True)
