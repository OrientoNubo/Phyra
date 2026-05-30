"""Vendored pure utilities copied from the Phyra repo (paper-read skill).

Kept byte-faithful so rate-limit / arXiv-resolution semantics stay in
lockstep with upstream Phyra. Only `resolve_input` is lightly decoupled
(its CLI `main()` removed; callers always pass an explicit out dir).
"""
