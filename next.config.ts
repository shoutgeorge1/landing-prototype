import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "employmentlawassist.com",
        pathname: "/wp-content/uploads/**",
      },
    ],
  },
  async redirects() {
    return [
      {
        source: "/bakersfield/en/thank-you",
        destination: "/thank-you",
        permanent: true,
      },
      {
        source: "/bakersfield/es/gracias",
        destination: "/gracias",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
