# N1MOX30 RELEASE POLICY

## Branches

main
    Production-ready code.

develop
    Integration branch.

feature/*
    New development.

hotfix/*
    Emergency production fixes.

## Release process

feature/* 
    ->
develop
    ->
tests
    ->
main
    ->
release tag
    ->
production

## Commit examples

feat: add creator workflow automation
fix: repair YouTube OAuth callback
security: harden token storage
perf: optimize dashboard loading
docs: update launch checklist
chore: update dependencies

## Never commit

.env
.env.production
OAuth tokens
API keys
private credentials
database files
generated secrets
production logs
