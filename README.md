<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>




# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/110c4226-2293-44ae-b73a-327310137674

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`

## GitHub Pages

The site is deployed from `dist/` by `.github/workflows/deploy-pages.yml`. In the repository settings, select **Settings → Pages → Build and deployment → Source → GitHub Actions**. The workflow builds the project with the `/townysuite-arena/` base path and deploys it after changes reach `main`.
