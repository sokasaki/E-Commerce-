/**
 * Admin Dashboard - Modern Interactions & Utilities
 * Streetwear E-Commerce Dashboard
 */

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", function () {
  initializeNavigation();
  initializeDropdowns();
  initializeTooltips();
  initializeAnimations();
});

/**
 * Sidebar Navigation Toggle
 */
function initializeNavigation() {
  const toggleButton = document.querySelector('[data-bs-toggle="sidebar"]');
  const mobileToggle = document.getElementById("menu-toggle");
  const wrapper = document.getElementById("wrapper");

  // Handle sidebar toggle button
  if (toggleButton) {
    toggleButton.addEventListener("click", function () {
      wrapper.classList.toggle("toggled");
    });
  }

  // Handle mobile menu toggle button
  if (mobileToggle) {
    mobileToggle.addEventListener("click", function () {
      wrapper.classList.toggle("toggled");
    });
  }

  // Close sidebar on mobile when a link is clicked
  const sidebarLinks = document.querySelectorAll(
    "#sidebar-wrapper .list-group-item"
  );
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", function () {
      if (window.innerWidth < 992) {
        wrapper.classList.remove("toggled");
      }
    });
  });
}

/**
 * Enhanced Dropdown Interactions
 */
function initializeDropdowns() {
  const dropdowns = document.querySelectorAll(".dropdown-toggle");

  dropdowns.forEach((dropdown) => {
    dropdown.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
    });
  });
}

/**
 * Initialize Bootstrap Tooltips
 */
function initializeTooltips() {
  const tooltipElements = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]'
  );
  tooltipElements.forEach((element) => {
    new bootstrap.Tooltip(element);
  });
}

/**
 * Smooth Animations & Transitions
 */
function initializeAnimations() {
  // Fade in cards on scroll
  const cards = document.querySelectorAll(".card, .summary-card");
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  cards.forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition = "opacity 0.4s ease, transform 0.4s ease";
    observer.observe(card);
  });
}

/**
 * Table Row Hover Effects
 */
document.addEventListener("DOMContentLoaded", function () {
  const tableRows = document.querySelectorAll("table tbody tr");

  tableRows.forEach((row) => {
    row.addEventListener("mouseenter", function () {
      this.style.backgroundColor = "rgba(88, 64, 115, 0.05)";
    });

    row.addEventListener("mouseleave", function () {
      this.style.backgroundColor = "";
    });
  });
});

/**
 * Form Validation Utilities
 */
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return false;

  const inputs = form.querySelectorAll(
    "input[required], textarea[required], select[required]"
  );
  let isValid = true;

  inputs.forEach((input) => {
    if (!input.value.trim()) {
      input.classList.add("is-invalid");
      isValid = false;
    } else {
      input.classList.remove("is-invalid");
    }
  });

  return isValid;
}

/**
 * Search functionality for tables
 */
function initializeSearch() {
  const searchInputs = document.querySelectorAll(
    'input[placeholder*="Search"]'
  );

  searchInputs.forEach((input) => {
    input.addEventListener("keyup", function () {
      const searchTerm = this.value.toLowerCase();
      const table = this.closest("form")
        ? this.closest("form").querySelector("table")
        : this.closest(".card-body").querySelector("table");

      if (!table) return;

      const rows = table.querySelectorAll("tbody tr");

      rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? "" : "none";
      });
    });
  });
}

// Initialize search on page load
document.addEventListener("DOMContentLoaded", function () {
  initializeSearch();
});

/**
 * Notification/Toast Helper
 */
function showNotification(message, type = "success", duration = 3000) {
  const alertClass = `alert-${type}`;
  const toast = document.createElement("div");
  toast.className = `alert ${alertClass} alert-dismissible fade show`;
  toast.setAttribute("role", "alert");
  toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  const container = document.querySelector(".container-fluid") || document.body;
  container.insertBefore(toast, container.firstChild);

  setTimeout(() => {
    toast.remove();
  }, duration);
}

/**
 * Sidebar Active State Management
 */
function setActiveSidebarItem() {
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll(
    "#sidebar-wrapper .list-group-item"
  );

  sidebarLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
}

// Set active state on load
document.addEventListener("DOMContentLoaded", function () {
  setActiveSidebarItem();
});

/**
 * Responsive Font Size Adjustment
 */
function adjustFontSizesForResponsive() {
  const headers = document.querySelectorAll("h2");

  window.addEventListener("resize", function () {
    headers.forEach((header) => {
      if (window.innerWidth < 768) {
        header.style.fontSize = "1.5rem";
      } else {
        header.style.fontSize = "2rem";
      }
    });
  });
}

// Initialize responsive adjustments
document.addEventListener("DOMContentLoaded", function () {
  adjustFontSizesForResponsive();
});

/**
 * Export Utilities
 */
function exportTableToCSV(tableId, filename = "export.csv") {
  const table = document.getElementById(tableId);
  if (!table) return;

  let csv = [];
  const rows = table.querySelectorAll("tr");

  rows.forEach((row) => {
    const cols = row.querySelectorAll("td, th");
    const csvRow = [];

    cols.forEach((col) => {
      csvRow.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
    });

    csv.push(csvRow.join(","));
  });

  const csvContent = csv.join("\n");
  const link = document.createElement("a");
  link.href = "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent);
  link.download = filename;
  link.click();
}

/**
 * Print Functionality
 */
function printContent(elementId) {
  const element = document.getElementById(elementId);
  if (!element) return;

  const printWindow = window.open("", "", "width=800,height=600");
  printWindow.document.write("<pre>" + element.innerHTML + "</pre>");
  printWindow.document.close();
  printWindow.print();
}

console.log("✓ Admin Dashboard JavaScript initialized successfully");
