#!/usr/bin/env node
/**
 * Expert Skills Updater - Cron Job
 * 
 * Periodically fetches open-source skills, prompts, and knowledge bases
 * to upgrade the 6 expert profiles (sherlock, femida, defender, marketer, financier, health)
 * 
 * Sources:
 * - GitHub awesome lists
 * - HuggingFace prompt collections
 * - LangChain/LlamaIndex prompt templates
 * - Specialized repos (legal-prompts, security-checklists, marketing-frameworks, etc.)
 */

import { execSync } from 'child_process'
import fs from 'fs'
import path from 'path'
import https from 'https'

const PROFILES_DIR = path.join(process.env.HOME || '/Users/igorvasin', '.hermes', 'profiles')
const SKILLS_DIR = path.join(process.env.HOME || '/Users/igorvasin', '.hermes', 'skills')

// Expert profiles with their skill sources
const EXPERT_SKILL_SOURCES = {
  sherlock: {
    name: 'Шерлок (Разведка/Поиск)',
    sources: [
      { type: 'github', repo: 'sindresorhus/awesome-osint', category: 'osint' },
      { type: 'github', repo: 'jivoi/awesome-osint', category: 'osint' },
      { type: 'github', repo: 'igorbarinov/awesome-data-science', category: 'research' },
      { type: 'huggingface', collection: 'prompts/research-analysis', category: 'prompts' },
      { type: 'github', repo: 'langchain-ai/langchain', path: 'libs/core/prompts', category: 'prompt-templates' },
    ],
    skillsToUpdate: ['web-search', 'fact-checking', 'source-verification', 'competitive-intelligence']
  },
  femida: {
    name: 'Фемида (Юриспруденция)',
    sources: [
      { type: 'github', repo: 'ektaraw/awesome-legal-tech', category: 'legal-tech' },
      { type: 'github', repo: 'mikesahas/awesome-law', category: 'legal-resources' },
      { type: 'github', repo: 'langchain-ai/langchain', path: 'libs/community/prompts/legal', category: 'legal-prompts' },
      { type: 'huggingface', collection: 'prompts/legal-contract-analysis', category: 'prompts' },
      { type: 'url', url: 'https://raw.githubusercontent.com/ivan-bilan/The-Novice-Programmer/main/law/152-FZ.md', category: 'rf-law' },
    ],
    skillsToUpdate: ['contract-analysis', 'gdpr-compliance', '152-fz', 'terms-of-service-review', 'ip-risk-assessment']
  },
  defender: {
    name: 'Дефендер (Безопасность)',
    sources: [
      { type: 'github', repo: 'sbilly/awesome-security', category: 'security' },
      { type: 'github', repo: 'paragonie/awesome-appsec', category: 'appsec' },
      { type: 'github', repo: 'OWASP/CheatSheetSeries', category: 'owasp-cheatsheets' },
      { type: 'github', repo: 'trimstray/the-book-of-secret-knowledge', category: 'security-knowledge' },
      { type: 'huggingface', collection: 'prompts/security-audit', category: 'prompts' },
      { type: 'github', repo: 'github/gitignore', path: '', category: 'secrets-patterns' },
    ],
    skillsToUpdate: ['secret-detection', 'dependency-audit', 'infra-security', 'threat-modeling', 'incident-response']
  },
  marketer: {
    name: 'Маркетолог (Маркетинг)',
    sources: [
      { type: 'github', repo: 'f/awesome-marketing', category: 'marketing' },
      { type: 'github', repo: 'kelseyhightower/nocode', category: 'growth-tools' },
      { type: 'github', repo: 'lllyasviel/ControlNet', category: 'visual-marketing' },
      { type: 'huggingface', collection: 'prompts/marketing-copywriting', category: 'prompts' },
      { type: 'github', repo: 'humanloop/awesome-llm-apps', path: 'marketing', category: 'llm-marketing' },
    ],
    skillsToUpdate: ['copywriting', 'positioning', 'channel-strategy', 'conversion-optimization', 'brand-voice']
  },
  financier: {
    name: 'Финансист (Финансы)',
    sources: [
      { type: 'github', repo: 'eugeneyan/applied-ml', category: 'ml-finance' },
      { type: 'github', repo: 'quantopian/zipline', category: 'quant-finance' },
      { type: 'github', repo: 'microsoft/qlib', category: 'quant-research' },
      { type: 'huggingface', collection: 'prompts/financial-analysis', category: 'prompts' },
      { type: 'url', url: 'https://raw.githubusercontent.com/jeffrey-lin/awesome-fintech/main/README.md', category: 'fintech-landscape' },
    ],
    skillsToUpdate: ['unit-economics', 'roi-modeling', 'cash-flow-forecasting', 'tax-optimization', 'fundraising']
  },
  health: {
    name: 'Айболит (Здоровье/MedTech)',
    sources: [
      { type: 'github', repo: 'khanlab/awesome-medical-ai', category: 'medical-ai' },
      { type: 'github', repo: 'deepmind/alphafold', category: 'protein-folding' },
      { type: 'github', repo: 'microsoft/HealthGPT', category: 'health-llm' },
      { type: 'huggingface', collection: 'prompts/medical-summarization', category: 'prompts' },
      { type: 'url', url: 'https://raw.githubusercontent.com/ewulczyn/awesome-healthcare/main/README.md', category: 'healthcare-landscape' },
    ],
    skillsToUpdate: ['medical-literature-review', 'clinical-trial-analysis', 'regulatory-compliance', 'health-data-privacy', 'wellness-tracking']
  }
}

async function fetchGitHubRepo(repo: string, targetPath: string, subPath: string = '') {
  console.log(`📥 Fetching ${repo}...`)
  try {
    const apiUrl = `https://api.github.com/repos/${repo}/contents/${subPath}`
    const response = await fetch(apiUrl, {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Hermes-Expert-Skills-Updater'
      }
    })
    if (!response.ok) throw new Error(`GitHub API: ${response.status}`)
    return await response.json()
  } catch (e) {
    console.warn(`Failed to fetch ${repo}:`, e.message)
    return null
  }
}

async function fetchHuggingFaceCollection(collection: string) {
  console.log(`🤗 Fetching HF collection: ${collection}`)
  try {
    const response = await fetch(`https://huggingface.co/api/collections/${collection}`)
    if (!response.ok) throw new Error(`HF API: ${response.status}`)
    return await response.json()
  } catch (e) {
    console.warn(`Failed to fetch HF collection ${collection}:`, e.message)
    return null
  }
}

async function fetchUrlContent(url: string) {
  console.log(`🌐 Fetching URL: ${url}`)
  return new Promise<string>((resolve, reject) => {
    https.get(url, (res) => {
      let data = ''
      res.on('data', chunk => data += chunk)
      res.on('end', () => resolve(data))
    }).on('error', reject)
  })
}

function extractSkillsFromContent(content: string, category: string): string[] {
  // Extract actionable skills/patterns from content
  const skills: string[] = []
  
  // Look for common patterns in markdown/text
  const patterns = [
    /^##\s+(.+)$/gm,           // Headers
    /^###\s+(.+)$/gm,          // Sub-headers
    /^\-\s+(.+)$/gm,           // List items
    /^\*\s+(.+)$/gm,           // List items
    /`([^`]+)`/g,              // Code snippets
  ]
  
  for (const pattern of patterns) {
    let match
    while ((match = pattern.exec(content)) !== null) {
      const skill = match[1]?.trim()
      if (skill && skill.length > 5 && skill.length < 100) {
        skills.push(`[${category}] ${skill}`)
      }
    }
  }
  
  return [...new Set(skills)].slice(0, 20) // Dedupe and limit
}

async function updateExpertProfile(expertId: string, config: typeof EXPERT_SKILLS_SOURCES[string]) {
  console.log(`\n🔧 Updating ${config.name}...`)
  
  const profileDir = path.join(PROFILES_DIR, expertId)
  const skillsDir = path.join(profileDir, 'skills')
  
  // Ensure skills directory exists
  if (!fs.existsSync(skillsDir)) {
    fs.mkdirSync(skillsDir, { recursive: true })
  }
  
  const allSkills: string[] = []
  
  for (const source of config.sources) {
    let content = ''
    
    if (source.type === 'github') {
      const data = await fetchGitHubRepo(source.repo, '', source.path || '')
      if (data && Array.isArray(data)) {
        // For directories, get README or main files
        for (const item of data.slice(0, 5)) {
          if (item.name.match(/\.(md|txt|py|js|ts)$/i)) {
            const fileData = await fetchGitHubRepo(source.repo, '', `${source.path || ''}/${item.name}`)
            if (fileData?.content) {
              content += Buffer.from(fileData.content, 'base64').toString('utf-8') + '\n\n'
            }
          }
        }
      } else if (data?.content) {
        content = Buffer.from(data.content, 'base64').toString('utf-8')
      }
    } else if (source.type === 'huggingface') {
      const data = await fetchHuggingFaceCollection(source.collection)
      if (data) content = JSON.stringify(data, null, 2)
    } else if (source.type === 'url') {
      content = await fetchUrlContent(source.url)
    }
    
    if (content) {
      const skills = extractSkillsFromContent(content, source.category)
      allSkills.push(...skills)
    }
  }
  
  // Create/update skill files for this expert
  for (const skillName of config.skillsToUpdate) {
    const skillFile = path.join(skillsDir, `${skillName}.md`)
    const relevantSkills = allSkills.filter(s => 
      s.toLowerCase().includes(skillName.replace('-', ' ').toLowerCase()) ||
      skillName.split('-').some(part => s.toLowerCase().includes(part))
    ).slice(0, 10)
    
    const skillContent = `# ${skillName.charAt(0).toUpperCase() + skillName.slice(1).replace(/-/g, ' ')} Skill

**Expert:** ${config.name}
**Updated:** ${new Date().toISOString()}
**Source:** Auto-updated from open sources

## Extracted Knowledge Patterns

${relevantSkills.length > 0 ? relevantSkills.map(s => `- ${s}`).join('\n') : '- No specific patterns extracted this run'}

## Core Prompt Additions

Add these to the expert's SOUL.md or system prompt:

\`\`\`
${relevantSkills.slice(0, 5).join('\n')}
\`\`\`

## Usage

This skill is auto-loaded when the ${expertId} profile is active.
`
    
    fs.writeFileSync(skillFile, skillContent)
    console.log(`  ✅ Created/updated: ${skillFile}`)
  }
  
  // Also update a master index
  const indexFile = path.join(skillsDir, 'INDEX.md')
  const indexContent = `# ${config.name} — Skill Index

**Last Updated:** ${new Date().toISOString()}
**Expert ID:** ${expertId}

## Available Skills

${config.skillsToUpdate.map(s => `- [${s}](${s}.md)`).join('\n')}

## Sources Checked

${config.sources.map(s => `- ${s.type}: ${s.repo || s.collection || s.url} (${s.category})`).join('\n')}

## Next Update

Run this script again or schedule via cron.
`
  fs.writeFileSync(indexFile, indexContent)
  
  console.log(`  📋 Index updated: ${indexFile}`)
}

async function main() {
  console.log('🚀 Starting Expert Skills Update...\n')
  console.log(`Profiles dir: ${PROFILES_DIR}`)
  console.log(`Skills dir: ${SKILLS_DIR}`)
  
  for (const [expertId, config] of Object.entries(EXPERT_SKILL_SOURCES)) {
    try {
      await updateExpertProfile(expertId, config)
    } catch (e) {
      console.error(`❌ Failed to update ${expertId}:`, e)
    }
  }
  
  console.log('\n✅ Expert Skills Update Complete!')
  console.log('\n📝 Next steps:')
  console.log('  1. Review generated skill files in each profile\'s skills/ directory')
  console.log('  2. Manually curate the best patterns into SOUL.md')
  console.log('  3. Test each expert with: hermes profile use <expert>')
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error)
}

export { EXPERT_SKILL_SOURCES, updateExpertProfile }