"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StorageService = void 0;
const better_sqlite3_1 = __importDefault(require("better-sqlite3"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
/**
 * Сервис хранения данных на базе SQLite
 */
class StorageService {
    db = null;
    dbPath;
    constructor(dbName = 'freelance.db') {
        // ПРИОРИТЕТ: Переменная окружения или новая "нейтральная зона" для обхода ограничений Mac
        this.dbPath = process.env.DASHBOARD_DB_PATH || '/tmp/freelance_active.db';
        console.log(`StorageService: Using database at ${this.dbPath}`);
        const dir = path_1.default.dirname(this.dbPath);
        if (!fs_1.default.existsSync(dir)) {
            fs_1.default.mkdirSync(dir, { recursive: true });
        }
    }
    /**
     * Инициализировать базу данных
     */
    init() {
        this.db = new better_sqlite3_1.default(this.dbPath);
        // Таблица задач
        this.db.exec(`
      CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        budget_amount REAL,
        budget_currency TEXT,
        budget_type TEXT,
        skills TEXT,
        client_name TEXT,
        client_payment_verified INTEGER,
        proposals_count INTEGER,
        posted_at TEXT,
        skill_match_score REAL,
        clarity_score REAL,
        status TEXT DEFAULT 'new',
        expert_proposal TEXT,
        sherlock_score REAL,
        analysis_report TEXT,
        attachments_content TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
        // Обновление схемы (добавление новых колонок для Шерлока)
        this.addColIfNotExists('jobs', 'expert_proposal', 'TEXT');
        this.addColIfNotExists('jobs', 'sherlock_score', 'REAL');
        this.addColIfNotExists('jobs', 'analysis_report', 'TEXT');
        this.addColIfNotExists('jobs', 'attachments_content', 'TEXT');
        this.addColIfNotExists('jobs', 'has_attachments', 'INTEGER DEFAULT 0');
        this.addColIfNotExists('jobs', 'attachment_urls', 'TEXT');
        this.addColIfNotExists('jobs', 'execution_plan', 'TEXT');
        // Таблица сессий
        this.db.exec(`
      CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        started_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        jobs_found INTEGER DEFAULT 0,
        jobs_filtered INTEGER DEFAULT 0,
        status TEXT DEFAULT 'running'
      )
    `);
        // Индексы для ускорения поиска
        this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform);
      CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
      CREATE INDEX IF NOT EXISTS idx_jobs_url ON jobs(url);
      CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs(posted_at);
    `);
    }
    /**
     * Обновить оценки задачи
     */
    updateJobScores(jobId, skillMatchScore, clarityScore) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }
        this.db.prepare(`
      UPDATE jobs 
      SET skill_match_score = ?, clarity_score = ?, updated_at = CURRENT_TIMESTAMP 
      WHERE id = ?
    `).run(skillMatchScore, clarityScore, jobId);
    }
    /**
     * Сохранить задачу
     */
    saveJob(job) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }
        const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO jobs (
        platform, url, title, description,
        budget_amount, budget_currency, budget_type,
        skills, client_name, client_payment_verified,
        proposals_count, posted_at,
        skill_match_score, clarity_score, status, 
        expert_proposal, sherlock_score, analysis_report, attachments_content, has_attachments, attachment_urls,
        execution_plan,
        updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    `);
        stmt.run(job.platform, job.url, job.title, job.description, job.budget?.amount || null, job.budget?.currency || null, job.budget?.type || null, JSON.stringify(job.skills), job.client?.name || null, job.client?.paymentVerified ? 1 : 0, job.proposalsCount || null, job.postedAt?.toISOString() || null, job.skillMatchScore || null, job.clarityScore || null, job.status || 'new', job.expert_proposal || null, job.sherlock_score || null, job.analysis_report || null, job.attachmentsContent || null, job.hasAttachments ? 1 : 0, job.attachmentUrls ? JSON.stringify(job.attachmentUrls) : null, job.execution_plan ? JSON.stringify(job.execution_plan) : null);
    }
    /**
     * Сохранить несколько задач
     */
    saveJobs(jobs) {
        if (!this.db) {
            console.warn('StorageService: Database not initialized in saveJobs, attempting to init...');
            this.init();
        }
        if (!this.db) {
            throw new Error('Критическая ошибка: База данных не инициализирована и не подлежит восстановлению в saveJobs.');
        }
        try {
            const transaction = this.db.transaction((jobs) => {
                for (const job of jobs) {
                    this.saveJob(job);
                }
            });
            transaction(jobs);
        }
        catch (error) {
            console.error('StorageService: Transaction error in saveJobs:', error);
            throw error;
        }
    }
    /**
     * Получить задачи по фильтру
     */
    getJobs(filters) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }
        let query = 'SELECT * FROM jobs WHERE 1=1';
        const params = [];
        if (filters?.platform) {
            query += ' AND platform = ?';
            params.push(filters.platform);
        }
        if (filters?.status) {
            query += ' AND status = ?';
            params.push(filters.status);
        }
        if (filters?.minSkillMatch !== undefined) {
            query += ' AND skill_match_score >= ?';
            params.push(filters.minSkillMatch);
        }
        if (filters?.url) {
            query += ' AND url = ?';
            params.push(filters.url);
        }
        query += ' ORDER BY posted_at DESC';
        if (filters?.limit) {
            query += ' LIMIT ?';
            params.push(filters.limit);
        }
        const stmt = this.db.prepare(query);
        const rows = stmt.all(...params);
        return rows.map(row => this.rowToJob(row));
    }
    /**
     * Обновить статус задачи
     */
    updateJobStatus(url, status, extraData) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }
        let query = 'UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP';
        const params = [status];
        if (extraData?.skillMatchScore !== undefined) {
            query += ', skill_match_score = ?';
            params.push(extraData.skillMatchScore);
        }
        if (extraData?.clarityScore !== undefined) {
            query += ', clarity_score = ?';
            params.push(extraData.clarityScore);
        }
        query += ' WHERE url = ?';
        params.push(url);
        const stmt = this.db.prepare(query);
        stmt.run(...params);
    }
    /**
     * Начать сессию
     */
    startSession(platform) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }
        const stmt = this.db.prepare(`
      INSERT INTO sessions (platform, status) VALUES (?, 'running')
    `);
        const result = stmt.run(platform);
        return result.lastInsertRowid;
    }
    /**
     * Завершить сессию
     */
    completeSession(sessionId, jobsFound, jobsFiltered) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }
        const stmt = this.db.prepare(`
      UPDATE sessions
      SET completed_at = CURRENT_TIMESTAMP,
          jobs_found = ?,
          jobs_filtered = ?,
          status = 'completed'
      WHERE id = ?
    `);
        stmt.run(jobsFound, jobsFiltered, sessionId);
    }
    /**
     * Преобразовать строку БД в Job
     */
    rowToJob(row) {
        return {
            id: row.id.toString(),
            platform: row.platform,
            url: row.url,
            title: row.title,
            description: row.description || '',
            budget: row.budget_amount ? {
                amount: row.budget_amount,
                currency: row.budget_currency || 'RUB',
                type: row.budget_type || 'fixed'
            } : undefined,
            skills: row.skills ? JSON.parse(row.skills) : [],
            client: {
                name: row.client_name || undefined,
                paymentVerified: row.client_payment_verified === 1
            },
            proposalsCount: row.proposals_count || undefined,
            postedAt: row.posted_at ? new Date(row.posted_at) : undefined,
            skillMatchScore: row.skill_match_score || undefined,
            clarityScore: row.clarity_score || undefined,
            status: row.status || 'new',
            expert_proposal: row.expert_proposal || undefined,
            sherlock_score: row.sherlock_score || undefined,
            analysis_report: row.analysis_report || undefined,
            attachmentsContent: row.attachments_content || undefined,
            attachmentUrls: row.attachment_urls ? JSON.parse(row.attachment_urls) : [],
            execution_plan: row.execution_plan ? JSON.parse(row.execution_plan) : undefined,
            createdAt: row.created_at ? new Date(row.created_at) : undefined,
            updatedAt: row.updated_at ? new Date(row.updated_at) : undefined
        };
    }
    /**
     * Добавить колонку в таблицу, если она отсутствует
     */
    addColIfNotExists(table, col, type) {
        if (!this.db)
            return;
        // Проверить наличие колонки через PRAGMA table_info
        const info = this.db.prepare(`PRAGMA table_info(${table})`).all();
        const exists = info.some(c => c.name === col);
        if (!exists) {
            this.db.exec(`ALTER TABLE ${table} ADD COLUMN ${col} ${type}`);
        }
    }
    /**
     * Закрыть соединение с БД
     */
    close() {
        this.db?.close();
        this.db = null;
    }
    /**
     * Получить путь к БД
     */
    getDbPath() {
        return this.dbPath;
    }
}
exports.StorageService = StorageService;
