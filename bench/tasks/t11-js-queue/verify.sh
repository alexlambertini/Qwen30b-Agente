timeout 60 node --test 2>&1 >/dev/null && timeout 30 node - <<'JS'
const assert = require('node:assert');
const { TaskQueue } = require('./queue');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  const q = new TaskQueue(2);
  let active = 0, max = 0;
  const job = async () => { active++; max = Math.max(max, active); await sleep(10); active--; return 1; };
  const rs = await Promise.allSettled([
    q.add(job), q.add(async () => { await sleep(5); throw new Error('boom'); }),
    q.add(() => { throw new Error('sync'); }), q.add(job), q.add(job), q.add(job), q.add(job),
  ]);
  assert.deepStrictEqual(rs.map((r) => r.status), ['fulfilled', 'rejected', 'rejected', 'fulfilled', 'fulfilled', 'fulfilled', 'fulfilled']);
  assert.strictEqual(rs[1].reason.message, 'boom'); assert.strictEqual(rs[2].reason.message, 'sync');
  assert.strictEqual(max, 2, 'concorrencia ' + max); assert.strictEqual(q.running, 0);
  const q1 = new TaskQueue(1); const order = [];
  await Promise.all([1, 2, 3].map((n) => q1.add(async () => { await sleep(5 * (4 - n)); order.push(n); })));
  assert.deepStrictEqual(order, [1, 2, 3]);
  const src = require('fs').readFileSync('queue.test.js', 'utf8');
  assert.ok((src.match(/\btest\(/g) || []).length >= 4, 'poucos testes');
  process.exit(0);
})().catch((e) => { console.error(e); process.exit(1); });
JS
