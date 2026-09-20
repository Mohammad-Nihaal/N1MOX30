# N1MOX30 PRE-LAUNCH CHECKLIST

## Application
- [ ] Backend starts successfully
- [ ] Frontend production build succeeds
- [ ] Database initializes correctly
- [ ] Authentication works
- [ ] Creator dashboard works
- [ ] Creator OS workflow works
- [ ] OAuth routes are reachable
- [ ] Publishing safety gate works
- [ ] Real YouTube publishing remains disabled until final verification

## Security
- [ ] No API keys committed to Git
- [ ] No OAuth tokens committed
- [ ] No production .env committed
- [ ] SECRET_KEY replaced with production secret
- [ ] Production CORS reviewed
- [ ] HTTPS configured
- [ ] Secure cookies configured where applicable
- [ ] Error responses do not expose secrets
- [ ] Debug mode disabled

## Website / UX
- [ ] Privacy Policy
- [ ] Terms & Conditions
- [ ] Cookie consent where legally applicable
- [ ] Custom 404 page
- [ ] Mobile responsive
- [ ] Color contrast reviewed
- [ ] Forms validated
- [ ] Broken links checked
- [ ] Images compressed
- [ ] Images have useful alt text
- [ ] Clear CTA
- [ ] Favicon
- [ ] Meta title
- [ ] Meta description
- [ ] Social preview image
- [ ] Open Graph metadata
- [ ] Twitter/X card metadata

## SEO / Discovery
- [ ] sitemap.xml
- [ ] robots.txt
- [ ] llms.txt if intentionally used
- [ ] Google Search Console configured
- [ ] Sitemap submitted to Google
- [ ] Important pages requested for indexing
- [ ] Bing Webmaster Tools configured
- [ ] Bing sitemap submitted

## Performance
- [ ] Production build
- [ ] Page load checked
- [ ] JavaScript bundle reviewed
- [ ] Images optimized
- [ ] Mobile performance checked
- [ ] Core Web Vitals checked

## Git / Release
- [ ] Git repository initialized
- [ ] .gitignore verified
- [ ] Secrets scan completed
- [ ] Clean release commit
- [ ] Release tag created
- [ ] Rollback point created
- [ ] Remote repository configured
- [ ] Deployment connected to Git

# RELEASE RULE

Never deploy uncommitted experimental code directly to production.

Use:

feature -> test -> commit -> release -> deploy -> verify
