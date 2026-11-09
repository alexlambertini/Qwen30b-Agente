const test = require('node:test');
const assert = require('node:assert');
const { TaskQueue } = require('./queue');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

test('resolve com o valor da tarefa', async () => {
  const q = new TaskQueue(2);
  assert.strictEqual(await q.add(async () => 42), 42);
});

test('respeita o limite de concorrencia', async () => {
  const q = new TaskQueue(2);
  let active = 0, max = 0;
  const job = async () => { active++; max = Math.max(max, active); await sleep(20); active--; };
  await Promise.all([1, 2, 3, 4, 5, 6].map(() => q.add(job)));
  assert.strictEqual(max, 2);
});
