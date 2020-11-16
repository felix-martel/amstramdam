const path = require("path");
const VueLoader = require('vue-loader');

module.exports = {
  mode: 'development',
  entry: {
    lobby: "./front/lobby.js",
    main: "./front/main.js"
  },
  output: {
    filename: "[name].js",
    path: path.resolve(__dirname, "amstramdam/static/script")
  },
  resolve: {
    alias: {
      vue: "vue/dist/vue.runtime.esm-bundler.js"
    }
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          'style-loader',
          'css-loader'
        ]
      },
      {
        test: /\.png$/,
        use: [
          'file-loader'
        ]
      },
      {
        test: /\.vue$/,
        loader: "vue-loader",
      }
    ]
  },
  plugins: [
      new VueLoader.VueLoaderPlugin(),
  ],
  devtool: 'inline-source-map',
}