// ============================================================================
// SHOPPING CART FUNCTIONALITY
// ============================================================================
// This file handles shopping cart operations for the e-commerce site.
// Product data is now fetched from the Flask backend API.
// ============================================================================

// ============================================================================
// CART STATE AND INITIALIZATION
// ============================================================================

let cart = JSON.parse(localStorage.getItem("cart")) || []; // Load cart from localStorage
const emptyCartMessage = document.getElementById("emptyCartMessage");
const totalElement = document.querySelector(".total h4");

// Save cart to localStorage
function saveCart() {
  localStorage.setItem("cart", JSON.stringify(cart));
}

// ============================================================================
// CART FUNCTIONS
// ============================================================================

// Add product to the cart
function addCartHome(selectedProduct) {
  if (selectedProduct) {
    const existingItem = cart.find(
      (item) => item.title === selectedProduct.title
    );
    if (existingItem) {
      existingItem.quantity = (existingItem.quantity || 1) + 1;
    } else {
      selectedProduct.quantity = 1;
      cart.push(selectedProduct);
    }
    saveCart();
    displayCart();
  } else {
    console.error("Product not found or invalid product object passed.");
  }
}

// Display cart contents
function displayCart() {
  const offcanvasBody = document.querySelector(
    "#offcanvasCart .offcanvas-body"
  );
  const viewCartBtn = document.querySelector('a[href*="cart"]');
  const checkoutBtn = document.querySelector('a[href*="check"]');

  if (!offcanvasBody) {
    console.error("Offcanvas body not found.");
    return;
  }

  if (cart.length === 0) {
    offcanvasBody.innerHTML =
      '<p class="text-muted text-center" id="emptyCartMessage">Your cart is empty.</p>';
    totalElement.innerHTML = "<h4>$0.00</h4>";
    document.querySelector(".icons.count").textContent = "0";

    // Disable buttons when cart is empty
    if (viewCartBtn) {
      viewCartBtn.classList.add("disabled");
      viewCartBtn.style.pointerEvents = "none";
      viewCartBtn.style.opacity = "0.5";
    }
    if (checkoutBtn) {
      checkoutBtn.classList.add("disabled");
      checkoutBtn.style.pointerEvents = "none";
      checkoutBtn.style.opacity = "0.5";
    }
    return;
  }

  let cartHtml = "";
  let totalPrice = 0;
  let totalItems = 0;

  cart.forEach((item, index) => {
    const quantity = item.quantity || 1;
    const itemPrice = item.price * quantity;
    totalPrice += itemPrice;
    totalItems += quantity;
    cartHtml += `
            <div class="cart-item d-flex align-items-center mb-3 pb-3 border-bottom">
                <img src="${item.image}" class="img-fluid rounded me-3" alt="${
      item.title
    }" style="width: 48px; height: 48px; object-fit: cover;">
                <div class="cart-item-details flex-grow-1">
                    <h6 class="cart-item-title mb-1">${item.title}</h6>
                    <div class="d-flex align-items-center mt-1">
                        <button class="btn btn-outline-secondary btn-sm px-2 me-1" type="button" onclick="changeQuantity(${index}, -1)"><i class="fa fa-minus"></i></button>
                        <span class="mx-2">${quantity}</span>
                        <button class="btn btn-outline-secondary btn-sm px-2 ms-1" type="button" onclick="changeQuantity(${index}, 1)"><i class="fa fa-plus"></i></button>
                    </div>
                </div>
                <div class="text-end ms-3">
                    <div class="fw-bold">$${itemPrice.toFixed(2)}</div>
                    <button type="button" class="btn btn-outline-danger btn-sm mt-2" aria-label="Remove" onclick="deleteItem(${index})"><i class="fa fa-trash"></i></button>
                </div>
            </div>
        `;
  });

  offcanvasBody.innerHTML = cartHtml;
  totalElement.innerHTML = `<h4>$${totalPrice.toFixed(2)}</h4>`;
  document.querySelector(".icons.count").textContent = totalItems.toString();

  // Enable buttons when cart has items
  if (viewCartBtn) {
    viewCartBtn.classList.remove("disabled");
    viewCartBtn.style.pointerEvents = "auto";
    viewCartBtn.style.opacity = "1";
  }
  if (checkoutBtn) {
    checkoutBtn.classList.remove("disabled");
    checkoutBtn.style.pointerEvents = "auto";
    checkoutBtn.style.opacity = "1";
  }
}

// Delete product from the cart
function deleteItem(index) {
  cart.splice(index, 1);
  saveCart();
  displayCart();
}

// Add this function to handle quantity changes
function changeQuantity(index, delta) {
  if (cart[index]) {
    cart[index].quantity = Math.max(1, (cart[index].quantity || 1) + delta);
    saveCart();
    displayCart();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // Navbar scroll effect
  const mainNavbar = document.getElementById("mainNavbar");
  if (mainNavbar) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 50) {
        // Adjust scroll threshold as needed
        mainNavbar.classList.add("scrolled");
      } else {
        mainNavbar.classList.remove("scrolled");
      }
    });
  }

  // Display cart on load
  displayCart();

  // Initialize shop page functionality if on shop page
  if (document.getElementById("productsContainer")) {
    initializeShopPage();
  }
});

// ============================================================================
// SHOP PAGE FUNCTIONALITY
// ============================================================================

let allProducts = [];
let currentProducts = [];

function initializeShopPage() {
  // Get products from server-rendered data
  if (typeof shopProducts !== "undefined") {
    allProducts = shopProducts;
    currentProducts = [...allProducts];
    updateResultsCount();
  }

  // Search functionality
  const searchInput = document.getElementById("searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const searchTerm = this.value.toLowerCase();
      if (searchTerm === "") {
        currentProducts = [...allProducts];
      } else {
        currentProducts = allProducts.filter(
          (product) =>
            product.title.toLowerCase().includes(searchTerm) ||
            product.category.toLowerCase().includes(searchTerm)
        );
      }
      renderProducts();
      updateResultsCount();
    });
  }

  // Handle search form submission
  const searchForm = document.getElementById("searchForm");
  if (searchForm) {
    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      applyFilters();
    });
  }
}

// Apply filters function
function applyFilters() {
  const category = document.getElementById("categoryFilter").value;
  const sort = document.getElementById("sortFilter").value;
  const search = document.getElementById("searchInput").value;

  // Show loading spinner
  document.getElementById("loadingSpinner").classList.remove("d-none");

  // Build URL with parameters
  const params = new URLSearchParams();
  if (category !== "all") params.append("category", category);
  if (search) params.append("search", search);
  if (sort !== "default") params.append("sort", sort);

  // Fetch filtered products
  fetch("/api/products/filter?" + params.toString())
    .then((response) => response.json())
    .then((data) => {
      currentProducts = data;
      renderProducts();
      updateResultsCount();
    })
    .catch((error) => {
      console.error("Error fetching filtered products:", error);
    })
    .finally(() => {
      // Hide loading spinner
      document.getElementById("loadingSpinner").classList.add("d-none");
    });
}

// Clear filters function
function clearFilters() {
  document.getElementById("categoryFilter").value = "all";
  document.getElementById("sortFilter").value = "default";
  document.getElementById("searchInput").value = "";

  // Reset to all products
  currentProducts = [...allProducts];
  renderProducts();
  updateResultsCount();
}

// Render products function
function renderProducts() {
  const container = document.getElementById("productsContainer");

  if (currentProducts.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5">
        <h3 class="text-muted">No products found</h3>
        <p>Try adjusting your filters or search terms</p>
      </div>
    `;
    return;
  }

  container.innerHTML = currentProducts
    .map(
      (product, index) => `
    <div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-4 product-card">
      <div class="card position-relative h-100">
        <a href="/detail?name=${encodeURIComponent(
          product.title
        )}" class="text-decoration-none text-dark">
          <img src="${
            product.image
          }" class="card-img-top" loading="lazy" alt="${
        product.title
      }" style="height: 250px; object-fit: cover;">
          <div class="card-body text-center">
            <h5 class="card-title fw-semibold text-truncate mb-1">${
              product.title
            }</h5>
            <p class="card-text text-muted small mb-2">${product.category}</p>
            <p class="card-text fw-bold fs-5 text-dark product-price">$${
              product.price
            }</p>
          </div>
        </a>
        <div class="card-footer bg-white border-0">
          <button type="button" class="btn btn-primary add-to-cart-btn w-100" data-product-index="${index}">
            Add to cart
          </button>
        </div>
      </div>
    </div>
  `
    )
    .join("");

  // Attach event listeners to all add-to-cart buttons
  const addToCartButtons = container.querySelectorAll(".add-to-cart-btn");
  addToCartButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const productIndex = parseInt(this.getAttribute("data-product-index"));
      const product = currentProducts[productIndex];
      addCartHome(product);
    });
  });
}

// Update results count
function updateResultsCount() {
  const resultsCount = document.getElementById("resultsCount");
  if (resultsCount) {
    const count = currentProducts.length;
    const total = allProducts.length;
    resultsCount.textContent = `Showing ${count} of ${total} products`;
  }
}
