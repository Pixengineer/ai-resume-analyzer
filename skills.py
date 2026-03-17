"""
skills.py - Categorized skill database for resume analysis
"""

SKILLS_DB = {
    "Programming Languages": [
        "python", "java", "javascript", "c++", "c#", "c", "r", "go", "golang",
        "rust", "swift", "kotlin", "scala", "ruby", "php", "perl", "matlab",
        "typescript", "dart", "bash", "shell", "powershell", "julia", "haskell",
        "lua", "groovy", "assembly", "fortran", "cobol", "vba", "objective-c"
    ],
    "Web Development": [
        "html", "css", "react", "angular", "vue", "node.js", "nodejs", "express",
        "django", "flask", "fastapi", "spring", "laravel", "rails", "asp.net",
        "next.js", "nuxt", "gatsby", "graphql", "rest", "restful", "api",
        "bootstrap", "tailwind", "sass", "scss", "webpack", "vite", "redux",
        "jquery", "ajax", "websocket", "nginx", "apache", "microservices",
        "svelte", "remix", "astro", "mongodb", "postgresql", "mysql", "sqlite",
        "redis", "elasticsearch", "prisma", "sequelize"
    ],
    "Data Science & ML": [
        "machine learning", "deep learning", "neural network", "tensorflow",
        "pytorch", "keras", "scikit-learn", "sklearn", "pandas", "numpy",
        "matplotlib", "seaborn", "plotly", "tableau", "power bi", "statistics",
        "data analysis", "data visualization", "nlp", "natural language processing",
        "computer vision", "opencv", "transformers", "bert", "gpt", "llm",
        "reinforcement learning", "xgboost", "lightgbm", "catboost", "regression",
        "classification", "clustering", "pca", "hadoop", "spark", "airflow",
        "dbt", "mlflow", "hugging face", "langchain", "rag", "fine-tuning",
        "feature engineering", "model deployment", "a/b testing"
    ],
    "Core CS & DevOps": [
        "data structures", "algorithms", "oop", "object oriented", "design patterns",
        "system design", "distributed systems", "operating systems", "networking",
        "docker", "kubernetes", "aws", "azure", "gcp", "google cloud",
        "ci/cd", "git", "github", "gitlab", "jenkins", "terraform", "ansible",
        "linux", "unix", "agile", "scrum", "devops", "cloud computing",
        "microservices", "serverless", "lambda", "kafka", "rabbitmq",
        "cybersecurity", "sql", "nosql", "database design", "software testing",
        "unit testing", "integration testing", "tdd", "bdd", "jira", "confluence"
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving", "critical thinking",
        "project management", "collaboration", "analytical", "presentation",
        "mentoring", "time management", "adaptability", "creativity"
    ]
}

# Important high-value keywords that boost ATS score
HIGH_VALUE_KEYWORDS = [
    "experience", "developed", "implemented", "designed", "built", "created",
    "managed", "led", "optimized", "improved", "deployed", "architected",
    "bachelor", "master", "phd", "degree", "university", "certification",
    "project", "team", "agile", "scrum", "production", "scalable",
    "performance", "results", "impact", "achievement", "award"
]

# Resume section keywords for section detection
SECTION_KEYWORDS = {
    "experience": ["experience", "work history", "employment", "professional background", "career"],
    "education": ["education", "academic", "university", "college", "degree", "bachelor", "master", "phd"],
    "skills": ["skills", "technical skills", "competencies", "expertise", "proficiencies"],
    "projects": ["projects", "portfolio", "personal projects", "side projects", "open source"],
    "certifications": ["certification", "certificate", "certified", "credential", "license"],
    "summary": ["summary", "objective", "profile", "about me", "professional summary"]
}
