/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router is stable in Next.js 15, no need for experimental flag
  eslint: {
    // During builds, ESLint will be run on the entire project
    ignoreDuringBuilds: false,
  },
  typescript: {
    // Type checking is done in a separate process during development
    ignoreBuildErrors: false,
  },
}

module.exports = nextConfig