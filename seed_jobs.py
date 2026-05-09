"""
seed_jobs.py — Run ONCE after creating the database schema.
Populates job_roles and job_role_skills from the original hardcoded dict.

Usage:
    python seed_jobs.py
"""

import MySQLdb

# ── DB config ─────────────────────────────────────────────────
DB = dict(host="localhost", user="root", passwd="root", db="skill_gap_analyzer")

# ── Original 24 job roles ─────────────────────────────────────
JOB_SKILLS = {
    "data scientist": {
        "technical": ["python","machine learning","deep learning","sql","statistics","pandas","numpy","matplotlib","data visualization","scikit-learn","feature engineering","model evaluation"],
        "soft": ["critical thinking","communication","problem solving","storytelling with data","collaboration","curiosity","attention to detail"]
    },
    "web developer": {
        "technical": ["html","css","javascript","react","flask","mysql","bootstrap","api integration","git","responsive design","typescript","nodejs"],
        "soft": ["creativity","time management","communication","teamwork","adaptability","attention to detail","problem solving"]
    },
    "software engineer": {
        "technical": ["python","c++","java","data structures","algorithms","oop","git","system design","unit testing","design patterns","rest api","agile"],
        "soft": ["problem solving","teamwork","communication","critical thinking","time management","adaptability","continuous learning"]
    },
    "ai engineer": {
        "technical": ["python","machine learning","deep learning","tensorflow","pytorch","nlp","computer vision","model deployment","mlops","transformers","data pipelines"],
        "soft": ["research mindset","curiosity","problem solving","communication","collaboration","critical thinking","patience"]
    },
    "cloud engineer": {
        "technical": ["aws","azure","gcp","docker","kubernetes","linux","networking","security","terraform","ci/cd","monitoring","iam"],
        "soft": ["problem solving","communication","adaptability","attention to detail","teamwork","time management","documentation"]
    },
    "mobile developer": {
        "technical": ["java","kotlin","swift","flutter","react native","api integration","firebase","ui/ux design","app store deployment","debugging","git"],
        "soft": ["creativity","attention to detail","problem solving","communication","adaptability","user empathy","teamwork"]
    },
    "cybersecurity analyst": {
        "technical": ["network security","ethical hacking","firewalls","linux","incident response","risk management","siem tools","penetration testing","cryptography","vulnerability assessment"],
        "soft": ["analytical thinking","attention to detail","problem solving","communication","ethics","calm under pressure","continuous learning"]
    },
    "devops engineer": {
        "technical": ["ci/cd","docker","kubernetes","aws","monitoring","linux","automation","ansible","jenkins","git","bash scripting","infrastructure as code"],
        "soft": ["collaboration","problem solving","communication","adaptability","attention to detail","time management","ownership mindset"]
    },
    "backend developer": {
        "technical": ["python","flask","mysql","sql","git","rest api","django","postgresql","caching","microservices","authentication","docker"],
        "soft": ["problem solving","communication","teamwork","attention to detail","time management","documentation","analytical thinking"]
    },
    "frontend developer": {
        "technical": ["html","css","javascript","react","typescript","redux","webpack","figma","accessibility","git","unit testing","performance optimization"],
        "soft": ["creativity","attention to detail","communication","user empathy","collaboration","adaptability","time management"]
    },
    "full stack developer": {
        "technical": ["html","css","javascript","react","nodejs","python","sql","rest api","docker","git","cloud basics","authentication"],
        "soft": ["problem solving","versatility","communication","teamwork","time management","adaptability","continuous learning"]
    },
    "data analyst": {
        "technical": ["sql","excel","python","tableau","power bi","statistics","data cleaning","pandas","reporting","data visualization","a/b testing","google analytics"],
        "soft": ["analytical thinking","attention to detail","communication","storytelling","curiosity","problem solving","collaboration"]
    },
    "data engineer": {
        "technical": ["python","sql","spark","hadoop","etl pipelines","kafka","airflow","cloud storage","data modeling","docker","scala","data warehousing"],
        "soft": ["problem solving","attention to detail","teamwork","communication","documentation","analytical thinking","time management"]
    },
    "machine learning engineer": {
        "technical": ["python","machine learning","deep learning","tensorflow","pytorch","scikit-learn","mlops","model deployment","feature engineering","docker","kubernetes","sql"],
        "soft": ["research mindset","problem solving","communication","collaboration","curiosity","critical thinking","patience"]
    },
    "product manager": {
        "technical": ["product roadmapping","agile","user research","wireframing","data analysis","jira","sql basics","a/b testing","market research","kpi tracking"],
        "soft": ["leadership","communication","empathy","decision making","strategic thinking","stakeholder management","prioritization","negotiation"]
    },
    "ui/ux designer": {
        "technical": ["figma","adobe xd","user research","wireframing","prototyping","usability testing","design systems","css basics","accessibility","information architecture"],
        "soft": ["empathy","creativity","communication","attention to detail","collaboration","critical thinking","user advocacy"]
    },
    "blockchain developer": {
        "technical": ["solidity","ethereum","smart contracts","web3.js","nft development","defi protocols","cryptography","javascript","python","hardhat","truffle"],
        "soft": ["innovation mindset","problem solving","continuous learning","attention to detail","analytical thinking","communication","adaptability"]
    },
    "game developer": {
        "technical": ["c#","unity","unreal engine","c++","game design","physics simulation","3d modeling basics","version control","debugging","performance optimization"],
        "soft": ["creativity","attention to detail","problem solving","teamwork","passion","resilience","communication"]
    },
    "embedded systems engineer": {
        "technical": ["c","c++","microcontrollers","rtos","hardware interfaces","debugging","pcb design basics","assembly language","iot protocols","linux"],
        "soft": ["analytical thinking","attention to detail","problem solving","patience","communication","documentation","adaptability"]
    },
    "network engineer": {
        "technical": ["cisco routing","switching","bgp","ospf","firewalls","vpn","network monitoring","linux","tcp/ip","sdwan","network security"],
        "soft": ["problem solving","communication","attention to detail","analytical thinking","calm under pressure","teamwork","documentation"]
    },
    "database administrator": {
        "technical": ["sql","mysql","postgresql","oracle","database design","performance tuning","backup and recovery","replication","indexing","mongodb","cloud databases"],
        "soft": ["attention to detail","problem solving","communication","analytical thinking","time management","documentation","reliability"]
    },
    "scrum master": {
        "technical": ["agile methodology","scrum framework","jira","sprint planning","kanban","retrospectives","backlog grooming","risk management","reporting"],
        "soft": ["facilitation","leadership","communication","conflict resolution","empathy","patience","servant leadership","motivating others"]
    },
    "quality assurance engineer": {
        "technical": ["manual testing","automation testing","selenium","pytest","api testing","performance testing","bug tracking","test case writing","postman","jenkins"],
        "soft": ["attention to detail","analytical thinking","communication","perseverance","collaboration","critical thinking","documentation"]
    },
    "it support specialist": {
        "technical": ["windows","linux","networking","active directory","troubleshooting","hardware knowledge","cloud basics","ticketing systems","cybersecurity basics"],
        "soft": ["communication","patience","problem solving","empathy","teamwork","time management","calm under pressure","customer service"]
    },
    "business analyst": {
        "technical": ["requirements gathering","uml diagrams","sql basics","excel","data analysis","process modeling","jira","wireframing","stakeholder interviews","reporting"],
        "soft": ["communication","analytical thinking","problem solving","negotiation","collaboration","critical thinking","documentation","presentation skills"]
    },
}

def seed():
    conn = MySQLdb.connect(**DB)
    cur  = conn.cursor()

    inserted_roles = 0
    inserted_skills = 0

    for role_key, data in JOB_SKILLS.items():
        display = role_key.title()
        try:
            cur.execute(
                "INSERT IGNORE INTO job_roles (role_key, display_name, is_ai_generated) VALUES (%s, %s, 0)",
                (role_key, display)
            )
            if cur.rowcount == 0:
                print(f"  SKIP (already exists): {role_key}")
                continue

            role_id = cur.lastrowid
            inserted_roles += 1

            for i, skill in enumerate(data.get("technical", [])):
                cur.execute(
                    "INSERT INTO job_role_skills (job_role_id, skill_name, skill_type, skill_order) VALUES (%s,%s,'technical',%s)",
                    (role_id, skill.lower().strip(), i)
                )
                inserted_skills += 1

            for i, skill in enumerate(data.get("soft", [])):
                cur.execute(
                    "INSERT INTO job_role_skills (job_role_id, skill_name, skill_type, skill_order) VALUES (%s,%s,'soft',%s)",
                    (role_id, skill.lower().strip(), i)
                )
                inserted_skills += 1

            print(f"  OK: {role_key} ({len(data['technical'])} tech + {len(data['soft'])} soft)")

        except Exception as e:
            print(f"  ERROR on {role_key}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"\nDone. Inserted {inserted_roles} roles, {inserted_skills} skills.")

if __name__ == "__main__":
    seed()
