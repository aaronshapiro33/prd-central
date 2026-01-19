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

Find the main App component (usually `App.tsx` or `App.jsx`) and add SDK initialization:

```javascript
// Add this useEffect to initialize Elera SDK
useEffect(() => {
  const apiKey = import.meta.env.VITE_PROVIDER_API_KEY;
  if (!apiKey) {
    console.warn('VITE_PROVIDER_API_KEY not set');
    return;
  }
  
  const elera = new EleraBooking(apiKey);
  elera.initialize().then(context => {
    window.ELERA_CONTEXT = context;
    window.elera = elera;
    console.log('Elera SDK initialized');
  }).catch(err => {
    console.error('Elera SDK init failed:', err);
  });
}, []);
```

**DO NOT** change any existing state, props, or component structure.

---

### 3. Update Booking Button Click Handlers

Find existing "Book Now", "Schedule", or "Book Appointment" buttons and update ONLY their onClick handler:

**Before:**
```jsx
<button onClick={someExistingHandler} className="existing-classes">
  Book Now
</button>
```

**After:**
```jsx
<button 
  onClick={() => {
    window.elera?.openBooking({
      onSuccess: (data) => console.log('Booked:', data),
      onClose: () => console.log('Closed')
    });
  }} 
  className="existing-classes"  // KEEP ALL EXISTING CLASSES
>
  Book Now
</button>
```

**DO NOT:**
- Change button text
- Change button styling/classes
- Change button position
- Add new buttons

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

- [ ] Add `<script src="https://app.elera.health/sdk.js"></script>` to index.html
- [ ] Add SDK initialization useEffect in main App component
- [ ] Update booking button onClick to use `window.elera.openBooking()`
- [ ] Connect blog posts to `window.ELERA_CONTEXT.blog_posts` (if blog exists)
- [ ] Ensure `VITE_PROVIDER_API_KEY` env var is used

**Total lines of code to change: ~20-30 lines maximum**

**Files to modify: 2-3 files maximum** (index.html, App.tsx, possibly a Blog component)

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
