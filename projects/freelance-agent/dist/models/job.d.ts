/**
 * Модель задачи (вакансии/проекта)
 */
export type JobStatus = 'new' | 'filtered_out_skills' | 'filtered_out_clarity' | 'shortlisted' | 'execution_planned' | 'prototype_ready' | 'proposal_sent' | 'in_negotiation' | 'closed' | 'ignored';
export type JobType = 'fixed' | 'hourly';
export interface Budget {
    amount?: number;
    min?: number;
    max?: number;
    currency: string;
    type: JobType;
}
export interface Client {
    id?: string;
    name?: string;
    country?: string;
    rating?: number;
    reviewsCount?: number;
    jobsPosted?: number;
    hireRate?: number;
    paymentVerified: boolean;
    totalSpent?: number;
}
export interface RawJob {
    id?: string;
    platform: string;
    url: string;
    title: string;
    description: string;
    descriptionHtml?: string;
    budget?: Budget;
    postedAt?: Date;
    category?: string;
    subcategory?: string;
    skills: string[];
    client?: Client;
    proposalsCount?: number;
    viewsCount?: number;
    skillMatchScore?: number;
    clarityScore?: number;
    status?: JobStatus;
    duration?: string;
    experienceLevel?: string;
    projectType?: string;
    remote?: boolean;
    attachmentsContent?: string;
    hasAttachments?: boolean;
    attachmentUrls?: string[];
    createdAt?: Date;
    updatedAt?: Date;
    executionPlan?: ExecutionPlan;
}
export interface ExecutionStep {
    week: number;
    title: string;
    deliverable: string;
    responsible: string;
}
export interface ExecutionRole {
    agentName: string;
    role: string;
    tasks: string[];
}
export interface ExecutionPlan {
    goal: string;
    roles: ExecutionRole[];
    roadmap: ExecutionStep[];
    rationale: string;
    risks: string[];
    expectedResult: string;
    estimatedTotalHours: number;
    estimatedCost: number;
}
//# sourceMappingURL=job.d.ts.map