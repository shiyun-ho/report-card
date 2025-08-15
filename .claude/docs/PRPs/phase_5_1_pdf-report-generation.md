# Product Requirements Planning (PRP) - Phase 5.1 PDF Report Generation

**Product**: Teacher Report Card Assistant  
**Feature**: Professional PDF Report Generation & Export  
**Phase**: 5.1 - PDF Generation Engine Implementation  
**PRP Date**: August 14, 2025  
**Estimated Duration**: 1 hour  
**Priority**: Critical (Final Assignment Requirement)  

---

## 🎯 **Executive Summary**

Implement the final missing piece of the assignment: professional PDF report generation and export functionality. This feature transforms collected report data (grades, achievements, behavioral comments) into printable report cards that teachers can download, print, or share. The implementation uses HTML templates with WeasyPrint for reliable, server-side PDF generation in the Docker environment.

**Success Metrics:**
- Teachers can generate professional PDF reports from the report generation page
- PDF includes all report components: student info, grades, achievements, comments
- Reports are branded with school information and formatted for A4 printing
- Download process is secure with proper authentication and RBAC enforcement
- PDF generation works reliably within Docker container environment

---

## 📋 **Requirements Analysis**

### **Functional Requirements**

#### FR1: PDF Generation API Endpoint
- New endpoint: `POST /api/v1/reports/generate/{student_id}/{term_id}`
- Accepts report data payload (achievements, behavioral comments)
- Generates PDF using HTML template engine (WeasyPrint)
- Returns PDF file as downloadable response with proper headers
- Enforces RBAC: only teachers with student access can generate reports

#### FR2: Professional Report Template
- HTML/CSS template matching Singapore report card standards
- School branding section with logo placeholder and school name
- Student information header (name, student ID, class, term, date)
- Grade table showing all subjects with scores and performance bands
- Achievement sections with selected achievements and descriptions  
- Behavioral comments section with teacher signature area
- Print-ready formatting (A4 size, proper margins, page breaks)

#### FR3: Report Data Compilation
- Service layer to aggregate all report data from existing APIs
- Student details, grade information, achievement selections
- Performance band calculations and grade comparisons
- Behavioral comments and metadata (teacher name, generation date)
- Data validation to ensure complete report information

#### FR4: Frontend Integration
- Update existing "Generate Report" button to call PDF endpoint
- Handle file download with proper filename (StudentName_Term_Report.pdf)
- Loading states during PDF generation process
- Error handling for generation failures or network issues
- Success feedback with download confirmation

### **Non-Functional Requirements**

#### NFR1: Performance & Scalability
- PDF generation completes within 10 seconds for typical reports
- Concurrent PDF generation support for multiple users
- Memory management for large PDF operations in container environment
- Efficient template rendering without resource leaks

#### NFR2: Security & Access Control
- RBAC enforcement - teachers can only generate reports for accessible students
- No sensitive data exposure in temporary files or error messages
- Secure file handling with automatic cleanup of temporary resources
- Session-based authentication required for all PDF operations

#### NFR3: Quality & Reliability
- Professional PDF layout matching Singapore education standards
- Consistent rendering across different browsers and operating systems
- Graceful error handling with user-friendly error messages
- Robust template processing with validation for missing data

#### NFR4: Docker Environment Compatibility
- WeasyPrint dependencies properly configured in container
- Font handling for professional typography in Docker environment
- Efficient container resource usage during PDF generation
- Environment variables for PDF configuration settings

---

## 🔍 **Codebase Analysis & Patterns**

### **Existing Architecture Patterns to Follow**

Based on analysis of `/backend/src/app/api/v1/endpoints/` and service patterns:

#### 1. **Endpoint Structure Pattern** (following `grades.py`, `achievements.py`)
```python
# File: /backend/src/app/api/v1/endpoints/reports.py
from fastapi import APIRouter, Depends, HTTPException, Response
from app.dependencies.auth import get_current_user
from app.services.report_service import ReportService

router = APIRouter()

@router.post("/generate/{student_id}/{term_id}")
async def generate_report(
    student_id: int,
    term_id: int,
    report_data: ReportGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Implementation follows established RBAC patterns
```

#### 2. **Schema Structure Pattern** (following `grade_schemas.py`, `student_schemas.py`)
```python
# File: /backend/src/app/schemas/report_schemas.py
class ReportGenerationRequest(BaseModel):
    selected_achievements: List[SelectedAchievement]
    behavioral_comments: str
    
class SelectedAchievement(BaseModel):
    title: str
    description: str
    category_name: str
    
class ReportGenerationResponse(BaseModel):
    success: bool
    filename: str
    file_size: int
    generation_time_ms: int
```

#### 3. **Service Layer Pattern** (following `achievement_service.py`, `grade_service.py`)
```python
# File: /backend/src/app/services/report_service.py
class ReportService:
    def __init__(self, db: Session):
        self.db = db
        
    def generate_pdf_report(
        self, 
        student_id: int, 
        term_id: int, 
        report_data: ReportGenerationRequest,
        current_user: User
    ) -> bytes:
        # Implementation follows established RBAC and data compilation patterns
```

### **Existing API Integration Points**

The PDF generation will leverage existing, tested API endpoints:

1. **Student Data**: `GET /api/v1/students/{student_id}` (from `student_schemas.py`)
2. **Grade Data**: `GET /api/v1/grades/students/{student_id}/terms/{term_id}` (from `grade_schemas.py`)
3. **Achievement Data**: `GET /api/v1/achievements/suggest/{student_id}/{term_id}` (from `achievement_schemas.py`)
4. **Term Data**: `GET /api/v1/terms/{term_id}` (from `term_schemas.py`)

### **Frontend Integration Points**

Based on analysis of `/frontend/src/components/reports/ReportForm.tsx`:

```typescript
// Current handleGenerateReport function (lines 110-126):
const handleGenerateReport = () => {
  if (!validateForm(formData)) {
    console.error('Form validation failed')
    return
  }

  // Phase 5.1 will implement actual PDF generation
  console.log('Generating report with data:', {
    studentId,
    termId: selectedTermId,
    ...formData
  })
  
  alert('Report generation initiated! (Phase 5.1 will implement PDF creation)')
}
```

**Integration Change Required:**
Replace placeholder with actual API call to `/api/v1/reports/generate/{studentId}/{termId}`

---

## 🛠️ **Technical Implementation Plan**

### **Approach: WeasyPrint + HTML Templates**

Based on research findings, WeasyPrint is optimal for this use case:
- ✅ **HTML/CSS Based**: Leverage existing web development skills
- ✅ **Professional Output**: High-quality PDF rendering suitable for official reports
- ✅ **Container Compatible**: Works reliably in Docker environment
- ✅ **Jinja2 Integration**: Dynamic template rendering with Python data
- ✅ **FastAPI Compatible**: Proven integration patterns available

**Key Research Sources:**
- [Python PDF Generation with WeasyPrint - DEV Community](https://dev.to/bowmanjd/python-pdf-generation-from-html-with-weasyprint-538h)
- [Generate good looking PDFs with WeasyPrint and Jinja2](https://joshkaramuth.com/blog/generate-good-looking-pdfs-weasyprint-jinja2/)
- [Stack Overflow: WeasyPrint inside Docker FastAPI](https://stackoverflow.com/questions/68832433/fonts-in-pdf-exported-using-weasyprint-inside-docker-fastapi)

### **Implementation Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   PDF Engine    │
│   Button Click  │───▶│   Report API     │───▶│   WeasyPrint    │
│   (ReportForm)  │    │   Data Compiler  │    │   + Jinja2      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File Download │    │   RBAC Security  │    │   HTML Template │
│   Success State │    │   Data Validation│    │   CSS Styling   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### **Development Dependencies**

Update `/backend/pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies
    "weasyprint>=61.2",     # PDF generation from HTML
    "jinja2>=3.1.4",       # Template rendering
]
```

**Note**: WeasyPrint has system dependencies for fonts and rendering that must be handled in Docker.

---

## 📝 **Detailed Task Breakdown**

### **Task 5.1.1: Backend PDF Service Implementation** (20 minutes)

#### **5.1.1a: Create Report Schemas**
Create `/backend/src/app/schemas/report_schemas.py`:

```python
from typing import List
from pydantic import BaseModel, Field

class SelectedAchievement(BaseModel):
    title: str
    description: str
    category_name: str
    
class ReportGenerationRequest(BaseModel):
    selected_achievements: List[SelectedAchievement] = Field(default_factory=list)
    behavioral_comments: str = Field(..., min_length=1, max_length=500)

class ReportGenerationResponse(BaseModel):
    success: bool
    filename: str
    file_size: int
    generation_time_ms: int
    message: str
```

#### **5.1.1b: Create Report Service**
Create `/backend/src/app/services/report_service.py`:

```python
import time
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

from app.models.user import User
from app.services.student_service import StudentService  
from app.services.grade_service import GradeService
from app.services.achievement_service import AchievementService
from app.schemas.report_schemas import ReportGenerationRequest

class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.student_service = StudentService(db)
        self.grade_service = GradeService(db)
        self.achievement_service = AchievementService(db)
        
        # Initialize Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader('/app/templates')
        )
    
    def generate_pdf_report(
        self,
        student_id: int,
        term_id: int, 
        report_data: ReportGenerationRequest,
        current_user: User
    ) -> bytes:
        """Generate PDF report with RBAC enforcement."""
        start_time = time.time()
        
        # RBAC: Verify access to student
        if not self.student_service.can_access_student(current_user, student_id):
            raise HTTPException(status_code=403, detail="Access denied to student")
            
        # Compile all report data
        template_data = self._compile_report_data(student_id, term_id, report_data, current_user)
        
        # Render HTML template
        template = self.template_env.get_template('report_card.html')
        html_content = template.render(**template_data)
        
        # Generate PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        return pdf_bytes
    
    def _compile_report_data(self, student_id: int, term_id: int, report_data: ReportGenerationRequest, current_user: User) -> Dict[str, Any]:
        """Compile all data needed for report template."""
        # Get student details
        student = self.student_service.get_student_detail(student_id, current_user)
        
        # Get grades
        grades = self.grade_service.get_student_grades(student_id, term_id, current_user)
        
        # Calculate performance band
        if grades:
            average = sum(float(g.score) for g in grades) / len(grades)
            performance_band = self.grade_service.calculate_performance_band(average)
        else:
            average = 0
            performance_band = "No Data"
        
        return {
            'student': student,
            'term': self.grade_service.get_term(term_id),
            'grades': grades,
            'average_score': round(average, 1),
            'performance_band': performance_band,
            'selected_achievements': report_data.selected_achievements,
            'behavioral_comments': report_data.behavioral_comments,
            'teacher_name': current_user.full_name,
            'generation_date': datetime.now().strftime('%B %d, %Y'),
            'school_name': student.school.name if hasattr(student, 'school') else 'School Name'
        }
```

#### **5.1.1c: Create API Endpoint**
Create `/backend/src/app/api/v1/endpoints/reports.py`:

```python
import time
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.report_service import ReportService
from app.schemas.report_schemas import ReportGenerationRequest, ReportGenerationResponse

router = APIRouter()

@router.post("/generate/{student_id}/{term_id}", response_model=ReportGenerationResponse)
async def generate_student_report(
    student_id: int,
    term_id: int,
    report_data: ReportGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate PDF report for student."""
    start_time = time.time()
    
    try:
        report_service = ReportService(db)
        pdf_bytes = report_service.generate_pdf_report(
            student_id, term_id, report_data, current_user
        )
        
        # Prepare filename
        student = report_service.student_service.get_student_detail(student_id, current_user)
        filename = f"{student.full_name.replace(' ', '_')}_Term_{term_id}_Report.pdf"
        
        generation_time = int((time.time() - start_time) * 1000)
        
        # Return PDF as download
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/download/{student_id}/{term_id}")
async def download_report(
    student_id: int,
    term_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Alternative endpoint for direct PDF download."""
    # Minimal report data for basic PDF
    basic_report_data = ReportGenerationRequest(
        selected_achievements=[],
        behavioral_comments="Generated automatically"
    )
    
    return await generate_student_report(student_id, term_id, basic_report_data, current_user, db)
```

#### **5.1.1d: Update API Router**
Update `/backend/src/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import reports

# Add to router includes
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
```

### **Task 5.1.2: HTML Report Template Creation** (15 minutes)

Create `/backend/templates/report_card.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ student.full_name }} - Term {{ term.term_number }} Report</title>
    <style>
        @page {
            size: A4;
            margin: 2cm 1.5cm;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            color: #333;
        }
        
        .header {
            text-align: center;
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 1cm;
            margin-bottom: 1cm;
        }
        
        .school-logo {
            width: 60px;
            height: 60px;
            margin-bottom: 0.5cm;
        }
        
        .school-name {
            font-size: 18pt;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 0.2cm;
        }
        
        .report-title {
            font-size: 16pt;
            font-weight: bold;
            color: #333;
        }
        
        .student-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1cm;
            margin-bottom: 1cm;
            padding: 0.5cm;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        
        .info-group {
            margin-bottom: 0.3cm;
        }
        
        .info-label {
            font-weight: bold;
            color: #666;
        }
        
        .grades-section {
            margin-bottom: 1cm;
        }
        
        .section-title {
            font-size: 14pt;
            font-weight: bold;
            color: #2c5aa0;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.2cm;
            margin-bottom: 0.5cm;
        }
        
        .grades-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 0.5cm;
        }
        
        .grades-table th {
            background-color: #2c5aa0;
            color: white;
            padding: 0.3cm;
            text-align: left;
        }
        
        .grades-table td {
            border: 1px solid #ddd;
            padding: 0.3cm;
            text-align: center;
        }
        
        .performance-band {
            display: inline-block;
            padding: 0.1cm 0.3cm;
            border-radius: 3px;
            font-weight: bold;
        }
        
        .band-outstanding { background-color: #d4edda; color: #155724; }
        .band-good { background-color: #d1ecf1; color: #0c5460; }
        .band-satisfactory { background-color: #fff3cd; color: #856404; }
        .band-needs-improvement { background-color: #f8d7da; color: #721c24; }
        
        .achievements-section {
            margin-bottom: 1cm;
        }
        
        .achievement-item {
            margin-bottom: 0.3cm;
            padding: 0.3cm;
            background-color: #f8f9fa;
            border-left: 3px solid #2c5aa0;
        }
        
        .achievement-title {
            font-weight: bold;
            color: #2c5aa0;
        }
        
        .comments-section {
            margin-bottom: 1cm;
        }
        
        .comments-text {
            background-color: #f8f9fa;
            padding: 0.5cm;
            border-radius: 5px;
            min-height: 2cm;
        }
        
        .signature-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2cm;
            margin-top: 2cm;
            padding-top: 1cm;
            border-top: 1px solid #ddd;
        }
        
        .signature-box {
            text-align: center;
        }
        
        .signature-line {
            border-bottom: 1px solid #333;
            margin-bottom: 0.2cm;
            height: 1cm;
        }
        
        .footer {
            position: fixed;
            bottom: 1cm;
            right: 1.5cm;
            font-size: 10pt;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <!-- <img src="{{ school_logo_path }}" alt="School Logo" class="school-logo"> -->
        <div class="school-name">{{ school_name }}</div>
        <div class="report-title">Student Progress Report</div>
    </div>
    
    <div class="student-info">
        <div>
            <div class="info-group">
                <span class="info-label">Student Name:</span> {{ student.full_name }}
            </div>
            <div class="info-group">
                <span class="info-label">Student ID:</span> {{ student.student_id }}
            </div>
            <div class="info-group">
                <span class="info-label">Class:</span> {{ student.class_name }}
            </div>
        </div>
        <div>
            <div class="info-group">
                <span class="info-label">Academic Term:</span> {{ term.name }}
            </div>
            <div class="info-group">
                <span class="info-label">Report Date:</span> {{ generation_date }}
            </div>
            <div class="info-group">
                <span class="info-label">Teacher:</span> {{ teacher_name }}
            </div>
        </div>
    </div>
    
    <div class="grades-section">
        <h2 class="section-title">Academic Performance</h2>
        <table class="grades-table">
            <thead>
                <tr>
                    <th>Subject</th>
                    <th>Score</th>
                    <th>Grade</th>
                </tr>
            </thead>
            <tbody>
                {% for grade in grades %}
                <tr>
                    <td>{{ grade.subject_name }}</td>
                    <td>{{ grade.score }}%</td>
                    <td>
                        {% if grade.score >= 90 %}A+
                        {% elif grade.score >= 85 %}A
                        {% elif grade.score >= 70 %}B
                        {% elif grade.score >= 55 %}C
                        {% else %}D
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="info-group">
            <span class="info-label">Overall Average:</span> {{ average_score }}%
        </div>
        <div class="info-group">
            <span class="info-label">Performance Band:</span> 
            <span class="performance-band band-{{ performance_band.lower().replace(' ', '-') }}">
                {{ performance_band }}
            </span>
        </div>
    </div>
    
    {% if selected_achievements %}
    <div class="achievements-section">
        <h2 class="section-title">Notable Achievements</h2>
        {% for achievement in selected_achievements %}
        <div class="achievement-item">
            <div class="achievement-title">{{ achievement.title }}</div>
            <div>{{ achievement.description }}</div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="comments-section">
        <h2 class="section-title">Teacher's Comments</h2>
        <div class="comments-text">{{ behavioral_comments }}</div>
    </div>
    
    <div class="signature-section">
        <div class="signature-box">
            <div class="signature-line"></div>
            <div>Teacher Signature</div>
            <div>{{ teacher_name }}</div>
        </div>
        <div class="signature-box">
            <div class="signature-line"></div>
            <div>Date</div>
            <div>{{ generation_date }}</div>
        </div>
    </div>
    
    <div class="footer">
        Generated on {{ generation_date }}
    </div>
</body>
</html>
```

### **Task 5.1.3: Frontend Integration** (15 minutes)

#### **5.1.3a: Update API Client**
Update `/frontend/src/lib/api.ts`:

```typescript
// Add PDF generation method
export const generateReport = async (
  studentId: number,
  termId: number,
  reportData: {
    selectedAchievements: Array<{
      title: string
      description: string
      category_name: string
    }>
    behavioralComments: string
  }
): Promise<Blob> => {
  const response = await fetch(`${API_BASE_URL}/reports/generate/${studentId}/${termId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(reportData),
  })
  
  if (!response.ok) {
    throw new Error('PDF generation failed')
  }
  
  return response.blob()
}

// Utility function for file download
export const downloadPDF = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}
```

#### **5.1.3b: Update Report Form Component**
Update `/frontend/src/components/reports/ReportForm.tsx` (replace lines 110-126):

```typescript
const handleGenerateReport = async () => {
  if (!validateForm(formData)) {
    console.error('Form validation failed')
    return
  }

  try {
    setGenerating(true) // Add loading state
    
    // Transform form data to API format
    const apiData = {
      selectedAchievements: formData.selectedAchievements.map(achievement => ({
        title: achievement.title,
        description: achievement.description,
        category_name: achievement.category_name || 'General'
      })),
      behavioralComments: formData.behavioralComments
    }
    
    // Generate PDF
    const pdfBlob = await generateReport(studentId, selectedTermId!, apiData)
    
    // Download PDF
    const filename = `Student_${studentId}_Term_${selectedTermId}_Report.pdf`
    downloadPDF(pdfBlob, filename)
    
    // Show success message
    console.log('Report generated successfully')
    
  } catch (error) {
    console.error('PDF generation failed:', error)
    alert('Failed to generate report. Please try again.')
  } finally {
    setGenerating(false)
  }
}

// Add loading state to component state
const [generating, setGenerating] = useState(false)

// Update button with loading state
<Button 
  onClick={handleGenerateReport}
  className="bg-blue-600 hover:bg-blue-700 text-white"
  disabled={Object.values(validationErrors).some(error => !!error) || generating}
>
  {generating ? 'Generating PDF...' : 'Generate Report'}
</Button>
```

### **Task 5.1.4: Docker Dependencies** (10 minutes)

#### **5.1.4a: Update Backend Dependencies**
Update `/backend/pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies
    "weasyprint>=61.2",
    "jinja2>=3.1.4",
]
```

#### **5.1.4b: Update Backend Dockerfile** (if needed)
WeasyPrint requires system fonts. Verify `/backend/Dockerfile` includes:

```dockerfile
# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*
```

#### **5.1.4c: Create Templates Directory**
```bash
# Ensure templates directory exists in container
mkdir -p /backend/templates
```

---

## 🔒 **Security Considerations**

### **RBAC Enforcement**
- All PDF generation endpoints enforce existing RBAC patterns
- Teachers can only generate reports for students they can access
- Service layer validates permissions before data compilation
- No cross-school access violations possible

### **Data Security**
- No temporary files created on disk (in-memory PDF generation)
- Sensitive data never exposed in error messages
- PDF content filtered through existing data access controls
- Automatic cleanup of any temporary resources

### **Input Validation**
- Report data validated using Pydantic schemas
- Behavioral comments length limits enforced (500 characters)
- Achievement data structure validated before template rendering
- SQL injection prevention through existing ORM patterns

### **Environment Security**
- PDF generation secrets configurable via environment variables
- WeasyPrint configured to block external resource loading
- Container resource limits prevent PDF generation DoS attacks
- Error handling prevents information leakage

---

## ✅ **Validation Gates**

### **Gate 1: Backend API Validation**
```bash
# Must pass: API endpoint accessibility and data validation
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)

# Test PDF generation endpoint with valid data
docker run --rm --env-file .env.development --network $NETWORK_NAME curlimages/curl \
  -X POST -H "Content-Type: application/json" \
  -d '{"selected_achievements":[],"behavioral_comments":"Test report"}' \
  -b "session_id=valid_session_cookie" \
  http://report-card-backend:8000/api/v1/reports/generate/1/3

# Expected: PDF file response with proper headers
# Status: 200 OK
# Content-Type: application/pdf
# Content-Disposition: attachment; filename=...
```

### **Gate 2: PDF Content Validation**
```bash
# Must pass: Generated PDF contains required report sections
# Manual verification of PDF content:
# ✓ Student information header with correct data
# ✓ Grade table with all subjects and scores  
# ✓ Selected achievements section (when provided)
# ✓ Behavioral comments section
# ✓ Professional formatting with school branding
# ✓ Proper A4 page layout and margins
```

### **Gate 3: Frontend Integration Validation**
```bash
# Must pass: Complete user workflow from form to PDF download
# 1. Navigate to report generation page
# 2. Fill behavioral comments (achievements optional)
# 3. Click "Generate Report" button
# 4. Verify loading state appears
# 5. Verify PDF downloads with correct filename
# 6. Verify PDF opens and displays correctly
```

### **Gate 4: RBAC Security Validation**
```bash
# Must pass: Access control properly enforced
# Test 1: Form teacher accessing assigned student → SUCCESS
# Test 2: Form teacher accessing different school student → 403 FORBIDDEN  
# Test 3: Year head accessing any school student → SUCCESS
# Test 4: Unauthenticated request → 401 UNAUTHORIZED
```

### **Gate 5: Error Handling Validation**
```bash
# Must pass: Graceful error handling for edge cases
# Test 1: Invalid student ID → 404 NOT FOUND
# Test 2: Invalid term ID → 404 NOT FOUND  
# Test 3: Missing behavioral comments → 422 VALIDATION ERROR
# Test 4: Network failure → User-friendly error message
```

### **Gate 6: Performance Validation**
```bash
# Must pass: PDF generation performance within acceptable limits
# Test: Generate PDF for typical report
# Expected: Completion within 10 seconds
# Monitor: Memory usage stays within container limits
# Verify: No memory leaks after multiple generations
```

---

## 📊 **Success Metrics & KPIs**

### **Functional Success**
- [ ] Teachers can generate PDF reports from report generation page
- [ ] PDF includes all report components (grades, achievements, comments)
- [ ] Reports are professionally formatted and print-ready
- [ ] Download process works reliably with proper filenames
- [ ] All student types supported (high achievers, consistent performers, etc.)

### **Technical Success**  
- [ ] PDF generation API endpoint responds within 10 seconds
- [ ] RBAC security prevents unauthorized report access
- [ ] Docker container integration works without dependency issues
- [ ] Template rendering handles missing data gracefully
- [ ] Memory usage stays within reasonable limits

### **User Experience Success**
- [ ] Generate Report button provides clear loading feedback
- [ ] PDF download starts automatically after generation
- [ ] Error messages are user-friendly and actionable
- [ ] Generated filename clearly identifies student and term
- [ ] PDF layout is professional and suitable for official use

---

## 🎯 **Definition of Done**

### **Code Implementation Complete**
- [ ] Backend API endpoint created and tested
- [ ] Report service with data compilation logic implemented
- [ ] HTML template created with professional styling
- [ ] Frontend integration updated with PDF download
- [ ] Docker dependencies configured and working

### **Quality Assurance Complete**
- [ ] All validation gates pass successfully
- [ ] RBAC security verified with different user roles
- [ ] PDF content accuracy validated against test data  
- [ ] Performance benchmarks met in container environment
- [ ] Error handling tested for common failure scenarios

### **Integration Complete**
- [ ] Frontend generates PDF when button clicked
- [ ] Backend APIs return properly formatted PDF files
- [ ] Docker containers support PDF generation dependencies
- [ ] Template rendering works with all report data combinations
- [ ] File download process works across different browsers

### **Documentation Complete**
- [ ] API endpoint documented in backend reference
- [ ] PDF generation process added to learnings documentation
- [ ] Error handling scenarios documented
- [ ] Performance characteristics documented
- [ ] Security considerations validated and documented

---

## 🎓 **Risk Assessment & Mitigation**

### **High Risk: WeasyPrint Docker Integration**
**Risk**: WeasyPrint font rendering issues in container environment
**Mitigation**: Use system fonts included in Dockerfile, test rendering early
**Fallback**: Basic HTML download if PDF generation fails

### **Medium Risk: PDF Generation Performance**
**Risk**: Large reports or concurrent requests causing timeouts
**Mitigation**: Implement timeout handling, optimize template complexity
**Fallback**: Asynchronous PDF generation for complex reports

### **Low Risk: Template Data Completeness**
**Risk**: Missing data causing template rendering errors  
**Mitigation**: Comprehensive data validation, default value handling
**Fallback**: Graceful degradation with placeholder content

### **Low Risk: File Download Browser Compatibility**
**Risk**: PDF download issues in certain browsers
**Mitigation**: Use standard download APIs, test across browsers
**Fallback**: Display PDF in browser tab if download fails

---

## 📚 **Key Resources & References**

### **Technical Documentation**
- [WeasyPrint Documentation](https://weasyprint.readthedocs.io/) - Official PDF generation library docs
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/) - Template engine reference
- [FastAPI File Responses](https://fastapi.tiangolo.com/advanced/custom-response/) - File download patterns

### **Implementation Guides**
- [WeasyPrint + FastAPI Integration](https://dev.to/bowmanjd/python-pdf-generation-from-html-with-weasyprint-538h)
- [Professional PDFs with WeasyPrint](https://joshkaramuth.com/blog/generate-good-looking-pdfs-weasyprint-jinja2/)
- [Docker Font Handling](https://stackoverflow.com/questions/68832433/fonts-in-pdf-exported-using-weasyprint-inside-docker-fastapi)

### **Existing Codebase Patterns**
- `/backend/src/app/api/v1/endpoints/grades.py` - API endpoint patterns
- `/backend/src/app/services/achievement_service.py` - Service layer patterns  
- `/backend/src/app/schemas/grade_schemas.py` - Pydantic schema patterns
- `/frontend/src/components/reports/ReportForm.tsx` - Frontend integration point

---

**PRP Confidence Score: 9/10**

This PRP provides comprehensive implementation guidance with:
- ✅ Complete technical architecture based on proven patterns
- ✅ Detailed task breakdown with specific code examples
- ✅ Thorough validation gates covering functionality, security, and performance
- ✅ Risk assessment with mitigation strategies
- ✅ Integration with existing codebase patterns and APIs
- ✅ Docker-first approach following established project patterns
- ✅ Professional PDF template suitable for Singapore education standards

**Expected one-pass implementation success rate: 90%+**