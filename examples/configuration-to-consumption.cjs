'use strict';

// Optional, dependency-free model demonstration. Run with Node.js:
// node examples/configuration-to-consumption.cjs --demo
// All rules and data below are synthetic; this does not test a user's prototype.
const assert = require('node:assert/strict');
const copy = value => JSON.parse(JSON.stringify(value));

// JSON serialization models save/reopen, not disk durability or browser controls.
class DemoTask {
  constructor(fault) {
    this.fault = fault;
    this.saved = JSON.stringify({
      config: { renames: [], outputScope: 'retain', priority: ['A', 'B'] },
      output: [{ id: 'OLD', value: 11 }],
      watermark: 40
    });
  }

  reopen() { return JSON.parse(this.saved); }

  saveConfiguration(config) {
    const state = this.reopen();
    state.config = copy(config);
    this.saved = JSON.stringify(state);
  }

  mapAndCalculate(input) {
    const config = this.reopen().config;
    // An absent scope belongs to the legacy fixture and still means mapped-only.
    const retain = config.outputScope === 'retain' && this.fault !== 'drop-unmapped';
    const row = retain ? copy(input) : {};
    for (const { fieldId, name } of config.renames) {
      delete row[fieldId];
      row[name] = input[fieldId];
    }
    if (!Object.hasOwn(row, 'weight')) {
      return { ok: false, code: 'MISSING_WEIGHT', row };
    }
    if (Object.hasOwn(row, 'freight') && this.fault === 'reject-source-name') {
      return { ok: false, code: 'RESERVED_FIELD', row };
    }
    if (this.fault === 'overwrite-source-name') row.freight = row.weight * 2;
    return { ok: true, row, freight: row.weight * 2 };
  }

  combineAndCalculate(sources) {
    const config = this.reopen().config;
    const priority = this.fault === 'ignore-priority' ? ['A', 'B'] : config.priority;
    const byKey = new Map();
    for (const sourceId of priority) {
      for (const row of sources[sourceId]) {
        if (!byKey.has(row.id)) byKey.set(row.id, copy(row));
      }
    }
    return [...byKey.values()].map(row => ({ ...row, freight: row.weight * row.rate }));
  }

  adoptBatch(rows, nextWatermark, failAdoption = false) {
    const seen = new Set();
    const duplicate = rows.find(row => {
      if (seen.has(row.id)) return true;
      seen.add(row.id);
      return false;
    });
    if (duplicate) {
      if (this.fault === 'warn-but-write') this.commit(rows, nextWatermark);
      return { ok: false, code: 'DUPLICATE_KEY', key: duplicate.id,
        recovery: 'Correct the duplicate key in this batch and submit again.' };
    }
    if (failAdoption) {
      const state = this.reopen();
      if (this.fault === 'advance-on-failure') state.watermark = nextWatermark;
      if (this.fault === 'replace-on-failure') state.output = copy(rows);
      if (this.fault === 'advance-on-failure' || this.fault === 'replace-on-failure') {
        this.saved = JSON.stringify(state);
      }
      return { ok: false, code: 'OUTPUT_NOT_ADOPTED' };
    }
    this.commit(rows, nextWatermark);
    return { ok: true };
  }

  commit(rows, nextWatermark) {
    const state = this.reopen();
    state.output = copy(rows);
    state.watermark = nextWatermark;
    this.saved = JSON.stringify(state);
  }
}

// Decided fixture: app scope is sufficient; the former full-column condition
// was cancelled. Fixing the response wrapper must not bring that condition back.
function queryApplication(grant, structureChanged, fault) {
  if (!grant || (fault === 'revive-cancelled-rule' && !grant.allColumns)) {
    return { ok: false, status: 403, code: 'NO_APPLICATION_GRANT' };
  }
  if (structureChanged) {
    return { ok: false, status: fault === 'wrong-error-status' ? 422 : 409,
      code: 'STRUCTURE_CHANGED' };
  }
  const published = [{ q: 1, total: 10 }, { q: 2, total: 20 }, { q: 3, total: 30 }];
  const rows = published.filter(row => row.q >= grant.minimumQ)
    .map(row => Object.fromEntries(grant.columns.map(name => [name, row[name]])));
  return { ok: true, status: 200, rows };
}

// Expected values are literal answers derived from the declared fixture rules,
// never calculated by calling the implementation under test.
const scenarios = [
  {
    id: 'rename',
    label: 'Rename only: retained columns feed freight = 16; legacy scope stays unchanged',
    run(fault) {
      const task = new DemoTask(fault);
      const draft = task.reopen().config;
      draft.renames = [{ fieldId: 'device', name: 'asset_id' }];
      task.saveConfiguration(draft);
      draft.renames[0].name = 'unsaved_name';
      assert.deepEqual(task.reopen().config.renames,
        [{ fieldId: 'device', name: 'asset_id' }], 'reopen must read saved configuration');
      const input = { device: 'D1', weight: 8, region: 'north', freight: 99 };
      assert.deepEqual(task.mapAndCalculate(input), {
        ok: true, row: { asset_id: 'D1', weight: 8, region: 'north', freight: 99 }, freight: 16
      }, 'renaming one column must retain the others and feed the downstream calculation');
      const mappedOnly = task.reopen().config;
      mappedOnly.outputScope = 'mapped-only';
      task.saveConfiguration(mappedOnly);
      assert.deepEqual(task.mapAndCalculate(input), {
        ok: false, code: 'MISSING_WEIGHT', row: { asset_id: 'D1' }
      }, 'explicitly removing weight must reject its consumer');
      mappedOnly.outputScope = 'retain';
      task.saveConfiguration(mappedOnly);
      assert.equal(task.mapAndCalculate(input).freight, 16, 'restoring scope must restore consumption');
      delete mappedOnly.outputScope;
      task.saveConfiguration(mappedOnly);
      assert.deepEqual(task.mapAndCalculate(input), {
        ok: false, code: 'MISSING_WEIGHT', row: { asset_id: 'D1' }
      }, 'a new default must not silently migrate the legacy fixture');
    }
  },
  {
    id: 'priority',
    label: 'Different source values: priority A/B gives 16; B/A gives 40',
    run(fault) {
      const task = new DemoTask(fault);
      const sources = {
        A: [{ id: 'D1', weight: 8, rate: 2 }],
        B: [{ id: 'D1', weight: 8, rate: 5 }]
      };
      assert.deepEqual(task.combineAndCalculate(sources),
        [{ id: 'D1', weight: 8, rate: 2, freight: 16 }], 'A must win before the change');
      const draft = task.reopen().config;
      draft.priority = ['B', 'A'];
      task.saveConfiguration(draft);
      assert.deepEqual(task.reopen().config.priority, ['B', 'A']);
      assert.deepEqual(task.combineAndCalculate(sources),
        [{ id: 'D1', weight: 8, rate: 5, freight: 40 }], 'saved priority must change the actual consumer result');
    }
  },
  {
    id: 'duplicate',
    label: 'Duplicate key: reject with no write, then corrected batch is adopted',
    run(fault) {
      const task = new DemoTask(fault);
      const before = task.reopen();
      const response = task.adoptBatch([{ id: 'D1', value: 3 }, { id: 'D1', value: 4 }], 42);
      assert.deepEqual(response, { ok: false, code: 'DUPLICATE_KEY', key: 'D1',
        recovery: 'Correct the duplicate key in this batch and submit again.' });
      assert.deepEqual(task.reopen(), before, 'a rejection message must also prevent every write');
      assert.deepEqual(task.adoptBatch([{ id: 'D1', value: 3 }, { id: 'D2', value: 4 }], 42), { ok: true });
      assert.deepEqual(task.reopen().output, [{ id: 'D1', value: 3 }, { id: 'D2', value: 4 }]);
      assert.equal(task.reopen().watermark, 42);
    }
  },
  {
    id: 'failure',
    label: 'Adoption failure: existing output OLD=11 and nonzero watermark 40 survive; retry succeeds',
    run(fault) {
      const task = new DemoTask(fault);
      assert.deepEqual(task.adoptBatch([{ id: 'D1', value: 99 }], 42, true),
        { ok: false, code: 'OUTPUT_NOT_ADOPTED' });
      assert.deepEqual({ output: task.reopen().output, watermark: task.reopen().watermark }, {
        output: [{ id: 'OLD', value: 11 }], watermark: 40
      }, 'failure must neither replace existing output nor advance the established watermark');
      assert.deepEqual(task.adoptBatch([{ id: 'D1', value: 99 }], 42), { ok: true });
      assert.deepEqual(task.reopen().output, [{ id: 'D1', value: 99 }]);
      assert.equal(task.reopen().watermark, 42);
    }
  },
  {
    id: 'decided-rule',
    label: 'Decided-rule repair: total-only grant works; structure error stays 409; no grant stays 403',
    run(fault) {
      const grant = { minimumQ: 2, columns: ['total'] };
      const legal = { ok: true, status: 200, rows: [{ total: 20 }, { total: 30 }] };
      assert.deepEqual(queryApplication(grant, false, fault), legal,
        'repair must preserve the legal path without reviving the cancelled full-column restriction');
      assert.deepEqual(queryApplication(grant, true, fault),
        { ok: false, status: 409, code: 'STRUCTURE_CHANGED' }, 'final response must follow the decided error contract');
      assert.deepEqual(queryApplication(grant, false, fault), legal, 'legal query must recover after the structure is corrected');
      assert.deepEqual(queryApplication(null, false, fault),
        { ok: false, status: 403, code: 'NO_APPLICATION_GRANT' }, 'the active application grant rule still applies');
    }
  }
];

const faults = [
  ['rename', 'drop-unmapped'],
  ['rename', 'overwrite-source-name'],
  ['rename', 'reject-source-name'],
  ['priority', 'ignore-priority'],
  ['duplicate', 'warn-but-write'],
  ['failure', 'advance-on-failure'],
  ['failure', 'replace-on-failure'],
  ['decided-rule', 'wrong-error-status'],
  ['decided-rule', 'revive-cancelled-rule']
];

function runDemo() {
let failed = 0;
let passed = 0;
let detected = 0;
for (const scenario of scenarios) {
  try {
    scenario.run();
    passed++;
    console.log(`PASS ${scenario.id}: ${scenario.label}`);
  } catch (error) {
    failed++;
    console.error(`FAIL ${scenario.id}: ${error.stack}`);
  }
}
for (const [id, fault] of faults) {
  try {
    scenarios.find(scenario => scenario.id === id).run(fault);
    failed++;
    console.error(`MISSED ${fault}: the faulty implementation passed`);
  } catch (error) {
    if (!(error instanceof assert.AssertionError)) {
      failed++;
      console.error(`ERROR ${fault}: ${error.stack}`);
      continue;
    }
    detected++;
    console.log(`DETECTED ${fault}: ${error.message.split('\n')[0]}`);
    console.log(`  actual=${JSON.stringify(error.actual)} expected=${JSON.stringify(error.expected)}`);
  }
}
console.log(`Result: ${passed}/${scenarios.length} normal scenarios passed; ${detected}/${faults.length} controlled faults detected.`);
console.log('Boundary: synthetic handler/model assertions only; no browser, real API, durable storage, or user-system acceptance.');
process.exitCode = failed ? 1 : 0;

}

// This adapter calls the current artifact; unlike runDemo it does not instantiate
// DemoTask. The caller derives expected values from its own authorized requirement.
async function runActual(adapter) {
  if (!adapter || !adapter.subject || !['browser','handler'].includes(adapter.kind)
      || !Array.isArray(adapter.scenarios) || !adapter.scenarios.length) {
    throw new Error('Adapter needs subject, kind (browser/handler), and nonempty scenarios');
  }
  let failed=0;const results=[];
  for (const scenario of adapter.scenarios) {
    if (!scenario.name || typeof scenario.observe!=='function' || !Object.hasOwn(scenario,'expected'))
      throw new Error('Each scenario needs name, expected, and observe()');
    const expected=structuredClone(scenario.expected);
    let actual;
    try { actual=await scenario.observe(); }
    catch (error) { failed++;results.push({name:scenario.name,status:'UNOBSERVED',message:error.message});continue; }
    try { assert.deepStrictEqual(actual,expected);results.push({name:scenario.name,status:'MATCH',actual}); }
    catch (error) { failed++;results.push({name:scenario.name,status:'DIFFERENT',expected,actual}); }
  }
  return {scope:'project-adapter',subject:adapter.subject,kind:adapter.kind,results,failed,
    boundary:'Only the observations returned by this adapter; no inferred production acceptance.'};
}
module.exports={runActual};
if (require.main===module) {
  if (process.argv[2]==='--demo') runDemo();
  else if (process.argv[2]==='--actual' && process.argv[3]) {
    const adapter=require(require('node:path').resolve(process.argv[3]));
    runActual(adapter).then(result=>{console.log(JSON.stringify(result,null,2));process.exitCode=result.failed?1:0;})
      .catch(error=>{console.error(error.message);process.exitCode=2;});
  } else {
    console.log('Usage: node examples/configuration-to-consumption.cjs --demo | --actual <task-check.cjs>');
    console.log('No project artifact was tested. --demo is a synthetic model only.');
  }
}
