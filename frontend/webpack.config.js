const webpack = require('webpack');
const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

const SRC = path.resolve(__dirname, 'src');
const BUILD = path.resolve(path.dirname(__dirname), 'web_pdb', 'static');

const config = {
  entry: SRC + '/index.js',
  output: {
    path: BUILD,
    filename: 'bundle.min.js'
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      'window.jQuery': 'jquery',
      tether: 'tether',
      Tether: 'tether',
      'window.Tether': 'tether',
    }),
    new MiniCssExtractPlugin({
      filename: 'styles.min.css'
    }),
    new CopyWebpackPlugin(
      [
        {
          from: 'node_modules/prismjs/themes/prism-*.css',
          to: BUILD + '/themes/[name].[ext]'
        },
      ]
    ),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['env', 'stage-3']
          }
        }
      },
      {
        test: /\.(svg|woff2?|ttf|eot)$/,
        use: {
          loader: 'file-loader',
          options: {
            name: './fonts/[name].[ext]'
          },
        },
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      }
    ]
  }
};

module.exports = config;
