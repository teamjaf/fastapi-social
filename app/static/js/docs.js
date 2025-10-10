// Fast Social Media API Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Copy to clipboard functionality
    function addCopyButtons() {
        document.querySelectorAll('code').forEach(code => {
            if (code.textContent.length > 20) { // Only add to longer code blocks
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-btn';
                copyBtn.innerHTML = '📋';
                copyBtn.title = 'Copy to clipboard';
                copyBtn.style.cssText = `
                    position: absolute;
                    top: 0.5rem;
                    right: 0.5rem;
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: 0.25rem;
                    padding: 0.25rem 0.5rem;
                    cursor: pointer;
                    font-size: 0.75rem;
                    opacity: 0.7;
                    transition: opacity 0.3s ease;
                `;
                
                copyBtn.addEventListener('mouseenter', () => {
                    copyBtn.style.opacity = '1';
                });
                
                copyBtn.addEventListener('mouseleave', () => {
                    copyBtn.style.opacity = '0.7';
                });
                
                copyBtn.addEventListener('click', async () => {
                    try {
                        await navigator.clipboard.writeText(code.textContent);
                        copyBtn.innerHTML = '✅';
                        setTimeout(() => {
                            copyBtn.innerHTML = '📋';
                        }, 2000);
                    } catch (err) {
                        console.error('Failed to copy: ', err);
                    }
                });
                
                // Make parent relative positioned
                code.style.position = 'relative';
                code.appendChild(copyBtn);
            }
        });
    }

    // Add copy buttons after content loads
    setTimeout(addCopyButtons, 100);

    // Search functionality
    function addSearch() {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search endpoints...';
        searchInput.className = 'search-input';
        searchInput.style.cssText = `
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            font-size: 1rem;
            margin-bottom: 2rem;
            background: var(--bg-primary);
            transition: border-color 0.3s ease;
        `;

        searchInput.addEventListener('focus', () => {
            searchInput.style.borderColor = 'var(--primary-color)';
        });

        searchInput.addEventListener('blur', () => {
            searchInput.style.borderColor = 'var(--border-color)';
        });

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const endpoints = document.querySelectorAll('.endpoint');
            
            endpoints.forEach(endpoint => {
                const text = endpoint.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    endpoint.style.display = 'block';
                } else {
                    endpoint.style.display = 'none';
                }
            });
        });

        // Insert search input after the header
        const header = document.querySelector('.header');
        if (header) {
            header.insertAdjacentElement('afterend', searchInput);
        }
    }

    addSearch();

    // Add interactive features to endpoint cards
    function enhanceEndpoints() {
        document.querySelectorAll('.endpoint').forEach(endpoint => {
            // Add click to expand/collapse details
            const header = endpoint.querySelector('.endpoint-header');
            if (header) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    const details = endpoint.querySelector('.endpoint-details');
                    if (details) {
                        details.style.display = details.style.display === 'none' ? 'grid' : 'none';
                    }
                });
            }

            // Add hover effects
            endpoint.addEventListener('mouseenter', () => {
                endpoint.style.transform = 'translateX(5px)';
                endpoint.style.boxShadow = 'var(--shadow-lg)';
            });

            endpoint.addEventListener('mouseleave', () => {
                endpoint.style.transform = 'translateX(0)';
                endpoint.style.boxShadow = 'none';
            });
        });
    }

    enhanceEndpoints();

    // Add loading animation
    function addLoadingAnimation() {
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    addLoadingAnimation();

    // Add tooltips for status codes
    function addTooltips() {
        document.querySelectorAll('.status-code').forEach(statusCode => {
            const code = statusCode.textContent;
            let tooltip = '';
            
            switch(code) {
                case '200': tooltip = 'Success - Request completed successfully'; break;
                case '201': tooltip = 'Created - Resource created successfully'; break;
                case '204': tooltip = 'No Content - Request successful but no content returned'; break;
                case '400': tooltip = 'Bad Request - Invalid request data'; break;
                case '401': tooltip = 'Unauthorized - Authentication required'; break;
                case '403': tooltip = 'Forbidden - Access denied'; break;
                case '404': tooltip = 'Not Found - Resource not found'; break;
                case '422': tooltip = 'Unprocessable Entity - Validation error'; break;
                case '500': tooltip = 'Internal Server Error - Server error'; break;
                default: tooltip = `HTTP ${code} status code`; break;
            }
            
            statusCode.title = tooltip;
            statusCode.style.cursor = 'help';
        });
    }

    addTooltips();

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.search-input');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });

    // Add scroll to top button
    function addScrollToTop() {
        const scrollBtn = document.createElement('button');
        scrollBtn.innerHTML = '↑';
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 3rem;
            height: 3rem;
            border-radius: 50%;
            background: var(--primary-color);
            color: white;
            border: none;
            cursor: pointer;
            font-size: 1.25rem;
            font-weight: bold;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
        `;

        scrollBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollBtn.style.opacity = '1';
            } else {
                scrollBtn.style.opacity = '0';
            }
        });

        document.body.appendChild(scrollBtn);
    }

    addScrollToTop();

    // Add theme toggle
    function addThemeToggle() {
        const themeBtn = document.createElement('button');
        themeBtn.innerHTML = '🌙';
        themeBtn.className = 'theme-toggle';
        themeBtn.title = 'Toggle theme';
        themeBtn.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            width: 3rem;
            height: 3rem;
            border-radius: 50%;
            background: var(--primary-color);
            color: white;
            border: 2px solid var(--border-color);
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-lg);
        `;

        // Check for saved theme preference or default to dark
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeBtn.innerHTML = savedTheme === 'dark' ? '🌙' : '☀️';

        themeBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            themeBtn.innerHTML = newTheme === 'dark' ? '🌙' : '☀️';
            localStorage.setItem('theme', newTheme);
        });

        document.body.appendChild(themeBtn);
    }

    addThemeToggle();
});
