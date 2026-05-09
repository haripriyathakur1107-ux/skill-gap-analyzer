from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import PyPDF2
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import spacy
import re
import json as _json
import os

# ─────────────────────────────────────────────────────────────
# NLP SETUP
# ─────────────────────────────────────────────────────────────
try:
    nlp = spacy.load("en_core_web_sm")
    NLP_ENABLED = True
except Exception:
    NLP_ENABLED = False
    print("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")

# ─────────────────────────────────────────────────────────────
# SKILL SYNONYMS (short forms → canonical names)
# ─────────────────────────────────────────────────────────────
SKILL_SYNONYMS = {
    "ml": "machine learning", "ai": "machine learning", "dl": "deep learning",
    "py": "python", "js": "javascript", "ts": "typescript",
    "c plus plus": "c++", "cpp": "c++", "c sharp": "c#", "golang": "go",
    "data science": "python", "data analysis": "data visualization",
    "powerbi": "power bi", "tableau": "data visualization",
    "statstics": "statistics", "stat": "statistics",
    "amazon web services": "aws", "google cloud": "gcp", "microsoft azure": "azure",
    "ci cd": "ci/cd", "cicd": "ci/cd", "docker container": "docker",
    "k8s": "kubernetes", "kube": "kubernetes",
    "infra as code": "infrastructure as code", "iac": "infrastructure as code",
    "reactjs": "react", "react js": "react",
    "nodejs": "nodejs", "node js": "nodejs", "node": "nodejs",
    "html css": "html", "html and css": "css",
    "flask framework": "flask", "django framework": "django",
    "mysql": "sql", "postgresql": "sql", "postgres": "sql",
    "mongodb": "nosql", "relational database": "sql", "database": "sql", "rdbms": "sql",
    "cyber security": "cybersecurity", "pen testing": "penetration testing",
    "pentest": "penetration testing", "ethical hack": "ethical hacking",
    "team work": "teamwork", "team player": "teamwork",
    "leadership skill": "leadership", "critical think": "critical thinking",
    "problem solve": "problem solving",
    "attention to details": "attention to detail",
    "natural language processing": "nlp",
    "tensorflow": "tensorflow", "tf": "tensorflow",
    "pytorch": "pytorch", "torch": "pytorch",
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn",
    "android": "java", "ios": "swift",
    "flutter dev": "flutter", "react native dev": "react native",
    "qa": "manual testing", "quality assurance": "manual testing",
    "selenium testing": "selenium", "unit test": "unit testing",
    "scrum": "agile methodology", "agile": "agile methodology",
    "kanban": "agile methodology", "jira tool": "jira",
    "smart contract": "smart contracts", "solidity lang": "solidity", "web3": "web3.js",
    "unity engine": "unity", "unreal": "unreal engine", "game design": "game design",
    # Teaching synonyms
"lesson planning":        "curriculum development",
"classroom management":   "student management",
"algebra":                "linear algebra",
"maths":                  "mathematics",
"math":                   "mathematics",
"ms excel":               "microsoft excel",
"excel":                  "microsoft excel",
}

# ─────────────────────────────────────────────────────────────
# LEARNING RESOURCES
# ─────────────────────────────────────────────────────────────
LEARNING_RESOURCES = {
    "python": {"resource": "Python.org Official Tutorial + Automate the Boring Stuff", "link": "https://docs.python.org/3/tutorial/", "duration": "4-6 weeks", "level": "Beginner"},
    "machine learning": {"resource": "Andrew Ng ML Course – Coursera", "link": "https://www.coursera.org/learn/machine-learning", "duration": "8-10 weeks", "level": "Intermediate"},
    "deep learning": {"resource": "Deep Learning Specialization – Coursera", "link": "https://www.coursera.org/specializations/deep-learning", "duration": "10-12 weeks", "level": "Advanced"},
    "sql": {"resource": "SQLZoo + Mode Analytics SQL Tutorial", "link": "https://sqlzoo.net/", "duration": "2-3 weeks", "level": "Beginner"},
    "statistics": {"resource": "Khan Academy Statistics + StatQuest YouTube", "link": "https://www.khanacademy.org/math/statistics-probability", "duration": "4-6 weeks", "level": "Beginner"},
    "html": {"resource": "freeCodeCamp Responsive Web Design", "link": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "duration": "2-3 weeks", "level": "Beginner"},
    "css": {"resource": "CSS Tricks + freeCodeCamp", "link": "https://css-tricks.com/", "duration": "2-3 weeks", "level": "Beginner"},
    "javascript": {"resource": "JavaScript.info – Modern JS Tutorial", "link": "https://javascript.info/", "duration": "6-8 weeks", "level": "Beginner"},
    "react": {"resource": "Official React Docs + Scrimba React Course", "link": "https://react.dev/learn", "duration": "4-6 weeks", "level": "Intermediate"},
    "docker": {"resource": "Docker Official Get Started + TechWorld with Nana YouTube", "link": "https://docs.docker.com/get-started/", "duration": "2-3 weeks", "level": "Intermediate"},
    "kubernetes": {"resource": "Kubernetes Official Tutorial + KodeKloud", "link": "https://kubernetes.io/docs/tutorials/", "duration": "4-6 weeks", "level": "Advanced"},
    "aws": {"resource": "AWS Cloud Practitioner Essentials", "link": "https://explore.skillbuilder.aws/learn", "duration": "4-6 weeks", "level": "Intermediate"},
    "git": {"resource": "Pro Git Book (free) + GitHub Learning Lab", "link": "https://git-scm.com/book", "duration": "1-2 weeks", "level": "Beginner"},
    "tensorflow": {"resource": "TensorFlow Official Tutorials", "link": "https://www.tensorflow.org/tutorials", "duration": "6-8 weeks", "level": "Advanced"},
    "pytorch": {"resource": "PyTorch Tutorials – Official", "link": "https://pytorch.org/tutorials/", "duration": "6-8 weeks", "level": "Advanced"},
    "nlp": {"resource": "Hugging Face NLP Course (free)", "link": "https://huggingface.co/learn/nlp-course/", "duration": "6-8 weeks", "level": "Advanced"},
    "pandas": {"resource": "Pandas Official Docs + Kaggle Pandas Course", "link": "https://pandas.pydata.org/docs/", "duration": "2-3 weeks", "level": "Beginner"},
    "numpy": {"resource": "NumPy Official Quickstart + W3Schools", "link": "https://numpy.org/doc/stable/user/quickstart.html", "duration": "1-2 weeks", "level": "Beginner"},
    "linux": {"resource": "Linux Command Line Book by William Shotts (free)", "link": "https://linuxcommand.org/tlcl.php", "duration": "3-4 weeks", "level": "Beginner"},
    "network security": {"resource": "CompTIA Security+ Study Guide + TryHackMe", "link": "https://tryhackme.com/", "duration": "8-10 weeks", "level": "Intermediate"},
    "ethical hacking": {"resource": "Ethical Hacking Course – TCM Security / TryHackMe", "link": "https://tryhackme.com/", "duration": "8-10 weeks", "level": "Advanced"},
    "flutter": {"resource": "Flutter Official Docs + The Complete Flutter Guide Udemy", "link": "https://docs.flutter.dev/get-started/codelab", "duration": "6-8 weeks", "level": "Intermediate"},
    "kotlin": {"resource": "Kotlin Official Docs + Android Developer Codelabs", "link": "https://kotlinlang.org/docs/getting-started.html", "duration": "4-6 weeks", "level": "Intermediate"},
    "swift": {"resource": "Swift Playgrounds + Apple Developer Tutorials", "link": "https://developer.apple.com/tutorials/swiftui", "duration": "4-6 weeks", "level": "Intermediate"},
    "figma": {"resource": "Figma Official Learn Hub", "link": "https://www.figma.com/resources/learn-design/", "duration": "2-3 weeks", "level": "Beginner"},
    "agile": {"resource": "Agile Manifesto + Scrum.org Learning Paths", "link": "https://www.scrum.org/resources/what-is-scrum", "duration": "1-2 weeks", "level": "Beginner"},
    "selenium": {"resource": "Selenium Official Docs + Test Automation University", "link": "https://www.selenium.dev/documentation/", "duration": "3-4 weeks", "level": "Intermediate"},
    "data visualization": {"resource": "Tableau Public + Storytelling with Data Book", "link": "https://public.tableau.com/", "duration": "2-3 weeks", "level": "Beginner"},
    "solidity": {"resource": "CryptoZombies + Ethereum Solidity Docs", "link": "https://cryptozombies.io/", "duration": "6-8 weeks", "level": "Advanced"},
    "nodejs": {"resource": "Node.js Official Docs + The Odin Project", "link": "https://nodejs.org/en/learn", "duration": "4-6 weeks", "level": "Intermediate"},
    "typescript": {"resource": "TypeScript Official Handbook", "link": "https://www.typescriptlang.org/docs/handbook/", "duration": "2-3 weeks", "level": "Intermediate"},
    "rest api": {"resource": "REST API Tutorial + Postman Learning Center", "link": "https://www.postman.com/api-platform/api-design/", "duration": "1-2 weeks", "level": "Beginner"},
    "django": {"resource": "Django Official Tutorial + MDN Django Guide", "link": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "duration": "4-6 weeks", "level": "Intermediate"},
    "power bi": {"resource": "Microsoft Power BI Learning Path", "link": "https://learn.microsoft.com/en-us/training/powerbi/", "duration": "3-4 weeks", "level": "Beginner"},
    "tableau": {"resource": "Tableau eLearning + Tableau Public", "link": "https://www.tableau.com/learn/training", "duration": "3-4 weeks", "level": "Beginner"},
    "communication": {"resource": "Coursera: Communication Skills for Engineers", "link": "https://www.coursera.org/learn/communication-skills-engineers", "duration": "2-3 weeks", "level": "Beginner"},
    "problem solving": {"resource": "LeetCode + HackerRank + Brilliant.org", "link": "https://leetcode.com/", "duration": "Ongoing", "level": "Beginner"},
    "critical thinking": {"resource": "edX: Critical Thinking & Problem Solving", "link": "https://www.edx.org/learn/critical-thinking-skills", "duration": "3-4 weeks", "level": "Beginner"},
    "leadership": {"resource": "Coursera: Everyday Leadership – Duke University", "link": "https://www.coursera.org/learn/everyday-leadership-new", "duration": "3-4 weeks", "level": "Intermediate"},
    "teamwork": {"resource": "Coursera: Inspiring and Motivating Individuals", "link": "https://www.coursera.org/learn/motivate-people-teams", "duration": "2-3 weeks", "level": "Beginner"},
    "time management": {"resource": "Getting Things Done (GTD) Book + Coursera Work Smarter", "link": "https://www.coursera.org/learn/work-smarter-not-harder", "duration": "1-2 weeks", "level": "Beginner"},
    "creativity": {"resource": "IDEO Design Thinking + Coursera Creative Thinking", "link": "https://www.coursera.org/learn/creative-thinking-techniques", "duration": "2-3 weeks", "level": "Beginner"},
    "adaptability": {"resource": "LinkedIn Learning: Developing Adaptability", "link": "https://www.linkedin.com/learning/developing-adaptability-as-a-manager", "duration": "1-2 weeks", "level": "Beginner"},
    "empathy": {"resource": "Coursera: Emotional Intelligence Cultivation", "link": "https://www.coursera.org/learn/emotional-intelligence-cultivating-immensely-human-interactions", "duration": "2-3 weeks", "level": "Beginner"},
    "attention to detail": {"resource": "MindTools: Improving Attention to Detail", "link": "https://www.mindtools.com/pages/article/attention-to-detail.htm", "duration": "1-2 weeks", "level": "Beginner"},
    "analytical thinking": {"resource": "edX: Data Analysis for Life Sciences", "link": "https://www.edx.org/learn/data-analysis", "duration": "3-4 weeks", "level": "Beginner"},
    "collaboration": {"resource": "Coursera: Collaboration Skills for the Workplace", "link": "https://www.coursera.org/learn/communication-collaboration", "duration": "2-3 weeks", "level": "Beginner"},
    "negotiation": {"resource": "Coursera: Successful Negotiation – University of Michigan", "link": "https://www.coursera.org/learn/negotiation-skills", "duration": "3-4 weeks", "level": "Intermediate"},
    "decision making": {"resource": "Coursera: Decision-Making & Scenarios", "link": "https://www.coursera.org/learn/decision-making", "duration": "2-3 weeks", "level": "Intermediate"},
    "agile methodology": {"resource": "Agile Alliance Resources + Scrum.org", "link": "https://www.agilealliance.org/agile101/", "duration": "1-2 weeks", "level": "Beginner"},
    "jira": {"resource": "Atlassian Jira Tutorials", "link": "https://www.atlassian.com/software/jira/guides", "duration": "1 week", "level": "Beginner"},
    "excel": {"resource": "ExcelJet + Microsoft Excel Training", "link": "https://exceljet.net/", "duration": "2-3 weeks", "level": "Beginner"},
    "documentation": {"resource": "Write the Docs Community Resources", "link": "https://www.writethedocs.org/guide/", "duration": "1-2 weeks", "level": "Beginner"},
    "user research": {"resource": "Nielsen Norman Group UX Research Training", "link": "https://www.nngroup.com/training/", "duration": "2-3 weeks", "level": "Intermediate"},
}

def get_resource(skill):
    sl = skill.lower()
    if sl in LEARNING_RESOURCES:
        return LEARNING_RESOURCES[sl]
    return {
        "resource": f"Search '{skill}' on Coursera or YouTube",
        "link": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}",
        "duration": "Varies", "level": "Varies"
    }

# ─────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────
from PyPDF2 import PdfReader

app = Flask(__name__)
app.config.from_object(Config)
import os
print("FLASK CONFIG:", app.config.get('MYSQL_HOST'), app.config.get('MYSQL_PORT'), app.config.get('MYSQL_DB'))
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'railway')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
mysql = MySQL(app)

# In-process cache: role_key → {"technical": [...], "soft": [...]}
_SKILLS_CACHE = {}

# ─────────────────────────────────────────────────────────────
# DB HELPERS — job roles
# ─────────────────────────────────────────────────────────────
def db_get_job_skills(role_key: str) -> dict | None:
    """Fetch skills for a role from the DB. Returns None if not found."""
    if role_key in _SKILLS_CACHE:
        return _SKILLS_CACHE[role_key]
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM job_roles WHERE role_key = %s", (role_key,))
        row = cur.fetchone()
        if not row:
            cur.close()
            return None
        role_id = row[0]
        cur.execute(
            "SELECT skill_name, skill_type FROM job_role_skills WHERE job_role_id = %s ORDER BY skill_order",
            (role_id,)
        )
        rows = cur.fetchall()
        cur.close()
        data = {
            "technical": [r[0] for r in rows if r[1] == "technical"],
            "soft":      [r[0] for r in rows if r[1] == "soft"],
        }
        _SKILLS_CACHE[role_key] = data
        return data
    except Exception as e:
        print("db_get_job_skills error:", e)
        return None


def db_save_job_skills(role_key: str, display_name: str, skills: dict, is_ai: bool = True):
    """Save a newly AI-generated role and its skills to the DB."""
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT IGNORE INTO job_roles (role_key, display_name, is_ai_generated) VALUES (%s, %s, %s)",
            (role_key, display_name, 1 if is_ai else 0)
        )
        if cur.rowcount == 0:
            cur.close()
            return  # Already exists (race condition)
        role_id = cur.lastrowid
        for i, skill in enumerate(skills.get("technical", [])):
            cur.execute(
                "INSERT INTO job_role_skills (job_role_id,skill_name,skill_type,skill_order) VALUES(%s,%s,'technical',%s)",
                (role_id, skill.lower().strip(), i)
            )
        for i, skill in enumerate(skills.get("soft", [])):
            cur.execute(
                "INSERT INTO job_role_skills (job_role_id,skill_name,skill_type,skill_order) VALUES(%s,%s,'soft',%s)",
                (role_id, skill.lower().strip(), i)
            )
        mysql.connection.commit()
        cur.close()
        _SKILLS_CACHE[role_key] = skills
        print(f"Saved AI-generated role to DB: {role_key}")
    except Exception as e:
        print("db_save_job_skills error:", e)


def get_job_skills(role_key: str) -> dict | None:
    """
    Primary skill lookup:
      1. Try in-process cache
      2. Try database
      3. Generate with AI → save to DB → return
    Returns None only if AI also fails.
    """
    role_key = role_key.strip().lower()
    if not role_key:
        return None

    # 1 & 2: cache + DB
    data = db_get_job_skills(role_key)
    if data:
        return data

    # 3: AI generation
    print(f"Role '{role_key}' not in DB — generating with AI...")
    try:
        from ai_skills import generate_job_skills
        skills = generate_job_skills(role_key)
        display = role_key.title()
        db_save_job_skills(role_key, display, skills, is_ai=True)
        return skills
    except Exception as e:
        print(f"AI generation failed for '{role_key}':", e)
        raise  # re-raise so the route can show the real error message


def get_all_job_roles() -> list[dict]:
    """Return all job roles from DB sorted by display_name."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT role_key, display_name, is_ai_generated FROM job_roles ORDER BY display_name")
        rows = cur.fetchall()
        cur.close()
        return [{"key": r[0], "name": r[1], "ai": bool(r[2])} for r in rows]
    except Exception as e:
        print("get_all_job_roles error:", e)
        return []

# ─────────────────────────────────────────────────────────────
# NLP FUNCTIONS
# ─────────────────────────────────────────────────────────────
def normalize_skill(skill):
    skill = skill.lower().strip()
    return SKILL_SYNONYMS.get(skill, skill)

def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + " "
        return text.lower()
    except Exception as e:
        print("PDF ERROR:", e)
        return ""

def extract_skills_from_resume(resume_text, required_skills):
    found = []
    rl = resume_text.lower()
    for skill in required_skills:
        sl = skill.lower()
        if sl in rl:
            found.append(skill)
            continue
        for synonym, canonical in SKILL_SYNONYMS.items():
            if canonical == sl:
                pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(pattern, rl):
                    found.append(skill)
                    break
    return list(set(found))

def process_user_skills(raw):
    skills = []
    for s in raw.split(","):
        s = s.strip().lower()
        if s:
            norm = normalize_skill(s)
            skills.append(norm)
            if norm != s:
                skills.append(s)
    return list(set(skills))

def smart_match(user_skills, required_skill, threshold=0.85):
    rl = required_skill.lower()
    if rl in user_skills:
        return True
    nr = normalize_skill(rl)
    if nr in user_skills:
        return True
    for us in user_skills:
        if normalize_skill(us) == rl or normalize_skill(us) == nr:
            return True
    return False

# ─────────────────────────────────────────────────────────────
# ROUTES — AUTH
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, username))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[4], password):
            session['user_id']   = user[0]
            session['username']  = user[3]
            session['full_name'] = user[1]
            flash(f"Welcome back, {user[1]}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip()
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '').strip()
        confirm   = request.form.get('confirm_password', '').strip()
        role      = request.form.get('role', 'student')
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template('register.html')
        hashed = generate_password_hash(password)
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO users (full_name,email,username,password,role) VALUES (%s,%s,%s,%s,%s)",
                (full_name, email, username, hashed, role)
            )
            mysql.connection.commit()
            cur.close()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('login'))
        except Exception:
            flash("Username or Email already exists.", "error")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# ─────────────────────────────────────────────────────────────
# ROUTES — DASHBOARD
# ─────────────────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    progress_summary = []
    total_completed  = 0
    is_returning     = False

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT job_role, completed_skills, last_updated
            FROM user_progress WHERE user_id=%s ORDER BY last_updated DESC LIMIT 3
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()

        if rows:
            is_returning = True
            for row in rows:
                job           = row[0]
                completed_list = _json.loads(row[1])
                job_data       = get_job_skills(job)
                if not job_data:
                    continue
                total_skills = len(job_data['technical']) + len(job_data['soft'])
                completed    = len(completed_list)
                total_completed += completed
                percent = int((completed / total_skills) * 100) if total_skills > 0 else 0
                progress_summary.append({
                    'job': job, 'job_title': job.title(),
                    'completed': completed, 'total': total_skills, 'percent': percent
                })
    except Exception as e:
        print("Dashboard error:", e)

    return render_template('dashboard.html',
                           is_returning=is_returning,
                           progress_summary=progress_summary,
                           total_completed=total_completed)

# ─────────────────────────────────────────────────────────────
# ROUTES — SKILL GAP  (now accepts ANY job role via AI)
# ─────────────────────────────────────────────────────────────
@app.route("/skill_gap", methods=["GET", "POST"])
def skill_gap():
    matched_skills       = []
    missing_skills       = []
    soft_skills_matched  = []
    soft_skills_missing  = []
    learning_paths       = []
    selected_job         = request.args.get("job", "")
    progress_percent     = 0
    ai_generated         = False
    error_msg            = None

    # All roles for the dropdown (from DB)
    all_roles = get_all_job_roles()

    def _build_results(job_key, user_skills=None):
        nonlocal matched_skills, missing_skills, soft_skills_matched
        nonlocal soft_skills_missing, learning_paths, progress_percent
        nonlocal selected_job, ai_generated

        job_data = get_job_skills(job_key)
        if not job_data:
            return False

        # Check if this is an AI-generated role
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT is_ai_generated FROM job_roles WHERE role_key=%s", (job_key,))
            r = cur.fetchone()
            cur.close()
            if r:
                ai_generated = bool(r[0])
        except Exception:
            pass

        for skill in job_data["technical"]:
            if user_skills and smart_match(user_skills, skill):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        for skill in job_data["soft"]:
            if user_skills and smart_match(user_skills, skill):
                soft_skills_matched.append(skill)
            else:
                soft_skills_missing.append(skill)

        total        = len(job_data["technical"]) + len(job_data["soft"])
        matched_tot  = len(matched_skills) + len(soft_skills_matched)
        progress_percent = int((matched_tot / total) * 100) if total > 0 else 0

        for skill in missing_skills + soft_skills_missing:
            res = get_resource(skill)
            learning_paths.append({
                "skill":    skill,
                "resource": res["resource"],
                "link":     res["link"],
                "duration": res["duration"],
                "level":    res["level"],
                "is_soft":  skill in soft_skills_missing,
            })
        return True

    if request.method == "GET" and selected_job:
        try:
            ok = _build_results(selected_job.strip().lower())
            if not ok:
                error_msg = f"Could not load skills for '{selected_job}'. Please try again."
        except Exception as e:
            error_msg = f"Could not load skills for '{selected_job}': {e}"

    if request.method == "POST":
        job = request.form.get("job", "").strip().lower()

        # Validate and sanitise the job input
        job = re.sub(r'[^a-z0-9 /\-]', '', job)[:100].strip()
        selected_job = job

        if not job:
            error_msg = "Please enter or select a job role."
        else:
            user_skills = []
            manual = request.form.get("skills", "").strip().lower()
            if manual:
                user_skills.extend(process_user_skills(manual))

            resume = request.files.get("resume")
            if resume and resume.filename:
                resume_text = extract_text_from_pdf(resume)
                if resume_text and len(resume_text.strip()) > 10:
                    # We need all skills to scan the resume against
                    temp_data = get_job_skills(job)
                    if temp_data:
                        all_req = temp_data["technical"] + temp_data["soft"]
                        found   = extract_skills_from_resume(resume_text, all_req)
                        user_skills.extend(found)

            user_skills = list(set(user_skills))
            try:
                ok = _build_results(job, user_skills if user_skills else None)
                if not ok:
                    error_msg = (
                        f"Could not generate skills for '{job}'. "
                        "Please check your GROQ_API_KEY (get one free at console.groq.com) "
                        "or try a more specific job title."
                    )
            except Exception as e:
                error_msg = f"Could not generate skills for '{job}': {e}"

    return render_template(
        "skill_gap.html",
        matched_skills      = matched_skills,
        missing_skills      = missing_skills,
        soft_skills_matched = soft_skills_matched,
        soft_skills_missing = soft_skills_missing,
        learning_paths      = learning_paths,
        all_roles           = all_roles,
        selected_job        = selected_job,
        progress_percent    = progress_percent,
        ai_generated        = ai_generated,
        error_msg           = error_msg,
    )

# ─────────────────────────────────────────────────────────────
# API — Generate skills for a role (AJAX, used by the UI)
# ─────────────────────────────────────────────────────────────
@app.route("/api/generate_role", methods=["POST"])
def api_generate_role():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data     = request.get_json()
    job_role = (data.get("job_role", "") or "").strip().lower()
    job_role = re.sub(r'[^a-z0-9 /\-]', '', job_role)[:100].strip()

    if not job_role:
        return jsonify({"status": "error", "message": "No job role provided"}), 400

    skills = get_job_skills(job_role)
    if not skills:
        return jsonify({"status": "error", "message": f"Could not generate skills for '{job_role}'"}), 500

    # Check if freshly AI-generated
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT is_ai_generated FROM job_roles WHERE role_key=%s", (job_role,))
        r = cur.fetchone()
        cur.close()
        is_ai = bool(r[0]) if r else False
    except Exception:
        is_ai = False

    return jsonify({
        "status":       "ok",
        "job_role":     job_role,
        "display_name": job_role.title(),
        "is_ai":        is_ai,
        "technical":    skills["technical"],
        "soft":         skills["soft"],
    })

# ─────────────────────────────────────────────────────────────
# ROUTES — PROGRESS
# ─────────────────────────────────────────────────────────────
@app.route("/save_progress", methods=["POST"])
def save_progress():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    data      = request.get_json()
    job       = data.get('job', '').strip()
    completed = data.get('completed', [])
    user_id   = session['user_id']

    if not job:
        return jsonify({"status": "error", "message": "No job specified"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO user_progress (user_id, job_role, completed_skills)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                completed_skills = VALUES(completed_skills),
                last_updated     = CURRENT_TIMESTAMP
        """, (user_id, job, _json.dumps(completed)))
        mysql.connection.commit()
        cur.close()
        return jsonify({"status": "ok", "job": job, "completed_count": len(completed)})
    except Exception as e:
        return jsonify({"status": "db_error", "message": str(e)}), 500


@app.route("/load_progress", methods=["GET"])
def load_progress():
    if 'user_id' not in session:
        return jsonify({"completed": []})

    job     = request.args.get('job', '').strip()
    user_id = session['user_id']
    if not job:
        return jsonify({"completed": []})

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT completed_skills FROM user_progress WHERE user_id=%s AND job_role=%s",
            (user_id, job)
        )
        row = cur.fetchone()
        cur.close()
        if row:
            return jsonify({"completed": _json.loads(row[0])})
        return jsonify({"completed": []})
    except Exception as e:
        print("load_progress error:", e)
        return jsonify({"completed": []})


@app.route("/my_progress")
def my_progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id      = session['user_id']
    progress_data = {}
    total_completed = 0
    best_job     = "—"
    best_pct     = 0

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT job_role, completed_skills, last_updated
            FROM user_progress WHERE user_id=%s ORDER BY last_updated DESC
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()

        for row in rows:
            job = row[0].lower().strip()
            try:
                completed_list = _json.loads(row[1]) if row[1] else []
            except Exception:
                completed_list = []
            if not completed_list:
                continue

            job_data = get_job_skills(job) or {"technical": [], "soft": []}
            total_skills = len(job_data["technical"]) + len(job_data["soft"])
            completed    = len(completed_list)
            remaining    = max(0, total_skills - completed)
            percent      = int((completed / total_skills) * 100) if total_skills > 0 else 0
            last_str     = row[2].strftime('%d %b %Y, %I:%M %p') if row[2] else "—"

            progress_data[job] = {
                "completed":      completed,
                "remaining":      remaining,
                "percent":        percent,
                "completed_list": completed_list,
                "last_updated":   last_str,
            }
            total_completed += completed
            if percent > best_pct:
                best_pct = percent
                best_job = job.title()

    except Exception as e:
        print("my_progress error:", e)

    return render_template("my_progress.html",
                           progress_data=progress_data,
                           total_completed=total_completed,
                           best_job=best_job)


@app.route("/job_explorer")
def job_explorer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    all_roles = get_all_job_roles()
    # Build full skills dict for the template
    jobs = {}
    for r in all_roles:
        data = db_get_job_skills(r["key"])
        if data:
            jobs[r["key"]] = {**data, "display": r["name"], "ai": r["ai"]}
    return render_template("job_explorer.html", jobs=jobs)


@app.route("/reset_all_progress", methods=["POST"])
def reset_all_progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM user_progress WHERE user_id=%s", (user_id,))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("reset_all error:", e)
    return redirect(url_for('my_progress'))


@app.route("/clear_progress", methods=["POST"])
def clear_progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    job     = request.form.get('job', '').strip()
    user_id = session['user_id']
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM user_progress WHERE user_id=%s AND job_role=%s", (user_id, job))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("clear_progress error:", e)
    return redirect(url_for('my_progress'))



if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    print("GROQ KEY LOADED:", os.environ.get("GROQ_API_KEY", "NOT FOUND"))
    app.run(debug=True)