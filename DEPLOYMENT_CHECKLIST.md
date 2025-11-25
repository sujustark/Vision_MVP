# Deployment Checklist

## Pre-Deployment

- [ ] Code is working locally (backend on :8000, frontend on :5173)
- [ ] All tests pass
- [ ] Code is committed to Git
- [ ] GitHub repository created
- [ ] Code pushed to GitHub

## Backend Deployment (Railway)

- [ ] Sign up at railway.app with GitHub
- [ ] Create new project from GitHub repo
- [ ] Railway detects backend automatically
- [ ] Add environment variables:
  - [ ] `PORT=8000`
  - [ ] `SECRET_KEY=<random-string>`
- [ ] Generate domain in Railway
- [ ] Copy backend URL: `_______________________________`
- [ ] Run database migration via Railway CLI or Shell
- [ ] Test backend: `curl https://your-backend.railway.app/`

## Frontend Deployment (Vercel)

- [ ] Create `frontend/.env.production` with backend URL
- [ ] Sign up at vercel.com with GitHub
- [ ] Import Vision_MVP repository
- [ ] Configure:
  - [ ] Root Directory: `frontend`
  - [ ] Framework: Vite
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `dist`
- [ ] Add environment variable:
  - [ ] `VITE_API_URL=https://your-backend.railway.app/api/v1`
- [ ] Deploy
- [ ] Copy frontend URL: `_______________________________`

## Post-Deployment

- [ ] Update CORS in `backend/app/main.py` with Vercel URL
- [ ] Push CORS update to GitHub (Railway auto-deploys)
- [ ] Test signup at Vercel URL
- [ ] Test login
- [ ] Test Studio page (create event)
- [ ] Test User page (upload selfie)
- [ ] Share Vercel URL with users! 🎉

## URLs to Save

- Frontend: `https://________________________.vercel.app`
- Backend: `https://________________________.railway.app`
- API Docs: `https://________________________.railway.app/docs`

## Troubleshooting

If something doesn't work:
1. Check Railway logs for backend errors
2. Check Vercel logs for frontend errors
3. Check browser console for CORS errors
4. Verify environment variables are set correctly
5. See QUICK_DEPLOY.md for detailed troubleshooting
