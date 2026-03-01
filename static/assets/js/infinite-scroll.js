/**
 * Infinite Scroll for FidaMano
 * Handles loading more services without pagination
 */

class InfiniteScroll {
    constructor(options = {}) {
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMorePages = true;
        this.threshold = options.threshold || 100;
        this.containerSelector = options.container || '#dashboard-results, .search-results';
        this.itemsSelector = options.itemsSelector || '.service-card';
        this.loadingSelector = options.loadingSelector || '#infinite-loading';
        this.endpoint = window.location.pathname;
        this.filters = new URLSearchParams(window.location.search);
        
        this.init();
    }

    init() {
        this.container = document.querySelector(this.containerSelector);
        if (!this.container) return;

        // Create loading indicator
        this.createLoadingIndicator();
        
        // Bind scroll event
        this.bindScroll();
        
        // Initial setup
        this.updateCurrentPage();
        console.log('Infinite scroll initialized');
    }

    createLoadingIndicator() {
        const loading = document.createElement('div');
        loading.id = 'infinite-loading';
        loading.className = 'infinite-loading';
        loading.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>{% trans "Caricamento altri servizi..." %}</p>
            </div>
        `;
        this.container.appendChild(loading);
        this.loadingIndicator = loading;
    }

    bindScroll() {
        let ticking = false;
        
        const scrollHandler = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    this.checkScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', scrollHandler);
        window.addEventListener('resize', scrollHandler);
    }

    checkScroll() {
        if (this.isLoading || !this.hasMorePages) return;

        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;

        // Check if user is near bottom
        if (scrollTop + windowHeight >= documentHeight - this.threshold) {
            this.loadMore();
        }
    }

    updateCurrentPage() {
        const pageParam = this.filters.get('page');
        this.currentPage = pageParam ? parseInt(pageParam) : 1;
    }

    async loadMore() {
        if (this.isLoading || !this.hasMorePages) return;

        this.isLoading = true;
        this.showLoading();

        try {
            const nextPage = this.currentPage + 1;
            const url = new URL(window.location.origin + this.endpoint);
            
            // Copy current filters and update page
            const params = new URLSearchParams(this.filters);
            params.set('page', nextPage);
            params.set('infinite_scroll', 'true'); // Flag for server detection
            url.search = params.toString();

            console.log(`Loading page ${nextPage}: ${url.toString()}`);

            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'HX-Request': 'true'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const html = await response.text();
            
            // Parse the response HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Find new items
            const newItems = doc.querySelectorAll(this.itemsSelector);
            
            if (newItems.length > 0) {
                // Append new items to container
                const resultsContainer = this.container.querySelector('.services-grid, .results-grid');
                if (resultsContainer) {
                    newItems.forEach(item => {
                        resultsContainer.appendChild(item);
                    });
                } else {
                    // Fallback: append to main container
                    newItems.forEach(item => {
                        this.container.appendChild(item);
                    });
                }

                this.currentPage = nextPage;
                
                // Update URL without page reload
                const newUrl = new URL(window.location);
                newUrl.searchParams.set('page', nextPage);
                window.history.replaceState({}, '', newUrl);
                
                console.log(`Loaded ${newItems.length} more items`);
            } else {
                // No more items
                this.hasMorePages = false;
                this.showEndMessage();
            }

        } catch (error) {
            console.error('Error loading more items:', error);
            this.showError();
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'block';
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'none';
        }
    }

    showEndMessage() {
        const endMessage = document.createElement('div');
        endMessage.className = 'infinite-end';
        endMessage.innerHTML = `
            <div class="end-message">
                <p>{% trans "Hai visualizzato tutti i servizi disponibili" %}</p>
            </div>
        `;
        this.container.appendChild(endMessage);
    }

    showError() {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'infinite-error';
        errorDiv.innerHTML = `
            <div class="error-message">
                <p>{% trans "Errore nel caricamento. Riprova più tardi." %}</p>
                <button onclick="location.reload()" class="retry-btn">
                    {% trans "Riprova" %}
                </button>
            </div>
        `;
        this.container.appendChild(errorDiv);
    }

    // Public method to reset infinite scroll (useful for filters)
    reset() {
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMorePages = true;
        
        // Remove loading and end messages
        const loading = document.querySelector('#infinite-loading');
        const endMsg = document.querySelector('.infinite-end');
        const errorMsg = document.querySelector('.infinite-error');
        
        [loading, endMsg, errorMsg].forEach(el => {
            if (el) el.remove();
        });
        
        this.updateCurrentPage();
    }
}

// CSS for infinite scroll
const infiniteScrollCSS = `
.infinite-loading {
    padding: 2rem;
    text-align: center;
    display: none;
}

.loading-spinner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #077f46;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.infinite-end {
    padding: 2rem;
    text-align: center;
}

.end-message {
    color: #666;
    font-style: italic;
}

.infinite-error {
    padding: 2rem;
    text-align: center;
}

.error-message {
    color: #dc3545;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.retry-btn {
    background: #077f46;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
}

.retry-btn:hover {
    background: #055c34;
}

@media (max-width: 768px) {
    .infinite-loading,
    .infinite-end,
    .infinite-error {
        padding: 1rem;
    }
}
`;

// Initialize infinite scroll when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add CSS to page
    const style = document.createElement('style');
    style.textContent = infiniteScrollCSS;
    document.head.appendChild(style);

    // Initialize infinite scroll
    window.infiniteScroll = new InfiniteScroll({
        threshold: 200, // Load 200px before bottom
        container: '#dashboard-results, .search-results',
        itemsSelector: '.service-card'
    });

    // Reset infinite scroll when filters change
    const observer = new MutationObserver(() => {
        if (window.infiniteScroll) {
            window.infiniteScroll.reset();
        }
    });

    // Observe results container for changes
    const resultsContainer = document.querySelector('#dashboard-results, .search-results');
    if (resultsContainer) {
        observer.observe(resultsContainer, {
            childList: true,
            subtree: true
        });
    }
});

// Export for global access
window.InfiniteScroll = InfiniteScroll;
