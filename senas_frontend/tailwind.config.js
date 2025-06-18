// senas_frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}", // ¡Esta línea es crucial! Asegúrate de que apunte a tus archivos React.
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
