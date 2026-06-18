// Firebase web config.
//
// Values are read from Vite env vars when provided (set VITE_FIREBASE_* in your
// Vercel project), with empty fallbacks otherwise so the production build
// succeeds and the app loads even when Firebase isn't configured. When the
// config is empty, Firestore-backed features (e.g. dumping reports) degrade
// gracefully instead of breaking the page.
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "",
}

// Some modules import the config as a named export, others as default.
export const isFirebaseConfigured = Boolean(firebaseConfig.projectId && firebaseConfig.apiKey)
export { firebaseConfig }
export default firebaseConfig
