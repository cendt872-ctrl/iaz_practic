export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        uaf: {
          mundyr: '#4D4634',
          gold: '#F39200',
          step: '#6A653A',
          sky: '#293757',
          eskadra: '#111224',
          steel: '#707276',
          wave: '#035C6B',
          maroon: '#671318',
          olive: '#444A38',
          vspred: '#E52421',
          darkbg: '#1E1C16',
          panel: '#2B281F'
        }
      },
      fontFamily: {
        sans: ['"UAF Sans"', 'Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
};
