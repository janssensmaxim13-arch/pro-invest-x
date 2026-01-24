/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Disable server-side features for Tauri
  trailingSlash: true,
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : undefined,
}

module.exports = nextConfig
