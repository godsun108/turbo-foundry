#!/usr/bin/env node
import {verifyRelease, installRelease, rollback, readDeploymentStatus} from './release.mjs';
import {startSupervisor} from './supervisor.mjs';

const [command, ...args] = process.argv.slice(2);
const usage = () => {
  console.error('Usage: node src/cli.mjs verify <release-dir> | install <release-dir> <state-dir> | rollback <state-dir> | status <state-dir> | serve <state-dir> [port]');
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
  } else if (command === 'serve' && (args.length === 1 || args.length === 2)) {
    const runtime = await startSupervisor({stateDirectory:args[0],port:args[1]?Number(args[1]):Number(process.env.PORT)||8080});
    console.log(JSON.stringify({status:'supervisor_listening',address:runtime.address}));
    const stop = async () => { await runtime.close(); process.exit(0); };
    process.once('SIGINT',stop); process.once('SIGTERM',stop);
  } else usage();
} catch (error) {
  console.error(JSON.stringify({ok:false,error:error.message}));
  process.exitCode = 1;
}
