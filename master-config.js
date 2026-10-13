// ==========================================
// MASTER CV CONFIGURATION FILE
// ==========================================
window.CV_MASTER_CONFIG = {
    // 1. Security & Interaction Controls
    allowRightClick: false,      // false = Restricted (Default), true = Allowed
    allowLeftClick: false,       // true = Normal clicks, false = Blocks selection/clicks
    allowScreenshot: false,      // false = Blocks PrintScreen/shortcuts, true = Allowed
    
    // 2. Toolbar Icon Controls
    showDownloadIcon: true,     // true = Show PDF download icon, false = Hidden
    showThemeIcon: true,         // true = Show Theme toggle icon, false = Hidden
    
    // 3. Profile Image Setting (Filename or uploaded image path)
    profileImage: "me.jpeg",     // <--- NOTE: Added comma here!
        
    // 4. Favicon Setting
    favicon: "logo2.png"          // Favicon image file path
};

// ==========================================
// AUTOMATIC FAVICON INJECTOR
// ==========================================
(function() {
    if (window.CV_MASTER_CONFIG && window.CV_MASTER_CONFIG.favicon) {
        let link = document.querySelector("link[rel*='icon']") || document.createElement('link');
        link.type = 'image/png';
        link.rel = 'icon';
        link.href = window.CV_MASTER_CONFIG.favicon;
        if (!link.parentNode) {
            document.head.appendChild(link);
        }
    }
})();
