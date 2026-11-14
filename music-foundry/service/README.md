# Music Foundry private render service

A dependency-free Python HTTP service that runs the existing Music Foundry offline WAV renderers. It is designed for a Railway persistent volume mounted at `/data`.

## Runtime configuration

- `PORT`: Railway-provided HTTP port (default 8080)
- `MUSIC_FOUNDRY_DATA`: persistent data root (default `/data/music-foundry`)
- `MUSIC_FOUNDRY_API_TOKEN`: required bearer token; all API routes except `/health` return 503 until configured
- `MUSIC_FOUNDRY_ALLOWED_ORIGIN`: optional browser origin allowlist; default `*` (API token remains mandatory)

## API

- `GET /health`: unauthenticated health probe
- `GET /api/v1/projects`: authenticated project catalogue
- `POST /api/v1/render`: authenticated render request; JSON body:
  `{"project":"somebodys-gotta-do-it","arrangement":"warehouse-rave-v3","bpm":127}`
- `GET /api/v1/jobs/{uuid}`: authenticated job state and verified audio metadata
- `GET /api/v1/jobs/{uuid}/files/{filename}`: authenticated WAV/JSON download

The render request is asynchronous and returns HTTP 202. Job state and outputs are persisted beneath the data root. Only the known project and renderer choices are accepted; request sizes, BPM, output names and file paths are bounded.

## Railway setup

Use repository `godsun108/turbo-foundry`, branch `music/kokoro-score-conditioned-singer-v1`, Dockerfile `Dockerfile.music-foundry`, healthcheck `/health`, and a persistent volume mounted at `/data`. Set a long random `MUSIC_FOUNDRY_API_TOKEN` as a Railway secret. Do not put the token in GitHub, the browser bundle, or public documentation.

This service renders instrumental audio only. Spoken/sung vocal generation, final mixing/mastering and iPhone Safari playback are separate acceptance gates and must not be marked complete until validated.
