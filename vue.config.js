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
  },

  // Add PWA configuration
  pwa: {
    name: 'OpenCap Visualizer',
    short_name: 'OpenCapViz', // Shorter name for home screens
    themeColor: '#1E1E1E', // Dark background from your styles
    msTileColor: '#000000', // Black tile for Windows
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',

    // configure the workbox plugin
    workboxPluginMode: 'GenerateSW', // Use GenerateSW for simplicity initially
    workboxOptions: {
      // swSrc is required in InjectManifest mode.
      // skipWaiting: true, // Optional: forces the waiting service worker to become the active service worker
      // clientsClaim: true, // Optional: claims clients for the active service worker
    },

    // manifest configuration
    manifestOptions: {
      display: 'standalone', // Makes the app feel more native
      background_color: '#1E1E1E', // Match theme color
      // Icons will be automatically generated based on public/img/icons/android-chrome-*.png
      // Make sure you have a 512x512 icon there for best results.
      icons: [
        // Example - the plugin usually handles this based on files in public/img/icons
        {
          'src': '/img/icons/android-chrome-192x192.png',
          'sizes': '192x192',
          'type': 'image/png'
        },
        {
          'src': '/img/icons/android-chrome-512x512.png',
          'sizes': '512x512',
          'type': 'image/png'
        },
        {
          'src': '/img/icons/android-chrome-maskable-192x192.png',
          'sizes': '192x192',
          'type': 'image/png',
          'purpose': 'maskable'
        },
        {
          'src': '/img/icons/android-chrome-maskable-512x512.png',
          'sizes': '512x512',
          'type': 'image/png',
          'purpose': 'maskable'
        }
      ]
    },

    // Icon paths configuration (if needed, often automatic)
    iconPaths: {
      favicon32: 'img/icons/favicon-32x32.png',
      favicon16: 'img/icons/favicon-16x16.png',
      appleTouchIcon: 'img/icons/apple-touch-icon-152x152.png',
      maskIcon: 'img/icons/safari-pinned-tab.svg',
      msTileImage: 'img/icons/msapplication-icon-144x144.png'
    }
  }
} 