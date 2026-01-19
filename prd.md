# Elera Provider Website Integration PRD

## ⚠️ CRITICAL RULES

**DO NOT:**
- Change ANY colors, fonts, or styling
- Change ANY layout or component structure  
- Change ANY CSS or Tailwind classes
- Create ANY new functions or helpers
- Add ANY tracking code
- Modify SDK initialization if it already exists

**ONLY:**
- Update booking button onClick handlers

---

## ONLY TASK: Update Booking Button Click Handlers

**Search the codebase for buttons with text like:**
- "Schedule"
- "Book Now"  
- "Book Appointment"
- "Get Started"

**For EACH button found, replace the onClick with this EXACT code:**

### For `<button>` elements:

```jsx
<button 
  onClick={() => {
    if (window.elera && window.elera.openBooking) {
      window.elera.openBooking();
    }
  }} 
  className="...keep existing classes exactly..."
>
  Schedule Now
</button>
```

### For `<a>` elements:

```jsx
<a 
  href="#"
  onClick={(e) => {
    e.preventDefault();
    if (window.elera && window.elera.openBooking) {
      window.elera.openBooking();
    }
  }}
  className="...keep existing classes exactly..."
>
  Schedule Now
</a>
```

---

## DO NOT

❌ Do NOT create functions like `openEleraBooking()` or `handleSchedule()`
❌ Do NOT add `trackScheduleIntent()` or any tracking
❌ Do NOT modify SDK initialization code
❌ Do NOT add useEffect hooks
❌ Do NOT change button text or classes
❌ Do NOT change colors or styling
❌ Do NOT restructure components

---

## Example

**BEFORE:**
```jsx
<button 
  onClick={() => someExistingFunction()} 
  className="bg-primary text-white px-6 py-3 rounded-lg"
>
  Schedule Now
</button>
```

**AFTER:**
```jsx
<button 
  onClick={() => {
    if (window.elera && window.elera.openBooking) {
      window.elera.openBooking();
    }
  }} 
  className="bg-primary text-white px-6 py-3 rounded-lg"
>
  Schedule Now
</button>
```

**NOTICE:** The className is EXACTLY the same. Only onClick changed.

---

## That's It

The ONLY change needed is replacing onClick handlers on booking buttons with:
```javascript
() => {
  if (window.elera && window.elera.openBooking) {
    window.elera.openBooking();
  }
}
```

Nothing else. Do not change anything else. Do not add anything else.
