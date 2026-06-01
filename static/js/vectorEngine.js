const stage = document.getElementById('stage');
const pod = document.getElementById('pod');
const teleX = document.getElementById('tele-x');
const teleY = document.getElementById('tele-y');

let isInteracting = false;
let currentX = -15; 
let currentY = -25; 
let previousMouseX = 0;
let previousMouseY = 0;
let targetX = currentX;
let targetY = currentY;

if(pod) {
    // --- DESKTOP MOUSE EVENTS ---
    window.addEventListener('mousedown', (e) => {
        if(e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') return;
        isInteracting = true;
        previousMouseX = e.clientX;
        previousMouseY = e.clientY;
    });

    window.addEventListener('mousemove', (e) => {
        if (!isInteracting) return;
        const deltaMouseX = e.clientX - previousMouseX;
        const deltaMouseY = e.clientY - previousMouseY;
        targetY += deltaMouseX * 0.5; 
        targetX -= deltaMouseY * 0.5; 
        previousMouseX = e.clientX;
        previousMouseY = e.clientY;
    });

    window.addEventListener('mouseup', () => { isInteracting = false; });

    // --- MOBILE PHONE TOUCH EVENTS ---
    window.addEventListener('touchstart', (e) => {
        if(e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') return;
        isInteracting = true;
        previousMouseX = e.touches[0].clientX;
        previousMouseY = e.touches[0].clientY;
    }, { passive: false });

    window.addEventListener('touchmove', (e) => {
        if (!isInteracting) return;
        // Blocks the phone from scrolling the webpage while spinning the 3D object
        e.preventDefault(); 
        
        const deltaMouseX = e.touches[0].clientX - previousMouseX;
        const deltaMouseY = e.touches[0].clientY - previousMouseY;
        
        targetY += deltaMouseX * 0.4; // Softened slightly for phone screens
        targetX -= deltaMouseY * 0.4; 
        
        previousMouseX = e.touches[0].clientX;
        previousMouseY = e.touches[0].clientY;
    }, { passive: false });

    window.addEventListener('touchend', () => { isInteracting = false; });

    // --- RENDER CLOCK ---
    function execute3DTransformationTick() {
        currentX += (targetX - currentX) * 0.1;
        currentY += (targetY - currentY) * 0.1;
        pod.style.transform = `rotateX(${currentX}deg) rotateY(${currentY}deg)`;
        
        if (teleX && teleY) {
            teleX.innerText = `${((currentX % 360 + 360) % 360).toFixed(1)}°`;
            teleY.innerText = `${((currentY % 360 + 360) % 360).toFixed(1)}°`;
        }
        requestAnimationFrame(execute3DTransformationTick);
    }
    execute3DTransformationTick();
}

function isolateInput() {
    isInteracting = false;
}