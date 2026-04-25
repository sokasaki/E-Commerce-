/**
 * STYLELESS - Main Application Script (Vue.js Powered)
 * Real-time, reactive cart management with shared state
 */

const { createApp, ref, computed, onMounted, reactive } = Vue;

// 1. Shared Reactive State (accessible by both Vue and Global functions)
const cartState = reactive({
    items: [],
    loading: false,
    async sync() {
        try {
            const response = await fetch('/api/cart');
            const data = await response.json();
            if (Array.isArray(data)) {
                this.items = data.map(item => ({
                    id: item.id,
                    cart_item_id: item.cart_item_id,
                    title: item.title || item.name,
                    price: parseFloat(item.price),
                    image: item.image || item.image_url,
                    quantity: item.quantity || 1
                }));
                localStorage.setItem("cart", JSON.stringify(this.items));
            }
        } catch (err) {
            console.error('Sync Error:', err);
        }
    },
    async addToBag(product) {
        if (!product) return;
        const formData = new FormData();
        formData.append('product_id', product.id);
        formData.append('quantity', 1);

        try {
            const response = await fetch('/cart/add', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            
            if (response.status === 401) {
                if (window.notify) window.notify('Please log in to add items.', 'Access Denied', 'warning');
                else alert('Please log in to add items.');
                setTimeout(() => window.location.href = '/login', 1500);
                return;
            }

            const data = await response.json();
            if (data.message) {
                if (window.notify) window.notify(data.message, 'Added to Bag', 'success');
                await this.sync();
            }
        } catch (err) {
            console.error('Add Error:', err);
        }
    }
});

// 2. Vue Application
const cartApp = createApp({
    setup() {
        const cart = computed(() => cartState.items);
        const cartCount = computed(() => cartState.items.reduce((acc, item) => acc + item.quantity, 0));
        const cartTotal = computed(() => cartState.items.reduce((acc, item) => acc + (item.price * item.quantity), 0));

        const updateQty = async (index, delta) => {
            const item = cartState.items[index];
            if (!item) return;

            const newQty = Math.max(1, (item.quantity || 1) + delta);
            if (item.cart_item_id) {
                const formData = new FormData();
                formData.append('item_id', item.cart_item_id);
                formData.append('quantity', newQty);

                try {
                    await fetch('/cart/update', { method: 'POST', body: formData });
                    await cartState.sync();
                } catch (err) {
                    console.error('Update Error:', err);
                }
            }
        };

        const removeItem = async (index) => {
            const item = cartState.items[index];
            if (!item || !item.cart_item_id) return;

            try {
                await fetch(`/cart/remove/${item.cart_item_id}`, { method: 'POST' });
                await cartState.sync();
            } catch (err) {
                console.error('Delete Error:', err);
            }
        };

        onMounted(() => {
            const saved = localStorage.getItem("cart");
            if (saved) cartState.items = JSON.parse(saved);
            cartState.sync();
        });

        return {
            cart,
            cartCount,
            cartTotal,
            updateQty,
            removeItem
        };
    },
    delimiters: ['[[', ']]']
});

// Mount the App
cartApp.mount('#cartApp');

// 3. Global Compatibility Layer (Legacy Function Names)
window.addCartHome = (product) => {
    cartState.addToBag(product);
};

// ============================================================================
// NON-VUE LOGIC (Shop Grid & Filters)
// ============================================================================

let allProducts = [];
let currentProducts = [];

function initializeShopPage() {
    if (typeof shopProducts !== "undefined") {
        allProducts = shopProducts;
        currentProducts = [...allProducts];
        renderProducts();
        updateResultsCount();
    }

    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("input", () => applyFilters());
    }
}

function applyFilters() {
    const category = document.getElementById("categoryFilter")?.value || "all";
    const sort = document.getElementById("sortFilter")?.value || "default";
    const search = document.getElementById("searchInput")?.value.toLowerCase() || "";

    currentProducts = allProducts.filter(p => {
        const matchesCategory = (category === "all") || (p.category === category);
        const matchesSearch = (p.title || p.name || "").toLowerCase().includes(search);
        return matchesCategory && matchesSearch;
    });

    if (sort === "price-low") currentProducts.sort((a, b) => a.price - b.price);
    else if (sort === "price-high") currentProducts.sort((a, b) => b.price - a.price);
    else if (sort === "newest") currentProducts.sort((a, b) => (b.id || 0) - (a.id || 0));

    renderProducts();
    updateResultsCount();
}

function renderProducts() {
    const container = document.getElementById("productsContainer");
    if (!container) return;

    if (currentProducts.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="fa-solid fa-search fs-1 text-muted mb-3 opacity-25"></i>
                <h3 class="fw-bold">No results found</h3>
            </div>
        `;
        return;
    }

    container.innerHTML = currentProducts.map((p) => `
        <div class="col-lg-4 col-md-6 col-6">
            <div class="premium-card">
                <div class="card-img-box">
                    <a href="/detail?id=${p.id}">
                        <img src="${p.image || p.image_url}" alt="${p.title || p.name}">
                    </a>
                </div>
                <div class="premium-card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1 me-3">
                            <a href="/detail?id=${p.id}" class="card-product-title text-truncate">${p.title || p.name}</a>
                            <div class="card-product-price">$${parseFloat(p.price).toFixed(2)}</div>
                        </div>
                        <button class="btn-add-mini" onclick="addCartHome(${JSON.stringify(p).replace(/"/g, '&quot;')})" title="Add to Bag">
                            <i class="fa fa-shopping-bag"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join("");
}

function updateResultsCount() {
    const countEl = document.getElementById("resultsCount");
    if (countEl) countEl.textContent = `${currentProducts.length} Items Found`;
}

// Global Transitions
document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("productsContainer")) initializeShopPage();

    const navbar = document.getElementById("mainNavbar");
    if (navbar) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 40) navbar.classList.add("scrolled");
            else navbar.classList.remove("scrolled");
        });
    }
});
