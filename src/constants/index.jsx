import { ChartColumn, Home, NotepadText, Package, PackagePlus, Settings, ShoppingBag, UserCheck, UserPlus, Users } from "lucide-react";

import ProfileImage from "@/assets/profile-image.jpg";
import ProductImage from "@/assets/product-image.jpg";

export const navbarLinks = [
    {
        title: "Dashboard",
        links: [  {
            label: "G-Tron ChatBot",
            icon: Home,
            path: "/gtron"  // This will match the route in your router config
          },
          
            { label: "E-Waste Analytics", icon: Home, path: "/dataset/ewassteanalytics/wa" },
            { label: "Compliance Reports", icon: Home, path: "/compliance" },
            { 
                label: "ESG Tracking", 
                icon: Home, 
                path: "/esg" 
            },
           
            { 
                label: "EPR Tracking", 
                icon: Home, 
                path: "/epr" 
            },
            { label: "E-Waste Detection", icon: Home, path: "/e-wastedetection" },
        ],
    },
    {
        title: "E-Waste Management",
        links: [
            { label: "AI Waste Classification", icon: Home, path: "/classification" },
            { label: "Lifecycle Prediction", icon: Home, path: "/lifecycle" },
            { label: "Carbon  Prediction", icon: Home, path: "/carbon" },
            { label: "Toxic Material Detection", icon: Home, path: "/toxmat" },
        ],
    },
    {
        title: "Real-Time Monitoring",
        links: [
            { label: "Material Recovery", icon: Home, path: "/ma" },
            { label: "IoT Sensor Analytics", icon: Home, path: "/iotsensor" },
            { label: "Route Optimization", icon: Home, path: "/route" },
            { label: "Illegal Dumping Alerts", icon: Home, path: "/illegal" },
        ],
    },
    {
        title: "Marketplace",
        links: [
            { label: "Recyclers ", icon: Home, path: "/buyrecycle" },
            { label: "AI-Powered Pricing", icon: Home, path: "/pricing" },
            { label: "Sell E-Waste", icon: Home, path: "/" },
            { label: "Buy Recycled Materials", icon: Home, path: "/" },
            { label: "Refurbished Electronics", icon: Home, path: "/" },
           
        ],
    },
    // {
    //     title: "Compliance & Legal",
    //     links: [
    //         { label: "GDPR & RoHS Compliance", icon: Home, path: "/" },
    //         { label: "Automated Audits", icon: Home, path: "/" },
    //         { label: "ML-Based Risk Detection", icon: Home, path: "/" },
    //     ],
    // },
    // {
    //     title: "Smart Insights",
    //     links: [
    //         { label: "Recycling Efficiency Prediction", icon: Home, path: "/" },
    //         { label: "ML-Based Demand Forecasting", icon: Home, path: "/" },
    //         { label: "AI-Driven Policy Insights", icon: Home, path: "/" },
    //     ],
    // },
    // {
    //     title: "Industry Programs",
    //     links: [
    //         { label: "Consumer Buyback Programs", icon: Home, path: "/" },
    //         { label: "Government E-Waste Initiatives", icon: Home, path: "/" },
    //     ],
    // },
    {
        title: "Support & Assistance",
        links: [
          
            { label: "Help Center", icon: Home, path: "/" },
            { label: "Contact Support", icon: Home, path: "/" },
        ],
    },
    {
        title: "Settings",
        links: [
            { label: "Settings", icon: Home, path: "/" },
            { label: "User Management", icon: Home, path: "/" },
        ],
    },
];

export const overviewData = [
    { name: "Jan", total: 3200 },  // Tons of e-waste processed
    { name: "Feb", total: 4100 },
    { name: "Mar", total: 2900 },
    { name: "Apr", total: 5200 },
    { name: "May", total: 4500 },
    { name: "Jun", total: 6000 },
    { name: "Jul", total: 7000 },
    { name: "Aug", total: 7300 },
    { name: "Sep", total: 6200 },
    { name: "Oct", total: 5800 },
    { name: "Nov", total: 4900 },
    { name: "Dec", total: 5300 },
];


export const recentTransactionsData = [
    {
        id: 1,
        name: "EcoRecycle Solutions",
        email: "contact@ecorecycle.com",
        image: ProfileImage,
        total: 1200,  // Processed e-waste in kg
    },
    {
        id: 2,
        name: "GreenTech Recyclers",
        email: "support@greentechrecyclers.com",
        image: ProfileImage,
        total: 1850,
    },
    {
        id: 3,
        name: "Urban E-Waste Handlers",
        email: "info@urbanehandlers.com",
        image: ProfileImage,
        total: 3200,
    },
    {
        id: 4,
        name: "Circular Economy Pvt Ltd",
        email: "services@circulareconomy.com",
        image: ProfileImage,
        total: 2500,
    },
    {
        id: 5,
        name: "ZeroWaste Recycling Co.",
        email: "hello@zerowaste.com",
        image: ProfileImage,
        total: 3000,
    },
    {
        id: 6,
        name: "Smart E-Waste Disposal",
        email: "contact@smartewaste.com",
        image: ProfileImage,
        total: 4100,
    },
    {
        id: 7,
        name: "E-Cycle Industries",
        email: "team@ecycleindustries.com",
        image: ProfileImage,
        total: 5200,
    },
];


export const topEwasteItems = [
    {
        number: 1,
        name: "Old Smartphone",
        image: ProductImage, // Common Image
        description: "Obsolete smartphones with non-removable batteries.",
        price: 1500,
        status: "Recyclable",
        rating: 4.2,
    },
    {
        number: 2,
        name: "CRT Monitor",
        image: ProductImage, // Common Image
        description: "Heavy, outdated CRT monitors with lead glass.",
        price: 500,
        status: "Hazardous",
        rating: 3.5,
    },
    {
        number: 3,
        name: "Laptop Battery",
        image: ProductImage, // Common Image
        description: "Lithium-ion batteries that require special handling.",
        price: 700,
        status: "Recyclable",
        rating: 4.0,
    },
    {
        number: 4,
        name: "Worn-out Keyboard",
        image: ProductImage, // Common Image
        description: "Old keyboards with non-functional keys.",
        price: 300,
        status: "Recyclable",
        rating: 4.5,
    },
    {
        number: 5,
        name: "Broken LED TV",
        image: ProductImage, // Common Image
        description: "Damaged LED TV panels with mercury backlights.",
        price: 1200,
        status: "Hazardous",
        rating: 3.8,
    },
    {
        number: 6,
        name: "Used Printer",
        image: ProductImage, // Common Image
        description: "Inkjet printers with non-refillable cartridges.",
        price: 850,
        status: "Recyclable",
        rating: 4.1,
    },
    {
        number: 7,
        name: "Old Refrigerators",
        image: ProductImage, // Common Image
        description: "Refrigerators containing CFC gases.",
        price: 2000,
        status: "Hazardous",
        rating: 3.2,
    },
    {
        number: 8,
        name: "Copper Wires",
        image: ProductImage, // Common Image
        description: "Scrap copper wires from electronic circuits.",
        price: 2500,
        status: "Recyclable",
        rating: 4.9,
    },
    {
        number: 9,
        name: "Used Circuit Boards",
        image: ProductImage, // Common Image
        description: "Printed circuit boards with gold and silver traces.",
        price: 3500,
        status: "Recyclable",
        rating: 4.7,
    },
    {
        number: 10,
        name: "Defective Hard Drives",
        image: ProductImage, // Common Image
        description: "Old HDDs with rare earth magnets and metal casings.",
        price: 1000,
        status: "Recyclable",
        rating: 4.3,
    },
];
