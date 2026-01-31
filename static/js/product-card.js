// Premium Product Card Interactions

document.addEventListener("DOMContentLoaded", function () {
  initializeSaveButtons();
});

function initializeSaveButtons() {
  const saveButtons = document.querySelectorAll(".btn-save");

  saveButtons.forEach((btn) => {
    // Check if product is already saved in localStorage
    const productId = btn.getAttribute("data-product-id");
    const savedProducts = JSON.parse(
      localStorage.getItem("savedProducts") || "[]",
    );

    if (savedProducts.includes(productId)) {
      btn.classList.add("saved");
      btn.innerHTML = '<i class="fas fa-heart"></i>';
    }

    // Add click handler
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleSaveProduct(this);
    });
  });
}

function toggleSaveProduct(btn) {
  const productId = btn.getAttribute("data-product-id");
  const savedProducts = JSON.parse(
    localStorage.getItem("savedProducts") || "[]",
  );
  const isSaved = btn.classList.contains("saved");

  if (isSaved) {
    // Remove from saved
    btn.classList.remove("saved");
    btn.innerHTML = '<i class="far fa-heart"></i>';
    const index = savedProducts.indexOf(productId);
    if (index > -1) {
      savedProducts.splice(index, 1);
    }
    showNotification("Removed from saved items", "info");
  } else {
    // Add to saved
    btn.classList.add("saved");
    btn.innerHTML = '<i class="fas fa-heart"></i>';
    if (!savedProducts.includes(productId)) {
      savedProducts.push(productId);
    }
    showNotification("Saved to your wishlist", "success");
  }

  localStorage.setItem("savedProducts", JSON.stringify(savedProducts));
}

function showNotification(message, type = "info") {
  // Remove any existing notifications
  const existingNotif = document.querySelector(".premium-notification");
  if (existingNotif) {
    existingNotif.remove();
  }

  // Create notification element
  const notification = document.createElement("div");
  notification.className = `premium-notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <i class="notification-icon fas fa-${getIconForType(type)}"></i>
      <span>${message}</span>
    </div>
  `;

  document.body.appendChild(notification);

  // Trigger animation
  setTimeout(() => {
    notification.classList.add("show");
  }, 10);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

function getIconForType(type) {
  const icons = {
    success: "check-circle",
    info: "info-circle",
    warning: "exclamation-circle",
    danger: "times-circle",
  };
  return icons[type] || "info-circle";
}

// Add notification styles dynamically
const style = document.createElement("style");
style.textContent = `
  .premium-notification {
    position: fixed;
    bottom: -100px;
    right: 2rem;
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    z-index: 9999;
    transition: bottom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    max-width: 350px;
    min-width: 280px;
  }

  .premium-notification.show {
    bottom: 2rem;
  }

  .notification-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.95rem;
    font-weight: 500;
  }

  .notification-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
  }

  .notification-success {
    border-left: 4px solid #10b981;
  }

  .notification-success .notification-icon {
    color: #10b981;
  }

  .notification-info {
    border-left: 4px solid #3b82f6;
  }

  .notification-info .notification-icon {
    color: #3b82f6;
  }

  .notification-warning {
    border-left: 4px solid #f59e0b;
  }

  .notification-warning .notification-icon {
    color: #f59e0b;
  }

  .notification-danger {
    border-left: 4px solid #ef4444;
  }

  .notification-danger .notification-icon {
    color: #ef4444;
  }

  /* Mobile responsive */
  @media (max-width: 576px) {
    .premium-notification {
      right: 1rem;
      left: 1rem;
      max-width: none;
    }
  }
`;
document.head.appendChild(style);
