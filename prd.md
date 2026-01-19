# Elera Provider Website PRD

## Overview

This PRD defines the requirements for provider websites built on the Elera platform. All sites must integrate with the centralized Elera SDK for booking, blog content, and analytics tracking.

---

## Required SDK Integration

### Initialize the Elera SDK

Every site MUST include the Elera SDK and initialize it with the provider's API key:

```html
<!-- In the <head> section -->
<script src="https://app.elera.health/sdk.js"></script>

<script>
  // Initialize with the provider's API key (provided dynamically)
  const elera = new EleraBooking('{{PROVIDER_API_KEY}}');
  
  elera.initialize().then(context => {
    // Context contains:
    // - therapist_name: Provider's name
    // - specialty: Provider's specialty
    // - bio: Provider's bio
    // - profile_picture_url: Avatar URL
    // - blog_posts: Array of blog posts for this provider
    // - gtm_container_id: Google Tag Manager ID (if configured)
    // - meta_pixel_id: Meta Pixel ID (if configured)
    // - consultation_rate: Price for consultations
    
    console.log('Elera SDK initialized for:', context.therapist_name);
    
    // SDK automatically initializes tracking (Google, Meta) if IDs are configured
    // SDK automatically tracks page views
  });
</script>
```

---

## Booking Integration (REQUIRED)

### Book Now Button

Every page MUST have a prominent "Book Now" button that opens the Elera booking modal:

```jsx
// React example
function BookNowButton() {
  const handleBook = () => {
    // Opens the centralized Elera booking modal
    elera.openBooking({
      // Optional: Pass theme colors to match site
      primaryColor: '#your-primary-color',
      secondaryColor: '#your-secondary-color',
      accentColor: '#your-accent-color',
      fontFamily: 'Your Font Family'
    });
  };

  return (
    <button onClick={handleBook} className="book-now-btn">
      Book Your Appointment
    </button>
  );
}
```

### Booking Modal Features (Handled by Elera)
- Date selection with real-time availability
- Time slot selection
- Patient information form
- Automatic conversion tracking (Google Ads, Meta)
- Confirmation screen
- Mobile responsive

### Event Callbacks

Listen for booking events:

```javascript
elera.openBooking({
  onSuccess: (data) => {
    // Booking completed successfully
    console.log('Appointment booked:', data.appointment_id);
    // data includes: appointment_id, date, time, conversionSent
    
    // Optional: Show custom success message or redirect
  },
  onClose: () => {
    // Modal was closed (with or without booking)
  }
});
```

---

## Blog Integration (REQUIRED)

### Fetching Blog Posts

Use the SDK to get blog posts assigned to this provider:

```javascript
// After initialization
const posts = elera.getBlogPosts();

// Returns array of:
// {
//   id, slug, title, excerpt, content,
//   featured_image, author, reading_time,
//   published, created_at, category
// }
```

### Blog List Page

```jsx
function BlogList() {
  const [posts, setPosts] = useState([]);
  
  useEffect(() => {
    // Wait for SDK initialization
    window.addEventListener('elera:context', (e) => {
      setPosts(e.detail.blog_posts || []);
    });
    
    // Or if already initialized
    if (window.ELERA_CONTEXT) {
      setPosts(window.ELERA_CONTEXT.blog_posts || []);
    }
  }, []);
  
  return (
    <div className="blog-grid">
      {posts.map(post => (
        <article key={post.id}>
          <img src={post.featured_image} alt={post.title} />
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
          <a href={`/blog/${post.slug}`}>Read More</a>
        </article>
      ))}
    </div>
  );
}
```

### Single Blog Post Page

```javascript
// Fetch full blog post content by slug
const slug = 'your-blog-post-slug';

elera.getBlogPost(slug).then(post => {
  // post.content contains the full HTML content
  document.getElementById('blog-content').innerHTML = post.content;
});
```

### Blog Page Requirements
- Grid layout for blog listing (3 columns desktop, 1 mobile)
- Featured image support
- Reading time display
- Author attribution
- Category tags
- Related posts section
- Share buttons (optional)

---

## Analytics & Tracking (REQUIRED)

### Automatic Tracking (Handled by SDK)

The Elera SDK automatically handles:

1. **Google Tag Manager** - If `gtm_container_id` is configured
2. **Meta Pixel** - If `meta_pixel_id` is configured
3. **Page Views** - Tracked on initialization
4. **Booking Conversions** - Tracked when appointments are booked

### UTM Parameter Handling

The SDK automatically captures and forwards UTM parameters:

```javascript
// These are automatically captured from the URL and sent with bookings:
// - utm_source
// - utm_medium  
// - utm_campaign
// - utm_term
// - utm_content
// - gclid (Google Click ID)
// - fbclid (Facebook Click ID)
```

### Custom Event Tracking

Track custom events for specific user actions:

```javascript
// Track schedule button click (before modal opens)
elera._sendEleraEvent('schedule_click', {
  page: window.location.pathname,
  button_location: 'hero'
});

// Track contact form submission
elera._sendEleraEvent('contact_form_submit', {
  page: window.location.pathname
});
```

### Google Ads Conversion Tracking

For sites with Google Ads, ensure the conversion is tracked:

```javascript
// The booking modal handles this automatically, but for manual tracking:
if (window.gtag) {
  gtag('event', 'conversion', {
    'send_to': 'AW-17881598003/YOUR_CONVERSION_LABEL',
    'value': 150,
    'currency': 'USD'
  });
}
```

---

## Page Structure Requirements

### Home Page
1. **Hero Section**
   - Provider name and specialty from `context.therapist_name` and `context.specialty`
   - Profile image from `context.profile_picture_url`
   - Compelling tagline
   - Primary CTA: "Book Your Appointment" button

2. **About/Bio Section**
   - Provider bio from `context.bio`
   - Credentials and experience
   - Professional photo

3. **Services Section**
   - List of services offered
   - Brief descriptions
   - Secondary CTAs to book

4. **Testimonials Section**
   - Patient reviews (if available)
   - Star ratings

5. **Blog Preview Section**
   - Latest 3 blog posts from `elera.getBlogPosts()`
   - "View All" link to blog page

6. **Contact Section**
   - Contact information
   - Location/service area
   - Contact form (optional)
   - Final CTA to book

### About Page
- Extended bio
- Education and certifications
- Philosophy of care
- Professional photos

### Services Page
- Detailed service descriptions
- Who it's for
- What to expect
- Book CTA for each service

### Blog Page
- Blog post grid
- Category filtering (optional)
- Search (optional)
- Pagination

### Contact Page
- Contact form
- Phone and email
- Service area/location
- Business hours

---

## Design Requirements

### Mobile-First Responsive Design
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

### Performance
- Lighthouse score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Core Web Vitals: Pass

### Accessibility
- WCAG 2.1 AA compliant
- Keyboard navigation
- Screen reader compatible
- Sufficient color contrast

### SEO Requirements
- Semantic HTML (h1, h2, article, nav, etc.)
- Meta title and description on all pages
- Open Graph tags
- Structured data (LocalBusiness, Person schema)
- XML sitemap
- robots.txt

---

## Technical Stack

- **Framework**: React + Vite
- **Styling**: TailwindCSS
- **Language**: TypeScript
- **Animations**: Framer Motion (optional)
- **Fonts**: Google Fonts

---

## Required Environment Variables

Sites should support these environment variables for configuration:

```env
VITE_PROVIDER_API_KEY=elera_xxx  # Provider's Elera API key
VITE_SITE_URL=https://yoursite.com
```

---

## Example Full Implementation

```jsx
// App.jsx
import { useEffect, useState } from 'react';

function App() {
  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize Elera SDK
    const apiKey = import.meta.env.VITE_PROVIDER_API_KEY;
    const elera = new EleraBooking(apiKey);
    
    elera.initialize()
      .then(ctx => {
        setContext(ctx);
        setLoading(false);
        window.elera = elera; // Make available globally
      })
      .catch(err => {
        console.error('Failed to initialize Elera:', err);
        setLoading(false);
      });
  }, []);

  const handleBookNow = () => {
    window.elera?.openBooking({
      onSuccess: (data) => {
        // Optional: Show thank you page
        window.location.href = '/thank-you';
      }
    });
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <Hero 
        name={context?.therapist_name}
        specialty={context?.specialty}
        onBook={handleBookNow}
      />
      <Services onBook={handleBookNow} />
      <About bio={context?.bio} image={context?.profile_picture_url} />
      <BlogPreview posts={context?.blog_posts?.slice(0, 3)} />
      <Contact onBook={handleBookNow} />
    </div>
  );
}
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-01-18 | 2.0.0 | Complete rewrite with SDK integration, blog, and tracking |

---

**IMPORTANT**: All sites MUST use the Elera SDK for booking. Do NOT implement custom booking flows.
