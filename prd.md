# Elera Provider Website Integration PRD

## ⚠️ CRITICAL: DO NOT MODIFY DESIGN

**THIS PRD IS FOR INTEGRATION ONLY. DO NOT CHANGE:**
- Colors, fonts, or styling
- Layout or component structure  
- Images or visual elements
- CSS or Tailwind classes
- Any existing UI/UX design decisions
- Page structure or sections
- Animations or transitions

**ONLY ADD/MODIFY:**
- Elera SDK initialization
- Booking button click handlers (keep existing button styling)
- Blog data fetching (keep existing blog UI)
- Analytics/tracking code
- Environment variable usage

---

## What To Do

### 1. Add Elera SDK Script (if not present)

Add this script tag to the `<head>` of `index.html`:

```html
<script src="https://app.elera.health/sdk.js"></script>
```

**DO NOT** change any other HTML structure.

---

### 2. Initialize SDK in Main App Component

Find the main App component (usually `App.tsx` or `App.jsx`) and add SDK initialization.

**IMPORTANT:** The API key might already be hardcoded in the site. Check for existing EleraBooking initialization first. If it exists, just make sure `window.elera` is being set.

```javascript
// Add this useEffect to initialize Elera SDK
useEffect(() => {
  // Check if already initialized
  if (window.elera) {
    console.log('[Elera] SDK already initialized');
    return;
  }

  // Try to get API key from env or use existing hardcoded key
  const apiKey = import.meta.env.VITE_PROVIDER_API_KEY || 'YOUR_EXISTING_API_KEY';
  
  console.log('[Elera] Starting SDK initialization...');
  
  // @ts-ignore - EleraBooking is loaded from external script
  if (typeof EleraBooking === 'undefined') {
    console.error('[Elera] EleraBooking not loaded. Make sure sdk.js is included.');
    return;
  }
  
  // @ts-ignore
  const elera = new EleraBooking(apiKey);
  
  elera.initialize().then(context => {
    // CRITICAL: Set these globals so buttons can access them
    window.ELERA_CONTEXT = context;
    window.elera = elera;
    
    console.log('[Elera] ✅ SDK initialized for:', context.therapist_name);
    console.log('[Elera] window.elera set:', typeof window.elera);
    console.log('[Elera] openBooking available:', typeof window.elera.openBooking);
  }).catch(err => {
    console.error('[Elera] SDK init failed:', err);
  });
}, []);
```

**DO NOT** change any existing state, props, or component structure.

---

### 3. Create Global Booking Handler Function (REQUIRED)

**Add this helper function near the top of your main App component or in a utils file:**

```javascript
// Global function to open booking modal - call this from any button
function openEleraBooking() {
  console.log('[Booking] Button clicked, checking for Elera SDK...');
  
  if (window.elera && typeof window.elera.openBooking === 'function') {
    console.log('[Booking] Opening Elera booking modal...');
    window.elera.openBooking({
      onSuccess: (data) => {
        console.log('[Booking] Success:', data);
      },
      onClose: () => {
        console.log('[Booking] Modal closed');
      }
    });
  } else {
    console.error('[Booking] Elera SDK not ready. window.elera:', window.elera);
    alert('Booking system is loading, please try again in a moment.');
  }
}

// Make it globally available
window.openEleraBooking = openEleraBooking;
```

### 4. Update ALL Booking/Schedule Button Click Handlers (REQUIRED)

**Search the entire codebase** for ANY buttons or links related to booking.

**Search for buttons containing text like:**
- "Book Now"
- "Book Appointment" 
- "Schedule"
- "Schedule Now"
- "Book a Consultation"
- "Get Started"
- "Book Online"
- "Make Appointment"
- Any variation of booking/scheduling

**For EACH booking button found, update the onClick handler to call the global function:**

**Before:**
```jsx
<button onClick={someExistingHandler} className="existing-classes">
  Book Now
</button>
```

**After:**
```jsx
<button 
  onClick={() => openEleraBooking()} 
  className="existing-classes"
>
  Book Now
</button>
```

**OR if it's an anchor tag:**

**Before:**
```jsx
<a href="/book" className="existing-classes">Schedule Now</a>
```

**After:**
```jsx
<a 
  href="#" 
  onClick={(e) => { e.preventDefault(); openEleraBooking(); }} 
  className="existing-classes"
>
  Schedule Now
</a>
```

**Also check for:**
- `<a>` tags that link to booking pages
- Buttons inside hero sections
- Buttons in navigation/header
- Buttons in footer
- Buttons in contact sections
- Buttons on service pages
- Any CTA buttons related to appointments

**KEEP:**
- All existing button text
- All existing CSS classes and styling
- All existing button positions
- The visual design exactly as-is

**ONLY CHANGE:**
- The onClick/href handler to call `openEleraBooking()`

---

### 4. Connect Blog Data (if blog section exists)

If the site has a blog section, update it to fetch from Elera SDK instead of hardcoded data:

```javascript
// Replace hardcoded blog posts with SDK data
const [posts, setPosts] = useState([]);

useEffect(() => {
  // Wait for SDK context
  const checkContext = setInterval(() => {
    if (window.ELERA_CONTEXT?.blog_posts) {
      setPosts(window.ELERA_CONTEXT.blog_posts);
      clearInterval(checkContext);
    }
  }, 100);
  
  // Cleanup after 5 seconds
  setTimeout(() => clearInterval(checkContext), 5000);
}, []);
```

**DO NOT:**
- Change blog card design
- Change blog layout
- Change typography or colors
- Modify any CSS

---

### 5. Add Environment Variable Support

Ensure the site reads the API key from environment variables. Add to `.env` (if not exists):

```env
VITE_PROVIDER_API_KEY=
```

---

## What NOT To Do - Examples

❌ **DO NOT** change colors:
```jsx
// WRONG - Don't change this
<div className="bg-blue-500">  →  <div className="bg-primary">
```

❌ **DO NOT** change layout:
```jsx
// WRONG - Don't restructure components
<Hero />     →    <NewHeroSection />
<About />         <RedesignedAbout />
```

❌ **DO NOT** add new sections:
```jsx
// WRONG - Don't add new UI elements
<TestimonialsSection />  // Don't add if it doesn't exist
```

❌ **DO NOT** change fonts or typography:
```jsx
// WRONG - Don't modify text styling
<h1 className="text-4xl font-serif">  →  <h1 className="text-5xl font-sans">
```

❌ **DO NOT** modify images:
```jsx
// WRONG - Don't change image sources or styling
<img src="/hero.jpg" className="rounded-lg" />
```

---

## Summary Checklist

Only make these changes:

- [ ] Add `<script src="https://app.elera.health/sdk.js"></script>` to index.html (if not already present)
- [ ] Add SDK initialization useEffect that sets `window.elera` globally
- [ ] Add global `openEleraBooking()` helper function with console logging
- [ ] **FIND ALL booking/schedule buttons and update onClick to call `openEleraBooking()`**
- [ ] Connect blog posts to `window.ELERA_CONTEXT.blog_posts` (if blog exists)

**Booking buttons to find and update:**
- Hero section CTAs
- Navigation "Book" buttons
- Footer booking links
- Contact page buttons
- Service page CTAs
- Any "Schedule", "Book Now", "Book Appointment" buttons

**Total files to modify:** Likely 3-6 files (wherever booking buttons exist)

**Debug:** After deployment, clicking any booking button should log:
```
[Booking] Button clicked, checking for Elera SDK...
[Booking] Opening Elera booking modal...
```
If you see `[Booking] Elera SDK not ready`, the SDK initialization failed.

---

## DO NOT TOUCH

- Any `.css` files
- Any Tailwind config
- Any color values
- Any font declarations  
- Any layout components
- Any image assets
- Any animation code
- Any responsive breakpoints
- Component structure/hierarchy
- Page routing
- Any styling whatsoever

**If in doubt, DON'T CHANGE IT.**
