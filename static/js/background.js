// Canvas Background Animation
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('background-canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Check if dark mode is enabled
    function isDarkMode() {
        return document.documentElement.getAttribute('data-bs-theme') === 'dark';
    }
    
    // Car silhouette objects
    const cars = [];
    const numCars = 15;
    
    // Car silhouette path data
    const carPathLight = [
        {x: 0, y: 15},
        {x: 5, y: 15},
        {x: 10, y: 10},
        {x: 25, y: 10},
        {x: 30, y: 5},
        {x: 45, y: 5},
        {x: 50, y: 10},
        {x: 55, y: 10},
        {x: 60, y: 15},
        {x: 0, y: 15}
    ];
    
    const carPathDark = [
        {x: 0, y: 15},
        {x: 5, y: 15},
        {x: 10, y: 10},
        {x: 25, y: 10},
        {x: 30, y: 5},
        {x: 45, y: 5},
        {x: 50, y: 10},
        {x: 55, y: 10},
        {x: 60, y: 15},
        {x: 0, y: 15}
    ];
    
    // Initialize cars
    function initCars() {
        cars.length = 0;
        for (let i = 0; i < numCars; i++) {
            cars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: Math.random() * 0.5 + 0.5,
                speedX: (Math.random() - 0.5) * 1.5,
                speedY: (Math.random() - 0.5) * 1.5,
                opacity: Math.random() * 0.3 + 0.1,
                path: isDarkMode() ? carPathDark : carPathLight
            });
        }
    }
    
    // Draw car silhouette
    function drawCar(car) {
        ctx.save();
        ctx.translate(car.x, car.y);
        ctx.scale(car.size, car.size);
        
        ctx.beginPath();
        ctx.moveTo(car.path[0].x, car.path[0].y);
        
        for (let i = 1; i < car.path.length; i++) {
            ctx.lineTo(car.path[i].x, car.path[i].y);
        }
        
        ctx.closePath();
        
        if (isDarkMode()) {
            ctx.fillStyle = `rgba(255, 255, 255, ${car.opacity})`;
        } else {
            ctx.fillStyle = `rgba(52, 152, 219, ${car.opacity})`;
        }
        
        ctx.fill();
        ctx.restore();
    }
    
    // Update car positions
    function updateCars() {
        for (const car of cars) {
            car.x += car.speedX;
            car.y += car.speedY;
            
            // Wrap around screen edges
            if (car.x < -100) car.x = canvas.width + 50;
            if (car.x > canvas.width + 100) car.x = -50;
            if (car.y < -100) car.y = canvas.height + 50;
            if (car.y > canvas.height + 100) car.y = -50;
        }
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        updateCars();
        
        for (const car of cars) {
            drawCar(car);
        }
        
        requestAnimationFrame(animate);
    }
    
    // Initialize and start animation
    initCars();
    animate();
    
    // Re-initialize cars when theme changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'data-bs-theme') {
                initCars();
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-bs-theme']
    });
}); 