# Invoice Creation UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add invoice creation form to admin panel with dynamic line items, client/project selection, and live total calculation

**Architecture:** Modal-based form matching existing admin UI patterns (clients.html, projects.html). JavaScript handles dynamic line item rows, real-time calculation, and form submission to POST /api/v1/admin/invoices endpoint.

**Tech Stack:** Jinja2 templates, Vanilla JavaScript, TailwindCSS, Lucide icons, Fetch API

---

## Context

**Backend Status:** ✅ Complete
- InvoiceItem model exists
- Invoice service with auto-numbering and calculation exists
- POST /api/v1/admin/invoices endpoint ready
- Schemas support line items

**Frontend Status:** Needs Implementation
- Current invoices.html only displays/views invoices
- No creation modal or form exists
- Need to match existing pattern from clients.html

**Design System:**
- Port aesthetic (rounded-2xl, charcoal, light-grey, muted-blue)
- Lucide icons
- Modal forms with fade-in animations
- Client-side data fetching with JWT auth

---

## Task 1: Add "Create Invoice" Button

**Files:**
- Modify: `backend/app/templates/admin/invoices.html:6-9`

**Step 1: Add button to header**

In the header section, update to match clients.html pattern:

```html
<div class="fade-in mb-8 flex justify-between items-center">
    <div>
        <h1 class="text-4xl font-bold text-charcoal">Invoices</h1>
        <p class="text-gray-600 mt-2">Manage client invoices and payments</p>
    </div>
    <button onclick="openInvoiceModal()" class="flex items-center gap-2 bg-charcoal text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition">
        <i data-lucide="plus" class="w-5 h-5"></i>
        <span>Create Invoice</span>
    </button>
</div>
```

**Step 2: Verify styling**

Open http://127.0.0.1:8000/admin/invoices in browser
Expected: Button appears in top-right, matches projects/clients pages

---

## Task 2: Create Invoice Creation Modal Structure

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (after line 111, before {% endblock %})

**Step 1: Add modal HTML**

Insert after the existing invoice detail modal (after line 111):

```html
<!-- Invoice Creation Modal -->
<div id="create-invoice-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-6">
    <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-8">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-charcoal">Create Invoice</h2>
                <button onclick="closeCreateInvoiceModal()" class="text-gray-500 hover:text-charcoal">
                    <i data-lucide="x" class="w-6 h-6"></i>
                </button>
            </div>

            <form id="invoice-form" class="space-y-6">
                <!-- Client Selection -->
                <div>
                    <label class="block text-sm font-medium text-charcoal mb-2">Client *</label>
                    <select id="client-select" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
                        <option value="">Select a client</option>
                    </select>
                </div>

                <!-- Project Selection (Optional) -->
                <div>
                    <label class="block text-sm font-medium text-charcoal mb-2">Project (Optional)</label>
                    <select id="project-select" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
                        <option value="">No project</option>
                    </select>
                </div>

                <!-- Due Date -->
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Due Date</label>
                        <input type="date" id="due-date" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Tax Rate (%)</label>
                        <input type="number" id="tax-rate" value="0" min="0" max="100" step="0.01" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
                    </div>
                </div>

                <!-- Line Items -->
                <div>
                    <div class="flex justify-between items-center mb-3">
                        <label class="block text-sm font-medium text-charcoal">Line Items *</label>
                        <button type="button" onclick="addLineItem()" class="flex items-center gap-2 text-muted-blue hover:text-blue-700 font-medium">
                            <i data-lucide="plus-circle" class="w-4 h-4"></i>
                            <span>Add Item</span>
                        </button>
                    </div>
                    <div id="line-items-container" class="space-y-3">
                        <!-- Line items will be added here -->
                    </div>
                </div>

                <!-- Totals Display -->
                <div class="border-t pt-6 space-y-2">
                    <div class="flex justify-between text-gray-700">
                        <span>Subtotal:</span>
                        <span id="subtotal-display" class="font-semibold">$0.00</span>
                    </div>
                    <div class="flex justify-between text-gray-700">
                        <span>Tax:</span>
                        <span id="tax-display" class="font-semibold">$0.00</span>
                    </div>
                    <div class="flex justify-between text-xl font-bold text-charcoal border-t pt-2">
                        <span>Total:</span>
                        <span id="total-display">$0.00</span>
                    </div>
                </div>

                <!-- Notes and Terms -->
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Notes</label>
                        <textarea id="notes" rows="3" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue resize-none"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Terms</label>
                        <textarea id="terms" rows="3" placeholder="Payment terms..." class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue resize-none"></textarea>
                    </div>
                </div>

                <div id="form-error" class="hidden p-4 bg-red-50 text-red-800 border border-red-200 rounded-xl text-sm"></div>

                <div class="flex gap-4">
                    <button type="submit" class="flex-1 bg-charcoal text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition">
                        Create Invoice
                    </button>
                    <button type="button" onclick="closeCreateInvoiceModal()" class="px-6 py-3 border-2 border-gray-200 rounded-xl font-medium hover:border-muted-blue transition">
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
```

**Step 2: Verify modal structure**

Refresh page and click "Create Invoice" button
Expected: Error in console ("openInvoiceModal is not defined" - this is expected, we'll add JS next)

---

## Task 3: Load Clients and Projects Data

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (in extra_scripts block)

**Step 1: Add data loading functions**

Add after `let allInvoices = [];`:

```javascript
let allClients = [];
let allProjects = [];

async function loadClientsAndProjects() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
        // Load clients
        const clientsResponse = await fetch('/api/v1/admin/clients', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (clientsResponse.ok) {
            allClients = await clientsResponse.json();
        }

        // Load projects
        const projectsResponse = await fetch('/api/v1/admin/projects', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (projectsResponse.ok) {
            allProjects = await projectsResponse.json();
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}
```

**Step 2: Call on page load**

Update the page load section at the bottom:

```javascript
// Load all data on page load
loadInvoices();
loadClientsAndProjects();
```

**Step 3: Verify data loading**

Open browser console, refresh page
Expected: Network requests to /api/v1/admin/clients and /api/v1/admin/projects with 200 status

---

## Task 4: Modal Open/Close Functions

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (in extra_scripts block)

**Step 1: Add modal control functions**

Add before the page load section:

```javascript
function openInvoiceModal() {
    // Populate client dropdown
    const clientSelect = document.getElementById('client-select');
    clientSelect.innerHTML = '<option value="">Select a client</option>';
    allClients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = client.company_name || client.contact_name;
        clientSelect.appendChild(option);
    });

    // Populate project dropdown
    const projectSelect = document.getElementById('project-select');
    projectSelect.innerHTML = '<option value="">No project</option>';
    allProjects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.id;
        option.textContent = project.title;
        projectSelect.appendChild(option);
    });

    // Add initial line item
    document.getElementById('line-items-container').innerHTML = '';
    addLineItem();

    // Reset form
    document.getElementById('invoice-form').reset();
    document.getElementById('form-error').classList.add('hidden');
    updateTotals();

    // Show modal
    document.getElementById('create-invoice-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeCreateInvoiceModal() {
    document.getElementById('create-invoice-modal').classList.add('hidden');
}
```

**Step 2: Test modal opening**

Click "Create Invoice" button
Expected: Modal opens with client dropdown populated, one empty line item

---

## Task 5: Dynamic Line Items

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (in extra_scripts block)

**Step 1: Add line item management functions**

Add before modal control functions:

```javascript
let lineItemCount = 0;

function addLineItem() {
    lineItemCount++;
    const container = document.getElementById('line-items-container');
    const itemDiv = document.createElement('div');
    itemDiv.className = 'flex gap-3 items-start';
    itemDiv.id = `line-item-${lineItemCount}`;
    itemDiv.innerHTML = `
        <div class="flex-1">
            <input type="text"
                   data-item-id="${lineItemCount}"
                   data-field="description"
                   placeholder="Description"
                   required
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
        </div>
        <div class="w-24">
            <input type="number"
                   data-item-id="${lineItemCount}"
                   data-field="quantity"
                   placeholder="Qty"
                   min="0.01"
                   step="0.01"
                   value="1"
                   required
                   oninput="updateTotals()"
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
        </div>
        <div class="w-32">
            <input type="number"
                   data-item-id="${lineItemCount}"
                   data-field="unit_price"
                   placeholder="Price"
                   min="0"
                   step="0.01"
                   value="0"
                   required
                   oninput="updateTotals()"
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
        </div>
        <button type="button"
                onclick="removeLineItem(${lineItemCount})"
                class="p-3 text-red-600 hover:bg-red-50 rounded-xl transition">
            <i data-lucide="trash-2" class="w-5 h-5"></i>
        </button>
    `;
    container.appendChild(itemDiv);
    lucide.createIcons();
}

function removeLineItem(itemId) {
    const item = document.getElementById(`line-item-${itemId}`);
    if (item) {
        item.remove();
        updateTotals();
    }

    // Ensure at least one line item
    const container = document.getElementById('line-items-container');
    if (container.children.length === 0) {
        addLineItem();
    }
}
```

**Step 2: Test add/remove**

Click "Add Item" button multiple times
Expected: New line item rows appear

Click trash icon
Expected: Row removed, at least one row always present

---

## Task 6: Live Total Calculation

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (in extra_scripts block)

**Step 1: Add calculation function**

Add after line item functions:

```javascript
function updateTotals() {
    const container = document.getElementById('line-items-container');
    const items = container.querySelectorAll('[data-field="quantity"]');

    let subtotal = 0;
    items.forEach(qtyInput => {
        const itemId = qtyInput.dataset.itemId;
        const priceInput = container.querySelector(`[data-item-id="${itemId}"][data-field="unit_price"]`);

        const quantity = parseFloat(qtyInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        subtotal += quantity * price;
    });

    const taxRate = parseFloat(document.getElementById('tax-rate').value) || 0;
    const taxAmount = (subtotal * taxRate) / 100;
    const total = subtotal + taxAmount;

    document.getElementById('subtotal-display').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('tax-display').textContent = `$${taxAmount.toFixed(2)}`;
    document.getElementById('total-display').textContent = `$${total.toFixed(2)}`;
}
```

**Step 2: Add tax rate listener**

In openInvoiceModal function, after resetting form:

```javascript
// Add tax rate listener
document.getElementById('tax-rate').addEventListener('input', updateTotals);
```

**Step 3: Test calculation**

Enter quantities and prices in line items
Expected: Subtotal, tax, and total update in real-time

Change tax rate
Expected: Tax amount and total recalculate

---

## Task 7: Form Submission

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (in extra_scripts block)

**Step 1: Add form submit handler**

Add after updateTotals function:

```javascript
document.getElementById('invoice-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const errorDiv = document.getElementById('form-error');
    errorDiv.classList.add('hidden');

    // Gather line items
    const container = document.getElementById('line-items-container');
    const itemElements = container.querySelectorAll('[data-field="description"]');
    const items = [];

    for (const descInput of itemElements) {
        const itemId = descInput.dataset.itemId;
        const qtyInput = container.querySelector(`[data-item-id="${itemId}"][data-field="quantity"]`);
        const priceInput = container.querySelector(`[data-item-id="${itemId}"][data-field="unit_price"]`);

        const description = descInput.value.trim();
        const quantity = parseFloat(qtyInput.value);
        const unit_price = parseFloat(priceInput.value);

        if (description && quantity > 0) {
            items.push({ description, quantity, unit_price });
        }
    }

    if (items.length === 0) {
        errorDiv.textContent = 'Please add at least one line item';
        errorDiv.classList.remove('hidden');
        return;
    }

    // Build invoice data
    const invoiceData = {
        client_id: parseInt(document.getElementById('client-select').value),
        project_id: document.getElementById('project-select').value ?
                    parseInt(document.getElementById('project-select').value) : null,
        due_date: document.getElementById('due-date').value || null,
        tax_rate: parseFloat(document.getElementById('tax-rate').value) || 0,
        notes: document.getElementById('notes').value || null,
        terms: document.getElementById('terms').value || null,
        items: items
    };

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch('/api/v1/admin/invoices', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(invoiceData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create invoice');
        }

        closeCreateInvoiceModal();
        await loadInvoices();

        // Show success message (optional)
        alert('Invoice created successfully!');
    } catch (error) {
        console.error('Error creating invoice:', error);
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});
```

**Step 2: Test full workflow**

1. Click "Create Invoice"
2. Select a client
3. Add line items with descriptions, quantities, prices
4. Set tax rate and due date
5. Click "Create Invoice"

Expected:
- POST to /api/v1/admin/invoices with 201 status
- Modal closes
- Invoice list refreshes
- New invoice appears in table

---

## Task 8: Display Line Items in Detail Modal

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (viewInvoice function)

**Step 1: Add items display**

In the viewInvoice function, after the total section (around line 287), add:

```javascript
<!-- Add before the closing div of invoice-details -->
${invoice.items && invoice.items.length > 0 ? `
<div class="border-t pt-6">
    <label class="block text-sm font-medium text-gray-600 mb-3">Line Items</label>
    <div class="space-y-2">
        ${invoice.items.map(item => `
            <div class="flex justify-between text-gray-700 py-2 border-b border-gray-100">
                <div class="flex-1">
                    <span class="font-medium">${item.description}</span>
                    <span class="text-sm text-gray-500 ml-2">(${item.quantity} × $${parseFloat(item.unit_price).toFixed(2)})</span>
                </div>
                <span class="font-semibold">$${parseFloat(item.total).toFixed(2)}</span>
            </div>
        `).join('')}
    </div>
</div>
` : ''}
```

**Step 2: Test detail view**

Click on an invoice (after creating one)
Expected: Line items section shows all items with quantities, prices, and totals

---

## Task 9: Enhance Invoice Display with Client Name

**Files:**
- Modify: `backend/app/templates/admin/invoices.html` (displayInvoices function)

**Step 1: Update client display logic**

Around line 191, update the client cell:

```javascript
<td class="px-6 py-4 text-gray-600">${invoice.client ? (invoice.client.company_name || invoice.client.contact_name) : '-'}</td>
```

**Step 2: Verify invoice list**

Refresh invoices page
Expected: Client names display correctly in table

---

## Task 10: Database Migration for Invoice Items Table

**Files:**
- Run: Database migration check

**Step 1: Check if invoice_items table exists**

```bash
cd backend
python -c "from app.db import engine; from app.models.invoice import InvoiceItem; InvoiceItem.metadata.create_all(engine)"
```

Expected: Table created (or already exists message)

**Step 2: Verify in database**

Open database and confirm `invoice_items` table exists with columns:
- id
- invoice_id
- description
- quantity
- unit_price

---

## Verification Steps

After implementing all tasks:

**1. Create Invoice Flow**
- [ ] Click "Create Invoice" button
- [ ] Select client from dropdown
- [ ] Add 3 line items with different prices
- [ ] Set 10% tax rate
- [ ] Set due date 30 days from now
- [ ] Add notes
- [ ] Submit form
- [ ] Verify invoice appears in list

**2. View Invoice Details**
- [ ] Click on created invoice
- [ ] Verify all line items display
- [ ] Verify totals are correct
- [ ] Verify client/project names display

**3. Update Invoice Status**
- [ ] Open invoice detail
- [ ] Change status to "sent"
- [ ] Verify stats update

**4. Validation**
- [ ] Try to submit with no client selected
- [ ] Try to submit with no line items
- [ ] Try to submit with negative quantity
- [ ] Verify error messages display

---

## Integration Points

**Existing Patterns Used:**
- Modal structure from `clients.html` and `projects.html`
- Form styling from `clients.html`
- Stats dashboard pattern from existing invoices.html
- Button placement from `clients.html`

**API Endpoints Used:**
- GET /api/v1/admin/clients - Load client options
- GET /api/v1/admin/projects - Load project options
- POST /api/v1/admin/invoices - Create invoice with items
- GET /api/v1/admin/invoices - Refresh list after creation

**Design Consistency:**
- Port aesthetic maintained throughout
- Lucide icons for all actions
- rounded-2xl on all cards/modals
- charcoal/light-grey/muted-blue color scheme
- Fade-in animations
