import type { NextConfig } from "next";

const backendUrl = process.env.NEXT_PUBLIC_API_URL || "https://freightiq-api-dmtb.onrender.com";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/proxy/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
