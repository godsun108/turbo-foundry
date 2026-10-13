# Call-history settlement gate

`assess_settlement` is a deterministic offline review-only gate. Default requirements: call ended at least 300 seconds ago; at least two complete provider child-page observations; first and last observations at least 120 seconds apart; identical child SID sets across all observations; timezone-aware timestamps; no duplicate SIDs or future observations.

Passing means **stable history for human/automated review**, not evidence that no agent answered and not SMS eligibility. Observations must be collected from an authenticated provider adapter and persisted independently; that scheduling and storage integration is still pending. Delayed records after the settlement window remain a risk. No live SMS or billing is enabled.
