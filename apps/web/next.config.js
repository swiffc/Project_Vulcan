/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    DESKTOP_SERVER_URL: process.env.DESKTOP_SERVER_URL || "http://localhost:8000",
  },
};

module.exports = nextConfig;
