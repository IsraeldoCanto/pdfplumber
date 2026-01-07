"""PDFPlumber API - REST API for PDF text and table extraction"""
import io
import base64
from typing import Optional, List, Any

import httpx
import pdfplumber
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="PDFPlumber API",
    description="API REST para extração de texto e tabelas de PDFs",
    version="1.0.0"
)

# CORS para permitir chamadas do n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PDFInput(BaseModel):
    """Input model for PDF processing"""
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None


class TextResponse(BaseModel):
    """Response model for text extraction"""
    success: bool
    text: str
    pages: int
    chars_count: int


class TableResponse(BaseModel):
    """Response model for table extraction"""
    success: bool
    tables: List[List[List[Any]]]
    tables_count: int
    pages: int


class FullResponse(BaseModel):
    """Response model for full extraction"""
    success: bool
    text: str
    tables: List[List[List[Any]]]
    metadata: dict
    pages: int


async def get_pdf_bytes(pdf_input: PDFInput = None, file: UploadFile = None) -> bytes:
    """Get PDF bytes from URL, base64, or uploaded file"""
    if file:
        return await file.read()
    
    if pdf_input:
        if pdf_input.pdf_url:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(pdf_input.pdf_url)
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to download PDF: {response.status_code}")
                return response.content
        
        if pdf_input.pdf_base64:
            try:
                return base64.b64decode(pdf_input.pdf_base64)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64: {str(e)}")
    
    raise HTTPException(status_code=400, detail="Provide pdf_url, pdf_base64, or upload a file")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "PDFPlumber API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health",
            "POST /extract-text",
            "POST /extract-tables",
            "POST /extract-all",
            "POST /upload-extract-text",
            "POST /upload-extract-tables",
            "POST /upload-extract-all"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "pdfplumber-api"}


@app.post("/extract-text", response_model=TextResponse)
async def extract_text(pdf_input: PDFInput):
    """Extract text from PDF via URL or base64"""
    try:
        pdf_bytes = await get_pdf_bytes(pdf_input=pdf_input)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                all_text += page_text + "\n"
            
            return TextResponse(
                success=True,
                text=all_text.strip(),
                pages=len(pdf.pages),
                chars_count=len(all_text.strip())
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/extract-tables", response_model=TableResponse)
async def extract_tables(pdf_input: PDFInput):
    """Extract tables from PDF via URL or base64"""
    try:
        pdf_bytes = await get_pdf_bytes(pdf_input=pdf_input)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables() or []
                all_tables.extend(tables)
            
            return TableResponse(
                success=True,
                tables=all_tables,
                tables_count=len(all_tables),
                pages=len(pdf.pages)
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/extract-all", response_model=FullResponse)
async def extract_all(pdf_input: PDFInput):
    """Extract text, tables, and metadata from PDF"""
    try:
        pdf_bytes = await get_pdf_bytes(pdf_input=pdf_input)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = ""
            all_tables = []
            
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                all_text += page_text + "\n"
                tables = page.extract_tables() or []
                all_tables.extend(tables)
            
            return FullResponse(
                success=True,
                text=all_text.strip(),
                tables=all_tables,
                metadata=pdf.metadata or {},
                pages=len(pdf.pages)
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/upload-extract-text", response_model=TextResponse)
async def upload_extract_text(file: UploadFile = File(...)):
    """Extract text from uploaded PDF file"""
    try:
        pdf_bytes = await get_pdf_bytes(file=file)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                all_text += page_text + "\n"
            
            return TextResponse(
                success=True,
                text=all_text.strip(),
                pages=len(pdf.pages),
                chars_count=len(all_text.strip())
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/upload-extract-tables", response_model=TableResponse)
async def upload_extract_tables(file: UploadFile = File(...)):
    """Extract tables from uploaded PDF file"""
    try:
        pdf_bytes = await get_pdf_bytes(file=file)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_tables = []
            for page in pdf.pages:
                tables = page.extract_tables() or []
                all_tables.extend(tables)
            
            return TableResponse(
                success=True,
                tables=all_tables,
                tables_count=len(all_tables),
                pages=len(pdf.pages)
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/upload-extract-all", response_model=FullResponse)
async def upload_extract_all(file: UploadFile = File(...)):
    """Extract text, tables, and metadata from uploaded PDF file"""
    try:
        pdf_bytes = await get_pdf_bytes(file=file)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            all_text = ""
            all_tables = []
            
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                all_text += page_text + "\n"
                tables = page.extract_tables() or []
                all_tables.extend(tables)
            
            return FullResponse(
                success=True,
                text=all_text.strip(),
                tables=all_tables,
                metadata=pdf.metadata or {},
                pages=len(pdf.pages)
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
