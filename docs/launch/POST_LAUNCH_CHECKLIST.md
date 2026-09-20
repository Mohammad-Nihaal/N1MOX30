# N1MOX30 POST-LAUNCH CHECKLIST

## Immediately after deployment
- [ ] Open production website
- [ ] Check HTTPS
- [ ] Check login
- [ ] Check dashboard
- [ ] Check Creator OS
- [ ] Check connected accounts
- [ ] Check OAuth
- [ ] Check API health
- [ ] Check frontend console
- [ ] Check backend logs
- [ ] Check database connectivity
- [ ] Verify no secrets appear in browser
- [ ] Verify publishing safety gate

## First 24 hours
- [ ] Monitor application errors
- [ ] Monitor API failures
- [ ] Monitor authentication failures
- [ ] Monitor OAuth failures
- [ ] Monitor queue failures
- [ ] Monitor publishing failures
- [ ] Monitor analytics
- [ ] Check Search Console
- [ ] Check indexing
- [ ] Check broken URLs
- [ ] Check Core Web Vitals
- [ ] Check mobile usability

## First 7 days
- [ ] Review traffic
- [ ] Review conversion
- [ ] Review signup/login failures
- [ ] Review creator workflow failures
- [ ] Review YouTube API quota/errors
- [ ] Review server resources
- [ ] Review database size
- [ ] Review logs
- [ ] Review user feedback
- [ ] Review security alerts

## Every release
1. Create branch
2. Implement change
3. Run tests
4. Build frontend
5. Review diff
6. Commit
7. Tag release
8. Deploy
9. Smoke test
10. Monitor
11. Roll back if required

## Rollback

If a production release is broken:

git checkout <known-good-tag>

or redeploy the known-good release through the hosting platform.

Never delete the known-good release tag.
