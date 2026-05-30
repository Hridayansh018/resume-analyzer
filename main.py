from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pypdf import PdfReader
from fastapi.staticfiles import StaticFiles
import os, io
from client import client
from schema import ReviewResponse, ATSResponse, InterviewQuestionsResponse, CoverLetterResponse
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

AI_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"

cors_origins = os.getenv("CORS_ALLOW_ORIGINS")
if cors_origins:
    if cors_origins.strip() == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
else:
    allow_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_resume(contents:bytes)->str:
    reader = PdfReader(io.BytesIO(contents))
    text =  "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    ).strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF"
        )

    return text


def build_review_prompt(
    job_description: str,
    resume_text: str
):
    return f"""
You are a professional resume reviewer.

Analyze the resume against the job description.

Return STRICT JSON:

{{
    "score": 0-100,
    "summary": "",
    "strengths": [],
    "weaknesses": [],
    "missing_skills": [],
    "recommendations": [],
    "matched_skills": [],
    "experience_analysis": "",
    "education_analysis": "",
    "projects_analysis": ""
}}

JOB DESCRIPTION:

{job_description}

RESUME:

{resume_text}
"""

def build_ats_prompt(
    job_description:str,
    resume_text:str
):
    return f"""
You are an ATS system.

Compare the resume with the job description.

Return ONLY JSON:

{{
    "ats_score": 0,
    "keyword_match": 0,
    "missing_keywords": [],
    "suggestions": []
}}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
"""

def build_cover_ltter_prompt(
        company_name:str,
        job_title:str,
        resume_text:str
):
    return f"""
You are an expert career coach.

Generate a professional cover letter.

Return ONLY JSON:

{{
    "cover_letter": ""
}}

Company:
{company_name}

Job Title:
{job_title}

Resume:
{resume_text}
"""

def build_interview_question_prompt(
    job_description:str,
    resume_text:str
):
    return f"""
You are a technical interviewer.

Generate 10 interview questions.

Return ONLY JSON:

{{
    "questions": []
}}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
"""

@app.post("/review",response_model=ReviewResponse)
async def review_resume(
    file:UploadFile = File(...),
    job_description:str = Form(...)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )
    contents = await file.read()
    resume_text = read_resume(contents)
    prompt = build_review_prompt(
        job_description=job_description,
        resume_text = resume_text
    )

    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
            {
            "role":"user",
            "content":prompt
            }
        ],
        response_format={
            "type":"json_object"
        },
        temperature=0.7
    )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Error: {str(e)}"
        )


    try:
        data = json.loads(
            completion.choices[0].message.content
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model returned invalid JSON"
        )

    return ReviewResponse(**data)



@app.post("/ats-score",response_model=ATSResponse)
async def ats_score(
    file:UploadFile = File(...),
    job_description:str = Form(...)
):
    contents = await file.read()
    resume_text = read_resume(contents)
    prompt = build_ats_prompt(job_description, resume_text)

    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
            {
            "role":"user",
            "content":prompt
            }
        ],
        response_format={
            "type":"json_object"
        },
        temperature=0.7
    )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Error: {str(e)}"
        )


    try:
        data = json.loads(
            completion.choices[0].message.content
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model returned invalid JSON"
        )
    return ATSResponse(**data)

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(index_path)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.post("/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(
        file:UploadFile = File(...),
        company_name:str = Form(...),
        job_title:str = Form(...)
):
    contents = await file.read()
    resume_text = read_resume(contents)
    prompt = build_cover_ltter_prompt(
        company_name,
        job_title,
        resume_text
    )
    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
            {
            "role":"user",
            "content":prompt
            }
        ],
        response_format={
            "type":"json_object"
        },
        temperature=0.7
    )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Error: {str(e)}"
        )


    try:
        data = json.loads(
            completion.choices[0].message.content
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model returned invalid JSON"
        )
    
    return CoverLetterResponse(**data)



@app.post("/interview-questions",response_model=InterviewQuestionsResponse)
async def generate_interview_questions(
    file:UploadFile = File(...),
    job_description = Form(...)
):
    content = await file.read()
    resume_text = read_resume(content)
    prompt = build_interview_question_prompt(job_description, resume_text)
    try:
        completion = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
            {
            "role":"user",
            "content":prompt
            }
        ],
        response_format={
            "type":"json_object"
        },
        temperature=0.7
    )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Error: {str(e)}"
        )


    try:
        data = json.loads(
            completion.choices[0].message.content
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Model returned invalid JSON"
        )
    return InterviewQuestionsResponse(**data)