
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      colors: {
        brand: {
          forest:    "#123B2A",
          DEFAULT:   "#16845B",
          light:     "#E6F3EB",
          text:      "#202923",
          secondary: "#68736C",
          border:    "#DDE5DE",
          bg:        "#F6F8F5",
        },
        status: {
          amber:     "#D99A22",
          "amber-bg":"#FEF3DC",
          red:       "#C94040",
          "red-bg":  "#FDEAEA",
          blue:      "#386CB0",
          "blue-bg": "#EBF0FB",
        },
      },
    },
  },
  plugins: [],
};
