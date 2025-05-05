// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Image Upload Functionality
    setupImageUpload();
    
    // Brand-Model Relationship
    setupBrandModelRelationship();
    
    // Animation on Scroll
    setupAnimations();
});

// Setup image upload preview
function setupImageUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const carImage = document.getElementById('carImage');
    const imagePreview = document.getElementById('imagePreview');
    
    if (uploadArea && carImage) {
        // Click on upload area to trigger file input
        uploadArea.addEventListener('click', function() {
            carImage.click();
        });
        
        // Drag and drop functionality
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                carImage.files = e.dataTransfer.files;
                displayImagePreview(e.dataTransfer.files[0]);
            }
        });
        
        // File input change event
        carImage.addEventListener('change', function() {
            if (this.files.length) {
                displayImagePreview(this.files[0]);
            }
        });
        
        // Function to display image preview
        function displayImagePreview(file) {
            if (!file.type.match('image.*')) {
                alert('Please select an image file');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }
}

// Setup brand-model relationship
function setupBrandModelRelationship() {
    const brandSelect = document.getElementById('brand');
    const modelSelect = document.getElementById('model');
    
    if (brandSelect && modelSelect) {
        brandSelect.addEventListener('change', function() {
            const brand = this.value;
            
            // Clear current options and disable
            modelSelect.innerHTML = '<option value="" selected disabled>Loading models...</option>';
            modelSelect.disabled = true;
            
            // Fetch models for the selected brand
            fetch(`/api/models/${brand}`)
                .then(response => response.json())
                .then(models => {
                    // Create new options
                    modelSelect.innerHTML = '<option value="" selected disabled>Select model</option>';
                    
                    models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model;
                        option.textContent = model;
                        modelSelect.appendChild(option);
                    });
                    
                    // Enable select
                    modelSelect.disabled = false;
                })
                .catch(error => {
                    console.error('Error fetching models:', error);
                    modelSelect.innerHTML = '<option value="" selected disabled>Error loading models</option>';
                });
        });
    }
}

// Setup animations
function setupAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Add dark/light mode toggle
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            fetch('/dark_mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.dark_mode) {
                    document.documentElement.setAttribute('data-bs-theme', 'dark');
                    darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                } else {
                    document.documentElement.setAttribute('data-bs-theme', 'light');
                    darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                }
            });
        });
    }
}); 