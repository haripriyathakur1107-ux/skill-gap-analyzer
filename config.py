class Config:
    SECRET_KEY       = 'your_secret_key_here_change_in_production'
    MYSQL_HOST       = 'localhost'
    MYSQL_USER       = 'root'
    MYSQL_PASSWORD   = 'root'
    MYSQL_DB         = 'skill_gap_analyzer'

    # Cache for job skills fetched from DB (in-process, cleared on restart)
    # For production use Redis instead
    JOB_SKILLS_CACHE = {}
