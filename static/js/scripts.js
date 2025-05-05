// Main JavaScript Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Dark Mode Toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            // Send request to server to toggle dark mode
            fetch('/dark_mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                // Update the theme attribute
                document.documentElement.setAttribute('data-bs-theme', data.dark_mode ? 'dark' : 'light');
                
                // Update icon
                const icon = darkModeToggle.querySelector('i');
                if (icon) {
                    if (data.dark_mode) {
                        icon.classList.remove('fa-moon');
                        icon.classList.add('fa-sun');
                    } else {
                        icon.classList.remove('fa-sun');
                        icon.classList.add('fa-moon');
                    }
                }
            });
        });
    }
    
    // Image Upload Preview
    const uploadArea = document.getElementById('uploadArea');
    const imageInput = document.getElementById('carImage');
    const imagePreview = document.getElementById('imagePreview');
    
    if (uploadArea && imageInput) {
        // Drag and drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            uploadArea.classList.add('dragover');
        }
        
        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }
        
        // Handle file drop
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                imageInput.files = files;
                updateImagePreview(files[0]);
                
                // Add camera shutter effect
                addShutterEffect();
            }
        }
        
        // Handle file input change
        imageInput.addEventListener('change', function() {
            if (this.files.length) {
                updateImagePreview(this.files[0]);
                
                // Add camera shutter effect
                addShutterEffect();
            }
        });
        
        // Click on upload area to trigger file input
        uploadArea.addEventListener('click', function() {
            imageInput.click();
        });
        
        // Preview the image
        function updateImagePreview(file) {
            if (!file.type.match('image.*')) {
                return;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                if (imagePreview) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    
                    // Add zoom-in animation
                    imagePreview.classList.remove('zoom-in');
                    void imagePreview.offsetWidth; // Trigger reflow
                    imagePreview.classList.add('zoom-in');
                }
            }
            
            reader.readAsDataURL(file);
        }
        
        // Shutter effect
        function addShutterEffect() {
            const shutter = document.createElement('div');
            shutter.classList.add('shutter-effect');
            shutter.style.position = 'fixed';
            shutter.style.top = '0';
            shutter.style.left = '0';
            shutter.style.width = '100%';
            shutter.style.height = '100%';
            shutter.style.backgroundColor = '#000';
            shutter.style.opacity = '0.8';
            shutter.style.zIndex = '9999';
            shutter.style.transition = 'opacity 0.2s ease-out';
            
            document.body.appendChild(shutter);
            
            setTimeout(() => {
                shutter.style.opacity = '0';
                setTimeout(() => {
                    document.body.removeChild(shutter);
                }, 200);
            }, 100);
        }
    }
    
    // Brand/Model Dynamic Dropdowns
    const brandSelect = document.getElementById('brand');
    const modelSelect = document.getElementById('model');
    
    if (brandSelect && modelSelect) {
        brandSelect.addEventListener('change', function() {
            const brand = this.value;
            
            // Clear current options except the first one
            while (modelSelect.options.length > 1) {
                modelSelect.remove(1);
            }
            
            // Fetch models for selected brand
            fetch(`/api/models/${brand}`)
                .then(response => response.json())
                .then(models => {
                    // Add loading class
                    modelSelect.parentElement.classList.add('is-loading');
                    
                    setTimeout(() => {
                        // Add new options
                        models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            
                            // Add with slide-in animation (handled by CSS)
                            option.classList.add('slide-in');
                            modelSelect.appendChild(option);
                        });
                        
                        // Remove loading class
                        modelSelect.parentElement.classList.remove('is-loading');
                        
                        // Enable model select
                        modelSelect.removeAttribute('disabled');
                    }, 300); // Small delay for animation
                });
        });
    }
    
    // Animation for elements when they come into view
    const animateOnScroll = function() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        
        animatedElements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight * 0.9) {
                // Add the animation class specified in the data attribute
                const animation = element.dataset.animation || 'fade-in';
                element.classList.add(animation);
                element.classList.remove('animate-on-scroll');
            }
        });
    };
    
    // Initial check for elements in view
    animateOnScroll();
    
    // Check for new elements coming into view on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Form Submission Loading State - We handle estimate form in its own template
    const estimateForm = document.getElementById('estimateForm');
    const submitButton = document.querySelector('#estimateForm button[type="submit"]');
    
    // We're handling the estimateForm separately in the estimate.html template
    // This is to avoid duplicate loading spinners
    if (estimateForm && submitButton && window.location.pathname !== '/estimate') {
        estimateForm.addEventListener('submit', function() {
            // Show loading spinner
            submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Processing...
            `;
            submitButton.disabled = true;
            
            // Form will be submitted normally
        });
    }
    
    // Interactive hover effects for cards
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Confetti effect for estimation completion
    const showConfetti = document.getElementById('showConfetti');
    
    if (showConfetti) {
        // Create and trigger confetti when the estimation result page loads
        const canvas = document.createElement('canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '1000';
        document.body.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const confetti = [];
        const confettiCount = 150;
        const gravity = 0.5;
        const terminalVelocity = 5;
        const drag = 0.075;
        const colors = [
            { front: '#3498db', back: '#2980b9' },
            { front: '#e74c3c', back: '#c0392b' },
            { front: '#2ecc71', back: '#27ae60' },
            { front: '#f39c12', back: '#e67e22' },
            { front: '#9b59b6', back: '#8e44ad' }
        ];
        
        // Initialize confetti
        for (let i = 0; i < confettiCount; i++) {
            confetti.push({
                color: colors[Math.floor(Math.random() * colors.length)],
                dimensions: {
                    x: Math.random() * 10 + 5,
                    y: Math.random() * 10 + 5,
                },
                position: {
                    x: Math.random() * canvas.width,
                    y: -20,
                },
                rotation: Math.random() * 2 * Math.PI,
                scale: {
                    x: 1,
                    y: 1,
                },
                velocity: {
                    x: Math.random() * 25 - 12.5,
                    y: Math.random() * 10 + 3,
                },
            });
        }
        
        // Render loop
        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            confetti.forEach((confetto, index) => {
                let width = confetto.dimensions.x * confetto.scale.x;
                let height = confetto.dimensions.y * confetto.scale.y;
                
                // Move confetto
                confetto.velocity.x -= confetto.velocity.x * drag;
                confetto.velocity.y = Math.min(confetto.velocity.y + gravity, terminalVelocity);
                confetto.velocity.x += Math.random() > 0.5 ? Math.random() : -Math.random();
                
                confetto.position.x += confetto.velocity.x;
                confetto.position.y += confetto.velocity.y;
                
                // Spin confetto
                confetto.rotation += 0.01;
                
                // Draw confetto
                ctx.save();
                ctx.translate(confetto.position.x, confetto.position.y);
                ctx.rotate(confetto.rotation);
                
                // Draw back
                ctx.fillStyle = confetto.color.back;
                ctx.fillRect(-width / 2, -height / 2, width, height);
                
                // Draw front
                ctx.fillStyle = confetto.color.front;
                ctx.fillRect(-width / 2 + 1, -height / 2 + 1, width - 2, height - 2);
                
                ctx.restore();
                
                // Remove confetti when they fall off screen or after a specific timeframe
                if (confetto.position.y >= canvas.height) {
                    confetti.splice(index, 1);
                }
            });
            
            // Stop animation when all confetti are gone
            if (confetti.length <= 0) {
                document.body.removeChild(canvas);
                return;
            }
            
            window.requestAnimationFrame(render);
        }
        
        // Start animation
        window.requestAnimationFrame(render);
    }
});

// Scroll reveal animations
document.addEventListener('DOMContentLoaded', function() {
    // Scroll reveal
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    function checkInView() {
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            const isVisible = (elementTop < window.innerHeight - 100) && (elementBottom > 0);
            
            if (isVisible) {
                element.classList.add('visible');
            }
        });
    }
    
    // Check on load
    checkInView();
    
    // Check on scroll
    window.addEventListener('scroll', checkInView);
    
    // Add magical particle effects
    createParticles();
    
    // Add hover effects to important buttons
    addButtonEffects();
    
    // Initialize dynamic models for brand and car type selection
    initDynamicModels();
});

// Create particle effects
function createParticles() {
    const container = document.createElement('div');
    container.className = 'particle-container';
    container.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
        overflow: hidden;
    `;
    document.body.appendChild(container);
    
    // Create particles
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        const size = Math.random() * 6 + 2;
        
        particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: rgba(255, 255, 255, ${Math.random() * 0.3 + 0.2});
            border-radius: 50%;
            top: ${Math.random() * 100}vh;
            left: ${Math.random() * 100}vw;
            pointer-events: none;
            opacity: ${Math.random() * 0.8 + 0.2};
            animation: float ${Math.random() * 10 + 10}s linear infinite;
            box-shadow: 0 0 ${size * 2}px rgba(157, 78, 221, 0.8);
        `;
        
        // Add random animation delay
        particle.style.animationDelay = `${Math.random() * 10}s`;
        container.appendChild(particle);
    }
    
    // Add CSS animation for floating effect
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes float {
            0% {
                transform: translateY(0) translateX(0);
            }
            25% {
                transform: translateY(-${Math.random() * 30 + 20}px) translateX(${Math.random() * 30 + 10}px);
            }
            50% {
                transform: translateY(-${Math.random() * 20 + 10}px) translateX(-${Math.random() * 30 + 10}px);
            }
            75% {
                transform: translateY(${Math.random() * 20 + 10}px) translateX(${Math.random() * 30 + 10}px);
            }
            100% {
                transform: translateY(0) translateX(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Add hover effects to buttons
function addButtonEffects() {
    const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
    
    buttons.forEach(button => {
        button.addEventListener('mouseover', function(e) {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size * 2}px;
                height: ${size * 2}px;
                left: ${e.clientX - rect.left - size}px;
                top: ${e.clientY - rect.top - size}px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                transform: scale(0);
                transition: transform 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.appendChild(ripple);
            
            // Start animation on next frame
            requestAnimationFrame(() => {
                ripple.style.transform = 'scale(1)';
                ripple.style.opacity = '0';
            });
            
            // Remove after animation completes
            setTimeout(() => {
                ripple.remove();
            }, 700);
        });
    });
}

// Initialize dynamic models
function initDynamicModels() {
    // Get the brand and model elements
    const brandSelect = document.getElementById('brand');
    const modelSelect = document.getElementById('model');
    
    if (brandSelect && modelSelect) {
        // Add event listener to brand select
        brandSelect.addEventListener('change', function() {
            const brand = this.value;
            
            if (brand) {
                // Show loading
                modelSelect.innerHTML = '<option value="">Loading...</option>';
                modelSelect.disabled = true;
                
                // Fetch car models for the selected brand
                fetch(`/api/models/${brand}`)
                    .then(response => response.json())
                    .then(models => {
                        // Reset the model select
                        modelSelect.innerHTML = '<option value="">Select Model</option>';
                        
                        // Add the models
                        models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model;
                            option.textContent = model;
                            modelSelect.appendChild(option);
                        });
                        
                        // Enable model select
                        modelSelect.disabled = false;
                    })
                    .catch(error => {
                        console.error('Error fetching models:', error);
                        modelSelect.innerHTML = '<option value="">Error loading models</option>';
                        modelSelect.disabled = false;
                    });
            } else {
                // Reset and disable model select
                modelSelect.innerHTML = '<option value="">Select Brand First</option>';
                modelSelect.disabled = true;
            }
        });
    }
}

// Add mousemove interactive background effect
document.addEventListener('mousemove', function(e) {
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    
    // Create a subtle gradient following the mouse
    document.body.style.backgroundImage = `
        radial-gradient(
            circle at ${x * 100}% ${y * 100}%,
            rgba(123, 44, 191, 0.15),
            rgba(13, 27, 42, 0.05) 50%
        ),
        linear-gradient(135deg, var(--dark-color), var(--dark-color-light))
    `;
});

// Add magical typing effect to title elements
document.addEventListener('DOMContentLoaded', function() {
    const titles = document.querySelectorAll('h1.display-4');
    
    titles.forEach(title => {
        const text = title.textContent;
        title.textContent = '';
        title.classList.add('gradient-text');
        
        let i = 0;
        const typeInterval = setInterval(() => {
            if (i < text.length) {
                title.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(typeInterval);
                title.classList.add('pulse');
            }
        }, 100);
    });
}); 