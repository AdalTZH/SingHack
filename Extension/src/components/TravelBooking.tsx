import { motion, AnimatePresence } from "motion/react";
import {
  Plane,
  Cloud,
  Sun,
  CloudRain,
  CloudSnow,
  Wind,
  Calendar,
  MapPin,
  Shield,
  Check,
  ArrowDown,
  X,
  Luggage,
  Utensils,
  Users,
  Clock,
  Droplets,
  Eye,
  CloudDrizzle,
  Mic,
  MicOff,
} from "lucide-react";
import { useState, useEffect } from "react";

// Mock data for the travel booking
const flightData = {
  outbound: {
    from: "SINGAPORE",
    fromCode: "SIN",
    to: "TOKYO",
    toCode: "NRT",
    flightNumber: "SQ638",
    time: "10:30",
    gate: "A12",
    status: "ON TIME",
    date: "15 Dec 2024",
    duration: "7h 15m",
    aircraft: "Boeing 787-10",
    seat: "12A",
    class: "Economy",
    baggage: "30kg",
    terminal: "Terminal 3",
  },
  return: {
    from: "TOKYO",
    fromCode: "NRT",
    to: "SINGAPORE",
    toCode: "SIN",
    flightNumber: "SQ637",
    time: "18:45",
    gate: "B08",
    status: "ON TIME",
    date: "19 Dec 2024",
    duration: "7h 30m",
    aircraft: "Boeing 787-10",
    seat: "12A",
    class: "Economy",
    baggage: "30kg",
    terminal: "Terminal 1",
  },
};

const weatherData = {
  temperature: "8°C",
  location: "Tokyo",
  condition: "Partly Cloudy",
  humidity: "65%",
  wind: "12 km/h",
  pressure: "1013 hPa",
  visibility: "10 km",
  uvIndex: 3,
  hourlyForecast: [
    {
      time: "12:00",
      temp: "7°",
      condition: "Cloudy",
      icon: "cloud",
    },
    {
      time: "15:00",
      temp: "9°",
      condition: "Partly Cloudy",
      icon: "partlyCloudy",
    },
    {
      time: "18:00",
      temp: "6°",
      condition: "Clear",
      icon: "clear",
    },
    {
      time: "21:00",
      temp: "4°",
      condition: "Clear",
      icon: "clear",
    },
  ],
  weeklyForecast: [
    {
      day: "Monday",
      high: "9°",
      low: "5°",
      condition: "Sunny",
      icon: "sun",
    },
    {
      day: "Tuesday",
      high: "7°",
      low: "3°",
      condition: "Cloudy",
      icon: "cloud",
    },
    {
      day: "Wednesday",
      high: "6°",
      low: "2°",
      condition: "Rainy",
      icon: "rain",
    },
    {
      day: "Thursday",
      high: "4°",
      low: "0°",
      condition: "Snow",
      icon: "snow",
    },
    {
      day: "Friday",
      high: "8°",
      low: "4°",
      condition: "Sunny",
      icon: "sun",
    },
    {
      day: "Saturday",
      high: "10°",
      low: "6°",
      condition: "Partly Cloudy",
      icon: "partlyCloudy",
    },
    {
      day: "Sunday",
      high: "11°",
      low: "7°",
      condition: "Sunny",
      icon: "sun",
    },
  ],
};

const itineraryData = [
  {
    day: "Day 1",
    date: "15 Dec",
    time: "14:00",
    activity: "Arrival & Check-in",
    location: "Shibuya Hotel",
    description:
      "Check into hotel and explore Shibuya crossing",
    details:
      "Arrive at Narita Airport, take the Narita Express to Tokyo Station (1h), then transfer to Shibuya (20 min). Check into the Shibuya Excel Hotel Tokyu. Evening stroll around Shibuya Crossing and Center Gai shopping street. Dinner at an izakaya.",
    budget: "$150",
    bookings:
      "Hotel: Shibuya Excel Hotel Tokyu - Confirmation #SH123456",
  },
  {
    day: "Day 2",
    date: "16 Dec",
    time: "09:00",
    activity: "Temple Tour",
    location: "Senso-ji Temple",
    description: "Visit historic Asakusa temple district",
    details:
      "Start early at Senso-ji Temple, Tokyo's oldest temple. Explore Nakamise Shopping Street for traditional souvenirs. Visit the nearby Asakusa Shrine and take a rickshaw ride. Lunch at a traditional soba restaurant. Afternoon visit to Tokyo Skytree for panoramic views.",
    budget: "$100",
    bookings:
      "Rickshaw Tour - 30min ride - Confirmation #RT789012",
  },
  {
    day: "Day 3",
    date: "17 Dec",
    time: "07:00",
    activity: "Mt. Fuji Trip",
    location: "Mt. Fuji 5th Station",
    description: "Day trip to Mount Fuji and Lake Kawaguchi",
    details:
      "Early morning departure for Mt. Fuji. Visit the 5th Station (weather permitting) for stunning views. Explore Lake Kawaguchi area, take the Mt. Fuji Panoramic Ropeway. Visit Oishi Park for photo opportunities. Return to Tokyo in the evening.",
    budget: "$200",
    bookings:
      "Mt. Fuji Day Tour - Bus & Guide - Confirmation #MF345678",
  },
  {
    day: "Day 4",
    date: "18 Dec",
    time: "10:00",
    activity: "Shopping Day",
    location: "Harajuku & Omotesando",
    description: "Explore trendy shopping districts",
    details:
      "Morning at Harajuku's Takeshita Street for quirky fashion and crepes. Visit Meiji Shrine for a peaceful break. Afternoon shopping at Omotesando Hills and designer boutiques. Evening in Shibuya for last-minute shopping and dinner. Pack for departure tomorrow.",
    budget: "$180",
    bookings:
      "Personal Shopping Guide - 3 hours - Confirmation #PS901234",
  },
];

const insuranceData = {
  name: "TravelGuard Premium",
  coverage: "$500K",
  cost: "$89.99",
  provider: "AXA Travel Insurance",
  policyNumber: "TG-2024-123456",
  validFrom: "15 Dec 2024",
  validTo: "19 Dec 2024",
  features: [
    {
      name: "Medical",
      covered: true,
      limit: "$500,000",
      description:
        "Emergency medical expenses, hospital stays, surgery",
    },
    {
      name: "Baggage",
      covered: true,
      limit: "$5,000",
      description:
        "Lost, stolen, or damaged luggage and personal items",
    },
    {
      name: "Cancellation",
      covered: true,
      limit: "$10,000",
      description:
        "Trip cancellation or interruption due to covered reasons",
    },
    {
      name: "Delay",
      covered: true,
      limit: "$1,500",
      description:
        "Flight delays over 6 hours, accommodation and meals",
    },
  ],
  additionalBenefits: [
    "24/7 Emergency Assistance Hotline",
    "Worldwide Coverage",
    "Adventure Sports Coverage (skiing, hiking)",
    "Rental Car Damage Coverage",
    "Personal Liability up to $100,000",
    "Emergency Evacuation & Repatriation",
  ],
  exclusions: [
    "Pre-existing medical conditions",
    "High-risk activities (skydiving, bungee jumping)",
    "Travel to sanctioned countries",
    "Intentional self-injury",
  ],
};

// Multiple insurance plans for comparison
const insurancePlans = [
  {
    id: 1,
    name: "Basic Protection",
    provider: "SafeTravel Insurance",
    cost: "$45.99",
    coverage: "$100K",
    rating: 4.2,
    features: [
      { name: "Medical", limit: "$100,000" },
      { name: "Baggage", limit: "$2,000" },
      { name: "Cancellation", limit: "$5,000" },
      { name: "Delay", limit: "$500" },
    ],
    benefits: ["24/7 Support", "Basic Coverage", "Emergency Medical"],
    highlight: "Budget Friendly",
  },
  {
    id: 2,
    name: "TravelGuard Premium",
    provider: "AXA Travel Insurance",
    cost: "$89.99",
    coverage: "$500K",
    rating: 4.8,
    features: [
      { name: "Medical", limit: "$500,000" },
      { name: "Baggage", limit: "$5,000" },
      { name: "Cancellation", limit: "$10,000" },
      { name: "Delay", limit: "$1,500" },
    ],
    benefits: [
      "24/7 Emergency Assistance",
      "Worldwide Coverage",
      "Adventure Sports (skiing, hiking)",
      "Rental Car Coverage",
    ],
    highlight: "Most Popular",
  },
  {
    id: 3,
    name: "Elite Adventure",
    provider: "WorldWide Protect",
    cost: "$149.99",
    coverage: "$1M",
    rating: 4.9,
    features: [
      { name: "Medical", limit: "$1,000,000" },
      { name: "Baggage", limit: "$10,000" },
      { name: "Cancellation", limit: "$20,000" },
      { name: "Delay", limit: "$3,000" },
    ],
    benefits: [
      "Extreme Sports Coverage",
      "Premium Medical Care",
      "Concierge Service",
      "Cancel for Any Reason",
    ],
    highlight: "Maximum Coverage",
  },
  {
    id: 4,
    name: "Family Shield",
    provider: "FamilyFirst Insurance",
    cost: "$129.99",
    coverage: "$750K",
    rating: 4.7,
    features: [
      { name: "Medical", limit: "$750,000" },
      { name: "Baggage", limit: "$7,500" },
      { name: "Cancellation", limit: "$15,000" },
      { name: "Delay", limit: "$2,000" },
    ],
    benefits: [
      "Family Discount",
      "Child Care Coverage",
      "Multi-Trip Discount",
      "Pet Coverage Available",
    ],
    highlight: "Best for Families",
  },
  {
    id: 5,
    name: "Senior Care Plus",
    provider: "GoldenYears Travel",
    cost: "$119.99",
    coverage: "$600K",
    rating: 4.6,
    features: [
      { name: "Medical", limit: "$600,000" },
      { name: "Baggage", limit: "$6,000" },
      { name: "Cancellation", limit: "$12,000" },
      { name: "Delay", limit: "$2,500" },
    ],
    benefits: [
      "Pre-existing Conditions",
      "Medical Equipment Coverage",
      "Extended Trip Protection",
      "Priority Medical Support",
    ],
    highlight: "Age 60+",
  },
];

// Analog flight display letter component
function FlipLetter({ char }: { char: string }) {
  return (
    <div className="relative inline-flex items-center justify-center w-[0.7em] h-[1.1em] bg-[#2a2a2a] rounded-[2px] shadow-[inset_0_1px_2px_rgba(0,0,0,0.5)] overflow-hidden">
      {/* Top half */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#3a3a3a] to-[#2a2a2a]" />
      {/* Split line */}
      <div className="absolute top-1/2 left-0 right-0 h-[1px] bg-black/50 z-10" />
      {/* Character */}
      <span className="relative z-20 text-[#e8d4a0] drop-shadow-[0_1px_1px_rgba(0,0,0,0.8)] tracking-[0.05em]">
        {char}
      </span>
    </div>
  );
}

// Analog display text
function AnalogText({
  text,
  size = "normal",
}: {
  text: string;
  size?: "normal" | "large";
}) {
  const fontSize =
    size === "large" ? "text-[1.2rem]" : "text-[0.8rem]";
  return (
    <div className={`inline-flex gap-[2px] ${fontSize}`}>
      {text.split("").map((char, index) => (
        <FlipLetter
          key={index}
          char={char === " " ? "\u00A0" : char}
        />
      ))}
    </div>
  );
}

type ExpandedCard =
  | "flight"
  | "itinerary"
  | "insurance"
  | "weather"
  | null;

interface TravelBookingProps {
  openInsuranceComparison?: boolean;
}

export function TravelBooking({ openInsuranceComparison = false }: TravelBookingProps) {
  const [expandedCard, setExpandedCard] =
    useState<ExpandedCard>(null);
  const [selectedPlans, setSelectedPlans] = useState<number[]>([]);
  const [showComparison, setShowComparison] = useState(false);

  // Auto-open insurance comparison when prop is true
  useEffect(() => {
    if (openInsuranceComparison) {
      setExpandedCard('insurance');
      setSelectedPlans([1, 2]); // Select first two plans by default
      setTimeout(() => {
        setShowComparison(true);
      }, 300);
    }
  }, [openInsuranceComparison]);

  const renderWeatherIcon = (
    icon: string,
    size: number = 4,
  ) => {
    const className = `w-${size} h-${size}`;
    switch (icon) {
      case "sun":
        return (
          <Sun className={className + " text-yellow-300"} />
        );
      case "cloud":
        return (
          <Cloud className={className + " text-white/60"} />
        );
      case "rain":
        return (
          <CloudRain className={className + " text-blue-300"} />
        );
      case "snow":
        return (
          <CloudSnow className={className + " text-cyan-200"} />
        );
      case "partlyCloudy":
        return (
          <Cloud className={className + " text-white/60"} />
        );
      case "clear":
        return (
          <Sun className={className + " text-yellow-300"} />
        );
      default:
        return (
          <Cloud className={className + " text-white/60"} />
        );
    }
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="min-h-screen px-4 pt-4 pb-32 overflow-y-auto"
      >
      <div className="max-w-7xl mx-auto w-full">
        <div className="flex gap-6">
          {/* Responsive Grid Layout - 3 cols on large, 2x2 on medium, 1 col on small */}
          <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 auto-rows-[minmax(150px,auto)]">
          {/* FLIGHT - Column 1, Smaller (2 rows on large, 1 row on medium/small) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            onClick={() => setExpandedCard("flight")}
            className="row-span-1 sm:row-span-1 lg:row-span-2 bg-white/10 backdrop-blur-lg border border-white/20 rounded-[8px] p-4 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] cursor-pointer hover:bg-white/15 transition-colors"
          >
            <div className="flex items-center gap-2 mb-4">
              <Plane className="w-4 h-4 text-white/80" />
              <h3 className="text-white text-sm">Flight</h3>
            </div>

            {/* OUTBOUND FLIGHT ONLY */}
            <div className="bg-[#1a1a1a] rounded-md p-3">
                <div className="text-white/40 text-[0.55rem] mb-3 flex items-center gap-1">
                  <ArrowDown className="w-3 h-3 rotate-[-45deg]" />
                  OUTBOUND
                </div>

                {/* Flight Number & Status */}
                <div className="flex items-center justify-between mb-4">
                  <div className="text-[0.6rem]">
                    <AnalogText
                      text={flightData.outbound.flightNumber}
                    />
                  </div>
                  <div className="text-white/60 text-[0.45rem] px-2 py-0.5 bg-green-500/20 rounded">
                    {flightData.outbound.status}
                  </div>
                </div>

                {/* FROM - Emphasized */}
                <div className="mb-4">
                  <div className="text-white/50 text-[0.45rem] mb-1">
                    FROM
                  </div>
                  <div className="mb-0.5">
                    <AnalogText
                      text={flightData.outbound.from}
                      size="large"
                    />
                  </div>
                  <div className="text-white/40 text-[0.65rem]">
                    {flightData.outbound.fromCode}
                  </div>
                </div>

                {/* Arrow Separator */}
                <div className="flex justify-center my-3">
                  <ArrowDown className="w-5 h-5 text-white/40" />
                </div>

                {/* TO - Emphasized */}
                <div className="mb-4">
                  <div className="text-white/50 text-[0.45rem] mb-1">
                    TO
                  </div>
                  <div className="mb-0.5">
                    <AnalogText
                      text={flightData.outbound.to}
                      size="large"
                    />
                  </div>
                  <div className="text-white/40 text-[0.65rem]">
                    {flightData.outbound.toCode}
                  </div>
                </div>

                {/* Time & Gate */}
                <div className="flex items-center justify-between pt-3 border-t border-white/10">
                  <div>
                    <div className="text-white/50 text-[0.45rem] mb-1">
                      TIME
                    </div>
                    <div className="text-[0.65rem]">
                      <AnalogText
                        text={flightData.outbound.time}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="text-white/50 text-[0.45rem] mb-1">
                      GATE
                    </div>
                    <div className="text-[0.65rem]">
                      <AnalogText
                        text={flightData.outbound.gate}
                      />
                    </div>
                  </div>
                </div>
              </div>

            {/* Click to see return flight hint */}
            <div className="mt-3 text-center">
              <div className="text-white/40 text-[0.6rem]">
                + Return flight • Click for details
              </div>
            </div>
          </motion.div>

          {/* ITINERARY - Column 2, Full Height (3 rows on large, 2 rows on medium, auto on small) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            onClick={() => setExpandedCard("itinerary")}
            className="row-span-1 sm:row-span-2 lg:row-span-3 bg-white/10 backdrop-blur-lg border border-white/20 rounded-[8px] p-4 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] cursor-pointer hover:bg-white/15 transition-colors"
          >
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="w-4 h-4 text-white/80" />
              <h3 className="text-white text-sm">Itinerary</h3>
            </div>

            <div className="space-y-3">
              {itineraryData.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="bg-white/5 rounded-md p-3 border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="text-white text-xs">
                        {item.day}
                      </div>
                      <div className="text-white/60 text-[0.65rem]">
                        {item.date}
                      </div>
                    </div>
                    <div className="text-white/50 text-[0.65rem]">
                      {item.time}
                    </div>
                  </div>
                  <div className="text-white text-sm mb-1">
                    {item.activity}
                  </div>
                  <div className="flex items-center gap-1 text-white/60 text-[0.65rem] mb-2">
                    <MapPin className="w-3 h-3" />
                    {item.location}
                  </div>
                  <div className="text-white/50 text-[0.65rem] leading-relaxed">
                    {item.description}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* INSURANCE - Column 3, Top 2 rows */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            onClick={() => setExpandedCard("insurance")}
            className="row-span-2 bg-white/10 backdrop-blur-lg border border-white/20 rounded-[8px] p-4 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] cursor-pointer hover:bg-white/15 transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-white/80" />
                <div>
                  <h3 className="text-white text-sm">
                    {insuranceData.name}
                  </h3>
                  <p className="text-white/50 text-[0.6rem]">
                    {insuranceData.provider}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-white text-sm">
                  {insuranceData.cost}
                </div>
                <div className="text-white/60 text-[0.6rem]">
                  {insuranceData.coverage}
                </div>
              </div>
            </div>

            {/* Features with vertical layout for more space */}
            <div className="space-y-2">
              {insuranceData.features.map((feature, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-white/5 rounded-md p-2.5 border border-white/10 hover:bg-white/10 transition-colors"
                >
                  <span className="text-white/70 text-xs">
                    {feature.name}
                  </span>
                  <Check className="w-4 h-4 text-green-400" />
                </div>
              ))}
            </div>

            {/* Coverage Details */}
            <div className="mt-4 pt-4 border-t border-white/10">
              <div className="text-white/50 text-[0.6rem] mb-2">
                Coverage Details
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white/5 rounded-md p-2 border border-white/10">
                  <div className="text-white/60 text-[0.55rem]">
                    Max Coverage
                  </div>
                  <div className="text-white text-xs">
                    {insuranceData.coverage}
                  </div>
                </div>
                <div className="bg-white/5 rounded-md p-2 border border-white/10">
                  <div className="text-white/60 text-[0.55rem]">
                    Premium
                  </div>
                  <div className="text-white text-xs">
                    {insuranceData.cost}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* WEATHER - Column 3, Bottom 1 row */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            onClick={() => setExpandedCard("weather")}
            className="row-span-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-[8px] p-4 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] cursor-pointer hover:bg-white/15 transition-colors"
          >
            <div className="flex items-center gap-2 mb-3">
              <Cloud className="w-4 h-4 text-white/80" />
              <h3 className="text-white text-sm">Weather</h3>
            </div>

            {/* Compact Weather Display */}
            <div className="flex items-center justify-between">
              {/* Left: Location and Temp */}
              <div>
                  <div className="text-white/60 text-[0.6rem] mb-1">
                    {weatherData.location}
                  </div>
                  <div className="text-white text-2xl mb-0.5">
                    {weatherData.temperature}
                  </div>
                  <div className="text-white/50 text-[0.6rem]">
                    {weatherData.condition}
                  </div>
                </div>

                {/* Center: Animated Icon */}
                <div className="relative mx-4">
                  <motion.div
                    animate={{ y: [0, -3, 0] }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  >
                    <Cloud className="w-10 h-10 text-white/60" />
                  </motion.div>
                  <motion.div
                    className="absolute top-0 right-0"
                    animate={{
                      scale: [1, 1.15, 1],
                      opacity: [0.7, 1, 0.7],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  >
                    <Sun className="w-5 h-5 text-yellow-300/80" />
                  </motion.div>
                </div>

              {/* Right: Quick Stats */}
              <div className="space-y-1">
                <div className="flex items-center gap-1.5">
                  <CloudRain className="w-3 h-3 text-blue-300/70" />
                  <span className="text-white/70 text-[0.6rem]">
                    {weatherData.humidity}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Wind className="w-3 h-3 text-cyan-300/70" />
                  <span className="text-white/70 text-[0.6rem]">
                    {weatherData.wind}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
        </div>
      </div>

      {/* Expanded Card Modal */}
      <AnimatePresence>
        {expandedCard && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setExpandedCard(null)}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white/15 backdrop-blur-xl border border-white/30 rounded-[8px] p-6 shadow-[0_20px_60px_0_rgba(0,0,0,0.5)] max-w-4xl w-full max-h-[85vh] overflow-y-auto"
            >
              {/* Flight Expanded View */}
              {expandedCard === "flight" && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <Plane className="w-6 h-6 text-white/80" />
                      <h2 className="text-white text-xl">
                        Flight Details
                      </h2>
                    </div>
                    <button
                      onClick={() => setExpandedCard(null)}
                      className="text-white/60 hover:text-white transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>

                  <div className="space-y-6">
                    {/* OUTBOUND FLIGHT - Detailed */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <div className="flex items-center gap-2 mb-6">
                        <ArrowDown className="w-5 h-5 text-white/60 rotate-[-45deg]" />
                        <h3 className="text-white text-lg">
                          Outbound Flight
                        </h3>
                      </div>

                      <div className="grid grid-cols-2 gap-6">
                        {/* Left Column */}
                        <div className="space-y-4">
                          <div className="bg-[#1a1a1a] rounded-md p-4">
                            <div className="text-white/50 text-xs mb-2">
                              Flight Number
                            </div>
                            <div className="text-lg mb-3">
                              <AnalogText
                                text={
                                  flightData.outbound
                                    .flightNumber
                                }
                                size="large"
                              />
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="text-white/60 text-xs px-2 py-1 bg-green-500/20 rounded">
                                {flightData.outbound.status}
                              </div>
                              <div className="text-white/60 text-xs">
                                {flightData.outbound.date}
                              </div>
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="text-white/50 text-xs mb-3">
                              DEPARTURE
                            </div>
                            <div className="mb-2">
                              <AnalogText
                                text={flightData.outbound.from}
                                size="large"
                              />
                            </div>
                            <div className="text-white/60 text-sm mb-1">
                              {flightData.outbound.fromCode}
                            </div>
                            <div className="text-white text-xl mt-2">
                              {flightData.outbound.time}
                            </div>
                            <div className="text-white/50 text-xs mt-1">
                              {flightData.outbound.terminal}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="text-white/50 text-xs mb-3">
                              ARRIVAL
                            </div>
                            <div className="mb-2">
                              <AnalogText
                                text={flightData.outbound.to}
                                size="large"
                              />
                            </div>
                            <div className="text-white/60 text-sm mb-1">
                              {flightData.outbound.toCode}
                            </div>
                            <div className="text-white text-xl mt-2">
                              17:45
                            </div>
                            <div className="text-white/50 text-xs mt-1">
                              Terminal 1
                            </div>
                          </div>
                        </div>

                        {/* Right Column */}
                        <div className="space-y-4">
                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Clock className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                DURATION
                              </div>
                            </div>
                            <div className="text-white text-lg">
                              {flightData.outbound.duration}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Plane className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                AIRCRAFT
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              {flightData.outbound.aircraft}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Users className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                SEAT & CLASS
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              Seat {flightData.outbound.seat} -{" "}
                              {flightData.outbound.class}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Luggage className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                BAGGAGE
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              {flightData.outbound.baggage}{" "}
                              checked
                            </div>
                            <div className="text-white/60 text-xs mt-1">
                              + 7kg cabin bag
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Utensils className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                MEAL SERVICE
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              Lunch included
                            </div>
                            <div className="text-white/60 text-xs mt-1">
                              Special meal: Vegetarian
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 p-4 bg-blue-500/10 rounded-md border border-blue-500/20">
                        <div className="text-blue-200 text-xs">
                          ✓ Online check-in opens 48 hours
                          before departure
                        </div>
                      </div>
                    </div>

                    {/* RETURN FLIGHT - Detailed */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <div className="flex items-center gap-2 mb-6">
                        <ArrowDown className="w-5 h-5 text-white/60 rotate-[135deg]" />
                        <h3 className="text-white text-lg">
                          Return Flight
                        </h3>
                      </div>

                      <div className="grid grid-cols-2 gap-6">
                        {/* Left Column */}
                        <div className="space-y-4">
                          <div className="bg-[#1a1a1a] rounded-md p-4">
                            <div className="text-white/50 text-xs mb-2">
                              Flight Number
                            </div>
                            <div className="text-lg mb-3">
                              <AnalogText
                                text={
                                  flightData.return.flightNumber
                                }
                                size="large"
                              />
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="text-white/60 text-xs px-2 py-1 bg-green-500/20 rounded">
                                {flightData.return.status}
                              </div>
                              <div className="text-white/60 text-xs">
                                {flightData.return.date}
                              </div>
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="text-white/50 text-xs mb-3">
                              DEPARTURE
                            </div>
                            <div className="mb-2">
                              <AnalogText
                                text={flightData.return.from}
                                size="large"
                              />
                            </div>
                            <div className="text-white/60 text-sm mb-1">
                              {flightData.return.fromCode}
                            </div>
                            <div className="text-white text-xl mt-2">
                              {flightData.return.time}
                            </div>
                            <div className="text-white/50 text-xs mt-1">
                              {flightData.return.terminal}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="text-white/50 text-xs mb-3">
                              ARRIVAL
                            </div>
                            <div className="mb-2">
                              <AnalogText
                                text={flightData.return.to}
                                size="large"
                              />
                            </div>
                            <div className="text-white/60 text-sm mb-1">
                              {flightData.return.toCode}
                            </div>
                            <div className="text-white text-xl mt-2">
                              02:15
                            </div>
                            <div className="text-white/50 text-xs mt-1">
                              Terminal 3
                            </div>
                          </div>
                        </div>

                        {/* Right Column */}
                        <div className="space-y-4">
                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Clock className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                DURATION
                              </div>
                            </div>
                            <div className="text-white text-lg">
                              {flightData.return.duration}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Plane className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                AIRCRAFT
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              {flightData.return.aircraft}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Users className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                SEAT & CLASS
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              Seat {flightData.return.seat} -{" "}
                              {flightData.return.class}
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Luggage className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                BAGGAGE
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              {flightData.return.baggage}{" "}
                              checked
                            </div>
                            <div className="text-white/60 text-xs mt-1">
                              + 7kg cabin bag
                            </div>
                          </div>

                          <div className="bg-white/5 rounded-md p-4 border border-white/10">
                            <div className="flex items-center gap-2 mb-3">
                              <Utensils className="w-4 h-4 text-white/60" />
                              <div className="text-white/50 text-xs">
                                MEAL SERVICE
                              </div>
                            </div>
                            <div className="text-white text-sm">
                              Dinner included
                            </div>
                            <div className="text-white/60 text-xs mt-1">
                              Special meal: Vegetarian
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4 p-4 bg-blue-500/10 rounded-md border border-blue-500/20">
                        <div className="text-blue-200 text-xs">
                          ✓ Online check-in opens 48 hours
                          before departure
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Itinerary Expanded View */}
              {expandedCard === "itinerary" && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <Calendar className="w-6 h-6 text-white/80" />
                      <h2 className="text-white text-xl">
                        Detailed Itinerary
                      </h2>
                    </div>
                    <button
                      onClick={() => setExpandedCard(null)}
                      className="text-white/60 hover:text-white transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>

                  <div className="space-y-4">
                    {itineraryData.map((item, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-white/10 rounded-lg p-6 border border-white/20"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <div className="text-white text-lg mb-1">
                              {item.day}
                            </div>
                            <div className="text-white/60 text-sm">
                              {item.date}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center gap-2 text-white/60 text-sm">
                              <Clock className="w-4 h-4" />
                              {item.time}
                            </div>
                          </div>
                        </div>

                        <div className="text-white text-xl mb-3">
                          {item.activity}
                        </div>

                        <div className="flex items-center gap-2 text-white/70 mb-4">
                          <MapPin className="w-4 h-4" />
                          <span className="text-sm">
                            {item.location}
                          </span>
                        </div>

                        <div className="bg-white/5 rounded-md p-4 border border-white/10 mb-4">
                          <div className="text-white/50 text-xs mb-2">
                            OVERVIEW
                          </div>
                          <div className="text-white/80 text-sm leading-relaxed">
                            {item.description}
                          </div>
                        </div>

                        <div className="bg-white/5 rounded-md p-4 border border-white/10 mb-4">
                          <div className="text-white/50 text-xs mb-2">
                            DETAILED PLAN
                          </div>
                          <div className="text-white/80 text-sm leading-relaxed">
                            {item.details}
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-white/5 rounded-md p-3 border border-white/10">
                            <div className="text-white/50 text-xs mb-1">
                              ESTIMATED BUDGET
                            </div>
                            <div className="text-white text-lg">
                              {item.budget}
                            </div>
                          </div>
                          <div className="bg-white/5 rounded-md p-3 border border-white/10">
                            <div className="text-white/50 text-xs mb-1">
                              BOOKINGS
                            </div>
                            <div className="text-white/80 text-xs leading-relaxed">
                              {item.bookings}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  <div className="mt-6 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                    <div className="text-green-200 text-sm">
                      <strong>Total Estimated Budget:</strong>{" "}
                      $630 (excluding flights and accommodation)
                    </div>
                  </div>
                </div>
              )}

              {/* Insurance Expanded View */}
              {expandedCard === "insurance" && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <Shield className="w-6 h-6 text-white/80" />
                      <h2 className="text-white text-xl">
                        Insurance Policy Details
                      </h2>
                    </div>
                    <button
                      onClick={() => setExpandedCard(null)}
                      className="text-white/60 hover:text-white transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>

                  <div className="space-y-6">
                    {/* Policy Overview */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        Policy Overview
                      </h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/5 rounded-md p-4 border border-white/10">
                          <div className="text-white/50 text-xs mb-1">
                            PLAN NAME
                          </div>
                          <div className="text-white text-sm">
                            {insuranceData.name}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-4 border border-white/10">
                          <div className="text-white/50 text-xs mb-1">
                            PROVIDER
                          </div>
                          <div className="text-white text-sm">
                            {insuranceData.provider}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-4 border border-white/10">
                          <div className="text-white/50 text-xs mb-1">
                            POLICY NUMBER
                          </div>
                          <div className="text-white text-sm">
                            {insuranceData.policyNumber}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-4 border border-white/10">
                          <div className="text-white/50 text-xs mb-1">
                            PREMIUM COST
                          </div>
                          <div className="text-white text-lg">
                            {insuranceData.cost}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-4 border border-white/10">
                          <div className="text-white/50 text-xs mb-1">
                            VALID FROM
                          </div>
                          <div className="text-white text-sm">
                            {insuranceData.validFrom}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-4 border border-white/10">
                          <div className="text-white/50 text-xs mb-1">
                            VALID TO
                          </div>
                          <div className="text-white text-sm">
                            {insuranceData.validTo}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Coverage Details */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        Coverage Details
                      </h3>
                      <div className="space-y-3">
                        {insuranceData.features.map(
                          (feature, index) => (
                            <div
                              key={index}
                              className="bg-white/5 rounded-md p-4 border border-white/10"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                  <Check className="w-5 h-5 text-green-400" />
                                  <span className="text-white text-sm">
                                    {feature.name}
                                  </span>
                                </div>
                                <span className="text-white text-sm">
                                  {feature.limit}
                                </span>
                              </div>
                              <div className="text-white/60 text-xs ml-8">
                                {feature.description}
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                    </div>

                    {/* Additional Benefits */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        Additional Benefits
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        {insuranceData.additionalBenefits.map(
                          (benefit, index) => (
                            <div
                              key={index}
                              className="flex items-start gap-2 bg-white/5 rounded-md p-3 border border-white/10"
                            >
                              <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                              <span className="text-white/80 text-xs">
                                {benefit}
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    </div>

                    {/* Exclusions */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        Policy Exclusions
                      </h3>
                      <div className="space-y-2">
                        {insuranceData.exclusions.map(
                          (exclusion, index) => (
                            <div
                              key={index}
                              className="flex items-start gap-2 bg-red-500/10 rounded-md p-3 border border-red-500/20"
                            >
                              <X className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                              <span className="text-white/80 text-xs">
                                {exclusion}
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    </div>

                    {/* Emergency Contact */}
                    <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
                      <div className="text-blue-200 text-sm">
                        <strong>
                          24/7 Emergency Assistance:
                        </strong>{" "}
                        +1-800-TRAVEL-GUARD
                      </div>
                      <div className="text-blue-200/70 text-xs mt-1">
                        Keep your policy number handy when
                        calling: {insuranceData.policyNumber}
                      </div>
                    </div>

                    {/* Insurance Plans Carousel */}
                    <div className="mt-6 pt-6 border-t border-white/10">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="text-white">
                              Available Insurance Plans
                            </h3>
                            {selectedPlans.length > 0 && (
                              <div className="text-white/60 text-sm">
                                {selectedPlans.length}/2 selected
                              </div>
                            )}
                          </div>

                          {/* Horizontal Scrolling Carousel */}
                          <div className="relative">
                            <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide">
                              {insurancePlans.map((plan, index) => {
                                const isSelected = selectedPlans.includes(plan.id);
                                return (
                                  <motion.div
                                    key={plan.id}
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className={`flex-shrink-0 w-80 snap-center bg-white/10 backdrop-blur-lg border rounded-[8px] p-5 transition-all ${
                                      isSelected
                                        ? "border-green-400 shadow-[0_0_20px_rgba(74,222,128,0.3)]"
                                        : "border-white/20"
                                    }`}
                                  >
                                    {/* Plan Header */}
                                    <div className="mb-4">
                                      {/* Highlight Badge at Top */}
                                      {plan.highlight && (
                                        <div className="flex justify-center mb-3">
                                          <span className="px-3 py-1 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-full text-yellow-200 text-xs">
                                            {plan.highlight}
                                          </span>
                                        </div>
                                      )}
                                      
                                      {/* Plan Name/Provider and Coverage/Rating */}
                                      <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                          <h4 className="text-white">
                                            {plan.name}
                                          </h4>
                                          <p className="text-white/60 text-xs mb-2">
                                            {plan.provider}
                                          </p>
                                          <div className="flex items-baseline gap-1">
                                            <span className="text-white text-2xl">
                                              {plan.cost}
                                            </span>
                                            <span className="text-white/50 text-xs">
                                              / trip
                                            </span>
                                          </div>
                                        </div>
                                        <div className="text-right">
                                          <div className="text-white text-2xl">
                                            {plan.coverage}
                                          </div>
                                          <div className="flex items-center gap-1 mt-1 text-yellow-400 text-xs justify-end">
                                            <span>★</span>
                                            <span>{plan.rating}</span>
                                          </div>
                                        </div>
                                      </div>
                                    </div>

                                    {/* Features */}
                                    <div className="space-y-2 mb-4">
                                      {plan.features.map((feature, idx) => (
                                        <div
                                          key={idx}
                                          className="flex items-center justify-between bg-white/5 rounded-md p-2 border border-white/10"
                                        >
                                          <span className="text-white/80 text-xs">
                                            {feature.name}
                                          </span>
                                          <span className="text-white/60 text-xs">
                                            {feature.limit}
                                          </span>
                                        </div>
                                      ))}
                                    </div>

                                    {/* Benefits */}
                                    <div className="mb-4">
                                      <div className="text-white/50 text-[0.6rem] mb-2">
                                        KEY BENEFITS
                                      </div>
                                      <div className="flex flex-wrap gap-1.5">
                                        {plan.benefits.slice(0, 3).map((benefit, idx) => (
                                          <span
                                            key={idx}
                                            className="px-2 py-1 bg-white/5 border border-white/10 rounded text-white/70 text-[0.6rem]"
                                          >
                                            {benefit}
                                          </span>
                                        ))}
                                      </div>
                                    </div>

                                    {/* Compare Button */}
                                    <button
                                      onClick={() => {
                                        if (isSelected) {
                                          setSelectedPlans(selectedPlans.filter(id => id !== plan.id));
                                        } else {
                                          if (selectedPlans.length < 2) {
                                            const newSelected = [...selectedPlans, plan.id];
                                            setSelectedPlans(newSelected);
                                            if (newSelected.length === 2) {
                                              setShowComparison(true);
                                            }
                                          }
                                        }
                                      }}
                                      disabled={!isSelected && selectedPlans.length >= 2}
                                      className={`w-full py-2.5 px-4 rounded-lg transition-all ${
                                        isSelected
                                          ? "bg-green-500 hover:bg-green-600 text-white"
                                          : selectedPlans.length >= 2
                                          ? "bg-white/5 text-white/30 cursor-not-allowed"
                                          : "bg-white/10 hover:bg-white/20 border border-white/20 text-white"
                                      }`}
                                    >
                                      {isSelected ? (
                                        <span className="flex items-center justify-center gap-2">
                                          <Check className="w-4 h-4" />
                                          Selected
                                        </span>
                                      ) : selectedPlans.length >= 2 ? (
                                        "Max 2 Plans"
                                      ) : (
                                        "Compare This Plan"
                                      )}
                                    </button>
                                  </motion.div>
                                );
                              })}
                            </div>
                          </div>

                          {/* Compare Action Button */}
                          {selectedPlans.length === 2 && !showComparison && (
                            <motion.button
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              onClick={() => setShowComparison(true)}
                              className="w-full mt-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all shadow-lg"
                            >
                              Compare {selectedPlans.length} Selected Plans
                            </motion.button>
                          )}

                      </div>
                  </div>
                </div>
              )}

              {/* Weather Expanded View */}
              {expandedCard === "weather" && (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <Cloud className="w-6 h-6 text-white/80" />
                      <h2 className="text-white text-xl">
                        Weather Forecast -{" "}
                        {weatherData.location}
                      </h2>
                    </div>
                    <button
                      onClick={() => setExpandedCard(null)}
                      className="text-white/60 hover:text-white transition-colors"
                    >
                      <X className="w-6 h-6" />
                    </button>
                  </div>

                  <div className="space-y-6">
                    {/* Current Weather */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        Current Conditions
                      </h3>
                      <div className="flex items-center justify-between mb-6">
                        <div>
                          <div className="text-white text-5xl mb-2">
                            {weatherData.temperature}
                          </div>
                          <div className="text-white/70 text-lg">
                            {weatherData.condition}
                          </div>
                          <div className="text-white/50 text-sm">
                            {weatherData.location}
                          </div>
                        </div>
                        <div className="relative">
                          <motion.div
                            animate={{ y: [0, -5, 0] }}
                            transition={{
                              duration: 3,
                              repeat: Infinity,
                              ease: "easeInOut",
                            }}
                          >
                            <Cloud className="w-24 h-24 text-white/60" />
                          </motion.div>
                          <motion.div
                            className="absolute top-4 right-4"
                            animate={{
                              scale: [1, 1.2, 1],
                              opacity: [0.7, 1, 0.7],
                            }}
                            transition={{
                              duration: 2,
                              repeat: Infinity,
                              ease: "easeInOut",
                            }}
                          >
                            <Sun className="w-12 h-12 text-yellow-300/80" />
                          </motion.div>
                        </div>
                      </div>

                      <div className="grid grid-cols-4 gap-4">
                        <div className="bg-white/5 rounded-md p-3 border border-white/10">
                          <div className="flex items-center gap-2 mb-2">
                            <Droplets className="w-4 h-4 text-blue-300/70" />
                            <div className="text-white/50 text-xs">
                              HUMIDITY
                            </div>
                          </div>
                          <div className="text-white text-lg">
                            {weatherData.humidity}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-3 border border-white/10">
                          <div className="flex items-center gap-2 mb-2">
                            <Wind className="w-4 h-4 text-cyan-300/70" />
                            <div className="text-white/50 text-xs">
                              WIND
                            </div>
                          </div>
                          <div className="text-white text-lg">
                            {weatherData.wind}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-3 border border-white/10">
                          <div className="flex items-center gap-2 mb-2">
                            <CloudDrizzle className="w-4 h-4 text-white/60" />
                            <div className="text-white/50 text-xs">
                              PRESSURE
                            </div>
                          </div>
                          <div className="text-white text-lg">
                            {weatherData.pressure}
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-md p-3 border border-white/10">
                          <div className="flex items-center gap-2 mb-2">
                            <Eye className="w-4 h-4 text-white/60" />
                            <div className="text-white/50 text-xs">
                              VISIBILITY
                            </div>
                          </div>
                          <div className="text-white text-lg">
                            {weatherData.visibility}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Hourly Forecast */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        Hourly Forecast
                      </h3>
                      <div className="grid grid-cols-4 gap-4">
                        {weatherData.hourlyForecast.map(
                          (hour, index) => (
                            <div
                              key={index}
                              className="bg-white/5 rounded-md p-4 border border-white/10 text-center"
                            >
                              <div className="text-white/60 text-xs mb-2">
                                {hour.time}
                              </div>
                              <div className="flex justify-center mb-2">
                                {renderWeatherIcon(
                                  hour.icon,
                                  8,
                                )}
                              </div>
                              <div className="text-white text-lg mb-1">
                                {hour.temp}
                              </div>
                              <div className="text-white/50 text-xs">
                                {hour.condition}
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                    </div>

                    {/* Weekly Forecast */}
                    <div className="bg-white/10 rounded-lg p-6 border border-white/20">
                      <h3 className="text-white text-lg mb-4">
                        7-Day Forecast
                      </h3>
                      <div className="space-y-3">
                        {weatherData.weeklyForecast.map(
                          (day, index) => (
                            <div
                              key={index}
                              className="bg-white/5 rounded-md p-4 border border-white/10"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4 flex-1">
                                  <div className="text-white text-sm w-24">
                                    {day.day}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    {renderWeatherIcon(
                                      day.icon,
                                      5,
                                    )}
                                    <span className="text-white/70 text-sm">
                                      {day.condition}
                                    </span>
                                  </div>
                                </div>
                                <div className="flex items-center gap-4">
                                  <div className="text-white/50 text-sm">
                                    Low: {day.low}
                                  </div>
                                  <div className="text-white text-sm">
                                    High: {day.high}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                    </div>

                    {/* UV Index Info */}
                    <div className="p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
                      <div className="text-orange-200 text-sm">
                        <strong>UV Index:</strong>{" "}
                        {weatherData.uvIndex} (Moderate)
                      </div>
                      <div className="text-orange-200/70 text-xs mt-1">
                        Sunscreen recommended between 10 AM - 4
                        PM
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      </motion.div>

      {/* Insurance Comparison Modal */}
      <AnimatePresence>
        {showComparison && selectedPlans.length === 2 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => {
              setShowComparison(false);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-[8px] max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            >
              {/* Modal Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-white/20 bg-white/10 backdrop-blur-xl">
                <h2 className="text-white text-2xl font-bold">
                  Insurance Plan Comparison
                </h2>
                <button
                  onClick={() => {
                    setShowComparison(false);
                  }}
                  className="text-white/60 hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Side-by-Side Comparison */}
              <div className="overflow-y-auto p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {selectedPlans.map((planId) => {
                  const plan = insurancePlans.find(p => p.id === planId);
                  if (!plan) return null;

                  return (
                    <motion.div
                      key={plan.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-[8px] p-6 flex flex-col"
                    >
                      {/* Plan Header */}
                      <div className="text-center mb-6 pb-6 border-b border-white/10">
                        <h3 className="text-white text-2xl mb-2">
                          {plan.name}
                        </h3>
                        <p className="text-white/60 mb-3 text-sm">
                          {plan.provider}
                        </p>
                        <div className="text-white text-3xl mb-2">
                          {plan.cost}
                        </div>
                        <div className="text-white/50 text-sm">
                          Coverage: {plan.coverage}
                        </div>
                      </div>

                      {/* Features Grid - 2x2 Layout */}
                      <div className="mb-6">
                        <div className="text-white/50 text-xs tracking-wider mb-3">COVERAGE DETAILS</div>
                        <div className="grid grid-cols-2 gap-3">
                        {plan.features.map((feature, idx) => (
                          <div key={idx} className="bg-white/5 rounded-lg p-3 border border-white/10">
                            <div className="text-white/70 text-xs mb-1">
                              {feature.name}
                            </div>
                            <div className="text-white text-lg">
                              {feature.limit}
                            </div>
                          </div>
                        ))}
                        </div>
                      </div>

                      {/* Benefits - Flex Grow to Fill Space */}
                      <div className="mb-6 flex-1">
                        <div className="text-white/50 text-xs tracking-wider mb-3">KEY BENEFITS</div>
                        <div className="space-y-2">
                          {plan.benefits.map((benefit, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                              <div className="mt-0.5 flex-shrink-0">
                                <Check className="w-4 h-4 text-green-400" />
                              </div>
                              <span className="text-white/80 text-sm">
                                {benefit}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Select Button */}
                      <button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white py-3 px-6 rounded-lg transition-all shadow-lg hover:shadow-xl">
                        Select This Plan
                      </button>
                    </motion.div>
                  );
                })}
              </div>

              {/* Clear Selection Button */}
              <div className="mt-6 pt-6 border-t border-white/20 flex justify-center">
                <button
                  onClick={() => {
                    setSelectedPlans([]);
                    setShowComparison(false);
                  }}
                  className="text-white/60 hover:text-white transition-colors text-sm"
                >
                  Clear Selection & Close
                </button>
              </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}