#!/usr/bin/env node
import {verifyRelease, installRelease, rollback, readDeploymentStatus} from './release.mjs';

const [command, ...args] = process.argv.slice(2);
const usage = () => {
  console.error('Usage: node src/cli.mjs verify <release-dir> | install <release-dir> <state-dir> | rollback <state-dir> | status <state-dir>');
  process.exitCode = 2;
};
try {
  if (command === 'verify' && args.length === 1) {
    const result = await verifyRelease(args[0], {allowUnsignedLocal:process.env.SOVEREIGN_ALLOW_UNSIGNED_LOCAL === '1'});
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'install' && args.length === 2) {
    const result = await installRelease(args[0], args[1], {allowUnsignedLocal:process.env.SOVEREIGN_ALLOW_UNSIGNED_LOCAL === '1'});
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'rollback' && args.length === 1) {
    console.log(JSON.stringify(await rollback(args[0]), null, 2));
  } else if (command === 'status' && args.length === 1) {
    console.log(JSON.stringify(await readDeploymentStatus(args[0]), null, 2));
  } else usage();
} catch (error) {
  console.error(JSON.stringify({ok:false,error:error.message}));
  process.exitCode = 1;
}
