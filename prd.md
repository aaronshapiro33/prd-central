# Elera Provider Website Integration PRD

## ⚠️ CRITICAL: PRESERVE ALL EXISTING DESIGN

**This PRD is for INTEGRATION ONLY. You MUST preserve:**
- All colors, fonts, and styling
- All layouts and component structures
- All CSS/Tailwind classes
- All images and visual elements
- All existing UI/UX decisions

**You will ADD/MODIFY only:**
- SDK script loading
- SDK initialization code
- Booking button click handlers (keep all button styling)
- Blog data fetching (keep all blog UI styling)

---

## Required Changes

### 1. Add SDK Script to index.html

In the `<head>` section of `index.html`, add:

```html
<script src="https://app.elera.health/sdk.js"></script>
```

Do NOT change any other HTML structure.

---

### 2. Initialize SDK in App Entry Point

In the main app entry (e.g., `App.tsx`, `main.tsx`, or root component), add SDK initialization.

**IMPORTANT:** Use the provider's API key: `{{PROVIDER_API_KEY}}`

```jsx
// Add these imports at the top
import { useEffect, useState } from 'react';

// Inside your main App component, add this useEffect:
useEffect(() => {
  // Check if SDK is already initialized
  if (window.elera) {
    console.log('[Elera] SDK already initialized');
    return;
  }

  // Initialize Elera SDK with provider API key
  const apiKey = '{{PROVIDER_API_KEY}}';
  
  console.log('[Elera] Starting SDK initialization...');
  
  // @ts-ignore - EleraBooking is loaded from external script
  if (typeof EleraBooking === 'undefined') {
    console.error('[Elera] EleraBooking not loaded. Make sure sdk.js is in index.html');
    return;
  }
  
  // @ts-ignore
  const elera = new EleraBooking(apiKey);
  
  elera.initialize()
    .then((context) => {
      // Set global references for buttons and components to use
      window.elera = elera;
      window.ELERA_CONTEXT = context;
      
      console.log('[Elera] ✅ SDK initialized for:', context.therapist_name);
      console.log('[Elera] Blog posts available:', (context.blog_posts || []).length);
      
      // Dispatch event for components listening for SDK ready
      window.dispatchEvent(new CustomEvent('elera:ready', { detail: context }));
    })
    .catch((err) => {
      console.error('[Elera] SDK initialization failed:', err);
    });
}, []);
```

**Add TypeScript declarations (if using TypeScript):**

```typescript
// Add to a global.d.ts file or at the top of App.tsx:
declare global {
  interface Window {
    elera?: any;
    ELERA_CONTEXT?: any;
    EleraBooking?: any;
  }
}
```

---

### 3. Update Booking Button Click Handlers

Find ALL buttons related to booking/scheduling and update their onClick handlers.

**Search for buttons with text like:**
- "Book Now"
- "Book Appointment"
- "Schedule"
- "Schedule Now"
- "Get Started"
- "Book a Consultation"
- "Book Online"

**For each button, update the onClick to call the SDK:**

**BEFORE (example):**
```jsx
<button 
  onClick={() => navigate('/contact')} 
  className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary/90"
>
  Schedule Now
</button>
```

**AFTER:**
```jsx
<button 
  onClick={() => {
    console.log('[Booking] Opening Elera booking modal...');
    if (window.elera && window.elera.openBooking) {
      window.elera.openBooking({
        // DO NOT pass primaryColor if the site uses light colors!
        // The default blue (#5a7ffd) works well with white text
        onSuccess: (data) => {
          console.log('[Booking] Success:', data);
        },
        onClose: () => {
          console.log('[Booking] Modal closed');
        }
      });
    } else {
      console.error('[Booking] Elera SDK not ready');
      alert('Booking system is loading, please try again.');
    }
  }} 
  className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary/90"
>
  Schedule Now
</button>
```

**Theming Options for openBooking():**
The booking modal can be themed to match the site's branding:
```javascript
window.elera.openBooking({
  primaryColor: '#5a7ffd',      // Main button/accent color (hex) - MUST be dark!
  secondaryColor: '#ebf0fa',    // Background color (hex)
  accentColor: '#1eb464',       // Success states (hex)
  fontFamily: 'Poppins',        // Google Font name
  onSuccess: (data) => { ... },
  onClose: () => { ... }
});
```

**⚠️ CRITICAL: primaryColor MUST be a DARK color!**
The booking modal uses white text on the primaryColor background. If you pass a light color (white, cream, beige, light gray, etc.), the text will be INVISIBLE.

**DO NOT pass these colors as primaryColor:**
- White (#fff, #ffffff)
- Cream/beige (#f5f5dc, #faf0e6, etc.)
- Light grays (#eee, #ddd, #ccc, etc.)
- Any color that would have poor contrast with white text

**If the site uses a light primary color**, do NOT pass primaryColor at all - let the modal use the default blue (#5a7ffd):
```javascript
// Site has light/white primary color - don't pass it
window.elera.openBooking({
  // NO primaryColor - use default
  onSuccess: (data) => { ... },
  onClose: () => { ... }
});
```

**How to find a suitable dark color:**
- Look for dark button colors (not background colors)
- Check accent/brand colors that are used on light backgrounds
- If the site only has light colors, skip passing primaryColor entirely

**CRITICAL:** Keep ALL existing class names and styling exactly the same!

**For anchor tags (`<a>`):**

```jsx
<a 
  href="#"
  onClick={(e) => {
    e.preventDefault();
    if (window.elera && window.elera.openBooking) {
      window.elera.openBooking();
    }
  }}
  className="...existing classes..."
>
  Book Appointment
</a>
```

**Common locations to check:**
- Hero section CTA buttons
- Header/Navigation "Book" buttons
- Footer booking links
- Contact page buttons
- Service page CTAs
- Floating/sticky booking buttons

---

### 4. Connect Blog Section to SDK (if blog exists)

If the site has a blog section, update it to fetch posts from the SDK context.

**Find the blog component and update the data source:**

```jsx
// In your Blog component:
const [posts, setPosts] = useState([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  // Function to load posts from SDK context
  const loadPosts = () => {
    if (window.ELERA_CONTEXT?.blog_posts) {
      setPosts(window.ELERA_CONTEXT.blog_posts);
      setLoading(false);
      return true;
    }
    return false;
  };

  // Try immediately
  if (loadPosts()) return;

  // Listen for SDK ready event
  const handleReady = () => loadPosts();
  window.addEventListener('elera:ready', handleReady);

  // Fallback timeout
  const timeout = setTimeout(() => {
    setLoading(false);
    console.log('[Blog] Timeout waiting for SDK context');
  }, 5000);

  return () => {
    window.removeEventListener('elera:ready', handleReady);
    clearTimeout(timeout);
  };
}, []);
```

**Keep ALL existing blog card styling.** Only change where the data comes from.

Blog post object structure from SDK:
```typescript
interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  featured_image?: string;
  published_at: string;
}
```

---

## DO NOT Change

- Any CSS files
- Any Tailwind configuration
- Any color values (hex, rgb, oklch, etc.)
- Any font declarations
- Any layout components
- Any image assets
- Any animation code
- Any responsive breakpoints
- Component hierarchy/structure
- Page routing
- Existing prop interfaces
- Form validation logic
- Any styling whatsoever

---

## Summary Checklist

Only make these changes:

- [ ] Add `<script src="https://app.elera.health/sdk.js"></script>` to index.html `<head>`
- [ ] Add SDK initialization useEffect with API key `{{PROVIDER_API_KEY}}`
- [ ] Add TypeScript declarations for window.elera and window.ELERA_CONTEXT
- [ ] Update ALL booking/schedule button onClick handlers to call `window.elera.openBooking()`
- [ ] Connect blog components to use `window.ELERA_CONTEXT.blog_posts` (if blog exists)

**Expected console output after deployment:**
```
[EleraBooking] SDK v2.0.0 loaded
[Elera] Starting SDK initialization...
[Elera] ✅ SDK initialized for: [Provider Name]
[Elera] Blog posts available: [X]
```

**When clicking a booking button:**
```
[Booking] Opening Elera booking modal...
```

---

## Example: Complete App.tsx Integration

```tsx
import { useEffect } from 'react';
// ... other imports ...

// TypeScript declarations
declare global {
  interface Window {
    elera?: any;
    ELERA_CONTEXT?: any;
    EleraBooking?: any;
  }
}

function App() {
  // Elera SDK initialization
  useEffect(() => {
    if (window.elera) return;

    const apiKey = '{{PROVIDER_API_KEY}}';
    
    // @ts-ignore
    if (typeof EleraBooking === 'undefined') {
      console.error('[Elera] SDK not loaded');
      return;
    }
    
    // @ts-ignore
    const elera = new EleraBooking(apiKey);
    
    elera.initialize()
      .then((context) => {
        window.elera = elera;
        window.ELERA_CONTEXT = context;
        console.log('[Elera] ✅ SDK initialized for:', context.therapist_name);
        window.dispatchEvent(new CustomEvent('elera:ready', { detail: context }));
      })
      .catch((err) => {
        console.error('[Elera] Init failed:', err);
      });
  }, []);

  // ... rest of component unchanged ...
}
```

**Remember: Your ONLY job is integration. Do not redesign anything!**
