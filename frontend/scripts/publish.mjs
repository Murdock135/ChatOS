import { cp, mkdir } from 'node:fs/promises';

// Publish only compiled public app files; the private workspace is never input.
const target = new URL('../../src/chatos/static/', import.meta.url);
const output = new URL('../dist/', import.meta.url);
await mkdir(target, { recursive: true });
await cp(output, target, { recursive: true });
