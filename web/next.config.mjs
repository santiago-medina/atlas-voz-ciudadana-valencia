const isProd = process.env.NODE_ENV === 'production';
const repoName = 'atlas-voz-ciudadana-valencia';

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,
  // GitHub Pages serves at /<repo>/. For a custom domain (CNAME), set these to ''.
  basePath: isProd ? `/${repoName}` : '',
  assetPrefix: isProd ? `/${repoName}/` : '',
};

export default nextConfig;
