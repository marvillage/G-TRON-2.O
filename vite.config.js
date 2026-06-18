import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://localhost:5000',
                changeOrigin: true
            }
        },
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    optimizeDeps: {
        include: ['leaflet', 'react-leaflet']
    },
    build: {
        commonjsOptions: {
            // Must include node_modules broadly (not just leaflet) so CommonJS
            // deps like react/react-dom have their named exports detected by
            // Rollup during `vite build`. Narrowing this to [/leaflet/] broke
            // the production build ("createContext is not exported by react").
            include: [/leaflet/, /node_modules/],
        },
    }
});
