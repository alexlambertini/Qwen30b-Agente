// Fila de tarefas assincronas com limite de concorrencia.
class TaskQueue {
  constructor(concurrency = 2) {
    this.concurrency = concurrency;
    this.running = 0;
    this.pending = [];
  }

  // Agenda fn (funcao que devolve Promise) e devolve uma Promise com o resultado dela.
  add(fn) {
    return new Promise((resolve, reject) => {
      this.pending.push({ fn, resolve, reject });
      this._next();
    });
  }

  _next() {
    if (this.running > this.concurrency || this.pending.length === 0) return;
    const { fn, resolve, reject } = this.pending.shift();
    this.running++;
    fn().then((value) => {
      this.running--;
      resolve(value);
      this._next();
    }).catch(reject);
  }
}

module.exports = { TaskQueue };
