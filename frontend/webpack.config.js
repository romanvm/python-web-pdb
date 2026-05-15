const fs = require('fs');
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const SRC = path.resolve(__dirname, 'src');
const PROJECT_ROOT = path.dirname(__dirname);
const KODI_STATIC = path.resolve(PROJECT_ROOT, 'script.module.web-pdb', 'libs', 'web_pdb', 'static');
const DEFAULT_STATIC = path.resolve(PROJECT_ROOT, 'web_pdb', 'static');
const BUILD = fs.existsSync(path.dirname(KODI_STATIC)) ? KODI_STATIC : DEFAULT_STATIC;

const config = {
  entry: SRC + '/index.js',
  output: {
    path: BUILD,
    filename: 'bundle.min.js'
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'styles.min.css'
    })
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
      {
        test: /\.(svg|woff2?|ttf|eot)$/,
        type: 'asset/resource',
        generator: {
          filename: './fonts/[name][ext]'
        }
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
      }
    ]
  }
};

module.exports = config;
