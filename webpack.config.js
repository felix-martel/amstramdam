const path = require("path");

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
      }
    ]
  },
  devtool: 'inline-source-map',
}