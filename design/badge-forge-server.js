const http = require('http'), fs = require('fs'), path = require('path');
const dir = __dirname;
http.createServer((req, res) => {
  const name = decodeURIComponent(req.url.slice(1)).split('?')[0].replace(/[^a-zA-Z0-9._-]/g, '');
  if (req.method === 'PUT') {
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      fs.writeFileSync(path.join(dir, name), Buffer.concat(chunks));
      res.end('saved ' + name);
    });
    return;
  }
  const f = path.join(dir, name === '' ? 'forge.html' : name);
  if (!fs.existsSync(f)) { res.statusCode = 404; res.end('nf'); return; }
  const ext = path.extname(f);
  res.setHeader('content-type', ext === '.html' ? 'text/html; charset=utf-8' : ext === '.png' ? 'image/png' : 'text/plain');
  res.end(fs.readFileSync(f));
}).listen(8767, () => console.log('badge forge on 8767'));
