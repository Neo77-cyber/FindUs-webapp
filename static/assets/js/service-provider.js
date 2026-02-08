
      /**
       * Form Mobile Optimized - Interactions
       * Minimal JavaScript for enhanced UX
       */

      (function () {
        "use strict";

        // ============================================
        // Multiselect Dropdown
        // ============================================
        function initMultiselect() {
          const triggers = document.querySelectorAll(".multiselect-trigger");
          
          triggers.forEach(trigger => {
            const dropdown = trigger.nextElementSibling;
            if (!dropdown) return;
            
            const checkboxes = dropdown.querySelectorAll(".multiselect-checkbox");
            const searchInput = dropdown.querySelector(".multiselect-search-input");
            const options = dropdown.querySelectorAll(".multiselect-option");

            trigger.addEventListener("click", function (e) {
              e.preventDefault();
              const isExpanded = trigger.getAttribute("aria-expanded") === "true";
              trigger.setAttribute("aria-expanded", !isExpanded);
              dropdown.classList.toggle("active");
            });

            // Close dropdown when clicking outside
            document.addEventListener("click", function (e) {
              if (!trigger.contains(e.target) && !dropdown.contains(e.target)) {
                trigger.setAttribute("aria-expanded", "false");
                dropdown.classList.remove("active");
              }
            });

            // Update trigger text based on selections
            function updateTriggerText() {
              const selected = Array.from(checkboxes)
                .filter((cb) => cb.checked)
                .map((cb) => {
                  const label = cb
                    .closest(".multiselect-option")
                    .querySelector(".multiselect-option-text");
                  return label ? label.textContent : "";
                });

              const placeholder = trigger.querySelector(
                ".multiselect-placeholder"
              );
              if (selected.length === 0) {
                placeholder.textContent = "Select options";
                placeholder.style.color = "var(--text-muted)";
              } else if (selected.length === 1) {
                placeholder.textContent = selected[0];
                placeholder.style.color = "var(--text-primary)";
              } else {
                placeholder.textContent = `${selected.length} selected`;
                placeholder.style.color = "var(--text-primary)";
              }
            }

            checkboxes.forEach((checkbox) => {
              checkbox.addEventListener("change", updateTriggerText);
            });

            if (searchInput) {
              searchInput.addEventListener("input", function () {
                const searchTerm = this.value.toLowerCase();
                options.forEach((option) => {
                  const text = option
                    .querySelector(".multiselect-option-text")
                    .textContent.toLowerCase();
                  option.style.display = text.includes(searchTerm) ? "flex" : "none";
                });
              });
            }
          });
        }

        // ============================================
        // File Upload Preview
        // ============================================
        function initFileUpload() {
          const fileInput = document.getElementById("id_service_image");
          const fileLabel = document.querySelector(
            ".file-upload-label-compact"
          );

          if (!fileInput || !fileLabel) return;

          fileInput.addEventListener("change", function () {
            const file = this.files[0];
            if (!file) return;

            const fileMain = fileLabel.querySelector(
              ".file-upload-main-compact"
            );
            const fileSub = fileLabel.querySelector(".file-upload-sub-compact");

            if (fileMain) {
              fileMain.textContent = file.name;
              fileLabel.style.borderColor = "var(--primary)";
              fileLabel.style.background = "var(--bg-secondary)";
            }

            if (fileSub) {
              const fileSizeKB = (file.size / 1024).toFixed(1);
              const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
              const sizeText =
                file.size < 1024 * 1024
                  ? `${fileSizeKB} KB`
                  : `${fileSizeMB} MB`;
              fileSub.textContent = sizeText;
            }
          });
        }

        // ============================================
        // Collapsible Sections Auto-Expand
        // ============================================
        function initCollapsibles() {
          const collapsibles = document.querySelectorAll(".form-collapsible");

          collapsibles.forEach((collapsible) => {
            const trigger = collapsible.querySelector(
              ".form-collapsible-trigger"
            );

            if (trigger) {
              trigger.addEventListener("click", function () {
                // Scroll into view on mobile when opening
                if (
                  window.innerWidth <= 768 &&
                  !collapsible.hasAttribute("open")
                ) {
                  setTimeout(() => {
                    collapsible.scrollIntoView({
                      behavior: "smooth",
                      block: "start",
                    });
                  }, 300);
                }
              });
            }
          });
        }

        // ============================================
        // Form Validation Helper
        // ============================================

        // ============================================
        // Testimonial Carousel
        // ============================================
        function initTestimonialCarousel() {
          const container = document.querySelector(".testimonials-grid");
          const prevBtn = document.querySelector(".testimonial-prev");
          const nextBtn = document.querySelector(".testimonial-next");

          if (!container) return;

          const cards = container.querySelectorAll(".testimonial-card");
          const cardWidth = cards[0]?.offsetWidth || 340;
          const gap = 24; // 1.5rem
          const scrollAmount = cardWidth + gap;

          let autoSlideInterval;
          const AUTO_SLIDE_DELAY = 5000; // 5 seconds

          function scrollPrev() {
            container.scrollBy({ left: -scrollAmount, behavior: "smooth" });
          }

          function scrollNext() {
            // If at the end, scroll back to start
            if (
              container.scrollLeft + container.clientWidth >=
              container.scrollWidth - 10
            ) {
              container.scrollTo({ left: 0, behavior: "smooth" });
            } else {
              container.scrollBy({ left: scrollAmount, behavior: "smooth" });
            }
          }

          function startAutoSlide() {
            stopAutoSlide();
            autoSlideInterval = setInterval(scrollNext, AUTO_SLIDE_DELAY);
          }

          function stopAutoSlide() {
            if (autoSlideInterval) {
              clearInterval(autoSlideInterval);
              autoSlideInterval = null;
            }
          }

          // Navigation button listeners
          if (prevBtn) {
            prevBtn.addEventListener("click", () => {
              scrollPrev();
              startAutoSlide(); // Reset timer after manual nav
            });
          }

          if (nextBtn) {
            nextBtn.addEventListener("click", () => {
              scrollNext();
              startAutoSlide(); // Reset timer after manual nav
            });
          }

          // Pause auto-slide on hover
          container.addEventListener("mouseenter", stopAutoSlide);
          container.addEventListener("mouseleave", startAutoSlide);

          // Start auto-slide
          startAutoSlide();
        }

        

        // ============================================
        // Initialize on DOM ready
        // ============================================
        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", function () {
            initMultiselect();
            initFileUpload();
            initCollapsibles();
            initTestimonialCarousel();
          });
        } else {
          initMultiselect();
          initFileUpload();
          initCollapsibles();
          initTestimonialCarousel();
          
        }
      })();
   