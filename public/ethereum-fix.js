// Prevent ethereum property redefinition error from browser extensions
(function() {
  'use strict';
  
  // Check if ethereum property already exists
  if (typeof window !== 'undefined') {
    const descriptor = Object.getOwnPropertyDescriptor(window, 'ethereum');
    
    // If it doesn't exist, define it with configurable: true
    if (!descriptor) {
      try {
        Object.defineProperty(window, 'ethereum', {
          configurable: true,
          enumerable: true,
          writable: true,
          value: undefined
        });
      } catch (e) {
        console.warn('Could not pre-define ethereum property:', e);
      }
    }
  }
})();
