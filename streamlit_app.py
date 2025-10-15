import streamlit as st
import requests

# API Base URL
API_BASE = "http://localhost:8000/api"

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

# API functions with error handling
@st.cache_data(ttl=300)
def get_categories():
    try:
        response = requests.get(f"{API_BASE}/categories", timeout=5)
        if response.status_code == 200:
            return response.json().get("categories", [])
    except:
        st.error("⚠️ Backend API not running. Please start FastAPI with: `uvicorn main:app --reload`")
        return []
    return []

def get_products(category=None, limit=20, skip=0):
    try:
        params = {"limit": limit, "skip": skip}
        if category:
            params["category"] = category
        response = requests.get(f"{API_BASE}/products", params=params, timeout=10)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def search_similar(image_url, top_k=10, min_similarity=0.3, category=None):
    try:
        payload = {
            "image_url": image_url,
            "top_k": top_k,
            "min_similarity": min_similarity
        }
        if category:
            payload["category"] = category
        response = requests.post(f"{API_BASE}/search", json=payload, timeout=30)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return None

# Main App
st.markdown('<h1 class="main-header">🔍 Visual Product Matcher</h1>', unsafe_allow_html=True)
st.markdown("**Find visually similar products using AI-powered image embeddings**")

# Check backend connectivity
categories = get_categories()
if not categories:
    st.warning("⚠️ Cannot connect to backend. Make sure FastAPI is running on http://localhost:8000")
    st.code("uvicorn main:app --reload", language="bash")
    st.stop()

# Sidebar: Controls
st.sidebar.header("⚙️ Search Settings")
st.sidebar.markdown("---")

selected_category = st.sidebar.selectbox(
    "📂 Filter by Category",
    options=["All"] + categories,
    index=0,
    format_func=lambda x: x.capitalize() if x != "All" else "🌐 All Categories"
)
category_filter = None if selected_category == "All" else selected_category

st.sidebar.markdown("---")
top_k = st.sidebar.slider("🔢 Number of Results", 1, 20, 10)
min_similarity = st.sidebar.slider("📊 Min Similarity", 0.0, 1.0, 0.3, 0.05, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.info(f"**Current Filter:** {selected_category if selected_category != 'All' else 'All Categories'}")

# Main Content
tab1, tab2 = st.tabs(["🔎 Search", "📦 Browse Products"])

with tab1:
    st.header("Search by Image URL")
    
    col_input, col_preview = st.columns([2, 1])
    
    with col_input:
        image_url = st.text_input(
            "🖼️ Paste Image URL",
            placeholder="https://res.cloudinary.com/.../image.jpg",
            help="Enter a direct image URL (JPEG, PNG, etc.)"
        )
        
        search_button = st.button("🔎 Find Similar Products", type="primary", use_container_width=True)
    
    with col_preview:
        if image_url:
            try:
                st.image(image_url, caption="Query Image", use_container_width=True)
            except:
                st.warning("Invalid image URL")
    
    if search_button:
        if not image_url:
            st.warning("⚠️ Please enter an image URL")
        else:
            with st.spinner("🔄 Generating embedding and searching database..."):
                results = search_similar(image_url, top_k, min_similarity, category_filter)
                
                if results and results.get('results'):
                    st.success(f"✅ Found {results['total_results']} similar products!")
                    
                    st.markdown("---")
                    st.subheader("Search Results")
                    
                    # Display results in grid
                    cols = st.columns(3)
                    for idx, result in enumerate(results['results']):
                        product = result['product']
                        score = result['similarity_score']
                        
                        with cols[idx % 3]:
                            with st.container():
                                st.image(product['url'], use_container_width=True)
                                
                                # Similarity badge
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
                    st.error("❌ No similar products found. Try adjusting the similarity threshold or use a different image.")

with tab2:
    st.header("Browse All Products")
    
    if category_filter:
        st.info(f"📂 Showing: **{category_filter.title()}**")
    
    products = get_products(category_filter, 15, 0)
    
    if products:
        cols = st.columns(5)
        for idx, product in enumerate(products):
            with cols[idx % 5]:
                st.image(product['url'], use_container_width=True)
                st.caption(f"**{product['name']}**")
                st.text(f"📦 {product['category'].title()}")
    else:
        st.info("No products available in this category.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.9rem;'>
    Built with <strong>Streamlit</strong> + <strong>FastAPI</strong> + <strong>MongoDB Atlas</strong> + <strong>Jina AI</strong>
</div>
""", unsafe_allow_html=True)
