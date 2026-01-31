/**
 * Enhanced Form Validation and Feedback
 * Provides real-time validation and user-friendly feedback
 */

(function () {
  "use strict";

  /**
   * Validate email format
   */
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  /**
   * Validate phone number (basic validation)
   */
  function validatePhone(phone) {
    const re = /^[0-9\s\-\+\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, "").length >= 10;
  }

  /**
   * Validate required fields
   */
  function validateRequired(value) {
    return value.trim().length > 0;
  }

  /**
   * Validate password strength
   */
  function validatePasswordStrength(password) {
    if (password.length < 8) return false;
    // At least one uppercase, one lowercase, one number
    return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password);
  }

  /**
   * Show validation message
   */
  function showValidation(input, isValid, message = "") {
    const inputGroup = input.closest(".mb-3") || input.closest(".form-group");

    if (isValid) {
      input.classList.remove("is-invalid");
      input.classList.add("is-valid");
      if (message) {
        let feedback = inputGroup?.querySelector(".valid-feedback");
        if (!feedback) {
          feedback = document.createElement("div");
          feedback.className = "valid-feedback";
          input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        feedback.textContent = message;
      }
    } else {
      input.classList.remove("is-valid");
      input.classList.add("is-invalid");
      if (message) {
        let feedback = inputGroup?.querySelector(".invalid-feedback");
        if (!feedback) {
          feedback = document.createElement("div");
          feedback.className = "invalid-feedback";
          input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        feedback.textContent = message;
      }
    }
  }

  /**
   * Real-time validation listeners
   */
  function attachValidationListeners() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach((input) => {
      input.addEventListener("blur", function () {
        const isValid = validateEmail(this.value);
        showValidation(
          this,
          isValid,
          isValid ? "Email is valid" : "Please enter a valid email address",
        );
      });

      input.addEventListener("input", function () {
        if (this.classList.contains("is-invalid")) {
          const isValid = validateEmail(this.value);
          showValidation(this, isValid, isValid ? "" : "Invalid email format");
        }
      });
    });

    // Phone validation
    const phoneInputs = document.querySelectorAll(
      'input[type="tel"], input[name="phone"], input[name="phoneNumber"]',
    );
    phoneInputs.forEach((input) => {
      input.addEventListener("blur", function () {
        if (this.value.trim().length === 0) return;
        const isValid = validatePhone(this.value);
        showValidation(
          this,
          isValid,
          isValid
            ? "Phone number is valid"
            : "Please enter a valid phone number",
        );
      });
    });

    // Required field validation
    const requiredInputs = document.querySelectorAll("[required]");
    requiredInputs.forEach((input) => {
      input.addEventListener("blur", function () {
        const isValid = validateRequired(this.value);
        if (!isValid) {
          showValidation(
            this,
            false,
            `${this.placeholder || "This field"} is required`,
          );
        }
      });

      input.addEventListener("input", function () {
        if (this.classList.contains("is-invalid")) {
          const isValid = validateRequired(this.value);
          if (isValid) {
            showValidation(this, true);
          }
        }
      });
    });

    // Password strength validation
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach((input) => {
      input.addEventListener("input", function () {
        const strength = validatePasswordStrength(this.value);
        const messages = {
          length: this.value.length < 8 ? "Minimum 8 characters required" : "",
          strength:
            !strength && this.value.length >= 8
              ? "Password must contain uppercase, lowercase, and numbers"
              : "",
        };

        const message =
          messages.length || messages.strength || "Strong password";
        showValidation(this, strength && this.value.length >= 8, message);
      });
    });
  }

  /**
   * Form submission validation
   */
  function attachFormSubmitValidation() {
    const forms = document.querySelectorAll("form");
    forms.forEach((form) => {
      form.addEventListener("submit", function (e) {
        const requiredInputs = this.querySelectorAll("[required]");
        let isFormValid = true;

        requiredInputs.forEach((input) => {
          const isValid = validateRequired(input.value);
          showValidation(
            input,
            isValid,
            isValid ? "" : `${input.placeholder || input.name} is required`,
          );
          if (!isValid) isFormValid = false;
        });

        if (!isFormValid) {
          e.preventDefault();
        }
      });
    });
  }

  /**
   * Clear validation on focus
   */
  function attachClearValidationOnFocus() {
    const inputs = document.querySelectorAll("input, textarea, select");
    inputs.forEach((input) => {
      input.addEventListener("focus", function () {
        this.classList.remove("is-valid", "is-invalid");
      });
    });
  }

  /**
   * Initialize all validations when DOM is ready
   */
  document.addEventListener("DOMContentLoaded", function () {
    attachValidationListeners();
    attachFormSubmitValidation();
    attachClearValidationOnFocus();
  });

  // Export for use in other scripts
  window.FormValidation = {
    validateEmail,
    validatePhone,
    validateRequired,
    validatePasswordStrength,
    showValidation,
  };
})();
