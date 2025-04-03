module.exports = {
  transpileDependencies: [
    'vuetify',
    'chartjs-plugin-zoom'
  ],
  configureWebpack: {
    module: {
      rules: [
        {
          test: /\.m?js$/,
          include: /chartjs-plugin-zoom/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env'],
              plugins: [
                '@babel/plugin-proposal-optional-chaining',
                '@babel/plugin-proposal-nullish-coalescing-operator'
              ]
            }
          }
        }
      ]
    }
  },
  devServer: {
    port: 3000
  },
  chainWebpack: config => {
    config
      .plugin('html')
      .tap(args => {
        args[0].title = 'OpenCap Visualizer'
        return args
      })
  }
} 