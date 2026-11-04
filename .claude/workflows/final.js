export const meta = {
  name: 'final',
  description: 'Whole-feature check before the pull request: full test gate, three concept checkers, two extras scouts',
  whenToUse: 'Started by the /finish skill once every round has merged, never directly.',
  phases: [
    { title: 'Test gate', detail: 'full suite, ruff, mypy, check_sync', model: 'sonnet' },
    { title: 'Concept check', detail: 'three lenses against BRIEF.md', model: 'sonnet' },
    { title: 'Extras', detail: 'critical gaps and highest-value follow-ups', model: 'sonnet' },
  ],
}

// args (from /finish): { feature_dir, feature_branch }
// Read-only: nothing here writes, commits or pushes. /finish acts on the result.
// Returns { tests, checks: [{lens, pass, summary, findings}], extras: [...] }

const a = args || {}
for (const key of ['feature_dir', 'feature_branch']) {
  if (!a[key]) throw new Error(`final workflow: missing args.${key}`)
}

const CONTEXT =
  `The feature in ${a.feature_dir}/ (BRIEF.md, brief.json, one folder per round with log.md) is fully built on ` +
  `${a.feature_branch}, which is checked out. Read-only: change no file, make no commit.`

const FINDING = {
  type: 'object',
  properties: {
    severity: { type: 'string', enum: ['blocking', 'minor'] },
    where: { type: 'string' },
    issue: { type: 'string' },
    fix: { type: 'string' },
  },
  required: ['severity', 'where', 'issue'],
}
const TEST_RUN = {
  type: 'object',
  properties: {
    passed: { type: 'boolean' },
    summary: { type: 'string' },
    failures: { type: 'array', items: { type: 'string' } },
  },
  required: ['passed', 'summary', 'failures'],
}
const VERDICT = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    summary: { type: 'string' },
    findings: { type: 'array', items: FINDING },
  },
  required: ['pass', 'summary', 'findings'],
}
const EXTRAS = {
  type: 'object',
  properties: {
    extras: {
      type: 'array',
      maxItems: 5,
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          why: { type: 'string', description: 'The value it adds or the harm it prevents, concretely' },
          critical: { type: 'boolean', description: 'True only if shipping without it would be wrong: data loss, a broken promise of the BRIEF, a security hole, a crash on ordinary input' },
          size: { type: 'string', enum: ['small', 'round', 'feature'] },
        },
        required: ['title', 'why', 'critical', 'size'],
      },
    },
  },
  required: ['extras'],
}

const LENSES = {
  criteria: 'Is every feature-level acceptance criterion in BRIEF.md met? Cite the code or test proving each.',
  purpose: 'Does the feature as a whole serve its goal in BRIEF.md, used the way a caller would use it? Try it.',
  scope: 'Do the rounds fit together: nothing half-done, no round undoing another, nothing outside the BRIEF shipped by accident?',
}
const SCOUTS = {
  critical: 'Look for what would make shipping this feature wrong: unhandled ordinary inputs, broken promises of the BRIEF, security or data-loss risks. Report nothing rather than something minor.',
  value: 'Look for the few follow-ups that would add the most value to this feature for its users. Only the best two or three; none if nothing stands out.',
}

phase('Test gate')
const testsP = agent(
  `${CONTEXT}\nRun pytest (whole suite), ruff check, ruff format --check, mypy and python .claude/hooks/check_sync.py ` +
  '(the last one may report STRUCTURE.md, README and DEVLOG drift: that is expected before /finish writes them; ' +
  'report it separately in the summary and do not count it as a failure). Report exactly what fails.',
  { agentType: 'test-runner', model: 'sonnet', effort: 'low', schema: TEST_RUN, phase: 'Test gate', label: 'full gate' })

const checksP = parallel(Object.entries(LENSES).map(([lens, task]) => () =>
  agent(`${CONTEXT}\nFeature-level concept check, lens "${lens}": ${task}\npass=false only for a real gap; mark those findings blocking.`,
    { agentType: 'concept-checker', model: 'sonnet', effort: 'low', schema: VERDICT, phase: 'Concept check', label: `check: ${lens}` })
    .then(v => v && { lens, ...v })))

const extrasP = parallel(Object.entries(SCOUTS).map(([lens, task]) => () =>
  agent(`${CONTEXT}\nExtras scout, lens "${lens}": ${task}`,
    { agentType: 'extras-scout', model: 'sonnet', effort: 'medium', schema: EXTRAS, phase: 'Extras', label: `extras: ${lens}` })
    .then(r => r && r.extras.map(x => ({ ...x, lens })))))

const [tests, checks, extras] = await Promise.all([testsP, checksP, extrasP])
const verdicts = checks.filter(Boolean)
log(`tests ${tests && tests.passed ? 'green' : 'red'}; concept ${verdicts.filter(v => v.pass).length}/${verdicts.length} pass`)
return { tests, checks: verdicts, extras: extras.filter(Boolean).flat() }
