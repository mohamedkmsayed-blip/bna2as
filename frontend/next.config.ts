import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'm.media-amazon.com',
      },
      {
        protocol: 'https',
        hostname: 'images-na.ssl-images-amazon.com',
      },
      {
        protocol: 'https',
        hostname: 'eg.jumia.is',
      },
      {
        protocol: 'https',
        hostname: '*.jumia.is',
      },
      {
        protocol: 'https',
        hostname: 'f.nooncdn.com',
      },
      {
        protocol: 'https',
        hostname: 'z.nooncdn.com',
      },
    ],
  },
};

export default nextConfig;
