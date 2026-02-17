document.addEventListener("DOMContentLoaded", () => {
  const signinDialog = document.getElementById("signin-dialog");
  const signupDialog = document.getElementById("signup-dialog");

  const openSigninBtn = document.getElementById("open-signin");
  const closeSigninBtn = document.getElementById("close-signin");
  const closeSignupBtn = document.getElementById("close-signup");
  const switchToSignupBtn = document.getElementById("switch-to-signup");
  const switchToSigninBtn = document.getElementById("switch-to-signin");

  const closeAllDialogs = () => {
    signinDialog?.close();
    signupDialog?.close();
  };

  openSigninBtn?.addEventListener("click", () => {
    closeAllDialogs();
    signinDialog?.showModal();
  });

  closeSigninBtn?.addEventListener("click", () => {
    signinDialog?.close();
  });

  closeSignupBtn?.addEventListener("click", () => {
    signupDialog?.close();
  });

  switchToSignupBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    signinDialog?.close();
    signupDialog?.showModal();
  });

  switchToSigninBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    signupDialog?.close();
    signinDialog?.showModal();
  });

  [signinDialog, signupDialog].forEach((dialog) => {
    dialog?.addEventListener("click", (e) => {
      const dialogDimensions = dialog.getBoundingClientRect();
      if (
        e.clientX < dialogDimensions.left ||
        e.clientX > dialogDimensions.right ||
        e.clientY < dialogDimensions.top ||
        e.clientY > dialogDimensions.bottom
      ) {
        dialog.close();
      }
    });
  });

  const eyeIcon = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>`;
  const eyeOffIcon = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;

  document.querySelectorAll(".toggle-password").forEach((btn) => {
    btn.addEventListener("click", function () {
      const container = this.closest(".password-field");
      const passwordInput = container.querySelector("input");

      const isPassword = passwordInput.getAttribute("type") === "password";
      const type = isPassword ? "text" : "password";
      passwordInput.setAttribute("type", type);

      this.innerHTML = isPassword ? eyeOffIcon : eyeIcon;

      this.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
      );
    });
  });

  const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
  const navMenu = document.getElementById("nav-menu");
  const menuOverlay = document.getElementById("menu-overlay");

  const closeMenu = () => {
    navMenu?.classList.remove("active");
    menuOverlay?.classList.remove("active");
  };

  const toggleMenu = () => {
    navMenu?.classList.toggle("active");
    menuOverlay?.classList.toggle("active");
  };

  if (mobileMenuToggle && navMenu) {
    mobileMenuToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleMenu();
    });

    menuOverlay?.addEventListener("click", closeMenu);

    document.addEventListener("click", (e) => {
      if (
        navMenu.classList.contains("active") &&
        !navMenu.contains(e.target) &&
        !mobileMenuToggle.contains(e.target)
      ) {
        closeMenu();
      }
    });

    navMenu.querySelectorAll("a, button").forEach((link) => {
      link.addEventListener("click", closeMenu);
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 768) {
        navMenu.classList.remove("active");
        menuOverlay.classList.remove("active");
      }
    });
  }

  const searchSidebar = document.getElementById("search-sidebar");
  const btnMobileFilters = document.getElementById("btn-mobile-filters");
  const btnCloseFilters = document.getElementById("btn-close-filters");
  const btnApplyFilters = document.getElementById("btn-apply-filters");
  const btnCancelFilters = document.getElementById("btn-cancel-filters");

  const openFilterSidebar = () => {
    searchSidebar?.classList.add("open");
    document.body.style.overflow = "hidden";
  };

  const closeFilterSidebar = () => {
    searchSidebar?.classList.remove("open");
    document.body.style.overflow = "";
  };

  btnMobileFilters?.addEventListener("click", openFilterSidebar);
  btnCloseFilters?.addEventListener("click", closeFilterSidebar);
  btnApplyFilters?.addEventListener("click", closeFilterSidebar);
  btnCancelFilters?.addEventListener("click", closeFilterSidebar);

  const detectLocation = (inputElement, buttonElement) => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }

    buttonElement?.classList.add("loading");

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        try {
          const response = await fetch(
            `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
          );
          const data = await response.json();
          inputElement.value =
            data.city ||
            data.locality ||
            `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`;
        } catch (error) {
          console.error("Error fetching location:", error);
          inputElement.value = `${latitude.toFixed(2)}, ${longitude.toFixed(
            2
          )}`;
        } finally {
          buttonElement?.classList.remove("loading");
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        alert("Unable to retrieve your location");
        buttonElement?.classList.remove("loading");
      }
    );
  };

  const detectLocationBtn = document.getElementById("detect-location");
  const locationInput = document.getElementById("location");
  detectLocationBtn?.addEventListener("click", () =>
    detectLocation(locationInput, detectLocationBtn)
  );

  const filterDetectBtn = document.getElementById("filter-detect-location");
  const filterLocationInput = document.getElementById("filter-location");
  filterDetectBtn?.addEventListener("click", () =>
    detectLocation(filterLocationInput, filterDetectBtn)
  );

  const setupDropdown = (triggerId, menuId, inputId, dropdownClass) => {
    const trigger = document.getElementById(triggerId);
    const menu = document.getElementById(menuId);
    const input = document.getElementById(inputId);
    const dropdown = trigger?.closest(dropdownClass);
    const textSpan = trigger?.querySelector(".category-text, .region-text");

    if (trigger && menu && dropdown) {
      trigger.addEventListener("click", (e) => {
        e.stopPropagation();

        // Close other dropdowns
        document.querySelectorAll(".category-dropdown").forEach((d) => {
          if (d !== dropdown) d.classList.remove("open");
        });

        dropdown.classList.toggle("open");
      });

      menu.querySelectorAll(".category-option").forEach((option) => {
        option.addEventListener("click", (e) => {
          e.stopPropagation();

          menu
            .querySelectorAll(".category-option")
            .forEach((opt) => opt.classList.remove("active"));
          option.classList.add("active");

          const selectedValue = option.dataset.value;
          const selectedText = option.textContent;

          if (textSpan) textSpan.textContent = selectedText;
          if (input) input.value = selectedValue;

          dropdown.classList.remove("open");
        });
      });
    }
  };

  setupDropdown(
    "category-trigger",
    "category-menu",
    "category-input",
    ".category-dropdown"
  );
  setupDropdown(
    "region-trigger",
    "region-menu",
    "region-input",
    ".category-dropdown"
  );

  document.addEventListener("click", (e) => {
    document.querySelectorAll(".category-dropdown").forEach((dropdown) => {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".category-dropdown").forEach((dropdown) => {
        dropdown.classList.remove("open");
      });
    }
  });

  const searchForm = document.getElementById("service-search");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      const service = document.getElementById("service-type")?.value;
      const category = document.getElementById("category-input")?.value;
      console.log(`Searching for "${service}" in category "${category}"`);
    });
  }

  document.querySelectorAll(".filter-dropdown").forEach((dropdown) => {
    const trigger = dropdown.querySelector(".filter-trigger");
    const menu = dropdown.querySelector(".filter-menu");

    trigger?.addEventListener("click", (e) => {
      e.stopPropagation();
      const wasOpen = dropdown.classList.contains("open");

      document
        .querySelectorAll(".filter-dropdown")
        .forEach((d) => d.classList.remove("open"));

      if (!wasOpen) dropdown.classList.add("open");
    });

    menu?.addEventListener("click", (e) => {
      e.stopPropagation();
    });
  });

  document.addEventListener("click", () => {
    document
      .querySelectorAll(".filter-dropdown")
      .forEach((d) => d.classList.remove("open"));
  });

  const filterDropdowns = document.querySelectorAll(".filter-dropdown");
  const inlineClearBtn = document.querySelector(".inline-clear-filters");

  filterDropdowns.forEach((dropdown) => {
    const trigger = dropdown.querySelector(".filter-dropdown-trigger");
    const menu = dropdown.querySelector(".filter-dropdown-menu");

    trigger?.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.contains("open");

      filterDropdowns.forEach((d) => {
        d.classList.remove("open");
        d.querySelector(".filter-dropdown-trigger")?.setAttribute(
          "aria-expanded",
          "false"
        );
      });

      if (!isOpen) {
        dropdown.classList.add("open");
        trigger.setAttribute("aria-expanded", "true");

        if (menu) {
          const rect = trigger.getBoundingClientRect();
          menu.style.position = "fixed";
          menu.style.top = `${rect.bottom + 8}px`;
          menu.style.left = `${rect.left}px`;
        }
      }
    });

    menu?.addEventListener("click", (e) => {
      e.stopPropagation();
    });
  });

  document.addEventListener("click", () => {
    filterDropdowns.forEach((dropdown) => {
      dropdown.classList.remove("open");
      dropdown
        .querySelector(".filter-dropdown-trigger")
        ?.setAttribute("aria-expanded", "false");
    });
  });

  inlineClearBtn?.addEventListener("click", () => {
    const checkboxes = document.querySelectorAll(
      '.inline-filters input[type="checkbox"]'
    );
    checkboxes.forEach((cb) => {
      cb.checked = false;
    });
  });
});

// Add this to your main.js file
document.addEventListener('DOMContentLoaded', function() {
  const button = document.getElementById('language-button');
  const dropdown = document.getElementById('language-dropdown');
  
  // Only run if these elements exist (prevent errors on pages without language switcher)
  if (!button || !dropdown) return;
  
  const options = dropdown.querySelectorAll('.language-option');
  const form = document.getElementById('language-form');
  
  // Toggle dropdown
  button.addEventListener('click', function(e) {
      e.stopPropagation();
      const expanded = this.getAttribute('aria-expanded') === 'true' ? false : true;
      this.setAttribute('aria-expanded', expanded);
      dropdown.classList.toggle('open', expanded);
  });
  
  // Handle option selection
  options.forEach(function(option) {
      option.addEventListener('click', function(e) {
          e.preventDefault();
          
          // Update button display
          const flag = this.querySelector('.fi').className;
          const label = this.textContent.trim();
          
          button.querySelector('.fi').className = flag;
          button.querySelector('.language-label').textContent = label;
          
          // Update active state
          options.forEach(function(opt) {
              opt.classList.remove('active');
          });
          this.classList.add('active');
          
          // Submit the form with the selected language
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'language';
          input.value = this.getAttribute('data-value');
          form.appendChild(input);
          form.submit();
          
          // Close dropdown
          dropdown.classList.remove('open');
          button.setAttribute('aria-expanded', 'false');
      });
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', function(e) {
      if (!button.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.classList.remove('open');
          button.setAttribute('aria-expanded', 'false');
      }
  });
  
  // Close on escape key
  document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
          dropdown.classList.remove('open');
          button.setAttribute('aria-expanded', 'false');
      }
  });
});
