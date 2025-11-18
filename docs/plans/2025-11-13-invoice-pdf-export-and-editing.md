# Invoice PDF Export and Editing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add PDF export functionality with beautiful formatting and invoice editing with version history tracking

**Architecture:** Use WeasyPrint for HTML-to-PDF conversion with port aesthetic styling. Store business details in config. Track invoice changes with InvoiceVersion model for audit trail. Frontend adds download button and edit modal.

**Tech Stack:** WeasyPrint, Jinja2 templates, SQLAlchemy versioning, FastAPI streaming responses

---

## Context

**Current State:**
- Invoice creation works with line items
- Invoice viewing works in admin panel
- No PDF export capability
- No editing capability
- No version history

**Target State:**
- Click "Download PDF" → Beautiful PDF with Craig Mackenzie branding
- Click "Edit" → Modal to modify invoice, saves version history
- Easy config file for business name changes

---

## Task 1: Install WeasyPrint and Dependencies

**Files:**
- Modify: `backend/requirements.txt`

**Step 1: Add WeasyPrint to requirements**

Add to `backend/requirements.txt`:
```
weasyprint==60.1
```

**Step 2: Install dependencies**

```bash
cd backend
venv/Scripts/pip install weasyprint
```

Expected: "Successfully installed weasyprint-60.1..."

**Step 3: Verify installation**

```bash
venv/Scripts/python -c "import weasyprint; print(weasyprint.__version__)"
```

Expected: "60.1"

---

## Task 2: Create Business Configuration File

**Files:**
- Create: `backend/app/config/business.py`

**Step 1: Create config directory**

```bash
mkdir app/config
```

**Step 2: Create business config file**

Create `backend/app/config/business.py`:
```python
"""Business configuration for invoices and PDFs"""

BUSINESS_CONFIG = {
    "name": "Craig Mackenzie",
    "email": "contact@example.com",  # Update later
    "phone": "",  # Update later
    "address": "",  # Update later
    "city": "",
    "postcode": "",
    "country": "United Kingdom",
    "currency": "GBP",
    "currency_symbol": "£",
    "invoice_prefix": "INV",
    "tax_label": "VAT",
}

def get_business_config():
    """Get business configuration"""
    return BUSINESS_CONFIG.copy()
```

**Step 3: Test config loading**

```bash
venv/Scripts/python -c "from app.config.business import get_business_config; print(get_business_config()['name'])"
```

Expected: "Craig Mackenzie"

---

## Task 3: Create PDF Template

**Files:**
- Create: `backend/app/templates/pdf/invoice.html`

**Step 1: Create PDF templates directory**

```bash
mkdir app/templates/pdf
```

**Step 2: Create invoice PDF template**

Create `backend/app/templates/pdf/invoice.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #2d3748;
            line-height: 1.6;
        }

        .header {
            margin-bottom: 40px;
            border-bottom: 3px solid #2d3748;
            padding-bottom: 20px;
        }

        .business-name {
            font-size: 28px;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }

        .invoice-title {
            font-size: 32px;
            font-weight: bold;
            color: #5b8eb3;
            margin-bottom: 10px;
        }

        .details-grid {
            display: table;
            width: 100%;
            margin-bottom: 30px;
        }

        .details-row {
            display: table-row;
        }

        .details-cell {
            display: table-cell;
            width: 50%;
            vertical-align: top;
            padding: 10px 0;
        }

        .label {
            font-size: 12px;
            color: #718096;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .value {
            font-size: 14px;
            color: #2d3748;
            margin-top: 3px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
        }

        thead {
            background-color: #f7fafc;
            border-bottom: 2px solid #2d3748;
        }

        th {
            text-align: left;
            padding: 12px;
            font-size: 12px;
            font-weight: 600;
            color: #2d3748;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
        }

        .item-description {
            font-weight: 500;
        }

        .item-details {
            font-size: 12px;
            color: #718096;
        }

        .text-right {
            text-align: right;
        }

        .totals {
            margin-top: 20px;
            float: right;
            width: 300px;
        }

        .totals-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            font-size: 14px;
        }

        .totals-row.total {
            border-top: 2px solid #2d3748;
            margin-top: 10px;
            padding-top: 15px;
            font-size: 18px;
            font-weight: bold;
        }

        .notes {
            clear: both;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }

        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #718096;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="business-name">{{ business.name }}</div>
        {% if business.country %}
        <div class="value">{{ business.country }}</div>
        {% endif %}
    </div>

    <div class="invoice-title">INVOICE</div>

    <div class="details-grid">
        <div class="details-row">
            <div class="details-cell">
                <div class="label">Invoice Number</div>
                <div class="value">{{ invoice.invoice_number }}</div>
            </div>
            <div class="details-cell">
                <div class="label">Issue Date</div>
                <div class="value">{{ invoice.issue_date.strftime('%d %B %Y') }}</div>
            </div>
        </div>

        <div class="details-row">
            <div class="details-cell">
                <div class="label">Bill To</div>
                <div class="value">
                    {% if invoice.client.company_name %}
                    <strong>{{ invoice.client.company_name }}</strong><br>
                    {% endif %}
                    {{ invoice.client.contact_name }}<br>
                    {{ invoice.client.contact_email }}
                    {% if invoice.client.address %}
                    <br>{{ invoice.client.address }}
                    {% endif %}
                    {% if invoice.client.city or invoice.client.postcode %}
                    <br>{{ invoice.client.city }}{% if invoice.client.postcode %}, {{ invoice.client.postcode }}{% endif %}
                    {% endif %}
                </div>
            </div>
            <div class="details-cell">
                {% if invoice.due_date %}
                <div class="label">Due Date</div>
                <div class="value">{{ invoice.due_date.strftime('%d %B %Y') }}</div>
                {% endif %}
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th class="text-right">Quantity</th>
                <th class="text-right">Unit Price</th>
                <th class="text-right">Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for item in invoice.items %}
            <tr>
                <td>
                    <div class="item-description">{{ item.description }}</div>
                </td>
                <td class="text-right">{{ item.quantity }}</td>
                <td class="text-right">{{ business.currency_symbol }}{{ "%.2f"|format(item.unit_price) }}</td>
                <td class="text-right">{{ business.currency_symbol }}{{ "%.2f"|format(item.total) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="totals">
        <div class="totals-row">
            <span>Subtotal:</span>
            <span>{{ business.currency_symbol }}{{ "%.2f"|format(invoice.subtotal) }}</span>
        </div>
        <div class="totals-row">
            <span>{{ business.tax_label }} ({{ "%.1f"|format(invoice.tax_rate) }}%):</span>
            <span>{{ business.currency_symbol }}{{ "%.2f"|format(invoice.tax_amount) }}</span>
        </div>
        <div class="totals-row total">
            <span>Total:</span>
            <span>{{ business.currency_symbol }}{{ "%.2f"|format(invoice.total) }}</span>
        </div>
    </div>

    {% if invoice.notes or invoice.terms %}
    <div class="notes">
        {% if invoice.terms %}
        <div class="label">Payment Terms</div>
        <div class="value">{{ invoice.terms }}</div>
        {% endif %}

        {% if invoice.notes %}
        <div class="label" style="margin-top: 15px;">Notes</div>
        <div class="value">{{ invoice.notes }}</div>
        {% endif %}
    </div>
    {% endif %}

    <div class="footer">
        Thank you for your business
    </div>
</body>
</html>
```

**Step 3: Verify template syntax**

No verification needed - will test in next task.

---

## Task 4: Create PDF Generation Service

**Files:**
- Create: `backend/app/services/pdf_service.py`

**Step 1: Create PDF service**

Create `backend/app/services/pdf_service.py`:
```python
"""PDF generation service for invoices"""
from io import BytesIO
from weasyprint import HTML
from fastapi.templating import Jinja2Templates
from app.config.business import get_business_config
from app.models.invoice import Invoice

templates = Jinja2Templates(directory="app/templates")


def generate_invoice_pdf(invoice: Invoice) -> bytes:
    """
    Generate PDF for an invoice

    Args:
        invoice: Invoice object with items and client relationships loaded

    Returns:
        PDF file as bytes
    """
    business = get_business_config()

    # Render HTML template
    html_content = templates.get_template("pdf/invoice.html").render({
        "invoice": invoice,
        "business": business
    })

    # Generate PDF
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)

    return pdf_file.read()
```

**Step 2: Test PDF generation (manual)**

Will test via API endpoint in next task.

---

## Task 5: Add PDF Download Endpoint

**Files:**
- Modify: `backend/app/routers/admin/invoices.py`

**Step 1: Import dependencies**

Add to imports in `backend/app/routers/admin/invoices.py`:
```python
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.services import pdf_service
```

**Step 2: Add PDF endpoint**

Add after the DELETE endpoint (around line 90):
```python
@router.get("/{invoice_id}/pdf", response_class=StreamingResponse)
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Download invoice as PDF (admin only)"""
    invoice = invoice_service.get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Generate PDF
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice)

    # Return as streaming response
    pdf_stream = BytesIO(pdf_bytes)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"
        }
    )
```

**Step 3: Test PDF endpoint**

```bash
# First, get a valid token and invoice ID from your test data
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/v1/admin/invoices/1/pdf \
     --output test_invoice.pdf
```

Expected: PDF file downloaded, opens correctly

---

## Task 6: Add Download PDF Button to UI

**Files:**
- Modify: `backend/app/templates/admin/invoices.html`

**Step 1: Add download button in invoice detail modal**

In the invoice detail modal buttons section (around line 105-109), replace the Close button section with:
```html
<div class="mt-8 flex gap-4">
    <button onclick="downloadInvoicePDF(${invoice.id})" class="flex-1 bg-muted-blue text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition">
        <i data-lucide="download" class="w-5 h-5 inline-block mr-2"></i>
        Download PDF
    </button>
    <button onclick="closeInvoiceModal()" class="flex-1 px-6 py-3 border-2 border-gray-200 rounded-xl font-medium hover:border-muted-blue transition">
        Close
    </button>
</div>
```

**Step 2: Add JavaScript function**

Add before the page load section (around line 685):
```javascript
function downloadInvoicePDF(invoiceId) {
    const token = localStorage.getItem('access_token');

    fetch(`/api/v1/admin/invoices/${invoiceId}/pdf`, {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to download PDF');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `invoice_${invoiceId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Error downloading PDF:', error);
        alert('Failed to download PDF');
    });
}
```

**Step 3: Test PDF download**

1. Open http://127.0.0.1:8000/admin/invoices
2. Click on an invoice
3. Click "Download PDF"

Expected: PDF downloads automatically with correct filename

---

## Task 7: Add Invoice Version Model

**Files:**
- Create: `backend/app/models/invoice_version.py`

**Step 1: Create InvoiceVersion model**

Create `backend/app/models/invoice_version.py`:
```python
"""Invoice version history model for tracking changes"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class InvoiceVersion(Base):
    """Track changes to invoices"""
    __tablename__ = "invoice_versions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    change_type = Column(String(50), nullable=False)  # created, updated, status_changed
    changes = Column(JSON, nullable=True)  # Store what changed

    # Relationships
    invoice = relationship("Invoice", back_populates="versions")
    user = relationship("User")
```

**Step 2: Add versions relationship to Invoice model**

In `backend/app/models/invoice.py`, add to Invoice class:
```python
# Add to imports
from sqlalchemy.orm import relationship

# Add to Invoice class (around line 30)
versions = relationship("InvoiceVersion", back_populates="invoice", cascade="all, delete-orphan")
```

**Step 3: Update imports in models __init__.py**

In `backend/app/models/__init__.py`, add:
```python
from .invoice_version import InvoiceVersion
```

**Step 4: Create database migration**

```bash
cd backend
venv/Scripts/alembic revision --autogenerate -m "Add invoice version tracking"
```

Expected: New migration file created

**Step 5: Run migration**

```bash
venv/Scripts/alembic upgrade head
```

Expected: "Running upgrade... -> ..., Add invoice version tracking"

---

## Task 8: Add Version Tracking to Invoice Service

**Files:**
- Modify: `backend/app/services/invoice_service.py`

**Step 1: Import InvoiceVersion model**

Add to imports:
```python
from app.models.invoice_version import InvoiceVersion
```

**Step 2: Add version creation function**

Add this function:
```python
def create_invoice_version(
    db: Session,
    invoice: Invoice,
    user_id: int,
    change_type: str,
    changes: dict = None
) -> InvoiceVersion:
    """Create a version record for invoice changes"""
    # Get next version number
    version_count = db.query(InvoiceVersion).filter(
        InvoiceVersion.invoice_id == invoice.id
    ).count()

    version = InvoiceVersion(
        invoice_id=invoice.id,
        version_number=version_count + 1,
        changed_by=user_id,
        change_type=change_type,
        changes=changes
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version
```

**Step 3: Update create_invoice to add initial version**

In the `create_invoice` function, before the final return, add:
```python
# Create initial version
create_invoice_version(
    db,
    invoice,
    user_id,
    change_type="created",
    changes=None
)
```

**Step 4: Create update_invoice function**

Add this function:
```python
from datetime import date

def update_invoice(
    db: Session,
    invoice_id: int,
    invoice_data: dict,
    user_id: int
) -> Invoice:
    """Update an existing invoice and track changes"""
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return None

    # Track what changed
    changes = {}

    # Update basic fields
    if "due_date" in invoice_data and invoice_data["due_date"] != invoice.due_date:
        changes["due_date"] = {
            "old": str(invoice.due_date) if invoice.due_date else None,
            "new": str(invoice_data["due_date"]) if invoice_data["due_date"] else None
        }
        invoice.due_date = invoice_data["due_date"]

    if "tax_rate" in invoice_data and invoice_data["tax_rate"] != invoice.tax_rate:
        changes["tax_rate"] = {
            "old": float(invoice.tax_rate),
            "new": float(invoice_data["tax_rate"])
        }
        invoice.tax_rate = invoice_data["tax_rate"]

    if "notes" in invoice_data and invoice_data["notes"] != invoice.notes:
        changes["notes"] = {
            "old": invoice.notes,
            "new": invoice_data["notes"]
        }
        invoice.notes = invoice_data["notes"]

    if "terms" in invoice_data and invoice_data["terms"] != invoice.terms:
        changes["terms"] = {
            "old": invoice.terms,
            "new": invoice_data["terms"]
        }
        invoice.terms = invoice_data["terms"]

    # Update line items if provided
    if "items" in invoice_data:
        changes["items"] = "modified"

        # Delete existing items
        for item in invoice.items:
            db.delete(item)

        # Add new items
        for item_data in invoice_data["items"]:
            item = InvoiceItem(**item_data, invoice_id=invoice.id)
            db.add(item)

        # Recalculate totals
        totals = calculate_invoice_totals(invoice_data["items"], invoice.tax_rate)
        invoice.subtotal = totals["subtotal"]
        invoice.tax_amount = totals["tax_amount"]
        invoice.total = totals["total"]

    db.commit()
    db.refresh(invoice)

    # Create version record
    if changes:
        create_invoice_version(
            db,
            invoice,
            user_id,
            change_type="updated",
            changes=changes
        )

    return invoice
```

**Step 5: Test version tracking**

Will test via API in next task.

---

## Task 9: Add Invoice Update Endpoint

**Files:**
- Modify: `backend/app/routers/admin/invoices.py`
- Modify: `backend/app/schemas/invoice.py`

**Step 1: Create InvoiceUpdate schema**

In `backend/app/schemas/invoice.py`, add:
```python
class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    due_date: Optional[date] = None
    tax_rate: Optional[condecimal(ge=0, max_digits=5, decimal_places=2)] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    items: Optional[List[InvoiceItemCreate]] = None

    class Config:
        from_attributes = True
```

**Step 2: Update PUT endpoint**

Replace the existing PUT endpoint in `backend/app/routers/admin/invoices.py` (around line 60):
```python
@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an invoice (admin only)"""
    # Convert to dict, excluding None values
    update_dict = invoice_data.model_dump(exclude_none=True)

    invoice = invoice_service.update_invoice(db, invoice_id, update_dict, current_user.id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice
```

**Step 3: Test update endpoint**

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/admin/invoices/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Updated notes test",
    "tax_rate": 20.0
  }'
```

Expected: 200 response with updated invoice, version record created

---

## Task 10: Add Edit Invoice UI

**Files:**
- Modify: `backend/app/templates/admin/invoices.html`

**Step 1: Add Edit button in invoice detail modal**

In the invoice detail modal, update the buttons section (around line 105) to:
```html
<div class="mt-8 flex gap-4">
    <button id="edit-invoice-btn" onclick="openEditInvoiceModal(${invoice.id})" class="flex-1 bg-charcoal text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition">
        <i data-lucide="edit" class="w-5 h-5 inline-block mr-2"></i>
        Edit Invoice
    </button>
    <button onclick="downloadInvoicePDF(${invoice.id})" class="flex-1 bg-muted-blue text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition">
        <i data-lucide="download" class="w-5 h-5 inline-block mr-2"></i>
        Download PDF
    </button>
    <button onclick="closeInvoiceModal()" class="px-6 py-3 border-2 border-gray-200 rounded-xl font-medium hover:border-muted-blue transition">
        Close
    </button>
</div>
```

**Step 2: Add edit modal HTML**

Add after the create-invoice-modal (around line 216):
```html
<!-- Edit Invoice Modal -->
<div id="edit-invoice-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-6">
    <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-8">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-charcoal">Edit Invoice</h2>
                <button onclick="closeEditInvoiceModal()" class="text-gray-500 hover:text-charcoal">
                    <i data-lucide="x" class="w-6 h-6"></i>
                </button>
            </div>

            <form id="edit-invoice-form" class="space-y-6">
                <input type="hidden" id="edit-invoice-id">

                <!-- Due Date and Tax Rate -->
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Due Date</label>
                        <input type="date" id="edit-due-date" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Tax Rate (%)</label>
                        <input type="number" id="edit-tax-rate" value="0" min="0" max="100" step="0.01" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
                    </div>
                </div>

                <!-- Line Items -->
                <div>
                    <div class="flex justify-between items-center mb-3">
                        <label class="block text-sm font-medium text-charcoal">Line Items *</label>
                        <button type="button" onclick="addEditLineItem()" class="flex items-center gap-2 text-muted-blue hover:text-blue-700 font-medium">
                            <i data-lucide="plus-circle" class="w-4 h-4"></i>
                            <span>Add Item</span>
                        </button>
                    </div>
                    <div id="edit-line-items-container" class="space-y-3">
                        <!-- Line items will be added here -->
                    </div>
                </div>

                <!-- Totals Display -->
                <div class="border-t pt-6 space-y-2">
                    <div class="flex justify-between text-gray-700">
                        <span>Subtotal:</span>
                        <span id="edit-subtotal-display" class="font-semibold">£0.00</span>
                    </div>
                    <div class="flex justify-between text-gray-700">
                        <span>Tax:</span>
                        <span id="edit-tax-display" class="font-semibold">£0.00</span>
                    </div>
                    <div class="flex justify-between text-xl font-bold text-charcoal border-t pt-2">
                        <span>Total:</span>
                        <span id="edit-total-display">£0.00</span>
                    </div>
                </div>

                <!-- Notes and Terms -->
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Notes</label>
                        <textarea id="edit-notes" rows="3" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue resize-none"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-charcoal mb-2">Terms</label>
                        <textarea id="edit-terms" rows="3" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue resize-none"></textarea>
                    </div>
                </div>

                <div id="edit-form-error" class="hidden p-4 bg-red-50 text-red-800 border border-red-200 rounded-xl text-sm"></div>

                <div class="flex gap-4">
                    <button type="submit" class="flex-1 bg-charcoal text-white px-6 py-3 rounded-xl font-medium shadow-lg hover:shadow-xl transition">
                        Save Changes
                    </button>
                    <button type="button" onclick="closeEditInvoiceModal()" class="px-6 py-3 border-2 border-gray-200 rounded-xl font-medium hover:border-muted-blue transition">
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
```

**Step 3: Add JavaScript functions**

Add before the page load section:
```javascript
let editLineItemCount = 0;

function openEditInvoiceModal(invoiceId) {
    const invoice = allInvoices.find(i => i.id === invoiceId);
    if (!invoice) return;

    closeInvoiceModal();

    // Populate form
    document.getElementById('edit-invoice-id').value = invoice.id;
    document.getElementById('edit-due-date').value = invoice.due_date || '';
    document.getElementById('edit-tax-rate').value = invoice.tax_rate || 0;
    document.getElementById('edit-notes').value = invoice.notes || '';
    document.getElementById('edit-terms').value = invoice.terms || '';

    // Populate line items
    const container = document.getElementById('edit-line-items-container');
    container.innerHTML = '';
    editLineItemCount = 0;

    if (invoice.items && invoice.items.length > 0) {
        invoice.items.forEach(item => {
            addEditLineItem(item);
        });
    } else {
        addEditLineItem();
    }

    updateEditTotals();

    document.getElementById('edit-invoice-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeEditInvoiceModal() {
    document.getElementById('edit-invoice-modal').classList.add('hidden');
}

function addEditLineItem(itemData = null) {
    editLineItemCount++;
    const container = document.getElementById('edit-line-items-container');
    const itemDiv = document.createElement('div');
    itemDiv.className = 'flex gap-3 items-start';
    itemDiv.id = `edit-line-item-${editLineItemCount}`;
    itemDiv.innerHTML = `
        <div class="flex-1">
            <input type="text"
                   data-edit-item-id="${editLineItemCount}"
                   data-edit-field="description"
                   placeholder="Description"
                   value="${itemData?.description || ''}"
                   required
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
        </div>
        <div class="w-24">
            <input type="number"
                   data-edit-item-id="${editLineItemCount}"
                   data-edit-field="quantity"
                   placeholder="Qty"
                   min="0.01"
                   step="0.01"
                   value="${itemData?.quantity || 1}"
                   required
                   oninput="updateEditTotals()"
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
        </div>
        <div class="w-32">
            <input type="number"
                   data-edit-item-id="${editLineItemCount}"
                   data-edit-field="unit_price"
                   placeholder="Price"
                   min="0"
                   step="0.01"
                   value="${itemData?.unit_price || 0}"
                   required
                   oninput="updateEditTotals()"
                   class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-muted-blue">
        </div>
        <button type="button"
                onclick="removeEditLineItem(${editLineItemCount})"
                class="p-3 text-red-600 hover:bg-red-50 rounded-xl transition">
            <i data-lucide="trash-2" class="w-5 h-5"></i>
        </button>
    `;
    container.appendChild(itemDiv);
    lucide.createIcons();
}

function removeEditLineItem(itemId) {
    const item = document.getElementById(`edit-line-item-${itemId}`);
    if (item) {
        item.remove();
        updateEditTotals();
    }

    const container = document.getElementById('edit-line-items-container');
    if (container.children.length === 0) {
        addEditLineItem();
    }
}

function updateEditTotals() {
    const container = document.getElementById('edit-line-items-container');
    const items = container.querySelectorAll('[data-edit-field="quantity"]');

    let subtotal = 0;
    items.forEach(qtyInput => {
        const itemId = qtyInput.dataset.editItemId;
        const priceInput = container.querySelector(`[data-edit-item-id="${itemId}"][data-edit-field="unit_price"]`);

        const quantity = parseFloat(qtyInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        subtotal += quantity * price;
    });

    const taxRate = parseFloat(document.getElementById('edit-tax-rate').value) || 0;
    const taxAmount = (subtotal * taxRate) / 100;
    const total = subtotal + taxAmount;

    document.getElementById('edit-subtotal-display').textContent = `£${subtotal.toFixed(2)}`;
    document.getElementById('edit-tax-display').textContent = `£${taxAmount.toFixed(2)}`;
    document.getElementById('edit-total-display').textContent = `£${total.toFixed(2)}`;
}

// Add tax rate listener
document.addEventListener('DOMContentLoaded', () => {
    const editTaxRate = document.getElementById('edit-tax-rate');
    if (editTaxRate) {
        editTaxRate.addEventListener('input', updateEditTotals);
    }
});
```

**Step 4: Add form submission handler**

Add before the page load section:
```javascript
document.getElementById('edit-invoice-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const errorDiv = document.getElementById('edit-form-error');
    errorDiv.classList.add('hidden');

    const invoiceId = document.getElementById('edit-invoice-id').value;

    // Gather line items
    const container = document.getElementById('edit-line-items-container');
    const itemElements = container.querySelectorAll('[data-edit-field="description"]');
    const items = [];

    for (const descInput of itemElements) {
        const itemId = descInput.dataset.editItemId;
        const qtyInput = container.querySelector(`[data-edit-item-id="${itemId}"][data-edit-field="quantity"]`);
        const priceInput = container.querySelector(`[data-edit-item-id="${itemId}"][data-edit-field="unit_price"]`);

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

    // Build update data
    const updateData = {
        due_date: document.getElementById('edit-due-date').value || null,
        tax_rate: parseFloat(document.getElementById('edit-tax-rate').value) || 0,
        notes: document.getElementById('edit-notes').value || null,
        terms: document.getElementById('edit-terms').value || null,
        items: items
    };

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`/api/v1/admin/invoices/${invoiceId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update invoice');
        }

        closeEditInvoiceModal();
        await loadInvoices();

        alert('Invoice updated successfully!');
    } catch (error) {
        console.error('Error updating invoice:', error);
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});
```

**Step 5: Test edit functionality**

1. Open http://127.0.0.1:8000/admin/invoices
2. Click on an invoice
3. Click "Edit Invoice"
4. Modify line items, tax rate, notes
5. Click "Save Changes"

Expected: Invoice updates, modal closes, list refreshes

---

## Verification Steps

**PDF Export:**
- [ ] Click "Download PDF" on any invoice
- [ ] PDF opens with "Craig Mackenzie" header
- [ ] All invoice details visible and formatted beautifully
- [ ] Line items table shows quantity × price correctly
- [ ] Totals (subtotal, tax, total) are correct
- [ ] Client details display properly
- [ ] Port aesthetic colors (charcoal #2d3748, muted-blue #5b8eb3) used

**Invoice Editing:**
- [ ] Click "Edit" on an invoice
- [ ] Existing line items populate in form
- [ ] Can add new line items
- [ ] Can remove line items
- [ ] Totals update in real-time
- [ ] Save updates the invoice
- [ ] Version record created in database
- [ ] Changes tracked in version.changes JSON

**Database Verification:**
```sql
SELECT * FROM invoice_versions ORDER BY changed_at DESC LIMIT 5;
```

Expected: Version records with change_type and changes data

---

## Configuration Updates

**Easy Business Name Changes:**

Edit `backend/app/config/business.py`:
```python
BUSINESS_CONFIG = {
    "name": "Your New Business Name",  # Change here
    "email": "your@email.com",         # Update contact info
    # ... other fields
}
```

All PDFs will use the updated configuration immediately.

---

## Future Enhancements (Deferred)

- Email sending functionality
- Client portal for viewing invoices
- Online payment integration (Stripe)
- Invoice prefix customization UI
- Version history display in UI
- Revert to previous version
- Invoice templates (multiple styles)
